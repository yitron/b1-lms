#!/bin/bash
# B1 LMS - Installation Script
# Automatically sets up backend and CLI with all dependencies

set -e

echo "=================================="
echo "B1 LMS - Installation"
echo "=================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================
# PREREQUISITE CHECK
# ============================================

echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Install Python 3.10+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
echo ""

# ============================================
# BACKEND INSTALLATION
# ============================================

echo "=================================="
echo "Installing Backend"
echo "=================================="
echo ""

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}○${NC} Virtual environment already exists"
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r ../requirements.txt
echo -e "${GREEN}✓${NC} Backend dependencies installed"

# Run migrations
echo "Running database migrations..."
python manage.py migrate --no-input
echo -e "${GREEN}✓${NC} Database migrations complete"

# Seed lessons
if [ -f "seed_lessons.py" ]; then
    echo "Seeding lesson content..."
    python manage.py shell < seed_lessons.py > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Lesson content seeded (3 modules)"
fi

deactivate
cd ..

echo ""
echo -e "${GREEN}✓ Backend installation complete${NC}"
echo ""

# ============================================
# CLI INSTALLATION
# ============================================

echo "=================================="
echo "Installing CLI"
echo "=================================="
echo ""

cd cli

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}○${NC} Virtual environment already exists"
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install CLI package
echo "Installing CLI package..."
pip install --quiet --upgrade pip
pip install --quiet -e .
echo -e "${GREEN}✓${NC} CLI package installed"

# Verify installation
if command -v lms &> /dev/null; then
    echo -e "${GREEN}✓${NC} 'lms' command available"
else
    echo -e "${YELLOW}⚠${NC} 'lms' command not in PATH (try activating venv)"
fi

deactivate
cd ..

echo ""
echo -e "${GREEN}✓ CLI installation complete${NC}"
echo ""

# ============================================
# SUMMARY
# ============================================

echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Installed:"
echo "  • Backend (Django + DRF)"
echo "  • CLI (8 commands)"
echo "  • 3 lesson modules"
echo "  • 108 automated tests"
echo ""
echo "Next steps:"
echo "  1. Run tests:  ./test.sh"
echo "  2. Start app:  ./run.sh"
echo ""
echo "=================================="
