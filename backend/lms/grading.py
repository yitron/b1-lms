"""
Exam Grading System - Test cases and grading logic for picoshell
"""
from .code_runner import CodeRunner

# Picoshell test cases
PICOSHELL_TEST_CASES = [
    {
        'name': 'test_simple_echo',
        'args': ['echo', 'hello'],
        'expected_output': 'hello\n'
    },
    {
        'name': 'test_single_pipe',
        'args': ['echo', 'hello', '|', 'cat'],
        'expected_output': 'hello\n'
    },
    {
        'name': 'test_multiple_pipes',
        'args': ['echo', 'hello world', '|', 'cat', '|', 'cat'],
        'expected_output': 'hello world\n'
    },
    {
        'name': 'test_ls_grep',
        'args': ['ls', '|', 'grep', 'test'],
        'expected_output': ''  # Will vary by environment, we'll update this
    },
    {
        'name': 'test_echo_sed',
        'args': ['echo', 'squalala.', '|', 'sed', 's/a/b/g'],
        'expected_output': 'squblblb.\n'
    },
]


def get_exam_test_cases(exam_id):
    """
    Get test cases for an exam

    Args:
        exam_id (str): Exam identifier (e.g., 'picoshell')

    Returns:
        list: List of test case dicts
    """
    if exam_id == 'picoshell':
        return PICOSHELL_TEST_CASES
    return []


class ExamGrader:
    """Grades exam submissions by running test cases and comparing outputs"""

    def __init__(self, exam_id, timeout=5):
        """
        Initialize ExamGrader

        Args:
            exam_id (str): Exam identifier
            timeout (int): Timeout for code execution (default 5 seconds)
        """
        self.exam_id = exam_id
        self.timeout = timeout
        self.code_runner = CodeRunner(timeout=timeout)

    def get_test_cases(self):
        """Get test cases for this exam"""
        return get_exam_test_cases(self.exam_id)

    def grade_submission(self, code, language):
        """
        Grade a code submission

        Args:
            code (str): User's code
            language (str): 'c', 'python', or 'typescript'

        Returns:
            dict: {
                'grade': 'pass'|'fail',
                'tests_passed': int,
                'tests_total': int,
                'tests': [
                    {
                        'name': str,
                        'passed': bool,
                        'expected': str,
                        'actual': str,
                        'diff': str|None
                    }
                ],
                'compilation_error': str|None (if applicable)
            }
        """
        test_cases = self.get_test_cases()
        results = []

        # Try to compile/run first test to check for compilation errors
        if language == 'c':
            run_result = self.code_runner.run_c_code(code)
        elif language == 'python':
            run_result = self.code_runner.run_python_code(code)
        elif language == 'typescript':
            run_result = self.code_runner.run_typescript_code(code)
        else:
            return {
                'grade': 'fail',
                'tests_passed': 0,
                'tests_total': len(test_cases),
                'tests': [],
                'error': f'Unsupported language: {language}'
            }

        # If compilation/initial run failed, return early
        if not run_result['success'] and run_result['error']:
            return {
                'grade': 'fail',
                'tests_passed': 0,
                'tests_total': len(test_cases),
                'tests': [],
                'compilation_error': run_result['error']
            }

        # Run all test cases
        for test_case in test_cases:
            test_result = self.run_test_case(code, language, test_case)
            results.append(test_result)

        # Calculate grade
        tests_passed = sum(1 for r in results if r['passed'])
        tests_total = len(results)
        grade = 'pass' if tests_passed == tests_total else 'fail'

        return {
            'grade': grade,
            'tests_passed': tests_passed,
            'tests_total': tests_total,
            'tests': results
        }

    def run_test_case(self, code, language, test_case):
        """
        Run a single test case

        Args:
            code (str): User's code
            language (str): Programming language
            test_case (dict): Test case with 'name', 'args', 'expected_output'

        Returns:
            dict: Test result with 'name', 'passed', 'expected', 'actual', 'diff'
        """
        args = test_case['args']
        expected = test_case['expected_output']

        # Execute code with test case args
        if language == 'c':
            result = self.code_runner.run_c_code(code, args=args)
        elif language == 'python':
            result = self.code_runner.run_python_code(code, args=args)
        elif language == 'typescript':
            result = self.code_runner.run_typescript_code(code, args=args)

        # Get actual output
        if result['success']:
            actual = result['output']
        else:
            actual = ''

        # Compare outputs
        diff_result = self.diff_outputs(actual, expected)

        return {
            'name': test_case['name'],
            'passed': diff_result['passed'],
            'expected': expected,
            'actual': actual,
            'diff': diff_result['diff']
        }

    def diff_outputs(self, actual, expected):
        """
        Compare actual vs expected output (exact string match)

        Args:
            actual (str): Actual output
            expected (str): Expected output

        Returns:
            dict: {'passed': bool, 'diff': str|None}
        """
        if actual == expected:
            return {
                'passed': True,
                'diff': None
            }
        else:
            # Generate simple diff description
            diff_lines = []

            if len(actual) != len(expected):
                diff_lines.append(f"Length mismatch: actual={len(actual)}, expected={len(expected)}")

            if actual.rstrip() == expected.rstrip():
                diff_lines.append("Trailing whitespace difference")
            elif actual.replace('\n', '') == expected.replace('\n', ''):
                diff_lines.append("Newline difference")
            else:
                diff_lines.append(f"Expected: {repr(expected)}")
                diff_lines.append(f"Actual: {repr(actual)}")

            return {
                'passed': False,
                'diff': '\n'.join(diff_lines)
            }
