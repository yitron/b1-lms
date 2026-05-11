"""
TDD Cycles 6-9: API Endpoint Tests
Test lessons and progress API endpoints
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from lms.models import Lesson, UserProgress


@pytest.mark.django_db
class TestLessonsAPI:
    """Tests for lessons API endpoints"""

    def test_get_lessons_returns_all_lessons(self):
        """
        RED: Test GET /api/lessons/ returns all lessons
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create test lessons
        Lesson.objects.create(
            lesson_id='module-00',
            title='LLM API Communication',
            content='Content 1',
            module_number=0,
            order_index=1
        )
        Lesson.objects.create(
            lesson_id='module-01',
            title='Pydantic & Tool Use',
            content='Content 2',
            module_number=1,
            order_index=2
        )

        response = client.get('/api/lessons/')

        assert response.status_code == 200, "Should return 200 OK"
        assert 'lessons' in response.data, "Should have lessons key"
        assert len(response.data['lessons']) == 2, "Should return 2 lessons"

    def test_get_lessons_returns_ordered_by_order_index(self):
        """
        RED: Test lessons are ordered by order_index
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create lessons in reverse order
        Lesson.objects.create(lesson_id='module-02', title='Memory', content='C', module_number=2, order_index=3)
        Lesson.objects.create(lesson_id='module-00', title='LLM API', content='A', module_number=0, order_index=1)
        Lesson.objects.create(lesson_id='module-01', title='Pydantic', content='B', module_number=1, order_index=2)

        response = client.get('/api/lessons/')

        lessons = response.data['lessons']
        assert lessons[0]['lesson_id'] == 'module-00', "First lesson should be module-00"
        assert lessons[1]['lesson_id'] == 'module-01', "Second lesson should be module-01"
        assert lessons[2]['lesson_id'] == 'module-02', "Third lesson should be module-02"

    def test_get_lessons_returns_empty_list_when_no_lessons(self):
        """
        RED: Test empty lessons returns empty array
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        response = client.get('/api/lessons/')

        assert response.status_code == 200, "Should return 200 OK even with no lessons"
        assert response.data['lessons'] == [], "Should return empty array"

    def test_get_lessons_does_not_require_authentication(self):
        """
        RED: Test lessons endpoint is public (no auth required)
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create a lesson
        Lesson.objects.create(lesson_id='module-00', title='Test', content='C', module_number=0, order_index=1)

        # Don't authenticate
        response = client.get('/api/lessons/')

        assert response.status_code == 200, "Should be accessible without authentication"

    def test_get_lessons_includes_quiz_data(self):
        """
        RED: Test lessons include quiz_data if present
        Should FAIL - serializer doesn't exist yet
        """
        client = APIClient()

        quiz_data = {
            'questions': [
                {'id': 'q1', 'question': 'What is an API?', 'answers': ['A', 'B'], 'correct': 0}
            ]
        }

        Lesson.objects.create(
            lesson_id='module-00',
            title='Test',
            content='Content',
            module_number=0,
            order_index=1,
            quiz_data=quiz_data
        )

        response = client.get('/api/lessons/')

        assert response.data['lessons'][0]['quiz_data'] == quiz_data, "Should include quiz_data"

    def test_get_lesson_detail_returns_single_lesson(self):
        """
        RED: Test GET /api/lessons/<lesson_id>/ returns specific lesson
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        Lesson.objects.create(
            lesson_id='module-00',
            title='LLM API Communication',
            subtitle='Learn the fundamentals',
            content='# Module 00 Content',
            module_number=0,
            order_index=1
        )

        response = client.get('/api/lessons/module-00/')

        assert response.status_code == 200, "Should return 200 OK"
        assert response.data['lesson_id'] == 'module-00', "Should return correct lesson"
        assert response.data['title'] == 'LLM API Communication', "Title should match"

    def test_get_lesson_detail_returns_404_for_nonexistent_lesson(self):
        """
        RED: Test lesson detail returns 404 for invalid ID
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        response = client.get('/api/lessons/nonexistent/')

        assert response.status_code == 404, "Should return 404 Not Found"

    def test_get_lesson_detail_does_not_require_authentication(self):
        """
        RED: Test lesson detail endpoint is public
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        Lesson.objects.create(lesson_id='module-00', title='Test', content='C', module_number=0, order_index=1)

        # Don't authenticate
        response = client.get('/api/lessons/module-00/')

        assert response.status_code == 200, "Should be accessible without authentication"


