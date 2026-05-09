"""
TDD Cycle 2 & 3: Model Tests
Test that Lesson and UserProgress models work correctly
"""
import pytest
from django.db import IntegrityError
from django.contrib.auth.models import User
from lms.models import Lesson, UserProgress


@pytest.mark.django_db
class TestLessonModel:
    """Tests for Lesson model"""

    def test_lesson_creation(self):
        """
        RED: Test that we can create a Lesson
        Should FAIL - Lesson model doesn't exist yet
        """
        lesson = Lesson.objects.create(
            lesson_id='module-00',
            title='LLM API Communication',
            subtitle='Learn the fundamentals',
            content='# Module 00 Content',
            module_number=0,
            order_index=1
        )

        assert lesson.id is not None, "Lesson should have an ID"
        assert lesson.lesson_id == 'module-00', "lesson_id should match"
        assert lesson.title == 'LLM API Communication', "Title should match"

    def test_lesson_str_representation(self):
        """
        RED: Test __str__ method
        Should FAIL - __str__ not implemented yet
        """
        lesson = Lesson.objects.create(
            lesson_id='module-01',
            title='Pydantic & Tool Use',
            content='Content',
            module_number=1,
            order_index=2
        )

        assert str(lesson) == 'module-01: Pydantic & Tool Use', "__str__ should return lesson_id: title"

    def test_lesson_id_is_unique(self):
        """
        RED: Test that lesson_id is unique
        Should FAIL - unique constraint not enforced yet
        """
        Lesson.objects.create(
            lesson_id='module-00',
            title='First',
            content='Content',
            module_number=0,
            order_index=1
        )

        with pytest.raises(IntegrityError):
            Lesson.objects.create(
                lesson_id='module-00',  # Duplicate lesson_id
                title='Second',
                content='Content',
                module_number=0,
                order_index=2
            )

    def test_lesson_ordering(self):
        """
        RED: Test that lessons are ordered by order_index
        Should FAIL - ordering not configured yet
        """
        Lesson.objects.create(lesson_id='module-02', title='Memory', content='C', module_number=2, order_index=3)
        Lesson.objects.create(lesson_id='module-00', title='LLM API', content='A', module_number=0, order_index=1)
        Lesson.objects.create(lesson_id='module-01', title='Pydantic', content='B', module_number=1, order_index=2)

        lessons = Lesson.objects.all()

        assert lessons[0].lesson_id == 'module-00', "First lesson should be module-00"
        assert lessons[1].lesson_id == 'module-01', "Second lesson should be module-01"
        assert lessons[2].lesson_id == 'module-02', "Third lesson should be module-02"

    def test_lesson_quiz_data_optional(self):
        """
        RED: Test that quiz_data is optional (can be null)
        Should FAIL - quiz_data field doesn't exist yet
        """
        lesson = Lesson.objects.create(
            lesson_id='module-00',
            title='Test',
            content='Content',
            module_number=0,
            order_index=1,
            quiz_data=None  # Should be allowed
        )

        assert lesson.quiz_data is None, "quiz_data should be allowed to be None"

    def test_lesson_with_quiz_data(self):
        """
        RED: Test that quiz_data can store JSON
        Should FAIL - JSONField not configured yet
        """
        quiz_data = {
            'questions': [
                {
                    'id': 'q1',
                    'question': 'What is an API?',
                    'answers': ['A', 'B', 'C'],
                    'correct': 0
                }
            ]
        }

        lesson = Lesson.objects.create(
            lesson_id='module-00',
            title='Test',
            content='Content',
            module_number=0,
            order_index=1,
            quiz_data=quiz_data
        )

        # Retrieve from database
        retrieved = Lesson.objects.get(lesson_id='module-00')
        assert retrieved.quiz_data == quiz_data, "quiz_data should be stored and retrieved as JSON"


