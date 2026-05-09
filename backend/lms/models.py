from django.db import models


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
