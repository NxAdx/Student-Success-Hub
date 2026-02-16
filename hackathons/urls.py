from django.urls import path
from . import views

urlpatterns = [
    path('', views.hackathon_list, name='hackathon_list'),
    path('<int:pk>/', views.hackathon_detail, name='hackathon_detail'),
    path('<int:hackathon_pk>/create-team/', views.create_team, name='create_team'),
    path('team/<int:pk>/', views.team_detail, name='team_detail'),
    path('team/<int:pk>/join/', views.join_team, name='join_team'),
    path('join-request/<int:pk>/<str:action>/', views.handle_join_request, name='handle_join_request'),
]
