# B1 LMS - Interactive AI Agent Learning Platform

## Overview

### Problem

- **Who is affected?** Developers, students, and professionals learning about AI agent architecture who need structured, interactive educational content.

- **What is the issue?** Most AI agent documentation is scattered across technical papers, API docs, and blog posts. Learners need a cohesive, interactive platform that explains core concepts (LLM APIs, tool use, conversational memory) in a structured, progressive manner with multi-user support and persistent progress tracking.

### Outcome

- **What was achieved?** A fully functional, full-stack Learning Management System (LMS) teaching AI agent fundamentals through 3 progressive modules with user authentication, progress tracking, and interactive quizzes.

- **Measurable results:**
  - **Backend:** Django + Django REST Framework API
  - **Database:** SQLite with user authentication and progress tracking
  - **API Endpoints:** 7 REST endpoints (auth, lessons, progress)
  - **CLI:** 8 commands with Rich terminal formatting
  - **Test Coverage:** 108 automated tests (48 backend + 60 CLI)
  - **Content:** 3 comprehensive lessons (Modules 00-02, 22,691 chars)
  - **Features:** Multi-user support, token authentication, per-user progress tracking
  - **Code Quality:** All code passes ruff linting and pytest
  - **Architecture:** Clean separation (API-only backend, CLI frontend)

---

## Demo

### User Journey (CLI)

1. **Install CLI** - `pip install -e cli/`
2. **Create account** - `lms signup` → Enter username/password
3. **List lessons** - `lms lessons` → See 3 modules in beautiful table
4. **View lesson** - `lms view module-00` → Read with Rich markdown rendering
5. **Complete lesson** - `lms complete module-00` → Mark as done 🎉
6. **Check progress** - `lms progress` → See completion status with dates
7. **Continue learning** - Repeat for Module 01, 02
8. **Finish course** - Get congratulations panel when all complete!

### CLI Screenshots

**List Lessons:**
```
$ lms lessons

                               Available Lessons
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Module       ┃ Title                   ┃ Subtitle               ┃   Status   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Module 00    │ LLM API Communication   │ Learn the fundamentals │     ✓      │
│ Module 01    │ Pydantic Pattern & Tool │ Explore how agents use │     ○      │
│ Module 02    │ Conversational Memory   │ Master context         │     ○      │
└──────────────┴─────────────────────────┴────────────────────────┴────────────┘
```

**View Lesson Content:**
```
$ lms view module-00

╭──────────────────────────────── 📚 module-00 ────────────────────────────────╮
│ LLM API Communication                                                        │
│ Learn the fundamentals of communicating with Large Language Models           │
╰──────────────────────────────────────────────────────────────────────────────╯

                        Module 00: LLM API Communication

Introduction

Understanding how to communicate with Large Language Models (LLMs) through APIs
is the foundation of building AI agents...

[Beautiful markdown rendering with headers, lists, code blocks]
```

**Check Progress:**
```
$ lms progress

                             Your Learning Progress
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Module       ┃ Title                ┃     Status      ┃ Completed            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Module 00    │ LLM API Communication│   ✓ Complete    │ 2026-05-10           │
│ Module 01    │ Pydantic & Tool Use  │   ✓ Complete    │ 2026-05-10           │
│ Module 02    │ Conversational Memory│  ○ Not started  │                      │
└──────────────┴──────────────────────┴─────────────────┴──────────────────────┘

Progress: 2/3 lessons completed (66%)
Keep going! 1 lesson remaining.
```

**Quick Start:**
```bash
# 1. Start backend server (Terminal 1)
cd backend
source venv/bin/activate
python manage.py runserver 8000

# 2. Use CLI (Terminal 2)
cd cli
source venv/bin/activate
pip install -e .

# 3. Create account and start learning
lms signup          # Create account
lms lessons         # See available lessons
lms view module-00  # Read first lesson
lms complete module-00  # Mark as done
lms progress        # Check your progress
```

---

## Technology Stack

