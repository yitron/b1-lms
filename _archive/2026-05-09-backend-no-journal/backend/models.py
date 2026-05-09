"""
Data models for B1 LMS
User, Lesson, Progress, Quiz, Comment models
"""

from backend.database import get_db_connection
from backend.auth import hash_password
from datetime import datetime


class User:
    """Model for managing users"""

    @staticmethod
    def create(db_path, username, password, email=None):
        """
        Create a new user

        Args:
            db_path: Path to database
            username: Unique username
            password: Plain text password (will be hashed)
            email: Optional email address

        Returns:
            int: User ID of created user
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        password_hash = hash_password(password)

        cursor.execute(
            'INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)',
            (username, password_hash, email)
        )
        conn.commit()
        user_id = cursor.lastrowid

        conn.close()
        return user_id

    @staticmethod
    def get_by_username(db_path, username):
        """
        Get user by username

        Args:
            db_path: Path to database
            username: Username to search for

        Returns:
            dict: User data or None if not found
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        conn.close()

        return dict(user) if user else None


class Lesson:
    """Model for managing lessons"""

    @staticmethod
    def create(db_path, lesson_id, module_number, title, subtitle, content,
               duration=None, difficulty=None, objectives=None, quiz_data=None, order_index=1):
        """
        Create a new lesson

        Args:
            db_path: Path to database
            lesson_id: Unique lesson identifier (e.g., 'module-01-lesson-01')
            module_number: Module number (1, 2, 3)
            title: Lesson title
            subtitle: Lesson subtitle
            content: Lesson content (Markdown format)
            duration: Duration in minutes (optional)
            difficulty: Difficulty level (beginner, intermediate, advanced) (optional)
            objectives: Learning objectives as JSON string (optional)
            quiz_data: Quiz questions/answers as JSON string (optional)
            order_index: Display order (default 1)

        Returns:
            int: Lesson database ID
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO lessons (
                lesson_id, module_number, title, subtitle, content,
                duration, difficulty, objectives, quiz_data, order_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lesson_id, module_number, title, subtitle, content,
              duration, difficulty, objectives, quiz_data, order_index))

        conn.commit()
        db_id = cursor.lastrowid

        conn.close()
        return db_id

    @staticmethod
    def get_all(db_path):
        """
        Get all lessons ordered by order_index

        Args:
            db_path: Path to database

        Returns:
            list: List of lesson dicts
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM lessons ORDER BY order_index ASC')
        lessons = cursor.fetchall()

        conn.close()

        return [dict(lesson) for lesson in lessons]

    @staticmethod
    def get_by_id(db_path, lesson_id):
        """
        Get lesson by lesson_id

        Args:
            db_path: Path to database
            lesson_id: Lesson ID to search for (e.g., 'module-01-lesson-01')

        Returns:
            dict: Lesson data or None if not found
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM lessons WHERE lesson_id = ?', (lesson_id,))
        lesson = cursor.fetchone()

        conn.close()

        return dict(lesson) if lesson else None


class Progress:
    """Model for managing user progress on lessons"""

    @staticmethod
    def mark_complete(db_path, user_id, lesson_id):
        """
        Mark a lesson as completed for a user

        Args:
            db_path: Path to database
            user_id: User ID
            lesson_id: Lesson ID (e.g., 'module-01-lesson-01')

        Returns:
            None
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Use ISO format for timestamp
        completed_at = datetime.now().isoformat()

        # Insert or update progress
        cursor.execute('''
            INSERT INTO user_progress (user_id, lesson_id, completed, completed_at)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, lesson_id)
            DO UPDATE SET completed = 1, completed_at = ?
        ''', (user_id, lesson_id, completed_at, completed_at))

        conn.commit()
        conn.close()

    @staticmethod
    def get_user_progress(db_path, user_id):
        """
        Get all progress for a user

        Args:
            db_path: Path to database
            user_id: User ID

        Returns:
            list: List of progress records (completed lessons only)
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM user_progress
            WHERE user_id = ? AND completed = 1
            ORDER BY completed_at DESC
        ''', (user_id,))
        progress = cursor.fetchall()

        conn.close()

        return [dict(p) for p in progress]

    @staticmethod
    def is_completed(db_path, user_id, lesson_id):
        """
        Check if a user has completed a specific lesson

        Args:
            db_path: Path to database
            user_id: User ID
            lesson_id: Lesson ID

        Returns:
            bool: True if completed, False otherwise
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT completed FROM user_progress
            WHERE user_id = ? AND lesson_id = ?
        ''', (user_id, lesson_id))
        result = cursor.fetchone()

        conn.close()

        return result['completed'] == 1 if result else False


class Quiz:
    """Model for managing quiz results"""

    @staticmethod
    def submit_answer(db_path, user_id, lesson_id, question_id, selected_answer, is_correct):
        """
        Submit a quiz answer

        Args:
            db_path: Path to database
            user_id: User ID
            lesson_id: Lesson ID
            question_id: Question ID (e.g., 'question-1')
            selected_answer: Selected answer (e.g., 'answer-a')
            is_correct: Whether the answer is correct (bool)

        Returns:
            int: Quiz result ID
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Use ISO format for timestamp
        answered_at = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO quiz_results (user_id, lesson_id, question_id, selected_answer, is_correct, answered_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, lesson_id, question_id, selected_answer, 1 if is_correct else 0, answered_at))

        conn.commit()
        result_id = cursor.lastrowid

        conn.close()
        return result_id

    @staticmethod
    def get_results(db_path, user_id, lesson_id):
        """
        Get all quiz results for a user on a specific lesson

        Args:
            db_path: Path to database
            user_id: User ID
            lesson_id: Lesson ID

        Returns:
            list: List of quiz results ordered by answered_at
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM quiz_results
            WHERE user_id = ? AND lesson_id = ?
            ORDER BY answered_at ASC
        ''', (user_id, lesson_id))
        results = cursor.fetchall()

        conn.close()

        return [dict(r) for r in results]

    @staticmethod
    def get_score(db_path, user_id, lesson_id):
        """
        Get quiz score for a user on a specific lesson

        Args:
            db_path: Path to database
            user_id: User ID
            lesson_id: Lesson ID

        Returns:
            dict: {total: int, correct: int, percentage: float} or None if no answers
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(is_correct) as correct
            FROM quiz_results
            WHERE user_id = ? AND lesson_id = ?
        ''', (user_id, lesson_id))
        result = cursor.fetchone()

        conn.close()

        if result['total'] == 0:
            return None

        total = result['total']
        correct = result['correct'] if result['correct'] else 0
        percentage = round((correct / total) * 100, 2)

        return {
            'total': total,
            'correct': correct,
            'percentage': percentage
        }


class Comment:
    """Model for managing lesson comments and discussions"""

    @staticmethod
    def create(db_path, user_id, lesson_id, comment_text, parent_comment_id=None):
        """
        Create a new comment or reply

        Args:
            db_path: Path to database
            user_id: User ID
            lesson_id: Lesson ID
            comment_text: Comment text content
            parent_comment_id: Parent comment ID for replies (optional)

        Returns:
            int: Comment ID
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Use ISO format for timestamp
        created_at = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO comments (user_id, lesson_id, comment_text, parent_comment_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, lesson_id, comment_text, parent_comment_id, created_at))

        conn.commit()
        comment_id = cursor.lastrowid

        conn.close()
        return comment_id

    @staticmethod
    def get_by_lesson(db_path, lesson_id):
        """
        Get all comments for a lesson (top-level comments only)

        Args:
            db_path: Path to database
            lesson_id: Lesson ID

        Returns:
            list: List of top-level comments ordered by created_at ASC
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM comments
            WHERE lesson_id = ? AND parent_comment_id IS NULL
            ORDER BY created_at ASC
        ''', (lesson_id,))
        comments = cursor.fetchall()

        conn.close()

        return [dict(c) for c in comments]

    @staticmethod
    def get_replies(db_path, parent_comment_id):
        """
        Get all replies to a comment

        Args:
            db_path: Path to database
            parent_comment_id: Parent comment ID

        Returns:
            list: List of reply comments ordered by created_at ASC
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM comments
            WHERE parent_comment_id = ?
            ORDER BY created_at ASC
        ''', (parent_comment_id,))
        replies = cursor.fetchall()

        conn.close()

        return [dict(r) for r in replies]
