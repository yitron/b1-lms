#!/bin/bash
# B1 LMS - Run Script
# Starts the backend server and provides CLI instructions

set -e

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

# ============================================
# START BACKEND SERVER
# ============================================

echo "Starting backend server..."
echo "-------------------------------------------"

cd backend
source venv/bin/activate

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
        echo "Continuing anyway..."
    fi
fi

echo ""
echo -e "${BLUE}Starting Django development server at http://localhost:8000${NC}"
echo ""
echo "===================================="
echo "BACKEND SERVER RUNNING"
echo "===================================="
echo ""
echo "Keep this terminal open (backend must run for CLI to work)"
echo ""
echo -e "${GREEN}To use the CLI, open a NEW terminal and run:${NC}"
echo ""
echo "  cd $(pwd | sed 's/\/backend$//')/cli"
echo "  source venv/bin/activate"
echo "  lms signup    # Create an account"
echo "  lms lessons   # List lessons"
echo "  lms --help    # See all commands"
echo ""
echo "===================================="
echo ""

# Start the server (this will block)
python manage.py runserver 8000
