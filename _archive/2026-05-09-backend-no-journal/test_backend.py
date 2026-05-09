"""
Backend Tests - TDD for B1 LMS
Test database, models, and Flask app
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database import init_db, get_db_connection
from backend.models import User
from backend.session import Session
from datetime import datetime, timedelta

try:
    from backend.app import create_app
except ImportError:
    create_app = None


class TestDatabase:
    """Test database initialization and connection"""

    def test_database_init_creates_tables(self):
        """
        RED: Test that init_db creates all required tables
        Should FAIL - no init_db function exists yet
        """
        # Clean up any existing test db
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        # Initialize database
        init_db(test_db)

        # Verify database file was created
        assert os.path.exists(test_db), "Database file should be created"

        # Verify tables exist
        conn = get_db_connection(test_db)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row['name'] for row in cursor.fetchall()}

        # Expected tables
        expected_tables = {'users', 'lessons', 'user_progress', 'quiz_results', 'comments', 'sessions'}
        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

        conn.close()
        os.remove(test_db)

    def test_database_connection_uses_row_factory(self):
        """
        RED: Test that get_db_connection returns connection with Row factory
        Should FAIL - no Row factory configured yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)
        conn = get_db_connection(test_db)

        assert conn is not None, "Connection should not be None"

        # Test Row factory by querying a table
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
        row = cursor.fetchone()

        # Row factory enables dict-like access
        assert hasattr(row, 'keys'), "Row should have keys() method (Row factory)"
        assert 'name' in row.keys(), "Row should support dict-like access"

        conn.close()
        os.remove(test_db)


