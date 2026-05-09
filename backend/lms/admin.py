from django.contrib import admin
from .models import Lesson, UserProgress


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lesson model"""
    list_display = ['lesson_id', 'title', 'module_number', 'order_index', 'created_at']
    list_filter = ['module_number']
    search_fields = ['lesson_id', 'title', 'content']
    ordering = ['order_index']
    readonly_fields = ['created_at']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """Admin interface for UserProgress model"""
    list_display = ['user', 'lesson', 'completed', 'completed_at']
    list_filter = ['completed', 'lesson']
    search_fields = ['user__username', 'lesson__lesson_id', 'lesson__title']
    readonly_fields = ['completed_at']
    autocomplete_fields = ['user', 'lesson']
