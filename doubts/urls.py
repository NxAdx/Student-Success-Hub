from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('ask/', views.ask_question, name='ask_question'),
    path('<int:pk>/', views.question_detail, name='question_detail'),
    path('<int:pk>/answer/', views.post_answer, name='post_answer'),
    path('answer/<int:pk>/upvote/', views.upvote_answer, name='upvote_answer'),
    path('answer/<int:pk>/best/', views.mark_best_answer, name='mark_best_answer'),
]