### Backend:
- **Django 6.0** - Web framework
- **Django REST Framework 3.15** - RESTful API
- **SQLite** - Database (zero-config)
- **Token Authentication** - DRF TokenAuthentication
- **pytest-django** - Test framework (48 tests)
- **ruff** - Python linter

### CLI Frontend:
- **Python 3.10+** - CLI runtime
- **Click 8.1** - Command-line framework
- **Rich 13.7** - Terminal UI formatting (tables, markdown, colors)
- **Requests 2.31** - HTTP client for API calls
- **pytest 8.1** - Test framework (60 tests)

### Architecture:
- **API-only backend** - Django serves JSON (no templates)
- **Separate CLI frontend** - Terminal application calling API
- **Token-based auth** - Stored at ~/.lms/token (600 permissions)
- **CORS enabled** - Cross-origin support
- **Frontend-agnostic** - Can add web/mobile frontend later

---

## Development Approach with AI

### AI Tools and Models
- **Claude Sonnet 3.5** - Initial development assistant
- **Purpose:** Content creation, code structure, quiz generation

### AI Agents and Roles
1. **Content Creation Agent**
   - **Role:** Educational content writer
   - **Skills:** AI agent fundamentals, technical writing, pedagogy
   - **Responsibilities:** Write lesson content, create quiz questions, design learning progression

2. **Development Agent**
   - **Role:** Frontend developer
   - **Skills:** HTML, CSS, JavaScript, responsive design, accessibility
   - **Responsibilities:** Build SPA routing, quiz engine, progress tracking, responsive layout

### Key Prompts Used

**Content Creation:**
```
"Create 3 progressive lessons on AI agent architecture"
→ Result: Module 00 (LLM APIs), Module 01 (Tool Use), Module 02 (Memory)

"Generate quiz questions for each module"
→ Result: Interactive quizzes with multiple-choice questions

"Design visual diagrams explaining agent concepts"
→ Result: SVG diagrams for request/response, tool calling, memory management
```

**Implementation:**
```
"Build a single-page LMS with sidebar navigation"
→ Result: SPA routing with hash-based navigation

"Implement progress tracking with localStorage"
→ Result: Persistent progress across browser sessions

"Create responsive design for mobile and desktop"
→ Result: CSS Grid/Flexbox layout with breakpoints
```

### Key Review Points and Decisions

| Review Point | Decision Made | Rationale |
|-------------|---------------|-----------|
| **Backend Architecture** | API-only (Django + DRF) | Frontend-agnostic, reusable for web/mobile/CLI |
| **Frontend Type** | CLI (not web) | Target users are developers, faster development |
| **CLI Framework** | Click + Rich | Professional CLI with beautiful terminal UI |
| **Data persistence** | SQLite + Token auth | Multi-user support, secure authentication |
| **Lesson storage** | Database with seed script | Easy content management and updates |
| **Test approach** | TRUE TDD (RED-GREEN-REFACTOR) | All 12 cycles documented in DEVELOPMENT.md |

**Note:** This project was built using **TRUE Test-Driven Development (TDD)** following the 4D methodology (DISCOVER → DEFINE → DEVELOP → DELIVER). See [DEVELOPMENT.md](DEVELOPMENT.md) for complete development journal with timestamps.

---

## Installation

### Requirements

- Python 3.10+ (tested with Python 3.14)
- pip (Python package manager)
- Two terminal windows (one for backend, one for CLI)

### Quick Start

**Step 1: Backend Setup**

```bash
# Clone repository
git clone https://github.com/yourusername/b1-lms.git
cd b1-lms/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r ../requirements.txt

# Run database migrations
python manage.py migrate

# Seed lesson content
python manage.py shell < seed_lessons.py

# Create admin user (optional, for Django admin panel)
python manage.py createsuperuser

# Start development server
python manage.py runserver 8000
# Server running at http://localhost:8000
```

**Step 2: CLI Setup** (in a new terminal)

```bash
# Navigate to CLI directory
cd b1-lms/cli

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install CLI in editable mode
pip install -e .

# Verify installation
lms --help
```

