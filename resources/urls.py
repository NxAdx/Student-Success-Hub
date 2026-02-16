from django.urls import path
from . import views

urlpatterns = [
    path('', views.resource_list, name='resource_list'),
    path('add/', views.add_resource, name='add_resource'),
    path('<int:pk>/', views.resource_detail, name='resource_detail'),
    path('<int:pk>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
]
