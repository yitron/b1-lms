#!/bin/bash
# B1 LMS - Run Script
# Starts the backend server and sets up CLI environment

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================="
echo "B1 LMS - Starting Application"
echo "=================================="
echo ""

# ============================================
# CHECK INSTALLATION
# ============================================

if [ ! -d "backend/venv" ] || [ ! -d "cli/venv" ]; then
    echo -e "${RED}✗ Not installed yet${NC}"
    echo "Run: ./install.sh first"
    exit 1
fi

# Get absolute path to project root
PROJECT_ROOT=$(pwd)

# ============================================
# DETECT PLATFORM
# ============================================

if [ -f "backend/venv/bin/python" ]; then
    # Linux/macOS
    BACKEND_PYTHON="$PROJECT_ROOT/backend/venv/bin/python"
    CLI_ACTIVATE_SCRIPT="$PROJECT_ROOT/cli/venv/bin/activate"
elif [ -f "backend/venv/Scripts/python.exe" ]; then
    # Windows (Git Bash/MSYS)
    BACKEND_PYTHON="$PROJECT_ROOT/backend/venv/Scripts/python.exe"
    CLI_ACTIVATE_SCRIPT="$PROJECT_ROOT/cli/venv/Scripts/activate"
else
    echo -e "${RED}✗${NC} Backend virtual environment not found"
    echo "Run: ./install.sh first"
    exit 1
fi

# ============================================
# START BACKEND SERVER (BACKGROUND)
# ============================================

echo "Starting backend server..."
echo "-------------------------------------------"

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Port 8000 already in use${NC}"
    echo "Backend may already be running or another service is using the port."
    echo ""
    read -p "Kill existing process on port 8000? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Port 8000 cleared"
    else
        echo "Exiting..."
        exit 1
    fi
fi

# Start backend in background, redirect output to log file
cd "$PROJECT_ROOT/backend"
$BACKEND_PYTHON manage.py runserver 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd "$PROJECT_ROOT"

# Save PID for cleanup
echo $BACKEND_PID > .backend.pid

echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
echo "  Logs: backend/backend.log"
echo ""

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000 >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is ready at http://localhost:8000"
        break
    fi
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}✗${NC} Backend failed to start. Check backend/backend.log"
        exit 1
    fi
    sleep 0.5
done

echo ""

# ============================================
# SETUP CLI ENVIRONMENT
# ============================================

echo "===================================="
echo "CLI READY"
echo "===================================="
echo ""
echo -e "${GREEN}Backend is running in the background.${NC}"
echo ""
echo "You can now use the LMS CLI commands:"
echo ""
echo "  lms signup    # Create an account"
echo "  lms lessons   # List lessons"
echo "  lms --help    # See all commands"
echo ""
echo "To stop the backend server:"
echo "  kill $BACKEND_PID"
echo "  or run: kill \$(cat .backend.pid)"
echo ""
echo "===================================="
echo ""

# Activate CLI venv for the current shell
# Note: This needs to be sourced by the parent shell to work
if [ -f "$CLI_ACTIVATE_SCRIPT" ]; then
    # Export function to make lms command available
    export PATH="$PROJECT_ROOT/cli/venv/bin:$PROJECT_ROOT/cli/venv/Scripts:$PATH"

    echo -e "${BLUE}Starting interactive shell with CLI activated...${NC}"
    echo "Type 'exit' to stop the backend and return to your shell."
    echo ""

    # Start a new shell with the CLI in PATH
    PS1="(lms-cli) \[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ " bash --noprofile --norc

    # When user exits, cleanup backend
    echo ""
    echo "Stopping backend server..."
    kill $BACKEND_PID 2>/dev/null || true
    rm -f .backend.pid
    echo -e "${GREEN}✓${NC} Backend stopped"
else
    echo -e "${RED}✗${NC} CLI virtual environment not found"
    kill $BACKEND_PID 2>/dev/null || true
    rm -f .backend.pid
    exit 1
fi
