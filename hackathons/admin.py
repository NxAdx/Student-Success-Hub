from django.contrib import admin
from .models import Hackathon, Team, TeamMember, JoinRequest

@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'hackathon', 'leader', 'is_open']

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role']

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'status']
    list_filter = ['status']
