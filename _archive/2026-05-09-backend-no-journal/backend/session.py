"""
Session management for B1 LMS
Create, validate, and destroy user sessions
"""

from backend.database import get_db_connection
from datetime import datetime, timedelta
import secrets


class Session:
    """Model for managing user sessions"""

    @staticmethod
    def create(db_path, user_id, expires_in_hours=24):
        """
        Create a new session for a user

        Args:
            db_path: Path to database
            user_id: User ID to create session for
            expires_in_hours: Hours until session expires (default 24)

        Returns:
            str: Session ID (random token)
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Generate random session ID (32 bytes = 64 hex characters)
        session_id = secrets.token_hex(32)

        # Calculate expiry time
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)

        # Convert datetime to ISO format string for SQLite compatibility
        cursor.execute(
            'INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)',
            (session_id, user_id, expires_at.isoformat())
        )
        conn.commit()

        conn.close()
        return session_id

    @staticmethod
    def validate(db_path, session_id):
        """
        Validate a session and return user_id if valid

        Args:
            db_path: Path to database
            session_id: Session ID to validate

        Returns:
            int: User ID if session is valid and not expired, None otherwise
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT user_id, expires_at FROM sessions WHERE session_id = ?',
            (session_id,)
        )
        session = cursor.fetchone()

        conn.close()

        if not session:
            return None

        # Check if session is expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            return None

        return session['user_id']

    @staticmethod
    def destroy(db_path, session_id):
        """
        Destroy a session (logout)

        Args:
            db_path: Path to database
            session_id: Session ID to destroy

        Returns:
            None
        """
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        conn.commit()

        conn.close()
