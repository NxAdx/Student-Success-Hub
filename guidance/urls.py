from django.urls import path
from . import views

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('create/', views.create_session, name='create_session'),
    path('<int:pk>/', views.session_detail, name='session_detail'),
    path('<int:pk>/book/', views.book_session, name='book_session'),
]
