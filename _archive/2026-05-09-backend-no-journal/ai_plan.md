# B1-LMS Rebuild Implementation Plan: 4D + TRUE TDD

**Created:** 2026-05-08 17:52
**Methodology:** DISCOVER → DEFINE → DEVELOP → DELIVER
**Approach:** TRUE Test-Driven Development (RED-GREEN-REFACTOR)

---

## Executive Summary

Rebuild b1-lms as a full-stack multi-user Learning Management System with social learning features (comments/discussions). Follow the proven 4D + TDD methodology from b1-geocities.

**Tech Stack:**
- Backend: Python/Flask/SQLite
- Frontend: Vanilla JavaScript + Tailwind CSS
- Auth: Flask sessions
- Testing: pytest (TDD methodology)

**Key Features:**
- 3 lessons (Pydantic & Tool Use, Conversational Memory, Architecture)
- User authentication
- Progress tracking per user
- Interactive quizzes
- Comments/discussions on lessons
- Modern minimalist UI (n8n-style)

---

## Phase 1: DISCOVER (Complete)

Requirements gathered from user. See DEVELOPMENT.md for details.

**Key Decisions:**
- Multi-user with authentication (Flask sessions)
- Social learning (comments/discussions)
- Backend database (SQLite) + localStorage for caching
- Vanilla JS (no frameworks)
- Tailwind CSS for modern UI
- 3 lesson modules on AI agent fundamentals

---

## Phase 2: DEFINE (Architecture & Database Schema)

### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lessons table
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id TEXT UNIQUE NOT NULL,  -- 'lesson-01', 'lesson-02', 'lesson-03'
    module_number TEXT NOT NULL,      -- 'Module 01'
    title TEXT NOT NULL,
    subtitle TEXT,
    content TEXT NOT NULL,            -- HTML content
    duration TEXT,                    -- '15 min'
    difficulty TEXT,                  -- 'Beginner'
    objectives TEXT,                  -- JSON array
    quiz_data TEXT,                   -- JSON quiz questions
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User progress table
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id TEXT NOT NULL,
    completed BOOLEAN DEFAULT 0,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id),
    UNIQUE (user_id, lesson_id)
);

-- Quiz results table
CREATE TABLE quiz_results (
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
);

