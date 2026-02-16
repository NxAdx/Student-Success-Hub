from django.urls import path
from . import views

urlpatterns = [
    path('', views.alumni_list, name='alumni_list'),
    path('<int:pk>/', views.alumni_detail, name='alumni_detail'),
    path('<int:pk>/connect/', views.send_connection, name='send_connection'),
    path('connections/', views.my_connections, name='my_connections'),
    path('connections/<int:pk>/<str:action>/', views.handle_connection, name='handle_connection'),
]
