from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for Lesson model"""
    list_display = ['lesson_id', 'title', 'module_number', 'order_index', 'created_at']
    list_filter = ['module_number']
    search_fields = ['lesson_id', 'title', 'content']
    ordering = ['order_index']
    readonly_fields = ['created_at']