**Step 3: Start Learning!**

```bash
# Create your account
lms signup

# List available lessons
lms lessons

# View a lesson
lms view module-00

# Mark lesson as complete
lms complete module-00

# Check your progress
lms progress
```

### Access

- **API Base URL:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/
- **API Documentation:** See API Endpoints section below

---

## Usage

### Running the Backend Server

```bash
# From backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Start Django development server
python manage.py runserver 8000

# Server running at http://localhost:8000
```

### Using the CLI

**Authentication Commands:**
```bash
# Create a new account
lms signup
# Prompts: Username, Password, Email (optional)

# Login to existing account
lms login
# Prompts: Username, Password

# Check authentication status
lms whoami

# Logout
lms logout
```

**Learning Commands:**
```bash
# List all available lessons
lms lessons

# View a specific lesson (with Rich markdown rendering)
lms view <lesson-id>
# Example: lms view module-00

# Mark a lesson as complete
lms complete <lesson-id>
# Example: lms complete module-00

# Check your learning progress
lms progress
```

**CLI Features:**
- 📚 Beautiful Rich tables and markdown rendering
- ✓ Colored status indicators (green ✓ for complete, gray ○ for not started)
- 🎉 Congratulations message when all lessons complete
- 🔒 Secure token storage at ~/.lms/token (600 permissions)
- 📊 Progress tracking with completion dates
- 📝 Quiz indicators showing available quizzes

### Running Tests

**Backend Tests:**
```bash
# From backend directory with venv activated
cd backend
source venv/bin/activate

# Run all backend tests (48 tests)
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v
pytest tests/test_api.py -v
pytest tests/test_models.py -v

# Run with coverage
pytest tests/ --cov=lms --cov-report=html
```

**CLI Tests:**
```bash
# From CLI directory with venv activated
cd cli
source venv/bin/activate

# Run all CLI tests (60 tests)
pytest tests/ -v

# Run specific test file
pytest tests/test_auth_commands.py -v
pytest tests/test_lessons_commands.py -v
pytest tests/test_progress_commands.py -v
```

**All Tests:**
```bash
# Total: 108 tests (48 backend + 60 CLI)
# Backend: 48 passed
# CLI: 60 passed
```

### Expected Test Output

```
============================= test session starts ==============================
platform darwin -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0
collected 48 items

tests/test_api.py::TestLessonsAPI::... PASSED                          [ 17%]
tests/test_api.py::TestProgressAPI::... PASSED                         [ 37%]
tests/test_auth.py::TestAuthSignup::... PASSED                         [ 50%]
tests/test_auth.py::TestAuthLogin::... PASSED                          [ 62%]
tests/test_auth.py::TestAuthLogout::... PASSED                         [ 68%]
tests/test_models.py::TestLessonModel::... PASSED                      [ 81%]
tests/test_models.py::TestUserProgressModel::... PASSED                [ 93%]
tests/test_setup.py::... PASSED                                        [100%]

============================== 48 passed in 9.70s ===============================
```

### API Endpoints

**Authentication:**
```bash
# Signup
POST /api/auth/signup/
Body: {"username": "user", "password": "pass123", "email": "user@example.com"}
→ Returns: {"token": "...", "user": {...}}

# Login
POST /api/auth/login/
Body: {"username": "user", "password": "pass123"}
→ Returns: {"token": "...", "user": {...}}

# Logout (requires auth)
POST /api/auth/logout/
Headers: Authorization: Token <your-token>
→ Returns: {"message": "Successfully logged out"}
```

**Lessons (Public):**
```bash
# Get all lessons
GET /api/lessons/
→ Returns: {"lessons": [...]}

# Get specific lesson
GET /api/lessons/module-00/
→ Returns: {lesson data}
```

**Progress (Requires Auth):**
```bash
# Get user progress
GET /api/progress/
Headers: Authorization: Token <your-token>
→ Returns: {"progress": [...]}

# Mark lesson complete
POST /api/progress/complete/
Headers: Authorization: Token <your-token>
Body: {"lesson_id": "module-00"}
→ Returns: {"message": "...", "progress": {...}}
```