@pytest.mark.django_db
class TestUserProgressModel:
    """Tests for UserProgress model"""

    def test_user_progress_creation(self):
        """
        RED: Test that we can create UserProgress
        Should FAIL - UserProgress model doesn't exist yet
        """
        user = User.objects.create_user(username='testuser', password='password123')
        lesson = Lesson.objects.create(
            lesson_id='module-00',
            title='Test Lesson',
            content='Content',
            module_number=0,
            order_index=1
        )

        progress = UserProgress.objects.create(
            user=user,
            lesson=lesson,
            completed=True
        )

        assert progress.id is not None, "UserProgress should have an ID"
        assert progress.user == user, "User should match"
        assert progress.lesson == lesson, "Lesson should match"
        assert progress.completed is True, "Completed should be True"

    def test_user_progress_unique_together(self):
        """
        RED: Test that user+lesson combination is unique
        Should FAIL - unique_together constraint not enforced yet
        """
        user = User.objects.create_user(username='testuser', password='password123')
        lesson = Lesson.objects.create(
            lesson_id='module-00',
            title='Test',
            content='Content',
            module_number=0,
            order_index=1
        )

        UserProgress.objects.create(user=user, lesson=lesson, completed=True)

        # Try to create duplicate
        with pytest.raises(IntegrityError):
            UserProgress.objects.create(user=user, lesson=lesson, completed=False)

    def test_user_progress_completed_at_timestamp(self):
        """
        RED: Test that completed_at is set when marking complete
        Should FAIL - completed_at field doesn't exist yet
        """
        user = User.objects.create_user(username='testuser', password='password123')
        lesson = Lesson.objects.create(
            lesson_id='module-00',
            title='Test',
            content='Content',
            module_number=0,
            order_index=1
        )

        progress = UserProgress.objects.create(
            user=user,
            lesson=lesson,
            completed=True
        )

        assert progress.completed_at is not None, "completed_at should be set when completed=True"

    def test_user_can_have_multiple_lesson_progress(self):
        """
        RED: Test that one user can have progress on multiple lessons
        Should FAIL - model doesn't exist yet
        """
        user = User.objects.create_user(username='testuser', password='password123')
        lesson1 = Lesson.objects.create(lesson_id='module-00', title='L1', content='C', module_number=0, order_index=1)
        lesson2 = Lesson.objects.create(lesson_id='module-01', title='L2', content='C', module_number=1, order_index=2)

        UserProgress.objects.create(user=user, lesson=lesson1, completed=True)
        UserProgress.objects.create(user=user, lesson=lesson2, completed=True)

        user_progress = UserProgress.objects.filter(user=user)
        assert user_progress.count() == 2, "User should have progress on 2 lessons"

    def test_multiple_users_can_progress_same_lesson(self):
        """
        RED: Test that multiple users can have progress on the same lesson
        Should FAIL - model doesn't exist yet
        """
        user1 = User.objects.create_user(username='user1', password='password123')
        user2 = User.objects.create_user(username='user2', password='password123')
        lesson = Lesson.objects.create(lesson_id='module-00', title='Test', content='C', module_number=0, order_index=1)

        UserProgress.objects.create(user=user1, lesson=lesson, completed=True)
        UserProgress.objects.create(user=user2, lesson=lesson, completed=False)

        lesson_progress = UserProgress.objects.filter(lesson=lesson)
        assert lesson_progress.count() == 2, "Same lesson should have progress for 2 users"

    def test_user_progress_str_representation(self):
        """
        RED: Test __str__ method
        Should FAIL - __str__ not implemented yet
        """
        user = User.objects.create_user(username='testuser', password='password123')
        lesson = Lesson.objects.create(lesson_id='module-00', title='Test', content='C', module_number=0, order_index=1)
        progress = UserProgress.objects.create(user=user, lesson=lesson, completed=True)

        assert str(progress) == 'testuser - module-00 (completed)', "__str__ should show user, lesson, and status"
