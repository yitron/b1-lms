"""
Code Runner Service - Compiles and executes C, Python, and TypeScript code safely
"""
import os
import shutil
import subprocess
import tempfile


class CodeRunner:
    """Service to compile and execute code in multiple languages"""

    def __init__(self, timeout=5):
        """
        Initialize CodeRunner

        Args:
            timeout (int): Maximum execution time in seconds (default 5)
        """
        self.timeout = timeout

    def run_c_code(self, code, args=None):
        """
        Compile and run C code

        Args:
            code (str): C source code
            args (list): Optional command-line arguments

        Returns:
            dict: {'success': bool, 'output': str, 'error': str|None}
        """
        if args is None:
            args = []

        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='code_runner_c_')

            # Write source file
            source_file = os.path.join(temp_dir, 'program.c')
            with open(source_file, 'w') as f:
                f.write(code)

            # Compile
            executable = os.path.join(temp_dir, 'program')
            compile_result = subprocess.run(
                ['gcc', '-o', executable, source_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'output': '',
                    'error': compile_result.stderr
                }

            # Execute
            run_result = subprocess.run(
                [executable] + args,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return {
                'success': run_result.returncode == 0,
                'output': run_result.stdout,
                'error': run_result.stderr if run_result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Execution timeout exceeded'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def run_python_code(self, code, args=None):
        """
        Run Python code

        Args:
            code (str): Python source code
            args (list): Optional command-line arguments

        Returns:
            dict: {'success': bool, 'output': str, 'error': str|None}
        """
        if args is None:
            args = []

        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='code_runner_python_')

            # Write source file
            source_file = os.path.join(temp_dir, 'program.py')
            with open(source_file, 'w') as f:
                f.write(code)

            # Execute
            run_result = subprocess.run(
                ['python3', source_file] + args,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return {
                'success': run_result.returncode == 0,
                'output': run_result.stdout,
                'error': run_result.stderr if run_result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Execution timeout exceeded'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def run_typescript_code(self, code, args=None):
        """
        Compile and run TypeScript code

        Args:
            code (str): TypeScript source code
            args (list): Optional command-line arguments

        Returns:
            dict: {'success': bool, 'output': str, 'error': str|None}
        """
        if args is None:
            args = []

        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix='code_runner_ts_')

            # Write source file
            source_file = os.path.join(temp_dir, 'program.ts')
            with open(source_file, 'w') as f:
                f.write(code)

            # Compile
            compile_result = subprocess.run(
                ['tsc', '--outDir', temp_dir, source_file],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'output': '',
                    'error': compile_result.stderr
                }

            # Execute compiled JavaScript
            js_file = os.path.join(temp_dir, 'program.js')
            run_result = subprocess.run(
                ['node', js_file] + args,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return {
                'success': run_result.returncode == 0,
                'output': run_result.stdout,
                'error': run_result.stderr if run_result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Execution timeout exceeded'
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
