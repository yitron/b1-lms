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
    # Exams
    path('exams/', views.list_exams, name='list-exams'),
    path('exams/start/', views.start_exam, name='start-exam'),
    path('exams/submit/', views.submit_exam, name='submit-exam'),
    path('exams/status/<str:exam_id>/', views.exam_status, name='exam-status'),
    path('exams/results/<str:exam_id>/', views.exam_results, name='exam-results'),
]
