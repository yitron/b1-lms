#!/bin/bash

# ============================================
# B1 LMS - AGGREGATED TEST RUNNER
# Tests only essential functionality
# Robust component tests in tests/
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "B1 LMS - ESSENTIAL TESTS"
echo "=========================================="
echo ""

TOTAL_PASSED=0
TOTAL_FAILED=0

# ============================================
# ESSENTIAL TEST 1: Core files exist
# ============================================

echo "1. Core Files Check"
echo "-------------------------------------------"

if [ -f "index.html" ] && [ -f "style.css" ] && [ -f "script.js" ] && [ -f "lessons/lessons.js" ]; then
    echo -e "${GREEN}✓${NC} All core files present (HTML, CSS, JS, lessons data)"
    ((TOTAL_PASSED++))
else
    echo -e "${RED}✗${NC} Missing core files"
    ((TOTAL_FAILED++))
fi

echo ""

# ============================================
# ESSENTIAL TEST 2: SPA structure exists
# ============================================

echo "2. SPA Architecture"
echo "-------------------------------------------"

if grep -q "navigateToLesson" script.js && \
   grep -q "window.location.hash\|location.hash" script.js; then
    echo -e "${GREEN}✓${NC} SPA navigation implemented"
    ((TOTAL_PASSED++))
else
    echo -e "${RED}✗${NC} SPA navigation missing"
    ((TOTAL_FAILED++))
fi

echo ""

# ============================================
# ESSENTIAL TEST 3: Quiz system exists
# ============================================

echo "3. Quiz System"
echo "-------------------------------------------"

if grep -q "renderQuiz\|checkAnswer" script.js && \
   grep -q "quiz" lessons/lessons.js; then
    echo -e "${GREEN}✓${NC} Quiz system implemented with data"
    ((TOTAL_PASSED++))
else
    echo -e "${RED}✗${NC} Quiz system not properly implemented"
    ((TOTAL_FAILED++))
fi

echo ""

# ============================================
# ESSENTIAL TEST 4: Progress tracking exists
# ============================================

echo "4. Progress Tracking"
echo "-------------------------------------------"

if grep -q "localStorage" script.js && \
   grep -q "saveProgress\|loadProgress" script.js; then
    echo -e "${GREEN}✓${NC} Progress tracking with localStorage"
    ((TOTAL_PASSED++))
else
    echo -e "${RED}✗${NC} Progress tracking not implemented"
    ((TOTAL_FAILED++))
fi

echo ""

# ============================================
# ESSENTIAL TEST 5: Lesson content exists
# ============================================

echo "5. Lesson Content"
echo "-------------------------------------------"

lesson_count=$(grep -o '"id":\s*"lesson-' lessons/lessons.js | wc -l)
if [ "$lesson_count" -ge 3 ]; then
    echo -e "${GREEN}✓${NC} At least 3 lessons present ($lesson_count found)"
    ((TOTAL_PASSED++))
else
    echo -e "${RED}✗${NC} Insufficient lesson content (need 3+, found: $lesson_count)"
    ((TOTAL_FAILED++))
fi

echo ""

# ============================================
# ESSENTIAL TEST 6: No build dependencies
# ============================================

echo "6. Zero Dependencies Check"
echo "-------------------------------------------"

if [ ! -f "package.json" ] && [ ! -f "webpack.config.js" ]; then
    echo -e "${GREEN}✓${NC} No build dependencies (vanilla HTML/CSS/JS)"
    ((TOTAL_PASSED++))
else
    echo -e "${RED}✗${NC} Found build dependencies (should be zero)"
    ((TOTAL_FAILED++))
fi

echo ""

# ============================================
# RUN COMPONENT TEST SUITES (detailed)
# ============================================

echo "=========================================="
echo "RUNNING COMPONENT TEST SUITES"
echo "=========================================="
echo ""

COMPONENT_FAILED=0

# HTML Validation Suite
echo "Running HTML validation suite..."
./tests/html_validation.sh
if [ $? -ne 0 ]; then ((COMPONENT_FAILED++)); fi
echo ""

# Navigation Suite
echo "Running navigation suite..."
./tests/navigation.sh
if [ $? -ne 0 ]; then ((COMPONENT_FAILED++)); fi
echo ""

# Quiz Suite
echo "Running quiz suite..."
./tests/quiz.sh
if [ $? -ne 0 ]; then ((COMPONENT_FAILED++)); fi
echo ""

# Progress Tracking Suite
echo "Running progress tracking suite..."
./tests/progress.sh
if [ $? -ne 0 ]; then ((COMPONENT_FAILED++)); fi
echo ""

# ============================================
# FINAL SUMMARY
# ============================================

echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""
echo "Essential Tests: $TOTAL_PASSED passed, $TOTAL_FAILED failed"
echo "Component Suites: $((4 - COMPONENT_FAILED)) passed, $COMPONENT_FAILED failed"
echo ""

if [ $TOTAL_FAILED -eq 0 ] && [ $COMPONENT_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Ready to run:"
    echo "  python3 -m http.server 8001"
    echo "  Visit: http://localhost:8001"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