class TestUser:
    """Test User model"""

    def test_user_create_saves_to_database(self):
        """
        RED: Test that User.create() saves user to database
        Should FAIL - no User model exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user
        user_id = User.create(test_db, 'testuser', 'password123', 'test@example.com')
        assert user_id > 0, "Should return user ID"

        # Verify user exists in database
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        assert user is not None, "User should exist in database"
        assert user['username'] == 'testuser'
        assert user['email'] == 'test@example.com'
        assert user['password_hash'] != 'password123', "Password should be hashed"

        conn.close()
        os.remove(test_db)

    def test_user_get_by_username_returns_user(self):
        """
        RED: Test that User.get_by_username() retrieves user
        Should FAIL - no get_by_username method exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user
        User.create(test_db, 'testuser', 'password123', 'test@example.com')

        # Get user by username
        user = User.get_by_username(test_db, 'testuser')

        assert user is not None, "Should return user"
        assert user['username'] == 'testuser'
        assert user['email'] == 'test@example.com'

        os.remove(test_db)

    def test_user_get_by_username_returns_none_if_not_found(self):
        """
        RED: Test that User.get_by_username() returns None for non-existent user
        Should FAIL - no get_by_username method exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Try to get non-existent user
        user = User.get_by_username(test_db, 'nonexistent')

        assert user is None, "Should return None for non-existent user"

        os.remove(test_db)


class TestSession:
    """Test Session model"""

    def test_session_create_saves_to_database(self):
        """
        RED: Test that Session.create() creates session with expiry
        Should FAIL - no Session model exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user
        user_id = User.create(test_db, 'testuser', 'password123')

        # Create session (expires in 24 hours)
        session_id = Session.create(test_db, user_id, expires_in_hours=24)

        assert session_id is not None, "Should return session ID"
        assert len(session_id) > 0, "Session ID should not be empty"

        # Verify session in database
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
        session = cursor.fetchone()

        assert session is not None, "Session should exist in database"
        assert session['user_id'] == user_id
        assert session['session_id'] == session_id

        conn.close()
        os.remove(test_db)

    def test_session_validate_returns_user_id_for_valid_session(self):
        """
        RED: Test that Session.validate() returns user_id for valid session
        Should FAIL - no validate method exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and session
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id, expires_in_hours=24)

        # Validate session
        validated_user_id = Session.validate(test_db, session_id)

        assert validated_user_id == user_id, "Should return correct user ID"

        os.remove(test_db)

    def test_session_validate_returns_none_for_expired_session(self):
        """
        RED: Test that Session.validate() returns None for expired session
        Should FAIL - no validate method exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and session with 0 hour expiry (immediately expired)
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id, expires_in_hours=0)

        # Validate expired session
        validated_user_id = Session.validate(test_db, session_id)

        assert validated_user_id is None, "Should return None for expired session"

        os.remove(test_db)

    def test_session_destroy_removes_session(self):
        """
        RED: Test that Session.destroy() removes session from database
        Should FAIL - no destroy method exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and session
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id, expires_in_hours=24)

        # Destroy session
        Session.destroy(test_db, session_id)

        # Verify session no longer validates
        validated_user_id = Session.validate(test_db, session_id)

        assert validated_user_id is None, "Should return None after session destroyed"

        os.remove(test_db)


class TestFlaskApp:
    """Test Flask application factory"""

    def test_create_app_returns_flask_instance(self):
        """
        RED: Test that create_app() returns Flask instance
        Should FAIL - no create_app function exists yet
        """
        if create_app is None:
            pytest.skip("Flask app not created yet")

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)

        # Verify it's a Flask instance
        assert app is not None, "Should return app instance"
        assert hasattr(app, 'test_client'), "Should be Flask app with test_client"
        assert app.config['DATABASE'] == test_db, "Should configure database path"

        os.remove(test_db)

    def test_create_app_initializes_database(self):
        """
        RED: Test that create_app() initializes database
        Should FAIL - no create_app function exists yet
        """
        if create_app is None:
            pytest.skip("Flask app not created yet")

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        # Create app (should initialize database)
        app = create_app(test_db)

        # Verify database was initialized
        assert os.path.exists(test_db), "Database file should be created"

        # Verify tables exist
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row['name'] for row in cursor.fetchall()}

        expected_tables = {'users', 'lessons', 'user_progress', 'quiz_results', 'comments', 'sessions'}
        assert expected_tables.issubset(tables), "All tables should exist"

        conn.close()
        os.remove(test_db)


class TestAuthEndpoints:
    """Test authentication endpoints (signup, login, logout)"""

    def test_signup_creates_user_and_returns_session(self):
        """
        RED: Test POST /api/auth/signup creates user and returns session
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Signup new user
        response = client.post('/api/auth/signup', json={
            'username': 'newuser',
            'password': 'password123',
            'email': 'newuser@example.com'
        })

        assert response.status_code == 201, "Should return 201 Created"
        data = response.get_json()
        assert 'session_id' in data, "Should return session_id"
        assert 'user_id' in data, "Should return user_id"
        assert 'username' in data, "Should return username"
        assert data['username'] == 'newuser'

        # Verify user exists in database
        user = User.get_by_username(test_db, 'newuser')
        assert user is not None, "User should exist in database"
        assert user['email'] == 'newuser@example.com'

        os.remove(test_db)

    def test_signup_rejects_duplicate_username(self):
        """
        RED: Test POST /api/auth/signup rejects duplicate username
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user directly
        User.create(test_db, 'existinguser', 'password123', 'existing@example.com')

        # Try to signup with same username
        response = client.post('/api/auth/signup', json={
            'username': 'existinguser',
            'password': 'different',
            'email': 'different@example.com'
        })

        assert response.status_code == 409, "Should return 409 Conflict"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_login_returns_session_for_valid_credentials(self):
        """
        RED: Test POST /api/auth/login returns session for valid credentials
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user
        User.create(test_db, 'testuser', 'password123', 'test@example.com')

        # Login
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'session_id' in data, "Should return session_id"
        assert 'user_id' in data, "Should return user_id"
        assert 'username' in data, "Should return username"

        # Verify session is valid
        session_id = data['session_id']
        user_id = Session.validate(test_db, session_id)
        assert user_id is not None, "Session should be valid"

        os.remove(test_db)

    def test_login_rejects_invalid_password(self):
        """
        RED: Test POST /api/auth/login rejects invalid password
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user
        User.create(test_db, 'testuser', 'password123', 'test@example.com')

        # Login with wrong password
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_login_rejects_nonexistent_user(self):
        """
        RED: Test POST /api/auth/login rejects non-existent user
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Login with non-existent user
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_logout_destroys_session(self):
        """
        RED: Test POST /api/auth/logout destroys session
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user and session
        user_id = User.create(test_db, 'testuser', 'password123', 'test@example.com')
        session_id = Session.create(test_db, user_id)

        # Logout
        response = client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {session_id}'})

        assert response.status_code == 200, "Should return 200 OK"

        # Verify session is destroyed
        validated_user_id = Session.validate(test_db, session_id)
        assert validated_user_id is None, "Session should be destroyed"

        os.remove(test_db)


class TestLesson:
    """Test Lesson model"""

    def test_lesson_create_saves_to_database(self):
        """
        RED: Test that Lesson.create() saves lesson to database
        Should FAIL - no Lesson model exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create lesson
        lesson_id = Lesson.create(
            test_db,
            lesson_id='module-01-lesson-01',
            module_number=1,
            title='Introduction to Pydantic',
            subtitle='Learn structured data validation',
            content='# Pydantic Basics\n\nPydantic is...',
            duration=30,
            difficulty='beginner',
            objectives='["Understand Pydantic models", "Create validators"]',
            quiz_data='{"questions": []}',
            order_index=1
        )

        assert lesson_id > 0, "Should return lesson ID"

        # Verify lesson exists in database
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        lesson = cursor.fetchone()

        assert lesson is not None, "Lesson should exist in database"
        assert lesson['lesson_id'] == 'module-01-lesson-01'
        assert lesson['title'] == 'Introduction to Pydantic'
        assert lesson['module_number'] == 1
        assert lesson['difficulty'] == 'beginner'

        conn.close()
        os.remove(test_db)

    def test_lesson_get_all_returns_all_lessons(self):
        """
        RED: Test that Lesson.get_all() retrieves all lessons
        Should FAIL - no get_all method exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create multiple lessons
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)
        Lesson.create(test_db, 'module-01-lesson-02', 1, 'Lesson 2', 'Subtitle 2', 'Content 2', order_index=2)
        Lesson.create(test_db, 'module-02-lesson-01', 2, 'Lesson 3', 'Subtitle 3', 'Content 3', order_index=3)

        # Get all lessons
        lessons = Lesson.get_all(test_db)

        assert len(lessons) == 3, "Should return all 3 lessons"
        assert lessons[0]['lesson_id'] == 'module-01-lesson-01'
        assert lessons[1]['lesson_id'] == 'module-01-lesson-02'
        assert lessons[2]['lesson_id'] == 'module-02-lesson-01'

        os.remove(test_db)

    def test_lesson_get_by_id_returns_lesson(self):
        """
        RED: Test that Lesson.get_by_id() retrieves specific lesson
        Should FAIL - no get_by_id method exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create lesson
        Lesson.create(
            test_db,
            lesson_id='module-01-lesson-01',
            module_number=1,
            title='Test Lesson',
            subtitle='Test Subtitle',
            content='Test Content',
            order_index=1
        )

        # Get lesson by lesson_id
        lesson = Lesson.get_by_id(test_db, 'module-01-lesson-01')

        assert lesson is not None, "Should return lesson"
        assert lesson['lesson_id'] == 'module-01-lesson-01'
        assert lesson['title'] == 'Test Lesson'
        assert lesson['content'] == 'Test Content'

        os.remove(test_db)

    def test_lesson_get_by_id_returns_none_if_not_found(self):
        """
        RED: Test that Lesson.get_by_id() returns None for non-existent lesson
        Should FAIL - no get_by_id method exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Try to get non-existent lesson
        lesson = Lesson.get_by_id(test_db, 'nonexistent')

        assert lesson is None, "Should return None for non-existent lesson"

        os.remove(test_db)


class TestLessonEndpoints:
    """Test lesson REST API endpoints"""

    def test_get_lessons_returns_all_lessons(self):
        """
        RED: Test GET /api/lessons returns all lessons
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create lessons
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)
        Lesson.create(test_db, 'module-01-lesson-02', 1, 'Lesson 2', 'Subtitle 2', 'Content 2', order_index=2)
        Lesson.create(test_db, 'module-02-lesson-01', 2, 'Lesson 3', 'Subtitle 3', 'Content 3', order_index=3)

        # Get all lessons
        response = client.get('/api/lessons')

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'lessons' in data, "Should return lessons array"
        assert len(data['lessons']) == 3, "Should return all 3 lessons"
        assert data['lessons'][0]['lesson_id'] == 'module-01-lesson-01'
        assert data['lessons'][0]['title'] == 'Lesson 1'

        os.remove(test_db)

    def test_get_lessons_returns_empty_array_when_no_lessons(self):
        """
        RED: Test GET /api/lessons returns empty array when no lessons exist
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Get all lessons (none exist)
        response = client.get('/api/lessons')

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'lessons' in data, "Should return lessons array"
        assert len(data['lessons']) == 0, "Should return empty array"

        os.remove(test_db)

    def test_get_lesson_by_id_returns_lesson(self):
        """
        RED: Test GET /api/lessons/<id> returns specific lesson
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create lesson
        Lesson.create(
            test_db,
            lesson_id='module-01-lesson-01',
            module_number=1,
            title='Test Lesson',
            subtitle='Test Subtitle',
            content='# Test Content\n\nThis is a test.',
            duration=30,
            difficulty='beginner',
            order_index=1
        )

        # Get lesson by ID
        response = client.get('/api/lessons/module-01-lesson-01')

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert data['lesson_id'] == 'module-01-lesson-01'
        assert data['title'] == 'Test Lesson'
        assert data['content'] == '# Test Content\n\nThis is a test.'
        assert data['duration'] == 30
        assert data['difficulty'] == 'beginner'

        os.remove(test_db)

    def test_get_lesson_by_id_returns_404_if_not_found(self):
        """
        RED: Test GET /api/lessons/<id> returns 404 for non-existent lesson
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Get non-existent lesson
        response = client.get('/api/lessons/nonexistent')

        assert response.status_code == 404, "Should return 404 Not Found"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)


class TestProgress:
    """Test Progress model for tracking lesson completion"""

    def test_progress_mark_complete_saves_to_database(self):
        """
        RED: Test that Progress.mark_complete() marks lesson as completed
        Should FAIL - no Progress model exists yet
        """
        from backend.models import Progress, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Mark lesson complete
        Progress.mark_complete(test_db, user_id, 'module-01-lesson-01')

        # Verify progress exists
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_progress WHERE user_id = ? AND lesson_id = ?',
                      (user_id, 'module-01-lesson-01'))
        progress = cursor.fetchone()

        assert progress is not None, "Progress should exist in database"
        assert progress['user_id'] == user_id
        assert progress['lesson_id'] == 'module-01-lesson-01'
        assert progress['completed'] == 1, "Lesson should be marked complete"
        assert progress['completed_at'] is not None, "Should have completion timestamp"

        conn.close()
        os.remove(test_db)

    def test_progress_get_user_progress_returns_all_progress(self):
        """
        RED: Test that Progress.get_user_progress() returns all user progress
        Should FAIL - no get_user_progress method exists yet
        """
        from backend.models import Progress, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lessons
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)
        Lesson.create(test_db, 'module-01-lesson-02', 1, 'Lesson 2', 'Subtitle 2', 'Content 2', order_index=2)

        # Mark first lesson complete
        Progress.mark_complete(test_db, user_id, 'module-01-lesson-01')

        # Get user progress
        progress = Progress.get_user_progress(test_db, user_id)

        assert len(progress) == 1, "Should return 1 completed lesson"
        assert progress[0]['lesson_id'] == 'module-01-lesson-01'
        assert progress[0]['completed'] == 1

        os.remove(test_db)

    def test_progress_is_completed_returns_true_for_completed_lesson(self):
        """
        RED: Test that Progress.is_completed() returns True for completed lesson
        Should FAIL - no is_completed method exists yet
        """
        from backend.models import Progress, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Mark lesson complete
        Progress.mark_complete(test_db, user_id, 'module-01-lesson-01')

        # Check if completed
        is_completed = Progress.is_completed(test_db, user_id, 'module-01-lesson-01')

        assert is_completed is True, "Should return True for completed lesson"

        os.remove(test_db)

    def test_progress_is_completed_returns_false_for_incomplete_lesson(self):
        """
        RED: Test that Progress.is_completed() returns False for incomplete lesson
        Should FAIL - no is_completed method exists yet
        """
        from backend.models import Progress, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Check if completed (not marked yet)
        is_completed = Progress.is_completed(test_db, user_id, 'module-01-lesson-01')

        assert is_completed is False, "Should return False for incomplete lesson"

        os.remove(test_db)


class TestProgressEndpoints:
    """Test progress REST API endpoints (authenticated)"""

    def test_mark_complete_requires_authentication(self):
        """
        RED: Test POST /api/progress/complete requires session
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create lesson
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Try to mark complete without authentication
        response = client.post('/api/progress/complete', json={
            'lesson_id': 'module-01-lesson-01'
        })

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_mark_complete_marks_lesson_complete(self):
        """
        RED: Test POST /api/progress/complete marks lesson complete
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Progress

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user, session, and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id)
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Mark lesson complete
        response = client.post('/api/progress/complete',
            headers={'Authorization': f'Bearer {session_id}'},
            json={'lesson_id': 'module-01-lesson-01'})

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'message' in data, "Should return success message"

        # Verify lesson is marked complete
        is_completed = Progress.is_completed(test_db, user_id, 'module-01-lesson-01')
        assert is_completed is True, "Lesson should be marked complete"

        os.remove(test_db)

    def test_mark_complete_returns_404_for_invalid_lesson(self):
        """
        RED: Test POST /api/progress/complete returns 404 for invalid lesson
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user and session
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id)

        # Try to mark non-existent lesson complete
        response = client.post('/api/progress/complete',
            headers={'Authorization': f'Bearer {session_id}'},
            json={'lesson_id': 'nonexistent'})

        assert response.status_code == 404, "Should return 404 Not Found"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_get_progress_requires_authentication(self):
        """
        RED: Test GET /api/progress requires session
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Try to get progress without authentication
        response = client.get('/api/progress')

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_get_progress_returns_user_progress(self):
        """
        RED: Test GET /api/progress returns user's completed lessons
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Progress

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user, session, and lessons
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id)
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)
        Lesson.create(test_db, 'module-01-lesson-02', 1, 'Lesson 2', 'Subtitle 2', 'Content 2', order_index=2)

        # Mark first lesson complete
        Progress.mark_complete(test_db, user_id, 'module-01-lesson-01')

        # Get progress
        response = client.get('/api/progress',
            headers={'Authorization': f'Bearer {session_id}'})

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'progress' in data, "Should return progress array"
        assert len(data['progress']) == 1, "Should return 1 completed lesson"
        assert data['progress'][0]['lesson_id'] == 'module-01-lesson-01'

        os.remove(test_db)


