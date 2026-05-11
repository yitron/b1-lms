"""
Tests for exam commands

TDD Cycle 8: Exam CLI Commands
RED Phase - Write failing tests first
"""
from unittest.mock import Mock, mock_open, patch

import pytest
from click.testing import CliRunner

from lms_cli.cli import cli


class TestExamsListCommand:
    """Test 'lms exams' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exams_list_success(self, mock_api_class, mock_config_class, runner):
        """Should list all available exams"""
        # Mock config - user logged in
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        # Mock API response
        mock_api = Mock()
        mock_api.get.return_value = {
            'exams': [
                {
                    'exam_id': 'picoshell',
                    'title': 'Picoshell Implementation',
                    'time_limit_minutes': 60
                }
            ]
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exams'])

        assert result.exit_code == 0
        assert 'picoshell' in result.output
        assert 'Picoshell Implementation' in result.output
        mock_api.get.assert_called_once_with('exams/')

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exams_list_unauthenticated(self, mock_api_class, mock_config_class, runner):
        """Should require authentication"""
        # Mock config - no token
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['exams'])

        assert result.exit_code != 0
        assert 'login' in result.output.lower() or 'not logged in' in result.output.lower()

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exams_list_empty(self, mock_api_class, mock_config_class, runner):
        """Should handle empty exam list"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.return_value = {'exams': []}
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exams'])

        assert result.exit_code == 0
        assert 'no exams' in result.output.lower() or 'empty' in result.output.lower()


class TestExamStartCommand:
    """Test 'lms exam start <exam_id>' command"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exam_start_success(self, mock_api_class, mock_config_class, runner):
        """Should start exam session successfully"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'session_id': 123,
            'exam_id': 'picoshell',
            'started_at': '2026-05-11T12:00:00Z',
            'expires_at': '2026-05-11T13:00:00Z',
            'time_limit_minutes': 60,
            'instructions': 'Implement picoshell...'
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'start', 'picoshell'])

        assert result.exit_code == 0
        assert 'started' in result.output.lower() or 'session' in result.output.lower()
        assert '60' in result.output  # Time limit
        mock_api.post.assert_called_once_with('exams/start/', {'exam_id': 'picoshell'})

    @patch('lms_cli.commands.exam.Config')
    def test_exam_start_unauthenticated(self, mock_config_class, runner):
        """Should require authentication"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['exam', 'start', 'picoshell'])

        assert result.exit_code != 0
        assert 'login' in result.output.lower() or 'not logged in' in result.output.lower()

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exam_start_already_active(self, mock_api_class, mock_config_class, runner):
        """Should handle active session exists error"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.side_effect = Exception("Active session already exists")
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'start', 'picoshell'])

        assert result.exit_code != 0
        assert 'active' in result.output.lower() or 'already' in result.output.lower()


class TestExamStatusCommand:
    """Test 'lms exam status <exam_id>' command"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exam_status_success(self, mock_api_class, mock_config_class, runner):
        """Should show exam status with time remaining and attempts"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.return_value = {
            'session_id': 123,
            'exam_id': 'picoshell',
            'time_remaining_minutes': 45,
            'expired': False,
            'completed': False,
            'submissions': {
                'c': {'attempts': 2, 'latest_grade': 'pass'},
                'python': {'attempts': 1, 'latest_grade': 'fail'},
                'typescript': {'attempts': 0, 'latest_grade': None}
            }
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'status', 'picoshell'])

        assert result.exit_code == 0
        assert '45' in result.output  # Time remaining
        assert 'c' in result.output.lower() or 'C' in result.output
        assert 'python' in result.output.lower()
        assert 'typescript' in result.output.lower()
        assert 'pass' in result.output.lower()
        mock_api.get.assert_called_once_with('exams/status/picoshell/')

    @patch('lms_cli.commands.exam.Config')
    def test_exam_status_unauthenticated(self, mock_config_class, runner):
        """Should require authentication"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['exam', 'status', 'picoshell'])

        assert result.exit_code != 0

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exam_status_no_session(self, mock_api_class, mock_config_class, runner):
        """Should handle no active session"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.side_effect = Exception("No active session found")
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'status', 'picoshell'])

        assert result.exit_code != 0
        assert 'no' in result.output.lower() and 'session' in result.output.lower()


