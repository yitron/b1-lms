"""
TDD Cycle 2: Lesson Model Tests
Test that Lesson model works correctly
"""
import pytest
from django.db import IntegrityError
from lms.models import Lesson


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