class TestQuiz:
    """Test Quiz model for tracking quiz results"""

    def test_quiz_submit_answer_saves_to_database(self):
        """
        RED: Test that Quiz.submit_answer() saves quiz answer
        Should FAIL - no Quiz model exists yet
        """
        from backend.models import Quiz, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Submit quiz answer
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-1', 'answer-a', is_correct=True)

        # Verify answer exists
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM quiz_results WHERE user_id = ? AND question_id = ?',
                      (user_id, 'question-1'))
        result = cursor.fetchone()

        assert result is not None, "Quiz result should exist in database"
        assert result['user_id'] == user_id
        assert result['lesson_id'] == 'module-01-lesson-01'
        assert result['question_id'] == 'question-1'
        assert result['selected_answer'] == 'answer-a'
        assert result['is_correct'] == 1, "Answer should be marked correct"

        conn.close()
        os.remove(test_db)

    def test_quiz_get_results_returns_all_answers(self):
        """
        RED: Test that Quiz.get_results() returns all quiz answers for a lesson
        Should FAIL - no get_results method exists yet
        """
        from backend.models import Quiz, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Submit multiple quiz answers
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-1', 'answer-a', is_correct=True)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-2', 'answer-b', is_correct=False)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-3', 'answer-c', is_correct=True)

        # Get quiz results
        results = Quiz.get_results(test_db, user_id, 'module-01-lesson-01')

        assert len(results) == 3, "Should return all 3 quiz answers"
        assert results[0]['question_id'] == 'question-1'
        assert results[1]['question_id'] == 'question-2'
        assert results[2]['question_id'] == 'question-3'

        os.remove(test_db)

    def test_quiz_get_score_calculates_percentage(self):
        """
        RED: Test that Quiz.get_score() calculates correct percentage
        Should FAIL - no get_score method exists yet
        """
        from backend.models import Quiz, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Submit quiz answers (2 correct, 1 incorrect)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-1', 'answer-a', is_correct=True)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-2', 'answer-b', is_correct=False)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-3', 'answer-c', is_correct=True)

        # Get quiz score
        score = Quiz.get_score(test_db, user_id, 'module-01-lesson-01')

        assert score is not None, "Should return score"
        assert score['total'] == 3, "Should have 3 total questions"
        assert score['correct'] == 2, "Should have 2 correct answers"
        assert score['percentage'] == 66.67, "Should calculate 66.67% (2/3)"

        os.remove(test_db)

    def test_quiz_get_score_returns_none_if_no_answers(self):
        """
        RED: Test that Quiz.get_score() returns None if no answers submitted
        Should FAIL - no get_score method exists yet
        """
        from backend.models import Quiz, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Get quiz score (no answers submitted)
        score = Quiz.get_score(test_db, user_id, 'module-01-lesson-01')

        assert score is None, "Should return None if no answers submitted"

        os.remove(test_db)


