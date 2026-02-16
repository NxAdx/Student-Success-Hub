from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:pk>/', views.chat_room, name='chat_room'),
    path('room/<int:pk>/edit/', views.edit_room, name='edit_room'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('room/<int:pk>/fetch/', views.fetch_messages, name='fetch_messages'),
    path('support/create/', views.create_support_group, name='create_support_group'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),
]

