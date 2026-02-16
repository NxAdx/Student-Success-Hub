from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .models import Session, SessionBooking
from chat.models import Notification


@login_required
def session_list(request):
    upcoming = Session.objects.filter(scheduled_at__gte=timezone.now(), status='upcoming').select_related('mentor')
    my_bookings = SessionBooking.objects.filter(student=request.user).select_related('session', 'session__mentor')
    return render(request, 'guidance/session_list.html', {
        'sessions': upcoming,
        'my_bookings': my_bookings,
    })


@login_required
def session_detail(request, pk):
    session = get_object_or_404(Session.objects.select_related('mentor'), pk=pk)
    is_booked = SessionBooking.objects.filter(session=session, student=request.user).exists()
    attendees = SessionBooking.objects.filter(session=session, status='confirmed').select_related('student')
    return render(request, 'guidance/session_detail.html', {
        'session': session,
        'is_booked': is_booked,
        'attendees': attendees,
    })


@login_required
def book_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if session.available_slots > 0:
        SessionBooking.objects.get_or_create(session=session, student=request.user)
        Notification.objects.create(
            user=session.mentor,
            notification_type='session',
            title='New Session Booking',
            message=f"{request.user.get_full_name() or request.user.username} booked your session '{session.title}'.",
            link=reverse('session_detail', args=[session.pk])
        )
        messages.success(request, 'Session booked successfully!')
    else:
        messages.warning(request, 'No available slots.')
    return redirect('session_detail', pk=pk)


@login_required
def create_session(request):
    # Only teachers, professionals, and alumni can create sessions
    if request.user.role not in ['teacher', 'professional', 'alumni']:
        messages.warning(request, 'Only Teachers, Professionals, and Alumni can create mentorship sessions.')
        return redirect('session_list')
    if request.method == 'POST':
        session = Session(
            mentor=request.user,
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            session_type=request.POST.get('session_type', 'one_on_one'),
            scheduled_at=request.POST.get('scheduled_at', ''),
            duration_minutes=int(request.POST.get('duration', 60)),
            max_participants=int(request.POST.get('max_participants', 1)),
            meeting_link=request.POST.get('meeting_link', ''),
        )
        session.save()
        messages.success(request, 'Session created!')
        return redirect('session_detail', pk=session.pk)
    return render(request, 'guidance/create_session.html')
