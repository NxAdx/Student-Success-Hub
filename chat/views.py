from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from .models import ChatRoom, Message, Notification
from accounts.models import User


@login_required
def chat_list(request):
    dms = ChatRoom.objects.filter(participants=request.user, room_type='direct').prefetch_related('participants')
    groups = ChatRoom.objects.filter(room_type='group').prefetch_related('participants')
    support_groups = ChatRoom.objects.filter(room_type='support').prefetch_related('participants')
    return render(request, 'chat/chat_list.html', {
        'dms': dms,
        'groups': groups,
        'support_groups': support_groups,
    })


@login_required
def chat_room(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)
    
    # Access Control & Auto-Join for Groups/Support
    if room.room_type in ('group', 'support'):
        if request.user not in room.participants.all():
            room.participants.add(request.user)
    elif request.user not in room.participants.all():
        return redirect('chat_list')

    msgs = Message.objects.filter(room=room).select_related('sender').order_by('created_at')
    Message.objects.filter(room=room, is_read=False).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        if content:
            Message.objects.create(room=room, sender=request.user, content=content)
            return redirect('chat_room', pk=pk)
    
    other_participants = room.participants.exclude(id=request.user.id)
    other_user = other_participants.first()
    
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'messages_list': msgs,
        'other_user': other_user,
    })


@login_required
def create_support_group(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        if name:
            room = ChatRoom.objects.create(
                name=name,
                description=description,
                room_type='support',
                is_anonymous=True,
            )
            room.participants.add(request.user)
            messages.success(request, f'Support group "{name}" created!')
            return redirect('chat_room', pk=room.pk)
    return render(request, 'chat/create_support_group.html')


@login_required
def edit_room(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)
    if room.room_type in ('group', 'support') and request.user in room.participants.all():
        if request.method == 'POST':
            new_name = request.POST.get('name')
            if new_name:
                room.name = new_name
                room.save()
                messages.success(request, 'Group name updated!')
        return redirect('chat_room', pk=pk)
    return redirect('chat_list')


@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    rooms = ChatRoom.objects.filter(room_type='direct', participants=request.user).filter(participants=other_user)
    if rooms.exists():
        return redirect('chat_room', pk=rooms.first().pk)
    room = ChatRoom.objects.create(
        name=f"{request.user.username} & {other_user.username}",
        room_type='direct',
    )
    room.participants.add(request.user, other_user)
    return redirect('chat_room', pk=room.pk)


@login_required
def fetch_messages(request, pk):
    """AJAX endpoint for polling new messages"""
    room = get_object_or_404(ChatRoom, pk=pk, participants=request.user)
    after_id = request.GET.get('after', 0)
    msgs = Message.objects.filter(room=room, id__gt=int(after_id)).select_related('sender')
    data = [{
        'id': m.id,
        'sender': 'Anonymous' if room.is_anonymous and m.sender != request.user else m.sender.username,
        'sender_id': m.sender.id,
        'content': m.content,
        'created_at': m.created_at.strftime('%I:%M %p'),
        'timestamp': m.created_at.isoformat(),
        'is_mine': m.sender == request.user,
    } for m in msgs]
    return JsonResponse({'messages': data})


@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user)
    unread_count = notifs.filter(is_read=False).count()
    return render(request, 'chat/notifications.html', {
        'notifications': notifs[:30],
        'unread_count': unread_count,
    })


@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')


@login_required
def notification_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    msg_count = Message.objects.filter(room__participants=request.user, is_read=False).exclude(sender=request.user).count()
    return JsonResponse({'notification_count': count, 'message_count': msg_count})
