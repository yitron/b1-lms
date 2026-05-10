"""
Tests for progress commands

TDD Cycle 12: Progress Commands
RED Phase - Write failing tests first
"""
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from lms_cli.cli import cli


class TestProgressCommand:
    """Test 'lms progress' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_progress_shows_completed_lessons(self, mock_api_class, mock_config_class, runner):
        """Should show user's completed lessons"""
        # Mock config - user is logged in
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        # Mock API client
        mock_api = Mock()

        # First call: get lessons
        # Second call: get progress
        mock_api.get.side_effect = [
            {
                'lessons': [
                    {'lesson_id': 'module-00', 'title': 'LLM API Communication', 'module_number': 0},
                    {'lesson_id': 'module-01', 'title': 'Tool Use', 'module_number': 1},
                    {'lesson_id': 'module-02', 'title': 'Memory', 'module_number': 2}
                ]
            },
            {
                'progress': [
                    {'lesson_id': 'module-00', 'completed': True, 'completed_at': '2026-05-10T10:00:00Z'},
                    {'lesson_id': 'module-01', 'completed': True, 'completed_at': '2026-05-10T11:00:00Z'}
                ]
            }
        ]
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['progress'])

        assert result.exit_code == 0
        # Should show completion status
        assert 'module-00' in result.output or 'Module 00' in result.output or '✓' in result.output
        assert 'complete' in result.output.lower() or '2/3' in result.output

    @patch('lms_cli.commands.progress.Config')
    def test_progress_requires_login(self, mock_config_class, runner):
        """Should require user to be logged in"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['progress'])

        assert result.exit_code != 0
        assert 'not logged in' in result.output.lower() or 'login' in result.output.lower()

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_progress_shows_zero_when_no_progress(self, mock_api_class, mock_config_class, runner):
        """Should show 0/N when user hasn't completed any lessons"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.side_effect = [
            {'lessons': [{'lesson_id': 'module-00', 'title': 'Test', 'module_number': 0}]},
            {'progress': []}  # No completed lessons
        ]
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['progress'])

        assert result.exit_code == 0
        assert '0' in result.output or 'no lessons' in result.output.lower() or 'not completed' in result.output.lower()

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_progress_shows_percentage(self, mock_api_class, mock_config_class, runner):
        """Should show completion percentage"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.side_effect = [
            {
                'lessons': [
                    {'lesson_id': 'module-00', 'title': 'Test1', 'module_number': 0},
                    {'lesson_id': 'module-01', 'title': 'Test2', 'module_number': 1}
                ]
            },
            {
                'progress': [
                    {'lesson_id': 'module-00', 'completed': True, 'completed_at': '2026-05-10T10:00:00Z'}
                ]
            }
        ]
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['progress'])

        assert result.exit_code == 0
        # Should show 50% or 1/2
        assert '50' in result.output or '1/2' in result.output

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_progress_api_error(self, mock_api_class, mock_config_class, runner):
        """Should handle API errors gracefully"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.side_effect = Exception("Network error")
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['progress'])

        assert result.exit_code != 0
        assert 'error' in result.output.lower() or 'failed' in result.output.lower()


class TestCompleteCommand:
    """Test 'lms complete <lesson-id>' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_complete_marks_lesson_complete(self, mock_api_class, mock_config_class, runner):
        """Should mark a lesson as complete"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'message': 'Lesson marked as complete',
            'progress': {
                'lesson_id': 'module-00',
                'completed': True,
                'completed_at': '2026-05-10T10:00:00Z'
            }
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['complete', 'module-00'])

        assert result.exit_code == 0
        assert 'success' in result.output.lower() or 'complete' in result.output.lower()

        # Verify API was called
        mock_api.post.assert_called_once_with('progress/complete/', {'lesson_id': 'module-00'})

    @patch('lms_cli.commands.progress.Config')
    def test_complete_requires_login(self, mock_config_class, runner):
        """Should require user to be logged in"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['complete', 'module-00'])

        assert result.exit_code != 0
        assert 'not logged in' in result.output.lower() or 'login' in result.output.lower()

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_complete_lesson_not_found(self, mock_api_class, mock_config_class, runner):
        """Should handle lesson not found error"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.side_effect = Exception("404: Lesson not found")
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['complete', 'invalid-lesson'])

        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_complete_requires_lesson_id(self, mock_api_class, mock_config_class, runner):
        """Should require lesson_id argument"""
        result = runner.invoke(cli, ['complete'])

        assert result.exit_code != 0
        assert 'missing' in result.output.lower() or 'required' in result.output.lower()

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_complete_idempotent(self, mock_api_class, mock_config_class, runner):
        """Should handle already completed lessons (idempotent)"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'message': 'Lesson marked as complete',
            'progress': {
                'lesson_id': 'module-00',
                'completed': True,
                'completed_at': '2026-05-10T10:00:00Z'
            }
        }
        mock_api_class.return_value = mock_api

        # Mark complete twice
        result1 = runner.invoke(cli, ['complete', 'module-00'])
        result2 = runner.invoke(cli, ['complete', 'module-00'])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        # Both should succeed (idempotent operation)

    @patch('lms_cli.commands.progress.Config')
    @patch('lms_cli.commands.progress.APIClient')
    def test_complete_shows_congratulations(self, mock_api_class, mock_config_class, runner):
        """Should show positive feedback when marking complete"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {
            'message': 'Lesson marked as complete',
            'progress': {
                'lesson_id': 'module-00',
                'completed': True
            }
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['complete', 'module-00'])

        assert result.exit_code == 0
        # Should show positive feedback
        assert '✓' in result.output or 'success' in result.output.lower() or 'complete' in result.output.lower()
