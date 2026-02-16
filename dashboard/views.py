from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import User
from alumni.models import AlumniProfile
from resources.models import Resource
from guidance.models import Session, SessionBooking
from hackathons.models import Hackathon, TeamMember
from doubts.models import Question
from chat.models import Notification, ChatRoom
from django.db.models import Q


def landing_page(request):
    if request.user.is_authenticated:
        return dashboard_view(request)
    stats = {
        'students': User.objects.filter(role='student').count(),
        'alumni': User.objects.filter(role='alumni').count(),
        'resources': Resource.objects.count(),
        'questions': Question.objects.count(),
    }
    return render(request, 'dashboard/landing.html', {'stats': stats})


@login_required
def dashboard_view(request):
    now = timezone.now()
    context = {
        'upcoming_sessions': Session.objects.filter(scheduled_at__gte=now, status='upcoming')[:5],
        'my_bookings': SessionBooking.objects.filter(student=request.user).select_related('session')[:5],
        'recent_questions': Question.objects.all()[:5],
        'active_hackathons': Hackathon.objects.filter(is_active=True)[:3],
        'recent_resources': Resource.objects.all()[:5],
        'my_teams': TeamMember.objects.filter(user=request.user).select_related('team', 'team__hackathon')[:5],
        'notifications': Notification.objects.filter(user=request.user, is_read=False)[:5],
        'support_groups': ChatRoom.objects.filter(room_type='support')[:3],
        'stats': {
            'total_users': User.objects.count(),
            'total_resources': Resource.objects.count(),
            'total_questions': Question.objects.count(),
        },
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def search_view(request):
    query = request.GET.get('q', '')
    users = []
    resources = []
    questions = []
    groups = []
    
    
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    ).exclude(pk=request.user.pk)[:5]
    
    resources = Resource.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    )[:5]
    
    questions = Question.objects.filter(
        Q(title__icontains=query) | 
        Q(body__icontains=query)
    )[:5]

    groups = ChatRoom.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query),
        room_type='support'
    )[:5]
        
    return render(request, 'dashboard/search_results.html', {
        'query': query,
        'users': users,
        'resources': resources,
        'questions': questions,
        'groups': groups,
    })