@pytest.mark.django_db
class TestProgressAPI:
    """Tests for progress API endpoints"""

    def test_get_progress_requires_authentication(self):
        """
        RED: Test GET /api/progress/ requires authentication
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        response = client.get('/api/progress/')

        assert response.status_code == 401, "Should return 401 Unauthorized"

    def test_get_progress_returns_user_progress(self):
        """
        RED: Test GET /api/progress/ returns authenticated user's progress
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create user and authenticate
        user = User.objects.create_user(username='testuser', password='password123')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Create lessons and progress
        lesson1 = Lesson.objects.create(lesson_id='module-00', title='L1', content='C', module_number=0, order_index=1)
        _lesson2 = Lesson.objects.create(lesson_id='module-01', title='L2', content='C', module_number=1, order_index=2)  # noqa: F841

        UserProgress.objects.create(user=user, lesson=lesson1, completed=True)

        response = client.get('/api/progress/')

        assert response.status_code == 200, "Should return 200 OK"
        assert 'progress' in response.data, "Should have progress key"
        assert len(response.data['progress']) == 1, "Should return 1 completed lesson"
        assert response.data['progress'][0]['lesson_id'] == 'module-00', "Should be module-00"

    def test_get_progress_returns_empty_for_new_user(self):
        """
        RED: Test GET /api/progress/ returns empty array for user with no progress
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        user = User.objects.create_user(username='testuser', password='password123')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = client.get('/api/progress/')

        assert response.status_code == 200, "Should return 200 OK"
        assert response.data['progress'] == [], "Should return empty array"

    def test_get_progress_only_returns_current_user_progress(self):
        """
        RED: Test that users only see their own progress
        Should FAIL - user isolation not implemented yet
        """
        client = APIClient()

        # Create two users
        user1 = User.objects.create_user(username='user1', password='password123')
        user2 = User.objects.create_user(username='user2', password='password123')

        # Create lesson
        lesson = Lesson.objects.create(lesson_id='module-00', title='L1', content='C', module_number=0, order_index=1)

        # User2 completes lesson
        UserProgress.objects.create(user=user2, lesson=lesson, completed=True)

        # Authenticate as user1
        token1 = Token.objects.create(user=user1)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token1.key}')

        response = client.get('/api/progress/')

        assert response.data['progress'] == [], "User1 should not see user2's progress"

    def test_mark_complete_requires_authentication(self):
        """
        RED: Test POST /api/progress/complete/ requires authentication
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        response = client.post('/api/progress/complete/', {'lesson_id': 'module-00'})

        assert response.status_code == 401, "Should return 401 Unauthorized"

    def test_mark_complete_creates_progress_record(self):
        """
        RED: Test POST /api/progress/complete/ marks lesson as complete
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create user and authenticate
        user = User.objects.create_user(username='testuser', password='password123')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Create lesson
        Lesson.objects.create(lesson_id='module-00', title='L1', content='C', module_number=0, order_index=1)

        response = client.post('/api/progress/complete/', {'lesson_id': 'module-00'})

        assert response.status_code == 200, "Should return 200 OK"

        # Verify progress was created
        progress = UserProgress.objects.get(user=user, lesson__lesson_id='module-00')
        assert progress.completed is True, "Lesson should be marked complete"
        assert progress.completed_at is not None, "completed_at should be set"

    def test_mark_complete_returns_404_for_invalid_lesson(self):
        """
        RED: Test marking non-existent lesson returns 404
        Should FAIL - validation not implemented yet
        """
        client = APIClient()

        user = User.objects.create_user(username='testuser', password='password123')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = client.post('/api/progress/complete/', {'lesson_id': 'nonexistent'})

        assert response.status_code == 404, "Should return 404 Not Found"

    def test_mark_complete_requires_lesson_id(self):
        """
        RED: Test marking complete without lesson_id returns 400
        Should FAIL - validation not implemented yet
        """
        client = APIClient()

        user = User.objects.create_user(username='testuser', password='password123')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = client.post('/api/progress/complete/', {})

        assert response.status_code == 400, "Should return 400 Bad Request"

    def test_mark_complete_idempotent(self):
        """
        RED: Test marking complete twice works (idempotent)
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        user = User.objects.create_user(username='testuser', password='password123')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        lesson = Lesson.objects.create(lesson_id='module-00', title='L1', content='C', module_number=0, order_index=1)

        # Mark complete twice
        client.post('/api/progress/complete/', {'lesson_id': 'module-00'})
        response = client.post('/api/progress/complete/', {'lesson_id': 'module-00'})

        assert response.status_code == 200, "Should still return 200 OK"

        # Verify only one progress record
        assert UserProgress.objects.filter(user=user, lesson=lesson).count() == 1, "Should have only 1 progress record"
