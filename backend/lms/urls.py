"""
URL configuration for LMS API
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
]
