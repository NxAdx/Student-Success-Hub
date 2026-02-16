from django.contrib import admin
from .models import AlumniProfile, ConnectionRequest

@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'designation', 'industry', 'is_available_for_mentorship']
    list_filter = ['industry', 'is_available_for_mentorship']

@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at']
    list_filter = ['status']
