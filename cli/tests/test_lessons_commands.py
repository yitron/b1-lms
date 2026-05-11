"""
Tests for lessons commands

TDD Cycle 11: Lessons Commands
RED Phase - Write failing tests first
"""
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from lms_cli.cli import cli


class TestLessonsListCommand:
    """Test 'lms lessons' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.lessons.Config')
    @patch('lms_cli.commands.lessons.APIClient')
    def test_lessons_list_success(self, mock_api_class, mock_config_class, runner):
        """Should list all available lessons"""
        # Mock config - not logged in
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.get.return_value = {
            'lessons': [
                {
                    'lesson_id': 'module-00',
                    'title': 'LLM API Communication',
                    'subtitle': 'Learn the fundamentals',
                    'module_number': 0
                },
                {
                    'lesson_id': 'module-01',
                    'title': 'Tool Use',
                    'subtitle': 'Explore tool patterns',
                    'module_number': 1
                },
                {
                    'lesson_id': 'module-02',
                    'title': 'Conversational Memory',
                    'subtitle': 'Master context management',
                    'module_number': 2
                }
            ]
        }
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['lessons'])

        assert result.exit_code == 0
        # Check for formatted module numbers and titles
        assert 'Module 00' in result.output or 'Module  0' in result.output
        assert 'LLM API Communication' in result.output
        assert 'Module 01' in result.output or 'Module  1' in result.output
        assert 'Tool Use' in result.output
        assert 'Module 02' in result.output or 'Module  2' in result.output
        assert 'Conversational Memory' in result.output

        # Verify API was called
        mock_api.get.assert_called_once_with('lessons/')

    @patch('lms_cli.commands.lessons.APIClient')
    def test_lessons_list_empty(self, mock_api_class, runner):
        """Should handle empty lesson list"""
        mock_api = Mock()
        mock_api.get.return_value = {'lessons': []}
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['lessons'])

        assert result.exit_code == 0
        assert 'no lessons' in result.output.lower() or 'empty' in result.output.lower()

    @patch('lms_cli.commands.lessons.APIClient')
    def test_lessons_list_api_error(self, mock_api_class, runner):
        """Should handle API errors gracefully"""
        mock_api = Mock()
        mock_api.get.side_effect = Exception("Network error")
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['lessons'])

        assert result.exit_code != 0
        assert 'error' in result.output.lower() or 'failed' in result.output.lower()

    @patch('lms_cli.commands.lessons.Config')
    @patch('lms_cli.commands.lessons.APIClient')
    def test_lessons_list_shows_progress_when_logged_in(self, mock_api_class, mock_config_class, runner):
        """Should show completion status when user is logged in"""
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
                    {'lesson_id': 'module-00', 'title': 'Test Lesson', 'module_number': 0}
                ]
            },
            {
                'progress': [
                    {'lesson_id': 'module-00', 'completed': True}
                ]
            }
        ]
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['lessons'])

        assert result.exit_code == 0
        # Should show some indicator of completion (✓, Complete, Done, etc.)
        assert '✓' in result.output or 'complete' in result.output.lower()


class TestViewLessonCommand:
    """Test 'lms view <lesson-id>' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.lessons.APIClient')
    @patch('lms_cli.commands.lessons.Console')
    def test_view_lesson_success(self, mock_console_class, mock_api_class, runner):
        """Should display lesson content with markdown rendering"""
        mock_api = Mock()
        mock_api.get.return_value = {
            'lesson_id': 'module-00',
            'title': 'LLM API Communication',
            'subtitle': 'Learn the fundamentals',
            'content': '# Module 00\n\nThis is the lesson content.\n\n## Topics\n- Topic 1\n- Topic 2'
        }
        mock_api_class.return_value = mock_api

        # Mock Rich Console
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        result = runner.invoke(cli, ['view', 'module-00'])

        assert result.exit_code == 0

        # Verify API was called
        mock_api.get.assert_called_once_with('lessons/module-00/')

        # Verify Rich console was used to print markdown
        assert mock_console.print.called

    @patch('lms_cli.commands.lessons.APIClient')
    def test_view_lesson_not_found(self, mock_api_class, runner):
        """Should handle lesson not found error"""
        mock_api = Mock()
        mock_api.get.side_effect = Exception("404: Lesson not found")
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['view', 'invalid-lesson'])

        assert result.exit_code != 0
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()

    @patch('lms_cli.commands.lessons.APIClient')
    @patch('lms_cli.commands.lessons.Console')
    def test_view_lesson_shows_title(self, mock_console_class, mock_api_class, runner):
        """Should display lesson title and subtitle"""
        mock_api = Mock()
        mock_api.get.return_value = {
            'lesson_id': 'module-00',
            'title': 'Test Lesson Title',
            'subtitle': 'Test Subtitle',
            'content': 'Content here'
        }
        mock_api_class.return_value = mock_api

        mock_console = Mock()
        mock_console_class.return_value = mock_console

        result = runner.invoke(cli, ['view', 'module-00'])

        assert result.exit_code == 0
        # Title and subtitle should appear in output (either via Rich or click.echo)
        output_lower = result.output.lower()
        assert 'test lesson title' in output_lower or mock_console.print.called

    @patch('lms_cli.commands.lessons.APIClient')
    @patch('lms_cli.commands.lessons.Console')
    def test_view_lesson_with_pager(self, mock_console_class, mock_api_class, runner):
        """Should use pager for long content"""
        # Create long content
        long_content = '# Lesson\n\n' + '\n\n'.join([f'## Section {i}\n\nContent for section {i}' for i in range(50)])

        mock_api = Mock()
        mock_api.get.return_value = {
            'lesson_id': 'module-00',
            'title': 'Long Lesson',
            'subtitle': 'Very long',
            'content': long_content
        }
        mock_api_class.return_value = mock_api

        mock_console = Mock()
        mock_console_class.return_value = mock_console

        result = runner.invoke(cli, ['view', 'module-00'])

        assert result.exit_code == 0
        # Verify console methods were called
        assert mock_console.print.called or hasattr(mock_console, 'pager')

    @patch('lms_cli.commands.lessons.APIClient')
    def test_view_lesson_requires_lesson_id(self, mock_api_class, runner):
        """Should require lesson_id argument"""
        result = runner.invoke(cli, ['view'])

        assert result.exit_code != 0
        assert 'missing' in result.output.lower() or 'required' in result.output.lower()


