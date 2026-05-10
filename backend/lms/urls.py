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
    # Lessons
    path('lessons/', views.lessons_list, name='lessons-list'),
    path('lessons/<str:lesson_id>/', views.lesson_detail, name='lesson-detail'),
    # Progress
    path('progress/', views.get_progress, name='get-progress'),
    path('progress/complete/', views.mark_complete, name='mark-complete'),
]
