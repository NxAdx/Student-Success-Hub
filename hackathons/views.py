from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Hackathon, Team, TeamMember, JoinRequest


@login_required
def hackathon_list(request):
    hackathons = Hackathon.objects.all()
    return render(request, 'hackathons/hackathon_list.html', {'hackathons': hackathons})


@login_required
def hackathon_detail(request, pk):
    hackathon = get_object_or_404(Hackathon, pk=pk)
    teams = Team.objects.filter(hackathon=hackathon).prefetch_related('members__user')
    my_membership = TeamMember.objects.filter(user=request.user, team__hackathon=hackathon).select_related('team').first()
    user_team = my_membership.team if my_membership else None
    return render(request, 'hackathons/hackathon_detail.html', {
        'hackathon': hackathon,
        'teams': teams,
        'user_team': user_team,
    })


@login_required
def create_team(request, hackathon_pk):
    hackathon = get_object_or_404(Hackathon, pk=hackathon_pk)
    if request.method == 'POST':
        team = Team.objects.create(
            hackathon=hackathon,
            name=request.POST.get('name', ''),
            description=request.POST.get('description', ''),
            leader=request.user,
            required_skills=request.POST.get('required_skills', ''),
        )
        TeamMember.objects.create(team=team, user=request.user, role='Leader')
        messages.success(request, 'Team created!')
        return redirect('team_detail', pk=team.pk)
    return render(request, 'hackathons/create_team.html', {'hackathon': hackathon})


@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team.objects.select_related('hackathon', 'leader'), pk=pk)
    members = TeamMember.objects.filter(team=team).select_related('user')
    is_leader = request.user == team.leader
    join_requests = JoinRequest.objects.filter(team=team, status='pending').select_related('user') if is_leader else None
    is_member = TeamMember.objects.filter(team=team, user=request.user).exists()
    has_requested = JoinRequest.objects.filter(team=team, user=request.user, status='pending').exists()
    return render(request, 'hackathons/team_detail.html', {
        'team': team,
        'members': members,
        'join_requests': join_requests,
        'is_member': is_member,
        'is_leader': is_leader,
        'has_requested': has_requested,
    })


@login_required
def join_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        JoinRequest.objects.get_or_create(
            team=team,
            user=request.user,
            defaults={'message': request.POST.get('message', '')}
        )
        messages.success(request, 'Join request sent!')
    return redirect('team_detail', pk=pk)


@login_required
def handle_join_request(request, pk, action):
    jr = get_object_or_404(JoinRequest, pk=pk, team__leader=request.user)
    if action == 'accept':
        jr.status = 'accepted'
        jr.save()
        TeamMember.objects.get_or_create(team=jr.team, user=jr.user)
        messages.success(request, f'{jr.user.username} added to team!')
    elif action == 'reject':
        jr.status = 'rejected'
        jr.save()
        messages.info(request, 'Join request declined.')
    return redirect('team_detail', pk=jr.team.pk)
