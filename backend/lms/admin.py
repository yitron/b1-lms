from django.contrib import admin

from .models import Exam, ExamSession, ExamSubmission, Lesson, UserProgress


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


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin interface for Exam model"""
    list_display = ['exam_id', 'title', 'time_limit_minutes', 'created_at']
    search_fields = ['exam_id', 'title', 'instructions']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['exam_id']


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    """Admin interface for ExamSession model"""
    list_display = ['id', 'user', 'exam', 'started_at', 'expires_at', 'completed']
    list_filter = ['completed', 'exam']
    search_fields = ['user__username', 'exam__exam_id']
    readonly_fields = ['started_at']
    autocomplete_fields = ['user', 'exam']
    ordering = ['-started_at']


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for ExamSubmission model"""
    list_display = ['id', 'get_user', 'get_exam', 'language', 'grade', 'submitted_at']
    list_filter = ['language', 'grade']
    search_fields = ['session__user__username', 'session__exam__exam_id']
    readonly_fields = ['submitted_at']
    ordering = ['-submitted_at']

    def get_user(self, obj):
        return obj.session.user.username
    get_user.short_description = 'User'

    def get_exam(self, obj):
        return obj.session.exam.exam_id
    get_exam.short_description = 'Exam'
