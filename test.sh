#!/bin/bash
# B1 LMS - Environment & Test Runner
# Checks prerequisites and runs automated tests

set -e

echo "=================================="
echo "B1 LMS - Environment & Tests"
echo "=================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# ============================================
# PREREQUISITE CHECKS
# ============================================

echo "Checking prerequisites..."
echo "-------------------------------------------"

# Test Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (requires 3.10+)"
    else
        echo -e "${RED}✗${NC} Python $PYTHON_VERSION found, requires 3.10+"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${RED}✗${NC} Python 3 not found - install from https://www.python.org/"
    ERRORS=$((ERRORS + 1))
fi

# Test pip
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip available"
else
    echo -e "${RED}✗${NC} pip not found - run: python3 -m ensurepip --upgrade"
    ERRORS=$((ERRORS + 1))
fi

# Test venv or virtualenv module
if python3 -m venv --help &> /dev/null; then
    echo -e "${GREEN}✓${NC} venv module available"
elif python3 -m virtualenv --help &> /dev/null || pip3 show virtualenv &> /dev/null; then
    echo -e "${GREEN}✓${NC} virtualenv package available"
else
    echo -e "${YELLOW}○${NC} venv/virtualenv not found (will be installed via pip during setup)"
fi

echo ""

# Stop here if prerequisites not met
if [ $ERRORS -ne 0 ]; then
    echo -e "${RED}✗ Prerequisites not met. Please install missing dependencies.${NC}"
    exit 1
fi

# ============================================
# INSTALLATION CHECK
# ============================================

echo "Checking installation..."
echo "-------------------------------------------"

BACKEND_READY=false
CLI_READY=false

if [ -d "backend/venv" ] && [ -f "backend/db.sqlite3" ]; then
    echo -e "${GREEN}✓${NC} Backend installed"
    BACKEND_READY=true
else
    echo -e "${YELLOW}○${NC} Backend not installed"
fi

if [ -d "cli/venv" ]; then
    echo -e "${GREEN}✓${NC} CLI installed"
    CLI_READY=true
else
    echo -e "${YELLOW}○${NC} CLI not installed"
fi

echo ""

# If not installed, direct to install.sh
if [ "$BACKEND_READY" = false ] || [ "$CLI_READY" = false ]; then
    echo -e "${YELLOW}Installation required. Run: ./install.sh${NC}"
    exit 0
fi

# ============================================
# RUN AUTOMATED TESTS
# ============================================

echo "=================================="
echo "Running Automated Tests"
echo "=================================="
echo ""

# Backend tests
echo "Backend Tests (48 tests)..."
echo "-------------------------------------------"
cd backend

# Detect platform and set paths to venv executables
if [ -f "venv/bin/python" ]; then
    # Linux/macOS
    PYTEST="venv/bin/pytest"
elif [ -f "venv/Scripts/python.exe" ]; then
    # Windows (Git Bash/MSYS)
    PYTEST="venv/Scripts/pytest.exe"
else
    echo -e "${RED}✗${NC} Backend virtual environment not found"
    exit 1
fi

if $PYTEST tests/ --tb=short -q; then
    echo -e "${GREEN}✓ Backend: 48 tests passed${NC}"
else
    echo -e "${RED}✗ Backend tests failed${NC}"
    ERRORS=$((ERRORS + 1))
fi
cd ..

echo ""

# CLI tests
echo "CLI Tests (60 tests)..."
echo "-------------------------------------------"
cd cli

# Detect platform and set paths to venv executables
if [ -f "venv/bin/python" ]; then
    # Linux/macOS
    PYTEST="venv/bin/pytest"
elif [ -f "venv/Scripts/python.exe" ]; then
    # Windows (Git Bash/MSYS)
    PYTEST="venv/Scripts/pytest.exe"
else
    echo -e "${RED}✗${NC} CLI virtual environment not found"
    exit 1
fi

if $PYTEST tests/ --tb=short -q; then
    echo -e "${GREEN}✓ CLI: 60 tests passed${NC}"
else
    echo -e "${RED}✗ CLI tests failed${NC}"
    ERRORS=$((ERRORS + 1))
fi
cd ..

# ============================================
# SUMMARY
# ============================================

echo ""
echo "=================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! (108 total)${NC}"
    echo ""
    echo "Next step: ./run.sh to start the application"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
echo "=================================="
