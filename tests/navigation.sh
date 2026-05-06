#!/bin/bash

# ============================================
# NAVIGATION TESTS - B1 LMS
# TDD: RED-GREEN-REFACTOR
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

echo "Navigation Tests"
echo "-------------------------------------------"

# RED: Test for navigateToLesson function
# GREEN: Implemented SPA navigation function
# REFACTOR: Added error handling for invalid lesson IDs

if grep -q 'function navigateToLesson\|navigateToLesson.*=' script.js; then
    pass "navigateToLesson function exists"
else
    fail "Missing navigateToLesson function"
fi

# RED: Test for lesson list rendering
# GREEN: Created renderLessonList function
# REFACTOR: Added completion checkmarks

if grep -q 'function renderLessonList\|renderLessonList.*=' script.js; then
    pass "renderLessonList function exists"
else
    fail "Missing renderLessonList function"
fi

# RED: Test for hash routing
# GREEN: Added window.location.hash handling
# REFACTOR: Enabled direct links to lessons

if grep -q 'window.location.hash\|location.hash' script.js; then
    pass "Hash routing implemented"
else
    fail "Missing hash routing"
fi

# RED: Test for DOMContentLoaded
# GREEN: Wrapped initialization in DOMContentLoaded
# REFACTOR: Ensured DOM ready before execution

if grep -q 'DOMContentLoaded' script.js; then
    pass "DOMContentLoaded event handler present"
else
    fail "Missing DOMContentLoaded handler"
fi

# RED: Test for state management
# GREEN: Created global state object
# REFACTOR: Centralized lesson state

if grep -q 'const state\|let state\|var state' script.js; then
    pass "State management object exists"
else
    fail "Missing state management"
fi

echo ""
echo "Navigation: $PASSED passed, $FAILED failed"
exit $FAILED
