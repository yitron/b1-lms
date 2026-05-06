#!/bin/bash

# ============================================
# PROGRESS TRACKING TESTS - B1 LMS
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

echo "Progress Tracking Tests"
echo "-------------------------------------------"

# RED: Test for loadProgress function
# GREEN: Implemented localStorage loading
# REFACTOR: Added error handling for missing data

if grep -q 'function loadProgress\|loadProgress.*=' script.js; then
    pass "loadProgress function exists"
else
    fail "Missing loadProgress function"
fi

# RED: Test for saveProgress function
# GREEN: Implemented localStorage saving
# REFACTOR: Saved both completedLessons and quizScores

if grep -q 'function saveProgress\|saveProgress.*=' script.js; then
    pass "saveProgress function exists"
else
    fail "Missing saveProgress function"
fi

# RED: Test for markLessonComplete function
# GREEN: Created function to mark lessons complete
# REFACTOR: Updated progress bar on completion

if grep -q 'function markLessonComplete\|markLessonComplete.*=' script.js; then
    pass "markLessonComplete function exists"
else
    fail "Missing markLessonComplete function"
fi

# RED: Test for progress bar update
# GREEN: Implemented updateProgressBar function
# REFACTOR: Calculated percentage based on completed lessons

if grep -q 'function updateProgressBar\|updateProgressBar.*=' script.js; then
    pass "updateProgressBar function exists"
else
    fail "Missing updateProgressBar function"
fi

# RED: Test for localStorage usage
# GREEN: Used localStorage.getItem/setItem
# REFACTOR: Added try-catch for error handling

if grep -q 'localStorage' script.js; then
    pass "localStorage implementation present"
else
    fail "localStorage not implemented"
fi

# RED: Test for completion check
# GREEN: Created checkAllComplete function
# REFACTOR: Shows completion screen when all done

if grep -q 'function checkAllComplete\|checkAllComplete.*=\|allComplete' script.js; then
    pass "Completion check function exists"
else
    fail "Missing completion check"
fi

echo ""
echo "Progress: $PASSED passed, $FAILED failed"
exit $FAILED
