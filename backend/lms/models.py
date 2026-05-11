from django.contrib.auth.models import User
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


class Exam(models.Model):
    """
    Exam model - represents an exam that users can take
    """
    exam_id = models.CharField(max_length=50, unique=True, primary_key=True)
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    time_limit_minutes = models.IntegerField(default=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.exam_id}: {self.title}"


class ExamSession(models.Model):
    """
    ExamSession model - represents a user's exam attempt with time limit
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    completed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'exam'],
                condition=models.Q(completed=False),
                name='unique_active_session'
            )
        ]

    def is_expired(self):
        """Returns True if current time > expires_at"""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def time_remaining(self):
        """Returns minutes remaining (can be negative if expired)"""
        from django.utils import timezone
        delta = self.expires_at - timezone.now()
        return int(delta.total_seconds() / 60)

    def __str__(self):
        return f"{self.user.username} - {self.exam.exam_id} (started: {self.started_at})"


class ExamSubmission(models.Model):
    """
    ExamSubmission model - represents a code submission for grading
    """
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='submissions')
    language = models.CharField(max_length=20)  # 'c', 'python', 'typescript'
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10)  # 'pass', 'fail'
    test_results = models.JSONField()  # Detailed test results

    class Meta:
        ordering = ['-submitted_at']  # Most recent first

    def __str__(self):
        return f"{self.session.user.username} - {self.language} ({self.grade})"