class TestQuizEndpoints:
    """Test quiz REST API endpoints (authenticated)"""

    def test_submit_answer_requires_authentication(self):
        """
        RED: Test POST /api/quiz/submit requires session
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create lesson
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Try to submit answer without authentication
        response = client.post('/api/quiz/submit', json={
            'lesson_id': 'module-01-lesson-01',
            'question_id': 'question-1',
            'selected_answer': 'answer-a',
            'is_correct': True
        })

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_submit_answer_saves_quiz_result(self):
        """
        RED: Test POST /api/quiz/submit saves quiz answer
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Quiz

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user, session, and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id)
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Submit quiz answer
        response = client.post('/api/quiz/submit',
            headers={'Authorization': f'Bearer {session_id}'},
            json={
                'lesson_id': 'module-01-lesson-01',
                'question_id': 'question-1',
                'selected_answer': 'answer-a',
                'is_correct': True
            })

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'message' in data, "Should return success message"

        # Verify answer was saved
        results = Quiz.get_results(test_db, user_id, 'module-01-lesson-01')
        assert len(results) == 1, "Should have 1 quiz result"
        assert results[0]['question_id'] == 'question-1'

        os.remove(test_db)

    def test_get_results_requires_authentication(self):
        """
        RED: Test GET /api/quiz/results/<lesson_id> requires session
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Try to get results without authentication
        response = client.get('/api/quiz/results/module-01-lesson-01')

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_get_results_returns_quiz_results(self):
        """
        RED: Test GET /api/quiz/results/<lesson_id> returns quiz results
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Quiz

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user, session, and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id)
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Submit quiz answers
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-1', 'answer-a', is_correct=True)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-2', 'answer-b', is_correct=False)

        # Get quiz results
        response = client.get('/api/quiz/results/module-01-lesson-01',
            headers={'Authorization': f'Bearer {session_id}'})

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'results' in data, "Should return results array"
        assert len(data['results']) == 2, "Should return 2 quiz results"

        os.remove(test_db)

    def test_get_score_requires_authentication(self):
        """
        RED: Test GET /api/quiz/score/<lesson_id> requires session
        Should FAIL - no endpoint exists yet
        """
        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Try to get score without authentication
        response = client.get('/api/quiz/score/module-01-lesson-01')

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_get_score_returns_quiz_score(self):
        """
        RED: Test GET /api/quiz/score/<lesson_id> returns quiz score
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Quiz

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user, session, and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id)
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Submit quiz answers (2 correct, 1 incorrect)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-1', 'answer-a', is_correct=True)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-2', 'answer-b', is_correct=False)
        Quiz.submit_answer(test_db, user_id, 'module-01-lesson-01', 'question-3', 'answer-c', is_correct=True)

        # Get quiz score
        response = client.get('/api/quiz/score/module-01-lesson-01',
            headers={'Authorization': f'Bearer {session_id}'})

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'score' in data, "Should return score object"
        assert data['score']['total'] == 3
        assert data['score']['correct'] == 2
        assert data['score']['percentage'] == 66.67

        os.remove(test_db)


class TestComment:
    """Test Comment model for social learning discussions"""

    def test_comment_create_saves_to_database(self):
        """
        RED: Test that Comment.create() saves comment
        Should FAIL - no Comment model exists yet
        """
        from backend.models import Comment, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Create comment
        comment_id = Comment.create(test_db, user_id, 'module-01-lesson-01', 'This is a great lesson!')

        assert comment_id > 0, "Should return comment ID"

        # Verify comment exists
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM comments WHERE id = ?', (comment_id,))
        comment = cursor.fetchone()

        assert comment is not None, "Comment should exist in database"
        assert comment['user_id'] == user_id
        assert comment['lesson_id'] == 'module-01-lesson-01'
        assert comment['comment_text'] == 'This is a great lesson!'
        assert comment['parent_comment_id'] is None, "Should be top-level comment"

        conn.close()
        os.remove(test_db)

    def test_comment_create_reply_saves_with_parent_id(self):
        """
        RED: Test that Comment.create() with parent_comment_id creates reply
        Should FAIL - no Comment model exists yet
        """
        from backend.models import Comment, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create users and lesson
        user1_id = User.create(test_db, 'user1', 'password123')
        user2_id = User.create(test_db, 'user2', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Create parent comment
        parent_id = Comment.create(test_db, user1_id, 'module-01-lesson-01', 'Original comment')

        # Create reply
        reply_id = Comment.create(test_db, user2_id, 'module-01-lesson-01', 'I agree!', parent_comment_id=parent_id)

        # Verify reply has parent_comment_id set
        conn = get_db_connection(test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM comments WHERE id = ?', (reply_id,))
        reply = cursor.fetchone()

        assert reply is not None, "Reply should exist"
        assert reply['parent_comment_id'] == parent_id, "Should reference parent comment"

        conn.close()
        os.remove(test_db)

    def test_comment_get_by_lesson_returns_all_comments(self):
        """
        RED: Test that Comment.get_by_lesson() returns all comments for a lesson
        Should FAIL - no get_by_lesson method exists yet
        """
        from backend.models import Comment, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create users and lessons
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)
        Lesson.create(test_db, 'module-01-lesson-02', 1, 'Lesson 2', 'Subtitle 2', 'Content 2', order_index=2)

        # Create comments on first lesson
        Comment.create(test_db, user_id, 'module-01-lesson-01', 'Comment 1')
        Comment.create(test_db, user_id, 'module-01-lesson-01', 'Comment 2')

        # Create comment on second lesson (should not be returned)
        Comment.create(test_db, user_id, 'module-01-lesson-02', 'Comment 3')

        # Get comments for first lesson
        comments = Comment.get_by_lesson(test_db, 'module-01-lesson-01')

        assert len(comments) == 2, "Should return 2 comments for lesson 1"
        assert comments[0]['comment_text'] == 'Comment 1'
        assert comments[1]['comment_text'] == 'Comment 2'

        os.remove(test_db)

    def test_comment_get_replies_returns_child_comments(self):
        """
        RED: Test that Comment.get_replies() returns replies to a comment
        Should FAIL - no get_replies method exists yet
        """
        from backend.models import Comment, Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        init_db(test_db)

        # Create users and lesson
        user1_id = User.create(test_db, 'user1', 'password123')
        user2_id = User.create(test_db, 'user2', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Create parent comment
        parent_id = Comment.create(test_db, user1_id, 'module-01-lesson-01', 'Parent comment')

        # Create replies
        Comment.create(test_db, user2_id, 'module-01-lesson-01', 'Reply 1', parent_comment_id=parent_id)
        Comment.create(test_db, user1_id, 'module-01-lesson-01', 'Reply 2', parent_comment_id=parent_id)

        # Create another top-level comment (should not be in replies)
        Comment.create(test_db, user2_id, 'module-01-lesson-01', 'Another comment')

        # Get replies
        replies = Comment.get_replies(test_db, parent_id)

        assert len(replies) == 2, "Should return 2 replies"
        assert replies[0]['comment_text'] == 'Reply 1'
        assert replies[1]['comment_text'] == 'Reply 2'

        os.remove(test_db)


class TestCommentEndpoints:
    """Test comment REST API endpoints (authenticated)"""

    def test_create_comment_requires_authentication(self):
        """
        RED: Test POST /api/comments requires session
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create lesson
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Try to create comment without authentication
        response = client.post('/api/comments', json={
            'lesson_id': 'module-01-lesson-01',
            'comment_text': 'Great lesson!'
        })

        assert response.status_code == 401, "Should return 401 Unauthorized"
        data = response.get_json()
        assert 'error' in data, "Should return error message"

        os.remove(test_db)

    def test_create_comment_saves_comment(self):
        """
        RED: Test POST /api/comments creates comment
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Comment

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user, session, and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        session_id = Session.create(test_db, user_id)
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Create comment
        response = client.post('/api/comments',
            headers={'Authorization': f'Bearer {session_id}'},
            json={
                'lesson_id': 'module-01-lesson-01',
                'comment_text': 'Great lesson!'
            })

        assert response.status_code == 201, "Should return 201 Created"
        data = response.get_json()
        assert 'comment_id' in data, "Should return comment_id"

        # Verify comment was saved
        comments = Comment.get_by_lesson(test_db, 'module-01-lesson-01')
        assert len(comments) == 1, "Should have 1 comment"
        assert comments[0]['comment_text'] == 'Great lesson!'

        os.remove(test_db)

    def test_create_reply_saves_with_parent_id(self):
        """
        RED: Test POST /api/comments with parent_comment_id creates reply
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Comment

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create users, sessions, and lesson
        user1_id = User.create(test_db, 'user1', 'password123')
        user2_id = User.create(test_db, 'user2', 'password123')
        session1_id = Session.create(test_db, user1_id)
        session2_id = Session.create(test_db, user2_id)
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Create parent comment
        parent_id = Comment.create(test_db, user1_id, 'module-01-lesson-01', 'Parent comment')

        # Create reply
        response = client.post('/api/comments',
            headers={'Authorization': f'Bearer {session2_id}'},
            json={
                'lesson_id': 'module-01-lesson-01',
                'comment_text': 'I agree!',
                'parent_comment_id': parent_id
            })

        assert response.status_code == 201, "Should return 201 Created"

        # Verify reply was saved
        replies = Comment.get_replies(test_db, parent_id)
        assert len(replies) == 1, "Should have 1 reply"
        assert replies[0]['comment_text'] == 'I agree!'

        os.remove(test_db)

    def test_get_comments_returns_lesson_comments(self):
        """
        RED: Test GET /api/comments/<lesson_id> returns comments
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Comment

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create user and lesson
        user_id = User.create(test_db, 'testuser', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Create comments
        Comment.create(test_db, user_id, 'module-01-lesson-01', 'Comment 1')
        Comment.create(test_db, user_id, 'module-01-lesson-01', 'Comment 2')

        # Get comments
        response = client.get('/api/comments/module-01-lesson-01')

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'comments' in data, "Should return comments array"
        assert len(data['comments']) == 2, "Should return 2 comments"

        os.remove(test_db)

    def test_get_replies_returns_comment_replies(self):
        """
        RED: Test GET /api/comments/<comment_id>/replies returns replies
        Should FAIL - no endpoint exists yet
        """
        from backend.models import Lesson, Comment

        test_db = 'test_lms.db'
        if os.path.exists(test_db):
            os.remove(test_db)

        app = create_app(test_db)
        client = app.test_client()

        # Create users and lesson
        user1_id = User.create(test_db, 'user1', 'password123')
        user2_id = User.create(test_db, 'user2', 'password123')
        Lesson.create(test_db, 'module-01-lesson-01', 1, 'Lesson 1', 'Subtitle 1', 'Content 1', order_index=1)

        # Create parent comment
        parent_id = Comment.create(test_db, user1_id, 'module-01-lesson-01', 'Parent comment')

        # Create replies
        Comment.create(test_db, user2_id, 'module-01-lesson-01', 'Reply 1', parent_comment_id=parent_id)
        Comment.create(test_db, user1_id, 'module-01-lesson-01', 'Reply 2', parent_comment_id=parent_id)

        # Get replies
        response = client.get(f'/api/comments/{parent_id}/replies')

        assert response.status_code == 200, "Should return 200 OK"
        data = response.get_json()
        assert 'replies' in data, "Should return replies array"
        assert len(data['replies']) == 2, "Should return 2 replies"

        os.remove(test_db)
