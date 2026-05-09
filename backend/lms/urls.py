"""
URL configuration for LMS API
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/signup/', views.signup, name='signup'),
]