### Manual Testing Example

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}'

# 2. Get lessons (public)
curl http://localhost:8000/api/lessons/

# 3. Mark lesson complete (use token from signup)
curl -X POST http://localhost:8000/api/progress/complete/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"lesson_id": "module-00"}'

# 4. Check progress
curl http://localhost:8000/api/progress/ \
  -H "Authorization: Token <your-token>"
```

---

## Project Structure

```
b1-lms/
├── backend/                    # Django backend
│   ├── config/                 # Django project settings
│   │   ├── settings.py         # Django configuration
│   │   ├── urls.py             # Root URL routing
│   │   └── wsgi.py             # WSGI application
│   │
│   ├── lms/                    # Main Django app
│   │   ├── models.py           # Lesson, UserProgress models
│   │   ├── serializers.py      # DRF serializers
│   │   ├── views.py            # API views
│   │   ├── urls.py             # API URL routing
│   │   ├── admin.py            # Django admin configuration
│   │   └── migrations/         # Database migrations
│   │
│   ├── tests/                  # Backend tests
│   │   ├── test_setup.py       # Setup tests (4)
│   │   ├── test_models.py      # Model tests (12)
│   │   ├── test_auth.py        # Auth API tests (15)
│   │   └── test_api.py         # Lessons/Progress API tests (17)
│   │
│   ├── manage.py               # Django management script
│   ├── db.sqlite3              # SQLite database (created on migrate)
│   └── venv/                   # Virtual environment
│
├── cli/                        # CLI frontend
│   ├── lms_cli/                # CLI package
│   │   ├── __init__.py         # Package initialization
│   │   ├── cli.py              # Main CLI entry point (Click)
│   │   ├── api_client.py       # HTTP client for API
│   │   ├── config.py           # Token storage management
│   │   └── commands/           # CLI commands
│   │       ├── auth.py         # Auth commands (4 commands)
│   │       ├── lessons.py      # Lessons commands (2 commands)
│   │       └── progress.py     # Progress commands (2 commands)
│   │
│   ├── tests/                  # CLI tests
│   │   ├── test_api_client.py  # API client tests (13)
│   │   ├── test_config.py      # Config tests (13)
│   │   ├── test_auth_commands.py    # Auth command tests (12)
│   │   ├── test_lessons_commands.py # Lessons command tests (11)
│   │   └── test_progress_commands.py # Progress command tests (11)
│   │
│   ├── setup.py                # Package setup for pip install
│   ├── requirements.txt        # CLI dependencies
│   ├── pytest.ini              # pytest configuration
│   └── venv/                   # Virtual environment
│
├── _archive/                   # Archived implementations
│   ├── 2026-05-08-non-tdd/     # Original frontend-only version
│   └── 2026-05-09-backend-no-journal/  # Lost backend attempt
│
├── requirements.txt            # Python dependencies (backend)
├── pytest.ini                  # pytest configuration (backend)
├── DEVELOPMENT.md              # Development journal (TDD cycles)
├── README.md                   # This file
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore patterns
```

### Key Files

**Backend:**
- **`backend/lms/models.py`** - Lesson & UserProgress models (Django ORM)
- **`backend/lms/serializers.py`** - DRF serializers for API responses
- **`backend/lms/views.py`** - API views (auth, lessons, progress)
- **`backend/lms/urls.py`** - API endpoint routing
- **`backend/config/settings.py`** - Django + DRF configuration
- **`backend/seed_lessons.py`** - Seed script for lesson content
- **`backend/tests/`** - 48 automated tests (pytest-django)

**CLI:**
- **`cli/lms_cli/cli.py`** - Main CLI entry point with Click
- **`cli/lms_cli/api_client.py`** - HTTP client wrapper for API
- **`cli/lms_cli/config.py`** - Token storage at ~/.lms/token
- **`cli/lms_cli/commands/`** - 8 CLI commands (auth, lessons, progress)
- **`cli/setup.py`** - Makes `lms` command available globally
- **`cli/tests/`** - 60 automated tests (pytest)

---

## Reflection

### Development Journey

This project was **rebuilt from scratch using TRUE Test-Driven Development (TDD)** following the 4D methodology learned from b1-geocities. See **[DEVELOPMENT.md](DEVELOPMENT.md)** for complete development journal.

**Current State (2026-05-10):**
- [TDD Rebuild Complete](DEVELOPMENT.md)
  - **Approach:** TRUE TDD (RED-GREEN-REFACTOR for every feature)
  - **Result:** Full-stack LMS with Django backend + CLI frontend
  - **Methodology:** 4D (DISCOVER → DEFINE → DEVELOP → DELIVER)
  - **Documentation:** Every TDD cycle documented with timestamps

**Key Implementation:**
- **12 TDD Cycles:** All documented in DEVELOPMENT.md
- **Phase 1 (DISCOVER):** Requirements gathered through human-AI Q&A
- **Phase 2 (DEFINE):** Database schema, API endpoints, test strategy designed
- **Phase 3 (DEVELOP):** 12 TDD cycles
  - Cycles 1-8: Backend (Models → Auth → Lessons → Progress)
  - Cycles 9-12: CLI (API Client → Auth → Lessons → Progress)
- **Test Coverage:** 108 tests (48 backend + 60 CLI)
- **Manual Testing:** All API endpoints and CLI commands verified working

### What Worked

✅ **TRUE TDD Methodology**
- RED-GREEN-REFACTOR for every feature
- Tests written FIRST, code second
- 48 tests, all passing
- Complete test coverage of backend

✅ **Django + DRF**
- Clean API structure
- Built-in admin panel for managing lessons
- Token authentication out-of-the-box
- Excellent ORM for database operations

✅ **API Design**
- RESTful endpoints
- Proper HTTP status codes
- User isolation (security)
- Idempotent operations

✅ **Development Documentation**
- Every TDD cycle documented in DEVELOPMENT.md
- Timestamped human-AI collaboration
- Honest reflection on process
- Complete development journal

### What's Next (Phase 4: DELIVER)

**Remaining Tasks:**
1. ✅ Backend API complete (8 TDD cycles)
2. ⏳ Seed lesson data script
3. ⏳ Setup scripts (install.sh, run.sh, test.sh)
4. ⏳ Frontend implementation (Vanilla JS + Tailwind)
5. ⏳ Frontend-backend integration
6. ⏳ Final testing and documentation

**Future Enhancements (v2):**
- Quiz results storage (track history)
- Comments/discussions on lessons
- User profiles and statistics
- Admin dashboard with analytics
- Email notifications
- More AI agent content modules

### TDD Success

This project demonstrates **successful TRUE TDD implementation**:
- ✅ 48 automated tests (all passing)
- ✅ Manual testing confirms API functionality
- ✅ Code passes ruff linting
- ✅ Clean architecture (models → API → frontend)
- ✅ Complete development journal
- ✅ Human-AI collaboration documented

---

## Course Content

### Module 00: LLM API Communication
Learn the fundamentals of communicating with Large Language Models through APIs. Understand request/response patterns, message formatting, and basic agent architecture.

**Topics Covered:**
- API request structure
- Message roles (system, user, assistant)
- Response handling
- Basic agent loop

### Module 01: Pydantic Pattern & Tool Use
Explore how agents use structured data validation and tool calling. Understand the agent loop, tool integration, and structured outputs.

**Topics Covered:**
- Pydantic for data validation
- Tool calling pattern
- Agent decision-making
- Structured outputs

### Module 02: Conversational Memory
Master the concepts of message history, context management, and maintaining state across multi-turn conversations with AI agents.

**Topics Covered:**
- Message history management
- Context window limitations
- Conversation state
- Memory strategies

---

**Built for Learning AI Agent Fundamentals**

*"Whatsoever thy hand findeth to do, do it with thy might" - Ecclesiastes 9:10 (KJV)*
