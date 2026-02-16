from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import AlumniProfile, ConnectionRequest
from chat.models import Notification
from accounts.models import User


@login_required
def alumni_list(request):
    query = request.GET.get('q', '')
    industry = request.GET.get('industry', '')
    alumni = AlumniProfile.objects.select_related('user').all()
    if query:
        alumni = alumni.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(company__icontains=query) |
            Q(expertise_areas__icontains=query)
        )
    if industry:
        alumni = alumni.filter(industry__icontains=industry)
    industries = AlumniProfile.objects.values_list('industry', flat=True).distinct().order_by('industry')
    return render(request, 'alumni/alumni_list.html', {
        'alumni': alumni,
        'query': query,
        'industry': industry,
        'industries': [i for i in industries if i],
    })


@login_required
def alumni_detail(request, pk):
    profile = get_object_or_404(AlumniProfile.objects.select_related('user'), pk=pk)
    connection = ConnectionRequest.objects.filter(
        Q(from_user=request.user, to_user=profile.user) |
        Q(from_user=profile.user, to_user=request.user)
    ).first()
    return render(request, 'alumni/alumni_detail.html', {
        'profile': profile,
        'connection': connection,
    })


@login_required
def send_connection(request, pk):
    profile = get_object_or_404(AlumniProfile, pk=pk)
    if request.method == 'POST':
        msg = request.POST.get('message', '')
        ConnectionRequest.objects.get_or_create(
            from_user=request.user,
            to_user=profile.user,
            defaults={'message': msg}
        )
        Notification.objects.create(
            user=profile.user,
            notification_type='connection',
            title='New Connection Request',
            message=f"{request.user.get_full_name() or request.user.username} sent you a connection request.",
            link=reverse('my_connections')
        )
        messages.success(request, 'Connection request sent!')
    return redirect('alumni_detail', pk=pk)


@login_required
def my_connections(request):
    sent = ConnectionRequest.objects.filter(from_user=request.user).select_related('to_user')
    received = ConnectionRequest.objects.filter(to_user=request.user).select_related('from_user')
    return render(request, 'alumni/my_connections.html', {
        'sent': sent,
        'received': received,
    })


@login_required
def handle_connection(request, pk, action):
    conn = get_object_or_404(ConnectionRequest, pk=pk, to_user=request.user)
    if action == 'accept':
        conn.status = 'accepted'
        conn.save()
        Notification.objects.create(
            user=conn.from_user,
            notification_type='connection',
            title='Connection Accepted',
            message=f"{request.user.get_full_name() or request.user.username} accepted your connection request.",
            link=reverse('my_connections')
        )
        messages.success(request, 'Connection accepted!')
    elif action == 'reject':
        conn.status = 'rejected'
        conn.save()
        messages.info(request, 'Connection declined.')
    return redirect('my_connections')
