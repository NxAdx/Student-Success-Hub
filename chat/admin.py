from django.contrib import admin
from .models import ChatRoom, Message, Notification

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_type']
    list_filter = ['room_type']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read']
    list_filter = ['notification_type', 'is_read']
