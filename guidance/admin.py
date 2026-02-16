from django.contrib import admin
from .models import Session, SessionBooking

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'mentor', 'session_type', 'status', 'scheduled_at']
    list_filter = ['session_type', 'status']

@admin.register(SessionBooking)
class SessionBookingAdmin(admin.ModelAdmin):
    list_display = ['session', 'student', 'status', 'booked_at']
    list_filter = ['status']
