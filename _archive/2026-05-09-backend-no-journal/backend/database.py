"""
Database initialization and connection for B1 LMS
SQLite database with users, lessons, progress, quizzes, comments, sessions tables
"""

import sqlite3


def init_db(db_path='lms.db'):
    """
    Initialize SQLite database with required tables

    Args:
        db_path: Path to database file

    Returns:
        None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create lessons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id TEXT UNIQUE NOT NULL,
            module_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            content TEXT NOT NULL,
            duration INTEGER,
            difficulty TEXT,
            objectives TEXT,
            quiz_data TEXT,
            order_index INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create user_progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id),
            UNIQUE (user_id, lesson_id)
        )
    ''')

    # Create quiz_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            selected_answer INTEGER NOT NULL,
            is_correct BOOLEAN NOT NULL,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id),
            UNIQUE (user_id, lesson_id, question_id)
        )
    ''')

    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id TEXT NOT NULL,
            comment_text TEXT NOT NULL,
            parent_comment_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id),
            FOREIGN KEY (parent_comment_id) REFERENCES comments (id)
        )
    ''')

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()


def get_db_connection(db_path='lms.db'):
    """
    Get a database connection

    Args:
        db_path: Path to database file

    Returns:
        sqlite3.Connection object
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
