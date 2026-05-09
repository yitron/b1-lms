#!/bin/bash

# ============================================
# QUIZ FUNCTIONALITY TESTS - B1 LMS
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

echo "Quiz Functionality Tests"
echo "-------------------------------------------"

# RED: Test for renderQuiz function
# GREEN: Implemented quiz rendering
# REFACTOR: Added visual feedback for answers

if grep -q 'function renderQuiz\|renderQuiz.*=' script.js; then
    pass "renderQuiz function exists"
else
    fail "Missing renderQuiz function"
fi

# RED: Test for answer checking
# GREEN: Created checkAnswer function
# REFACTOR: Added instant feedback (correct/incorrect)

if grep -q 'function checkAnswer\|checkAnswer.*=' script.js; then
    pass "checkAnswer function exists"
else
    fail "Missing checkAnswer function"
fi

# RED: Test for quiz score tracking
# GREEN: Added quizScores to state
# REFACTOR: Persisted scores to localStorage

if grep -q 'quizScores' script.js; then
    pass "Quiz score tracking implemented"
else
    fail "Missing quiz score tracking"
fi

# RED: Test for quiz data structure
# GREEN: Created quiz array in lessons.js
# REFACTOR: Structured with questions, options, correct answer

if [ -f "lessons/lessons.js" ]; then
    if grep -q 'quiz' lessons/lessons.js; then
        pass "Quiz data structure exists in lessons.js"
    else
        fail "Missing quiz data in lessons.js"
    fi
else
    fail "lessons/lessons.js not found"
fi

echo ""
echo "Quiz: $PASSED passed, $FAILED failed"
exit $FAILED