-- Comments table
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id TEXT NOT NULL,
    comment_text TEXT NOT NULL,
    parent_comment_id INTEGER,  -- For threaded discussions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lesson_id) REFERENCES lessons (lesson_id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments (id)
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

### API Endpoints

```
Authentication:
POST   /api/auth/signup          - Create new user
POST   /api/auth/login           - Login (create session)
POST   /api/auth/logout          - Logout (destroy session)
GET    /api/auth/me              - Get current user

Lessons:
GET    /api/lessons              - Get all lessons (metadata)
GET    /api/lessons/:lesson_id   - Get specific lesson (full content)

Progress:
GET    /api/progress             - Get user's progress
POST   /api/progress/:lesson_id  - Mark lesson complete
GET    /api/progress/stats       - Get statistics

Quizzes:
POST   /api/quiz/:lesson_id      - Submit quiz answer
GET    /api/quiz/:lesson_id      - Get quiz results

Comments:
GET    /api/comments/:lesson_id  - Get comments for lesson
POST   /api/comments/:lesson_id  - Add comment
DELETE /api/comments/:comment_id - Delete own comment

Static:
GET    /                         - Serve index.html
```

### File Structure

```
b1-lms/
├── backend/
│   ├── __init__.py           # Package initialization
│   ├── database.py           # init_db(), get_db_connection()
│   ├── models.py             # User, Lesson, Progress, Quiz, Comment
│   ├── auth.py               # hash_password(), verify_password()
│   ├── session.py            # Session management
│   └── app.py                # Flask factory (create_app)
│
├── tests/
│   ├── test_backend.py       # All backend tests
│   └── test_frontend.py      # HTML structure tests
│
├── static/
│   ├── css/
│   │   └── main.css          # Tailwind-generated CSS
│   └── js/
│       ├── app.js            # Main application
│       ├── auth.js           # Authentication UI
│       ├── lessons.js        # Lesson rendering
│       ├── quiz.js           # Quiz functionality
│       └── comments.js       # Comments/discussions
│
├── templates/
│   └── index.html            # SPA template (Tailwind)
│
├── data/
│   └── lesson_content.json   # Lesson content (3 modules)
│
├── install.sh                # Setup script
├── run.sh                    # Start server
├── test.sh                   # Test runner
├── requirements.txt          # Python dependencies
├── .gitignore
├── README.md
├── DEVELOPMENT.md
└── ai_plan.md                # This file
```

---

## Phase 3: DEVELOP (TDD Cycles)

### TDD Cycle Order (15 Cycles)

Follow TRUE RED-GREEN-REFACTOR for each cycle:
- **RED:** Write failing test first
- **GREEN:** Write minimal code to pass
- **REFACTOR:** Clean up and improve

#### Cycle 1: Database Layer - Initialization
**RED:** Test that `init_db()` creates all tables
**GREEN:** Implement `init_db()` with CREATE TABLE statements
**REFACTOR:** Clean up SQL, ensure idempotency (IF NOT EXISTS)

**Critical Files:**
- `backend/database.py`
- `tests/test_backend.py` (class TestDatabase)

#### Cycle 2: Database Layer - Connection
**RED:** Test that `get_db_connection()` returns connection with Row factory
**GREEN:** Implement `get_db_connection()` with sqlite3.Row
**REFACTOR:** Ensure proper connection handling

**Critical Files:**
- `backend/database.py`
- `tests/test_backend.py`

#### Cycle 3: User Model - Basic Operations
**RED:** Test `User.create()` and `User.get_by_username()`
**GREEN:** Implement User model class with database methods
**REFACTOR:** Extract common patterns

**Critical Files:**
- `backend/models.py` (class User)
- `tests/test_backend.py` (class TestUser)

#### Cycle 4: Password Hashing
**RED:** Test password hashing and verification
**GREEN:** Implement `hash_password()` and `verify_password()` using werkzeug.security
**REFACTOR:** Add password strength validation

**Critical Files:**
- `backend/auth.py`
- `tests/test_backend.py` (class TestAuth)

#### Cycle 5: Session Management
**RED:** Test session creation, validation, expiry
**GREEN:** Implement Session model with create/validate/destroy
**REFACTOR:** Add cleanup for expired sessions

**Critical Files:**
- `backend/session.py` (class Session)
- `tests/test_backend.py` (class TestSession)

#### Cycle 6: Flask App Factory
**RED:** Test that `create_app()` returns Flask instance
**GREEN:** Implement minimal `create_app(db_path)` factory
**REFACTOR:** Configure app settings (secret key, etc.)

**Critical Files:**
- `backend/app.py`
- `tests/test_backend.py` (class TestFlaskApp)

#### Cycle 7: Authentication Endpoints
**RED:** Test POST /api/auth/signup, /api/auth/login, /api/auth/logout
**GREEN:** Implement auth endpoints with session creation
**REFACTOR:** Add validation and error handling

**Critical Files:**
- `backend/app.py` (auth routes)
- `tests/test_backend.py` (class TestFlaskAPI)

#### Cycle 8: Lesson Model
**RED:** Test `Lesson.get_all()` and `Lesson.get_by_id()`
**GREEN:** Implement Lesson model with database queries
**REFACTOR:** Add JSON parsing for objectives/quiz_data

**Critical Files:**
- `backend/models.py` (class Lesson)
- `tests/test_backend.py` (class TestLesson)

#### Cycle 9: Lesson Endpoints
**RED:** Test GET /api/lessons and GET /api/lessons/:lesson_id
**GREEN:** Implement lesson endpoints
**REFACTOR:** Optimize queries

**Critical Files:**
- `backend/app.py` (lesson routes)
- `tests/test_backend.py` (class TestFlaskAPI)

#### Cycle 10: Progress Model
**RED:** Test progress tracking (mark complete, get progress)
**GREEN:** Implement Progress model
**REFACTOR:** Add aggregate statistics

**Critical Files:**
- `backend/models.py` (class Progress)
- `tests/test_backend.py` (class TestProgress)

#### Cycle 11: Progress Endpoints
**RED:** Test GET /api/progress, POST /api/progress/:lesson_id
**GREEN:** Implement progress endpoints with user isolation
**REFACTOR:** Ensure authentication required

**Critical Files:**
- `backend/app.py` (progress routes)
- `tests/test_backend.py` (class TestFlaskAPI)

#### Cycle 12: Quiz Model
**RED:** Test quiz answer submission and score calculation
**GREEN:** Implement QuizResult model
**REFACTOR:** Add validation

**Critical Files:**
- `backend/models.py` (class QuizResult)
- `tests/test_backend.py` (class TestQuiz)

#### Cycle 13: Quiz Endpoints
**RED:** Test POST /api/quiz/:lesson_id, GET /api/quiz/:lesson_id
**GREEN:** Implement quiz endpoints
**REFACTOR:** Add answer validation

**Critical Files:**
- `backend/app.py` (quiz routes)
- `tests/test_backend.py` (class TestFlaskAPI)

#### Cycle 14: Comment Model
**RED:** Test comment creation, retrieval, deletion
**GREEN:** Implement Comment model with threading support
**REFACTOR:** Add ownership validation

**Critical Files:**
- `backend/models.py` (class Comment)
- `tests/test_backend.py` (class TestComment)

#### Cycle 15: Comment Endpoints
**RED:** Test GET /api/comments/:lesson_id, POST /api/comments/:lesson_id, DELETE /api/comments/:comment_id
**GREEN:** Implement comment endpoints
**REFACTOR:** Add permission checks

**Critical Files:**
- `backend/app.py` (comment routes)
- `tests/test_backend.py` (class TestFlaskAPI)

---

## Phase 4: DELIVER (Frontend Integration)

### Frontend Architecture

**Tech Stack:**
- Vanilla JavaScript (ES6+)
- Tailwind CSS (CDN or CLI)
- localStorage for offline caching only

**Key Components:**

1. **Authentication (`auth.js`)**
   - Login/signup forms
   - Session management
   - Auto-redirect if not authenticated

2. **Lessons (`lessons.js`)**
   - Fetch from /api/lessons
   - Render lesson list
   - Display content
   - Show completion indicators

3. **Quiz (`quiz.js`)**
   - Interactive multiple-choice
   - Submit to /api/quiz/:lesson_id
   - Show immediate feedback

4. **Comments (`comments.js`)**
   - Fetch for current lesson
   - Display threaded comments
   - Add/delete comments

5. **App Orchestration (`app.js`)**
   - Initialize app
   - Handle routing
   - Manage authentication state
   - Update progress bar

### Implementation Steps

1. Create `templates/index.html` with Tailwind
2. Implement `static/js/auth.js` (login/signup UI)
3. Implement `static/js/lessons.js` (lesson display)
4. Implement `static/js/quiz.js` (quiz functionality)
5. Implement `static/js/comments.js` (discussions)
6. Implement `static/js/app.js` (main orchestration)
7. Migrate lesson content to `data/lesson_content.json`
8. Create `backend/seed_data.py` to populate lessons

---

## Dependencies

### requirements.txt
```
Flask==3.0.0
pytest==7.4.3
ruff==0.1.6
Werkzeug==3.0.0
```

### package.json (for Tailwind CLI)
```json
{
  "devDependencies": {
    "tailwindcss": "^3.0.0"
  }
}
```

---

## Installation Scripts

### install.sh
- Create venv (visible, not hidden)
- Install Python dependencies
- Initialize database (init_db)
- Seed lesson data
- Run tests
- Success message

### run.sh
- Check venv exists
- Activate venv
- Check database exists
- Start Flask on port 5050
- Auto-open browser

### test.sh
- Check venv exists
- Activate venv
- Run pytest with verbose output
- Report results

---

## Testing Strategy

### Backend Tests (pytest)

**Test Classes:**
- `TestDatabase` - Database initialization, connection
- `TestAuth` - Password hashing, verification
- `TestUser` - User creation, retrieval
- `TestSession` - Session creation, validation, expiry
- `TestLesson` - Lesson retrieval
- `TestProgress` - Progress tracking, statistics
- `TestQuiz` - Quiz submission, scoring
- `TestComment` - Comment CRUD, threading
- `TestFlaskAPI` - All API endpoints (auth, lessons, progress, quiz, comments)

**Test Pattern:**
```python
def test_something():
    # Arrange: Create test database
    test_db = 'test_lms.db'
    if os.path.exists(test_db):
        os.remove(test_db)
    init_db(test_db)

    # Act: Perform action
    result = do_something(test_db)

    # Assert: Verify result
    assert result == expected

    # Cleanup: Remove test database
    os.remove(test_db)
```

---

## Critical Success Factors

1. **Follow TDD Strictly:** Write tests BEFORE code (RED-GREEN-REFACTOR)
2. **Document Honestly:** Record decisions, mistakes, improvements in DEVELOPMENT.md
3. **Isolate Concerns:** Database → Models → API → Frontend (layers)
4. **Test Isolation:** Each test uses fresh database (test_lms.db)
5. **User Authentication:** All endpoints except /api/lessons require auth
6. **Data Isolation:** Users only see their own progress/quiz results
7. **Offline Support:** localStorage caches data, backend is source of truth
8. **Modern UI:** Tailwind CSS for clean, minimalist design (n8n-style)

---

## Verification Steps

After implementation:

1. **Backend Tests:** `./test.sh` → All tests pass
2. **Manual Flow:**
   - Signup new user
   - Login
   - View lessons
   - Take quiz
   - See progress update
   - Add comment
   - Logout
3. **Multi-User Test:**
   - Create 2 users
   - Each completes different lessons
   - Verify isolated progress
   - Verify both can comment on same lesson

---

## Next Steps

1. Create file structure
2. Start TDD Cycle 1 (Database Layer)
3. Continue through all 15 cycles
4. Implement frontend
5. Migrate lesson content
6. Final testing
7. Documentation update

**Estimated Time:** 8-12 hours (following TDD discipline)

---

**Plan Created:** 2026-05-08 17:52
**Methodology:** 4D + TRUE TDD
**Confidence:** High (following proven b1-geocities pattern)
