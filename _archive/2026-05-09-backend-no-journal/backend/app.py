"""
Flask Application for B1 LMS
API endpoints and application factory
"""

from flask import Flask, request, jsonify
from backend.database import init_db, get_db_connection
from backend.models import User, Lesson, Progress, Quiz, Comment
from backend.session import Session
from backend.auth import verify_password
import sqlite3


def create_app(db_path='lms.db'):
    """
    Create and configure Flask application (factory pattern)

    Args:
        db_path: Path to SQLite database (configurable for testing)

    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    app.config['DATABASE'] = db_path
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    # Initialize database
    init_db(db_path)

    # ========== Authentication Endpoints ==========

    @app.route('/api/auth/signup', methods=['POST'])
    def signup():
        """
        Create new user account

        Request body:
            username: str (required)
            password: str (required)
            email: str (optional)

        Returns:
            201: {session_id, user_id, username}
            409: {error} if username exists
            400: {error} if missing required fields
        """
        data = request.get_json()

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'username and password required'}), 400

        username = data['username']
        password = data['password']
        email = data.get('email')

        # Check if user already exists
        existing_user = User.get_by_username(db_path, username)
        if existing_user:
            return jsonify({'error': 'username already exists'}), 409

        # Create user
        try:
            user_id = User.create(db_path, username, password, email)
        except sqlite3.IntegrityError:
            return jsonify({'error': 'username already exists'}), 409

        # Create session
        session_id = Session.create(db_path, user_id, expires_in_hours=24)

        return jsonify({
            'session_id': session_id,
            'user_id': user_id,
            'username': username
        }), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """
        Login existing user

        Request body:
            username: str (required)
            password: str (required)

        Returns:
            200: {session_id, user_id, username}
            401: {error} if credentials invalid
            400: {error} if missing required fields
        """
        data = request.get_json()

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'username and password required'}), 400

        username = data['username']
        password = data['password']

        # Get user
        user = User.get_by_username(db_path, username)
        if not user:
            return jsonify({'error': 'invalid credentials'}), 401

        # Verify password
        if not verify_password(user['password_hash'], password):
            return jsonify({'error': 'invalid credentials'}), 401

        # Create session
        session_id = Session.create(db_path, user['id'], expires_in_hours=24)

        return jsonify({
            'session_id': session_id,
            'user_id': user['id'],
            'username': user['username']
        }), 200

    @app.route('/api/auth/logout', methods=['POST'])
    def logout():
        """
        Logout user (destroy session)

        Headers:
            Authorization: Bearer <session_id>

        Returns:
            200: {message}
            401: {error} if no valid session
        """
        # Get session_id from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'no session provided'}), 401

        session_id = auth_header.replace('Bearer ', '')

        # Validate session exists
        user_id = Session.validate(db_path, session_id)
        if not user_id:
            return jsonify({'error': 'invalid session'}), 401

        # Destroy session
        Session.destroy(db_path, session_id)

        return jsonify({'message': 'logged out successfully'}), 200

    # ========== Lesson Endpoints ==========

    @app.route('/api/lessons', methods=['GET'])
    def get_lessons():
        """
        Get all lessons

        Returns:
            200: {lessons: [...]}
        """
        lessons = Lesson.get_all(db_path)
        return jsonify({'lessons': lessons}), 200

    @app.route('/api/lessons/<lesson_id>', methods=['GET'])
    def get_lesson(lesson_id):
        """
        Get specific lesson by ID

        URL Parameters:
            lesson_id: Lesson ID (e.g., 'module-01-lesson-01')

        Returns:
            200: {lesson data}
            404: {error} if lesson not found
        """
        lesson = Lesson.get_by_id(db_path, lesson_id)

        if not lesson:
            return jsonify({'error': 'lesson not found'}), 404

        return jsonify(lesson), 200

    # ========== Progress Endpoints ==========

    @app.route('/api/progress/complete', methods=['POST'])
    def mark_lesson_complete():
        """
        Mark a lesson as completed (requires authentication)

        Headers:
            Authorization: Bearer <session_id>

        Request body:
            lesson_id: str (required)

        Returns:
            200: {message}
            401: {error} if not authenticated
            404: {error} if lesson not found
            400: {error} if missing lesson_id
        """
        # Validate authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'authentication required'}), 401

        session_id = auth_header.replace('Bearer ', '')
        user_id = Session.validate(db_path, session_id)
        if not user_id:
            return jsonify({'error': 'invalid session'}), 401

        # Validate request body
        data = request.get_json()
        if not data or 'lesson_id' not in data:
            return jsonify({'error': 'lesson_id required'}), 400

        lesson_id = data['lesson_id']

        # Verify lesson exists
        lesson = Lesson.get_by_id(db_path, lesson_id)
        if not lesson:
            return jsonify({'error': 'lesson not found'}), 404

        # Mark lesson complete
        Progress.mark_complete(db_path, user_id, lesson_id)

        return jsonify({'message': 'lesson marked complete'}), 200

    @app.route('/api/progress', methods=['GET'])
    def get_user_progress():
        """
        Get authenticated user's progress (requires authentication)

        Headers:
            Authorization: Bearer <session_id>

        Returns:
            200: {progress: [...]}
            401: {error} if not authenticated
        """
        # Validate authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'authentication required'}), 401

        session_id = auth_header.replace('Bearer ', '')
        user_id = Session.validate(db_path, session_id)
        if not user_id:
            return jsonify({'error': 'invalid session'}), 401

        # Get user's progress
        progress = Progress.get_user_progress(db_path, user_id)

        return jsonify({'progress': progress}), 200

    # ========== Quiz Endpoints ==========

    @app.route('/api/quiz/submit', methods=['POST'])
    def submit_quiz_answer():
        """
        Submit a quiz answer (requires authentication)

        Headers:
            Authorization: Bearer <session_id>

        Request body:
            lesson_id: str (required)
            question_id: str (required)
            selected_answer: str (required)
            is_correct: bool (required)

        Returns:
            200: {message}
            401: {error} if not authenticated
            400: {error} if missing required fields
        """
        # Validate authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'authentication required'}), 401

        session_id = auth_header.replace('Bearer ', '')
        user_id = Session.validate(db_path, session_id)
        if not user_id:
            return jsonify({'error': 'invalid session'}), 401

        # Validate request body
        data = request.get_json()
        required_fields = ['lesson_id', 'question_id', 'selected_answer', 'is_correct']
        if not data or not all(field in data for field in required_fields):
            return jsonify({'error': 'missing required fields'}), 400

        # Submit quiz answer
        Quiz.submit_answer(
            db_path,
            user_id,
            data['lesson_id'],
            data['question_id'],
            data['selected_answer'],
            data['is_correct']
        )

        return jsonify({'message': 'quiz answer submitted'}), 200

    @app.route('/api/quiz/results/<lesson_id>', methods=['GET'])
    def get_quiz_results(lesson_id):
        """
        Get quiz results for a lesson (requires authentication)

        Headers:
            Authorization: Bearer <session_id>

        URL Parameters:
            lesson_id: Lesson ID (e.g., 'module-01-lesson-01')

        Returns:
            200: {results: [...]}
            401: {error} if not authenticated
        """
        # Validate authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'authentication required'}), 401

        session_id = auth_header.replace('Bearer ', '')
        user_id = Session.validate(db_path, session_id)
        if not user_id:
            return jsonify({'error': 'invalid session'}), 401

        # Get quiz results
        results = Quiz.get_results(db_path, user_id, lesson_id)

        return jsonify({'results': results}), 200

    @app.route('/api/quiz/score/<lesson_id>', methods=['GET'])
    def get_quiz_score(lesson_id):
        """
        Get quiz score for a lesson (requires authentication)

        Headers:
            Authorization: Bearer <session_id>

        URL Parameters:
            lesson_id: Lesson ID (e.g., 'module-01-lesson-01')

        Returns:
            200: {score: {total, correct, percentage}}
            401: {error} if not authenticated
        """
        # Validate authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'authentication required'}), 401

        session_id = auth_header.replace('Bearer ', '')
        user_id = Session.validate(db_path, session_id)
        if not user_id:
            return jsonify({'error': 'invalid session'}), 401

        # Get quiz score
        score = Quiz.get_score(db_path, user_id, lesson_id)

        return jsonify({'score': score}), 200

    # ========== Comment Endpoints ==========

    @app.route('/api/comments', methods=['POST'])
    def create_comment():
        """
        Create a comment or reply (requires authentication)

        Headers:
            Authorization: Bearer <session_id>

        Request body:
            lesson_id: str (required)
            comment_text: str (required)
            parent_comment_id: int (optional - for replies)

        Returns:
            201: {comment_id}
            401: {error} if not authenticated
            400: {error} if missing required fields
        """
        # Validate authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'authentication required'}), 401

        session_id = auth_header.replace('Bearer ', '')
        user_id = Session.validate(db_path, session_id)
        if not user_id:
            return jsonify({'error': 'invalid session'}), 401

        # Validate request body
        data = request.get_json()
        if not data or 'lesson_id' not in data or 'comment_text' not in data:
            return jsonify({'error': 'lesson_id and comment_text required'}), 400

        # Create comment
        comment_id = Comment.create(
            db_path,
            user_id,
            data['lesson_id'],
            data['comment_text'],
            parent_comment_id=data.get('parent_comment_id')
        )

        return jsonify({'comment_id': comment_id}), 201

    @app.route('/api/comments/<lesson_id>', methods=['GET'])
    def get_lesson_comments(lesson_id):
        """
        Get all top-level comments for a lesson (public access)

        URL Parameters:
            lesson_id: Lesson ID (e.g., 'module-01-lesson-01')

        Returns:
            200: {comments: [...]}
        """
        comments = Comment.get_by_lesson(db_path, lesson_id)
        return jsonify({'comments': comments}), 200

    @app.route('/api/comments/<int:comment_id>/replies', methods=['GET'])
    def get_comment_replies(comment_id):
        """
        Get all replies to a comment (public access)

        URL Parameters:
            comment_id: Parent comment ID

        Returns:
            200: {replies: [...]}
        """
        replies = Comment.get_replies(db_path, comment_id)
        return jsonify({'replies': replies}), 200

    return app
