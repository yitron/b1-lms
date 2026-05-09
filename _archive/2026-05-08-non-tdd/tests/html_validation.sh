#!/bin/bash

# ============================================
# HTML VALIDATION TESTS - B1 LMS
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

echo "HTML Validation Tests"
echo "-------------------------------------------"

# RED: Test for HTML5 doctype
# GREEN: Added <!DOCTYPE html>
# REFACTOR: Ensured proper structure

if grep -q "<!DOCTYPE html>" index.html; then
    pass "HTML5 doctype present"
else
    fail "Missing HTML5 doctype"
fi

# RED: Test for semantic structure
# GREEN: Used aside for sidebar, main for content
# REFACTOR: Added proper ARIA landmarks

if grep -q '<aside' index.html; then
    pass "Semantic <aside> for sidebar present"
else
    fail "Missing semantic <aside>"
fi

if grep -q '<main' index.html; then
    pass "Semantic <main> for content present"
else
    fail "Missing semantic <main>"
fi

# RED: Test for skip-to-content link
# GREEN: Added accessibility skip link
# REFACTOR: Positioned correctly at top

if grep -q 'skip-link\|Skip to' index.html; then
    pass "Skip-to-content link present (accessibility)"
else
    fail "Missing skip-to-content link"
fi

# RED: Test for progress bar
# GREEN: Added progress bar with ARIA attributes
# REFACTOR: Used role="progressbar"

if grep -q 'role="progressbar"' index.html; then
    pass "Progress bar with ARIA role present"
else
    fail "Missing progress bar ARIA role"
fi

# RED: Test for lesson list container
# GREEN: Added dynamic lesson list element
# REFACTOR: Used proper ID for JavaScript binding

if grep -q 'id="lessonList"' index.html; then
    pass "Lesson list container present"
else
    fail "Missing lesson list container"
fi

# RED: Test for content area
# GREEN: Added main content area for dynamic rendering
# REFACTOR: Used proper semantic structure

if grep -q 'id="lessonContent"' index.html || grep -q 'lesson-content' index.html; then
    pass "Lesson content area present"
else
    fail "Missing lesson content area"
fi

echo ""
echo "HTML Validation: $PASSED passed, $FAILED failed"
exit $FAILED
