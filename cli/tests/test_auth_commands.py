"""
Tests for authentication commands

TDD Cycle 10: Auth Commands
RED Phase - Write failing tests first
"""
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from lms_cli.cli import cli


class TestSignupCommand:
    """Test 'lms signup' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_signup_success(self, mock_config_class, mock_api_class, runner):
        """Should successfully signup and save token"""
        # Mock API client
        mock_api = Mock()
        mock_api.post.return_value = {
            'token': 'test-token-123',
            'user': {'username': 'testuser', 'email': 'test@example.com'}
        }
        mock_api_class.return_value = mock_api

        # Mock config
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        # Run command
        result = runner.invoke(cli, ['signup'], input='testuser\ntestpass123\ntest@example.com\n')

        # Assertions
        assert result.exit_code == 0
        assert 'successfully' in result.output.lower() or 'created' in result.output.lower()

        # Verify API was called
        mock_api.post.assert_called_once_with('auth/signup/', {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        })

        # Verify token was saved
        mock_config.save_token.assert_called_once_with('test-token-123')

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_signup_without_email(self, mock_config_class, mock_api_class, runner):
        """Should allow signup without email (optional)"""
        mock_api = Mock()
        mock_api.post.return_value = {
            'token': 'test-token-456',
            'user': {'username': 'testuser2'}
        }
        mock_api_class.return_value = mock_api

        mock_config = Mock()
        mock_config_class.return_value = mock_config

        # Run command with empty email
        result = runner.invoke(cli, ['signup'], input='testuser2\ntestpass123\n\n')

        assert result.exit_code == 0
        mock_api.post.assert_called_once()

        # Email should be empty string
        call_args = mock_api.post.call_args[0][1]
        assert call_args['email'] == ''

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_signup_api_error(self, mock_config_class, mock_api_class, runner):
        """Should handle API errors gracefully"""
        mock_api = Mock()
        mock_api.post.side_effect = Exception("400: Username already exists")
        mock_api_class.return_value = mock_api

        mock_config = Mock()
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['signup'], input='existing\npass123\n\n')

        assert result.exit_code != 0
        assert 'error' in result.output.lower() or 'failed' in result.output.lower()

        # Token should not be saved
        mock_config.save_token.assert_not_called()


class TestLoginCommand:
    """Test 'lms login' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_login_success(self, mock_config_class, mock_api_class, runner):
        """Should successfully login and save token"""
        mock_api = Mock()
        mock_api.post.return_value = {
            'token': 'login-token-789',
            'user': {'username': 'testuser'}
        }
        mock_api_class.return_value = mock_api

        mock_config = Mock()
        mock_config.has_token.return_value = False  # Not logged in yet
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['login'], input='testuser\ntestpass123\n')

        assert result.exit_code == 0
        assert 'success' in result.output.lower() or 'logged in' in result.output.lower()

        # Verify API was called
        mock_api.post.assert_called_once_with('auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        # Verify token was saved
        mock_config.save_token.assert_called_once_with('login-token-789')

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_login_with_flags(self, mock_config_class, mock_api_class, runner):
        """Should accept username/password as flags"""
        mock_api = Mock()
        mock_api.post.return_value = {
            'token': 'flag-token-123',
            'user': {'username': 'flaguser'}
        }
        mock_api_class.return_value = mock_api

        mock_config = Mock()
        mock_config.has_token.return_value = False  # Not logged in yet
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['login', '--username', 'flaguser', '--password', 'flagpass'])

        assert result.exit_code == 0
        mock_api.post.assert_called_once_with('auth/login/', {
            'username': 'flaguser',
            'password': 'flagpass'
        })

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_login_invalid_credentials(self, mock_config_class, mock_api_class, runner):
        """Should handle invalid credentials"""
        mock_api = Mock()
        mock_api.post.side_effect = Exception("400: Invalid credentials")
        mock_api_class.return_value = mock_api

        mock_config = Mock()
        mock_config.has_token.return_value = False  # Not logged in yet
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['login'], input='wronguser\nwrongpass\n')

        assert result.exit_code != 0
        assert 'error' in result.output.lower() or 'failed' in result.output.lower()
        mock_config.save_token.assert_not_called()

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_login_already_logged_in(self, mock_config_class, mock_api_class, runner):
        """Should warn if already logged in"""
        mock_api = Mock()
        mock_api_class.return_value = mock_api

        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'existing-token'
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['login'], input='testuser\ntestpass\n')

        # Should show warning but still allow login
        assert 'already' in result.output.lower() or 'logged in' in result.output.lower()


class TestLogoutCommand:
    """Test 'lms logout' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_logout_success(self, mock_config_class, mock_api_class, runner):
        """Should successfully logout and delete token"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.return_value = {'message': 'Successfully logged out'}
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['logout'])

        assert result.exit_code == 0
        assert 'success' in result.output.lower() or 'logged out' in result.output.lower()

        # Verify API was called with token
        mock_api_class.assert_called_once_with(token='test-token')
        mock_api.post.assert_called_once_with('auth/logout/', {})

        # Verify token was deleted
        mock_config.delete_token.assert_called_once()

    @patch('lms_cli.commands.auth.Config')
    def test_logout_when_not_logged_in(self, mock_config_class, runner):
        """Should handle logout when not logged in"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['logout'])

        assert result.exit_code != 0
        assert 'not logged in' in result.output.lower()
        mock_config.delete_token.assert_not_called()

    @patch('lms_cli.commands.auth.APIClient')
    @patch('lms_cli.commands.auth.Config')
    def test_logout_api_error_still_deletes_token(self, mock_config_class, mock_api_class, runner):
        """Should delete local token even if API call fails"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'test-token'
        mock_config_class.return_value = mock_config

        mock_api = Mock()
        mock_api.post.side_effect = Exception("Network error")
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ['logout'])

        # Should still delete local token even if API fails
        mock_config.delete_token.assert_called_once()
        assert 'logged out' in result.output.lower() or 'token removed' in result.output.lower()


class TestWhoamiCommand:
    """Test 'lms whoami' command"""

    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @patch('lms_cli.commands.auth.Config')
    def test_whoami_when_logged_in(self, mock_config_class, runner):
        """Should show token info when logged in"""
        mock_config = Mock()
        mock_config.has_token.return_value = True
        mock_config.load_token.return_value = 'abc123def456'
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['whoami'])

        assert result.exit_code == 0
        assert 'logged in' in result.output.lower()
        # Should show partial token (for security)
        assert 'abc123' in result.output or 'token' in result.output.lower()

    @patch('lms_cli.commands.auth.Config')
    def test_whoami_when_not_logged_in(self, mock_config_class, runner):
        """Should show not logged in message"""
        mock_config = Mock()
        mock_config.has_token.return_value = False
        mock_config_class.return_value = mock_config

        result = runner.invoke(cli, ['whoami'])

        assert result.exit_code == 0
        assert 'not logged in' in result.output.lower()