class TestExamSubmitCommand:
    """Test 'lms exam submit <exam_id> --lang <language>' command"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch('lms_cli.commands.exam.os.path.expanduser')
    @patch('lms_cli.commands.exam.os.path.exists')
    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    @patch('builtins.open', new_callable=mock_open, read_data='int main() { return 0; }')
    def test_exam_submit_success(self, mock_file, mock_api_class, mock_config_class, mock_exists, mock_expanduser, runner):
        """Should submit code successfully from ~/exam/picoshell.c"""
        # Mock home directory expansion
        mock_expanduser.return_value = '/home/testuser/exam'
        mock_exists.return_value = True  # File exists

        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'submission_id': 456,
            'session_id': 123,
            'language': 'c',
            'grade': 'pass',
            'test_results': {
                'grade': 'pass',
                'tests_passed': 5,
                'tests_total': 5
            }
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'submit', 'picoshell', '--lang', 'c'])

        assert result.exit_code == 0
        assert 'pass' in result.output.lower()
        assert '5/5' in result.output or '5' in result.output
        mock_api.post.assert_called_once()

        # Verify correct file path was checked
        mock_expanduser.assert_called_with('~/exam')
        mock_exists.assert_called_with('/home/testuser/exam/picoshell.c')

    @patch('lms_cli.commands.exam.Config')
    def test_exam_submit_unauthenticated(self, mock_config_class, runner):
        """Should require authentication"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['exam', 'submit', 'picoshell', '--lang', 'c'])

        assert result.exit_code != 0

    @patch('lms_cli.commands.exam.os.path.expanduser')
    @patch('lms_cli.commands.exam.os.path.exists')
    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    @patch('builtins.open', new_callable=mock_open, read_data='int main() { return 0; }')
    def test_exam_submit_failure(self, mock_file, mock_api_class, mock_config_class, mock_exists, mock_expanduser, runner):
        """Should show test failures"""
        mock_expanduser.return_value = '/home/testuser/exam'
        mock_exists.return_value = True

        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'submission_id': 456,
            'session_id': 123,
            'language': 'c',
            'grade': 'fail',
            'test_results': {
                'grade': 'fail',
                'tests_passed': 2,
                'tests_total': 5
            }
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'submit', 'picoshell', '--lang', 'c'])

        assert result.exit_code == 0  # Command runs successfully even if tests fail
        assert 'fail' in result.output.lower()
        assert '2' in result.output and '5' in result.output

    @patch('lms_cli.commands.exam.os.path.expanduser')
    @patch('lms_cli.commands.exam.os.path.exists')
    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exam_submit_file_not_found(self, mock_api_class, mock_config_class, mock_exists, mock_expanduser, runner):
        """Should handle file not found in ~/exam/ directory"""
        mock_expanduser.return_value = '/home/testuser/exam'
        mock_exists.return_value = False  # File does not exist

        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['exam', 'submit', 'picoshell', '--lang', 'c'])

        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'does not exist' in result.output.lower()
        assert 'picoshell.c' in result.output

    @patch('lms_cli.commands.exam.os.path.expanduser')
    @patch('lms_cli.commands.exam.os.path.exists')
    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    @patch('builtins.open', new_callable=mock_open, read_data='print("hello")')
    def test_exam_submit_python_file(self, mock_file, mock_api_class, mock_config_class, mock_exists, mock_expanduser, runner):
        """Should look for picoshell.py when language is python"""
        mock_expanduser.return_value = '/home/testuser/exam'
        mock_exists.return_value = True

        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'submission_id': 457,
            'session_id': 123,
            'language': 'python',
            'grade': 'pass',
            'test_results': {
                'grade': 'pass',
                'tests_passed': 5,
                'tests_total': 5
            }
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'submit', 'picoshell', '--lang', 'python'])

        assert result.exit_code == 0
        mock_exists.assert_called_with('/home/testuser/exam/picoshell.py')

    @patch('lms_cli.commands.exam.os.path.expanduser')
    @patch('lms_cli.commands.exam.os.path.exists')
    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    @patch('builtins.open', new_callable=mock_open, read_data='console.log("hello")')
    def test_exam_submit_typescript_file(self, mock_file, mock_api_class, mock_config_class, mock_exists, mock_expanduser, runner):
        """Should look for picoshell.ts when language is typescript"""
        mock_expanduser.return_value = '/home/testuser/exam'
        mock_exists.return_value = True

        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'submission_id': 458,
            'session_id': 123,
            'language': 'typescript',
            'grade': 'pass',
            'test_results': {
                'grade': 'pass',
                'tests_passed': 5,
                'tests_total': 5
            }
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'submit', 'picoshell', '--lang', 'typescript'])

        assert result.exit_code == 0
        mock_exists.assert_called_with('/home/testuser/exam/picoshell.ts')


class TestExamResultsCommand:
    """Test 'lms exam results <exam_id>' command"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exam_results_success(self, mock_api_class, mock_config_class, runner):
        """Should show detailed results"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.return_value = {
            'session_id': 123,
            'exam_id': 'picoshell',
            'submissions': [
                {
                    'submission_id': 456,
                    'language': 'c',
                    'grade': 'pass',
                    'test_results': {
                        'grade': 'pass',
                        'tests_passed': 5,
                        'tests_total': 5,
                        'tests': [
                            {'name': 'test1', 'passed': True},
                            {'name': 'test2', 'passed': True}
                        ]
                    },
                    'submitted_at': '2026-05-11T12:30:00Z'
                }
            ]
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'results', 'picoshell'])

        assert result.exit_code == 0
        assert 'c' in result.output.lower() or 'C' in result.output
        assert 'pass' in result.output.lower()
        assert '5/5' in result.output or '5' in result.output
        mock_api.get.assert_called_once_with('exams/results/picoshell/')

    @patch('lms_cli.commands.exam.Config')
    def test_exam_results_unauthenticated(self, mock_config_class, runner):
        """Should require authentication"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['exam', 'results', 'picoshell'])

        assert result.exit_code != 0

    @patch('lms_cli.commands.exam.Config')
    @patch('lms_cli.commands.exam.APIClient')
    def test_exam_results_empty(self, mock_api_class, mock_config_class, runner):
        """Should handle no submissions"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.return_value = {
            'session_id': 123,
            'exam_id': 'picoshell',
            'submissions': []
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['exam', 'results', 'picoshell'])

        assert result.exit_code == 0
        assert 'no submissions' in result.output.lower() or 'empty' in result.output.lower()
