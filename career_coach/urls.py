from django.urls import path
from . import views

app_name = 'career_coach'

urlpatterns = [
    path('', views.coach_landing, name='landing'),
    path('chat/', views.coach_chat, name='chat'),
    path('faq/', views.faq_list, name='faq'),
    path('history/', views.conversation_list, name='history'),
    # API endpoints
    path('api/chat/', views.coach_chat_api, name='chat_api'),
    path('api/key/', views.save_api_key, name='save_key'),
    path('api/validate-key/', views.validate_key_api, name='validate_key'),
    path('api/conversation/<int:pk>/', views.conversation_detail_api, name='conversation_detail'),
    path('api/conversation/<int:pk>/delete/', views.delete_conversation, name='delete_conversation'),
]
