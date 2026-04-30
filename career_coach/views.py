import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import UserAPIKey, CoachConversation, CoachMessage, FAQEntry, CoachAnalytics
from .encryption import encrypt_api_key, decrypt_api_key
from .services import get_ai_response, is_likely_career_related, APIError, validate_api_key


def coach_landing(request):
    """Career Coach landing page with feature overview and FAQ preview."""
    faqs = FAQEntry.objects.filter(is_active=True)[:6]
    return render(request, 'career_coach/landing.html', {
        'faqs': faqs,
    })


def coach_chat(request):
    """Main chat interface — works for both authenticated and guest users."""
    context = {
        'has_key': False,
        'provider': None,
        'conversations': [],
    }
    
    if request.user.is_authenticated:
        # Check if user has a saved API key
        saved_keys = UserAPIKey.objects.filter(user=request.user)
        if saved_keys.exists():
            key_obj = saved_keys.first()
            context['has_key'] = True
            context['provider'] = key_obj.provider
        
        # Load conversation history
        context['conversations'] = CoachConversation.objects.filter(
            user=request.user, is_archived=False
        )[:20]
    
    return render(request, 'career_coach/chat.html', context)


@require_POST
def coach_chat_api(request):
    """AJAX endpoint — send a message and get AI response."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user_message = data.get('message', '').strip()
    provider = data.get('provider', 'openrouter')
    api_key = data.get('api_key', '')  # For guest users
    conversation_id = data.get('conversation_id')
    history = data.get('history', [])  # For guest users (client-side history)
    
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)
    
    if len(user_message) > 2000:
        return JsonResponse({'error': 'Message too long (max 2000 characters)'}, status=400)
    
    # ── Topic guardrail ──
    if not is_likely_career_related(user_message):
        return JsonResponse({
            'content': "I appreciate your curiosity! However, I'm your dedicated **Career Coach** — I focus exclusively on career guidance and professional development. Could you rephrase your question to be about your career journey? For example, I can help with resumes, interviews, skill planning, or career strategy. 🎯",
            'blocked': True,
        })
    
    # ── Resolve API key ──
    decrypted_key = None
    
    if request.user.is_authenticated:
        try:
            key_obj = UserAPIKey.objects.get(user=request.user, provider=provider)
            decrypted_key = decrypt_api_key(key_obj.encrypted_key)
            key_obj.last_used = timezone.now()
            key_obj.save(update_fields=['last_used'])
        except UserAPIKey.DoesNotExist:
            pass
    
    # Fall back to client-provided key (guest mode)
    if not decrypted_key:
        if not api_key:
            return JsonResponse({'error': 'No API key provided'}, status=401)
        decrypted_key = api_key
    
    # ── Build conversation messages ──
    conversation_messages = []
    
    if request.user.is_authenticated and conversation_id:
        # Load from database
        try:
            conversation = CoachConversation.objects.get(
                pk=conversation_id, user=request.user
            )
            for msg in conversation.messages.all():
                conversation_messages.append({
                    'role': msg.role,
                    'content': msg.content,
                })
        except CoachConversation.DoesNotExist:
            conversation = None
    else:
        # Use client-provided history (guest mode)
        conversation_messages = history[-10:]  # Last 10 messages for context
        conversation = None
    
    # Add current message
    conversation_messages.append({
        'role': 'user',
        'content': user_message,
    })
    
    # ── Call AI ──
    try:
        result = get_ai_response(provider, decrypted_key, conversation_messages)
    except APIError as e:
        return JsonResponse({'error': str(e)}, status=502)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred. Please try again.'}, status=500)
    
    # ── Save to DB (authenticated only) ──
    if request.user.is_authenticated:
        if not conversation:
            # Create new conversation
            title = user_message[:50] + ('...' if len(user_message) > 50 else '')
            conversation = CoachConversation.objects.create(
                user=request.user,
                title=title,
                provider=provider,
            )
        
        # Save user message
        CoachMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_message,
            token_count=result.get('usage', {}).get('prompt_tokens', 0),
        )
        
        # Save assistant response
        CoachMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['content'],
            token_count=result.get('usage', {}).get('completion_tokens', 0),
        )
        
        conversation.save()  # Update updated_at
    
    # ── Update analytics ──
    today = timezone.now().date()
    analytics, _ = CoachAnalytics.objects.get_or_create(
        date=today,
        provider_used=provider,
        defaults={'total_queries': 0}
    )
    analytics.total_queries += 1
    if result.get('elapsed_ms'):
        if analytics.avg_response_time_ms:
            analytics.avg_response_time_ms = (analytics.avg_response_time_ms + result['elapsed_ms']) // 2
        else:
            analytics.avg_response_time_ms = result['elapsed_ms']
    analytics.save()
    
    return JsonResponse({
        'content': result['content'],
        'conversation_id': conversation.pk if conversation else None,
        'model': result.get('model', ''),
    })


@require_POST
def save_api_key(request):
    """Save or update an API key for a logged-in user."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    provider = data.get('provider', '')
    api_key = data.get('api_key', '').strip()
    
    if provider not in ('openrouter', 'nvidia'):
        return JsonResponse({'error': 'Invalid provider'}, status=400)
    
    if not api_key:
        return JsonResponse({'error': 'API key is required'}, status=400)
    
    # Validate the key
    if not validate_api_key(provider, api_key):
        return JsonResponse({'error': 'Invalid API key. Please check and try again.'}, status=400)
    
    # Save encrypted
    encrypted = encrypt_api_key(api_key)
    UserAPIKey.objects.update_or_create(
        user=request.user,
        provider=provider,
        defaults={'encrypted_key': encrypted}
    )
    
    return JsonResponse({'success': True, 'message': 'API key saved successfully!'})


@require_POST
def validate_key_api(request):
    """Validate an API key without saving it."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    provider = data.get('provider', '')
    api_key = data.get('api_key', '').strip()
    
    if provider not in ('openrouter', 'nvidia'):
        return JsonResponse({'error': 'Invalid provider'}, status=400)
    
    is_valid = validate_api_key(provider, api_key)
    return JsonResponse({'valid': is_valid})


@login_required
def conversation_list(request):
    """View past conversations."""
    conversations = CoachConversation.objects.filter(
        user=request.user
    ).order_by('-updated_at')
    
    return render(request, 'career_coach/history.html', {
        'conversations': conversations,
    })


@login_required
def conversation_detail_api(request, pk):
    """AJAX: Load messages for a conversation."""
    conversation = get_object_or_404(
        CoachConversation, pk=pk, user=request.user
    )
    messages = [
        {
            'role': msg.role,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%I:%M %p'),
        }
        for msg in conversation.messages.all()
    ]
    return JsonResponse({
        'title': conversation.title,
        'messages': messages,
        'provider': conversation.provider,
    })


@login_required
def delete_conversation(request, pk):
    """Delete a conversation."""
    conversation = get_object_or_404(
        CoachConversation, pk=pk, user=request.user
    )
    if request.method == 'POST':
        conversation.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'POST required'}, status=405)


def faq_list(request):
    """Browse career FAQ."""
    category = request.GET.get('category', '')
    faqs = FAQEntry.objects.filter(is_active=True)
    if category:
        faqs = faqs.filter(category=category)
    
    categories = FAQEntry.CATEGORY_CHOICES
    
    return render(request, 'career_coach/faq.html', {
        'faqs': faqs,
        'categories': categories,
        'active_category': category,
    })