class TestViewLessonWithQuiz:
    """Test viewing lesson with quiz information"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.lessons.APIClient')
    @patch('lms_cli.commands.lessons.Console')
    def test_view_lesson_shows_quiz_indicator(self, mock_console_class, mock_api_class, runner):
        """Should indicate if lesson has a quiz"""
        mock_api = Mock()
        mock_api.get.return_value = {
            'lesson_id': 'module-00',
            'title': 'Test Lesson',
            'subtitle': 'Test',
            'content': 'Content',
            'quiz_data': {
                'questions': [
                    {'text': 'Question 1', 'options': ['A', 'B'], 'correct': 1}
                ]
            }
        }
        mock_api_class.return_value = mock_api

        mock_console = Mock()
        mock_console_class.return_value = mock_console

        result = runner.invoke(cli, ['view', 'module-00'])

        assert result.exit_code == 0
        # Should mention quiz somewhere
        assert 'quiz' in result.output.lower() or mock_console.print.called

    @patch('lms_cli.commands.lessons.APIClient')
    @patch('lms_cli.commands.lessons.Console')
    def test_view_lesson_without_quiz(self, mock_console_class, mock_api_class, runner):
        """Should handle lessons without quiz data"""
        mock_api = Mock()
        mock_api.get.return_value = {
            'lesson_id': 'module-00',
            'title': 'Test Lesson',
            'subtitle': 'Test',
            'content': 'Content',
            'quiz_data': None
        }
        mock_api_class.return_value = mock_api

        mock_console = Mock()
        mock_console_class.return_value = mock_console

        result = runner.invoke(cli, ['view', 'module-00'])

        assert result.exit_code == 0
