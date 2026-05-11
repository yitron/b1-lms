import os
import tempfile


class TestCodeRunner:
    """Test code runner service for C, Python, and TypeScript"""

    def test_run_c_code_success(self):
        """Test running simple C code successfully"""
        from lms.code_runner import CodeRunner

        c_code = '''
#include <stdio.h>

int main() {
    printf("Hello from C\\n");
    return 0;
}
'''
        runner = CodeRunner()
        result = runner.run_c_code(c_code)

        assert result['success'] is True
        assert result['output'] == 'Hello from C\n'
        assert result['error'] is None

    def test_run_c_code_compilation_error(self):
        """Test C code with compilation error"""
        from lms.code_runner import CodeRunner

        c_code = '''
#include <stdio.h>

int main() {
    printf("Missing semicolon")
    return 0;
}
'''
        runner = CodeRunner()
        result = runner.run_c_code(c_code)

        assert result['success'] is False
        assert result['output'] == ''
        assert result['error'] is not None
        assert 'error' in result['error'].lower()

    def test_run_python_code_success(self):
        """Test running simple Python code successfully"""
        from lms.code_runner import CodeRunner

        python_code = '''
print("Hello from Python")
'''
        runner = CodeRunner()
        result = runner.run_python_code(python_code)

        assert result['success'] is True
        assert result['output'] == 'Hello from Python\n'
        assert result['error'] is None

    def test_run_python_code_runtime_error(self):
        """Test Python code with runtime error"""
        from lms.code_runner import CodeRunner

        python_code = '''
print(undefined_variable)
'''
        runner = CodeRunner()
        result = runner.run_python_code(python_code)

        assert result['success'] is False
        assert result['output'] == ''
        assert result['error'] is not None
        assert 'NameError' in result['error']

    def test_run_typescript_code_success(self):
        """Test running simple TypeScript code successfully"""
        from lms.code_runner import CodeRunner

        typescript_code = '''
console.log("Hello from TypeScript");
'''
        runner = CodeRunner()
        result = runner.run_typescript_code(typescript_code)

        assert result['success'] is True
        assert result['output'] == 'Hello from TypeScript\n'
        assert result['error'] is None

    def test_run_typescript_code_compilation_error(self):
        """Test TypeScript code with compilation error"""
        from lms.code_runner import CodeRunner

        typescript_code = '''
let x: number = "not a number";
console.log(x);
'''
        runner = CodeRunner()
        result = runner.run_typescript_code(typescript_code)

        assert result['success'] is False
        assert result['error'] is not None

    def test_run_code_timeout(self):
        """Test code execution timeout"""
        from lms.code_runner import CodeRunner

        # Infinite loop
        python_code = '''
while True:
    pass
'''
        runner = CodeRunner(timeout=1)  # 1 second timeout
        result = runner.run_python_code(python_code)

        assert result['success'] is False
        assert result['error'] is not None
        assert 'timeout' in result['error'].lower()

    def test_run_code_captures_multiline_output(self):
        """Test capturing multiple lines of output"""
        from lms.code_runner import CodeRunner

        python_code = '''
print("Line 1")
print("Line 2")
print("Line 3")
'''
        runner = CodeRunner()
        result = runner.run_python_code(python_code)

        assert result['success'] is True
        assert 'Line 1' in result['output']
        assert 'Line 2' in result['output']
        assert 'Line 3' in result['output']

    def test_run_code_with_arguments(self):
        """Test running code that uses command-line arguments"""
        from lms.code_runner import CodeRunner

        # Python code that echoes arguments
        python_code = '''
import sys
for arg in sys.argv[1:]:
    print(arg)
'''
        runner = CodeRunner()
        result = runner.run_python_code(python_code, args=['arg1', 'arg2'])

        assert result['success'] is True
        assert 'arg1' in result['output']
        assert 'arg2' in result['output']

    def test_cleanup_temp_files(self):
        """Test that temporary files are cleaned up"""
        from lms.code_runner import CodeRunner

        c_code = '''
#include <stdio.h>

int main() {
    printf("Test\\n");
    return 0;
}
'''
        runner = CodeRunner()

        # Count temp files before
        temp_dir = tempfile.gettempdir()
        files_before = len([f for f in os.listdir(temp_dir) if f.startswith('code_runner_')])

        # Run code
        runner.run_c_code(c_code)

        # Count temp files after (should be same or less)
        files_after = len([f for f in os.listdir(temp_dir) if f.startswith('code_runner_')])

        assert files_after <= files_before
