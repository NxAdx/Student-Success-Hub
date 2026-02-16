from django.urls import path
from . import views

app_name = 'roadmaps'

urlpatterns = [
    path('', views.roadmap_list, name='roadmap_list'),
    path('create/', views.create_roadmap, name='create_roadmap'),
    path('<int:pk>/', views.roadmap_detail, name='roadmap_detail'),
    path('<int:pk>/edit/', views.edit_roadmap, name='edit_roadmap'),
    path('<int:pk>/node-progress/', views.toggle_node_progress, name='toggle_node_progress'),
    path('review/', views.admin_review, name='admin_review'),
    path('<int:pk>/approve/', views.approve_roadmap, name='approve_roadmap'),
    path('<int:pk>/reject/', views.reject_roadmap, name='reject_roadmap'),
]
