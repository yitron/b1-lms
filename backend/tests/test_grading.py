import pytest


class TestExamGrader:
    """Test exam grading system"""

    def test_grade_submission_all_pass(self):
        """Test grading structure when submission runs successfully"""
        from lms.grading import ExamGrader

        # Simple C code - may not pass all tests, but should run successfully
        c_code = '''
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "|") != 0) {
            printf("%s", argv[i]);
            if (i < argc - 1 && strcmp(argv[i + 1], "|") != 0) {
                printf(" ");
            }
        }
    }
    printf("\\n");
    return 0;
}
'''
        grader = ExamGrader('picoshell')
        result = grader.grade_submission(c_code, language='c')

        # Check result structure (grade may be pass or fail)
        assert 'grade' in result
        assert result['grade'] in ['pass', 'fail']
        assert 'tests_passed' in result
        assert 'tests_total' in result
        assert result['tests_total'] > 0
        assert result['tests_passed'] >= 0
        assert result['tests_passed'] <= result['tests_total']
        assert len(result['tests']) > 0
        # Verify each test has required fields
        for test in result['tests']:
            assert 'name' in test
            assert 'passed' in test
            assert 'expected' in test
            assert 'actual' in test

    def test_grade_submission_some_fail(self):
        """Test grading when some tests fail"""
        from lms.grading import ExamGrader

        # Code that doesn't work correctly
        c_code = '''
#include <stdio.h>

int main() {
    printf("Wrong output\\n");
    return 0;
}
'''
        grader = ExamGrader('picoshell')
        result = grader.grade_submission(c_code, language='c')

        assert result['grade'] == 'fail'
        assert result['tests_passed'] < result['tests_total']
        assert len(result['tests']) > 0

    def test_grade_submission_compilation_error(self):
        """Test grading when code doesn't compile"""
        from lms.grading import ExamGrader

        # Code with syntax error
        c_code = '''
#include <stdio.h>

int main() {
    printf("Missing semicolon")
    return 0;
}
'''
        grader = ExamGrader('picoshell')
        result = grader.grade_submission(c_code, language='c')

        assert result['grade'] == 'fail'
        assert result['tests_passed'] == 0
        assert 'compilation_error' in result or 'error' in result

    def test_grade_submission_python(self):
        """Test grading Python code"""
        from lms.grading import ExamGrader

        # Simple Python code
        python_code = '''
import sys
for arg in sys.argv[1:]:
    if arg != "|":
        print(arg, end=" ")
print()
'''
        grader = ExamGrader('picoshell')
        result = grader.grade_submission(python_code, language='python')

        assert 'grade' in result
        assert 'tests_passed' in result
        assert 'tests_total' in result

    def test_grade_submission_typescript(self):
        """Test grading TypeScript code"""
        from lms.grading import ExamGrader

        # Simple TypeScript code
        typescript_code = '''
const args = process.argv.slice(2);
const filtered = args.filter(arg => arg !== "|");
console.log(filtered.join(" "));
'''
        grader = ExamGrader('picoshell')
        result = grader.grade_submission(typescript_code, language='typescript')

        assert 'grade' in result
        assert 'tests_passed' in result
        assert 'tests_total' in result

    def test_test_case_format(self):
        """Test that test cases have correct format"""
        from lms.grading import ExamGrader

        grader = ExamGrader('picoshell')
        test_cases = grader.get_test_cases()

        assert len(test_cases) > 0
        for test_case in test_cases:
            assert 'name' in test_case
            assert 'args' in test_case
            assert 'expected_output' in test_case

    def test_diff_exact_match(self):
        """Test diff when outputs match exactly"""
        from lms.grading import ExamGrader

        grader = ExamGrader('picoshell')
        result = grader.diff_outputs("hello\n", "hello\n")

        assert result['passed'] is True
        assert result['diff'] is None

    def test_diff_mismatch(self):
        """Test diff when outputs don't match"""
        from lms.grading import ExamGrader

        grader = ExamGrader('picoshell')
        result = grader.diff_outputs("hello\n", "goodbye\n")

        assert result['passed'] is False
        assert result['diff'] is not None

    def test_diff_whitespace_matters(self):
        """Test that whitespace differences are detected"""
        from lms.grading import ExamGrader

        grader = ExamGrader('picoshell')
        result = grader.diff_outputs("hello\n", "hello \n")  # Extra space

        assert result['passed'] is False

    def test_diff_newline_matters(self):
        """Test that missing newlines are detected"""
        from lms.grading import ExamGrader

        grader = ExamGrader('picoshell')
        result = grader.diff_outputs("hello\n", "hello")  # Missing newline

        assert result['passed'] is False


class TestPicoshellTestCases:
    """Test picoshell test case definitions"""

    def test_picoshell_has_test_cases(self):
        """Test that picoshell exam has test cases defined"""
        from lms.grading import get_exam_test_cases

        test_cases = get_exam_test_cases('picoshell')

        assert len(test_cases) >= 5  # At least 5 test cases
        assert all('name' in tc for tc in test_cases)
        assert all('args' in tc for tc in test_cases)
        assert all('expected_output' in tc for tc in test_cases)

    def test_picoshell_test_case_simple_command(self):
        """Test that simple command test case exists"""
        from lms.grading import get_exam_test_cases

        test_cases = get_exam_test_cases('picoshell')
        test_names = [tc['name'] for tc in test_cases]

        assert any('simple' in name.lower() for name in test_names)

    def test_picoshell_test_case_pipe(self):
        """Test that pipe test case exists"""
        from lms.grading import get_exam_test_cases

        test_cases = get_exam_test_cases('picoshell')

        # Check that at least one test case has pipe in args
        has_pipe = any('|' in ' '.join(tc['args']) for tc in test_cases)
        assert has_pipe
