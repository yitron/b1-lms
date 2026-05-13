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

    # Check if venv module is available
    if python3 -m venv --help &> /dev/null; then
        # Try to use built-in venv
        if python3 -m venv venv 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Virtual environment created"
        else
            # venv failed (likely ensurepip issue), try without pip
            echo -e "${YELLOW}⚠${NC} ensurepip not available, creating venv without pip..."
            python3 -m venv --without-pip venv

            # Manually install pip into the venv
            echo "Installing pip into virtual environment..."

            # Detect venv Python path
            if [ -f "venv/bin/python" ]; then
                VENV_PYTHON="venv/bin/python"
            elif [ -f "venv/Scripts/python.exe" ]; then
                VENV_PYTHON="venv/Scripts/python.exe"
            else
                echo -e "${RED}✗${NC} Could not find Python in virtual environment"
                exit 1
            fi

            if command -v curl &> /dev/null; then
                curl -sS https://bootstrap.pypa.io/get-pip.py | $VENV_PYTHON
            elif command -v wget &> /dev/null; then
                wget -qO- https://bootstrap.pypa.io/get-pip.py | $VENV_PYTHON
            else
                echo -e "${RED}✗${NC} curl or wget required to install pip"
                echo "Please install curl: your package manager may have it"
                exit 1
            fi

            echo -e "${GREEN}✓${NC} Virtual environment created and pip installed"
        fi
    else
        # venv not available, try virtualenv
        echo -e "${YELLOW}⚠${NC} Python venv module not found, checking for virtualenv..."

        if ! python3 -m virtualenv --help &> /dev/null; then
            echo "Installing virtualenv package..."
            python3 -m pip install --user virtualenv
        fi

        python3 -m virtualenv venv
        echo -e "${GREEN}✓${NC} Virtual environment created using virtualenv"
    fi
else
    echo -e "${YELLOW}○${NC} Virtual environment already exists"
fi

# Detect platform and set paths to venv executables
if [ -f "venv/bin/python" ]; then
    # Linux/macOS
    PYTHON="venv/bin/python"
    PIP="venv/bin/pip"
elif [ -f "venv/Scripts/python.exe" ]; then
    # Windows (Git Bash/MSYS)
    PYTHON="venv/Scripts/python.exe"
    PIP="venv/Scripts/pip.exe"
else
    echo -e "${RED}✗${NC} Could not find Python in virtual environment"
    exit 1
fi

# Install dependencies
echo "Installing backend dependencies..."
$PIP install --quiet --upgrade pip
$PIP install --quiet -r ../requirements.txt
echo -e "${GREEN}✓${NC} Backend dependencies installed"

# Run migrations
echo "Running database migrations..."
$PYTHON manage.py migrate --no-input
echo -e "${GREEN}✓${NC} Database migrations complete"

# Seed lessons
if [ -f "seed_lessons.py" ]; then
    echo "Seeding lesson content..."
    $PYTHON manage.py shell < seed_lessons.py > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Lesson content seeded (3 modules)"
fi
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

    # Check if venv module is available
    if python3 -m venv --help &> /dev/null; then
        # Try to use built-in venv
        if python3 -m venv venv 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Virtual environment created"
        else
            # venv failed (likely ensurepip issue), try without pip
            echo -e "${YELLOW}⚠${NC} ensurepip not available, creating venv without pip..."
            python3 -m venv --without-pip venv

            # Manually install pip into the venv
            echo "Installing pip into virtual environment..."

            # Detect venv Python path
            if [ -f "venv/bin/python" ]; then
                VENV_PYTHON="venv/bin/python"
            elif [ -f "venv/Scripts/python.exe" ]; then
                VENV_PYTHON="venv/Scripts/python.exe"
            else
                echo -e "${RED}✗${NC} Could not find Python in virtual environment"
                exit 1
            fi

            if command -v curl &> /dev/null; then
                curl -sS https://bootstrap.pypa.io/get-pip.py | $VENV_PYTHON
            elif command -v wget &> /dev/null; then
                wget -qO- https://bootstrap.pypa.io/get-pip.py | $VENV_PYTHON
            else
                echo -e "${RED}✗${NC} curl or wget required to install pip"
                echo "Please install curl: your package manager may have it"
                exit 1
            fi

            echo -e "${GREEN}✓${NC} Virtual environment created and pip installed"
        fi
    else
        # venv not available, try virtualenv
        echo -e "${YELLOW}⚠${NC} Python venv module not found, checking for virtualenv..."

        if ! python3 -m virtualenv --help &> /dev/null; then
            echo "Installing virtualenv package..."
            python3 -m pip install --user virtualenv
        fi

        python3 -m virtualenv venv
        echo -e "${GREEN}✓${NC} Virtual environment created using virtualenv"
    fi
else
    echo -e "${YELLOW}○${NC} Virtual environment already exists"
fi

# Detect platform and set paths to venv executables
if [ -f "venv/bin/python" ]; then
    # Linux/macOS
    PYTHON="venv/bin/python"
    PIP="venv/bin/pip"
    LMS="venv/bin/lms"
elif [ -f "venv/Scripts/python.exe" ]; then
    # Windows (Git Bash/MSYS)
    PYTHON="venv/Scripts/python.exe"
    PIP="venv/Scripts/pip.exe"
    LMS="venv/Scripts/lms.exe"
else
    echo -e "${RED}✗${NC} Could not find Python in virtual environment"
    exit 1
fi

# Install CLI package
echo "Installing CLI package..."
$PIP install --quiet --upgrade pip
$PIP install --quiet -e .
echo -e "${GREEN}✓${NC} CLI package installed"

# Verify installation
if [ -f "$LMS" ]; then
    echo -e "${GREEN}✓${NC} 'lms' command available at $LMS"
else
    echo -e "${YELLOW}⚠${NC} 'lms' command not found in venv"
fi
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
