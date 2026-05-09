from django.db import models
from django.contrib.auth.models import User


class Lesson(models.Model):
    """
    Lesson model - stores AI agent learning modules
    """
    lesson_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    module_number = models.IntegerField()
    order_index = models.IntegerField()
    quiz_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order_index']

    def __str__(self):
        return f"{self.lesson_id}: {self.title}"


class UserProgress(models.Model):
    """
    UserProgress model - tracks which lessons each user has completed
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name_plural = 'User Progress'

    def __str__(self):
        status = "completed" if self.completed else "incomplete"
        return f"{self.user.username} - {self.lesson.lesson_id} ({status})"

    def save(self, *args, **kwargs):
        """Auto-set completed_at when marking as completed"""
        if self.completed and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
