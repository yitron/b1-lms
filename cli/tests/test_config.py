"""
Tests for configuration management

TDD Cycle 9: Config tests
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from lms_cli.config import Config


class TestConfigInit:
    """Test configuration initialization"""

    def test_init_default_directory(self):
        """Should use ~/.lms/ as default config directory"""
        config = Config()
        assert config.config_dir == Path.home() / '.lms'
        assert config.token_file == Path.home() / '.lms' / 'token'

    def test_init_custom_directory(self):
        """Should allow custom config directory"""
        custom_dir = Path('/tmp/test-lms-config')
        config = Config(config_dir=custom_dir)
        assert config.config_dir == custom_dir
        assert config.token_file == custom_dir / 'token'

    def test_init_creates_directory(self):
        """Should create config directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / 'lms-config'
            assert not config_dir.exists()

            config = Config(config_dir=config_dir)
            assert config_dir.exists()
            assert config_dir.is_dir()


class TestConfigTokenManagement:
    """Test token save/load/delete operations"""

    @pytest.fixture
    def config(self):
        """Create config with temporary directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(config_dir=Path(tmpdir) / 'config')
            yield config
            # Cleanup happens automatically with TemporaryDirectory

    def test_save_token(self, config):
        """Should save token to file"""
        token = "test-token-123"
        config.save_token(token)

        assert config.token_file.exists()
        assert config.token_file.read_text() == token

    def test_save_token_creates_file_with_restricted_permissions(self, config):
        """Should create token file with 600 permissions (owner read/write only)"""
        config.save_token("test-token")

        # Check file permissions (600 = owner read/write only)
        import os
        import stat
        mode = os.stat(config.token_file).st_mode
        assert stat.S_IMODE(mode) == 0o600

    def test_load_token_success(self, config):
        """Should load token from file"""
        token = "test-token-456"
        config.save_token(token)

        loaded_token = config.load_token()
        assert loaded_token == token

    def test_load_token_when_not_exists(self, config):
        """Should return None when token file doesn't exist"""
        loaded_token = config.load_token()
        assert loaded_token is None

    def test_load_token_strips_whitespace(self, config):
        """Should strip whitespace from loaded token"""
        config.token_file.write_text("  test-token-789  \n")

        loaded_token = config.load_token()
        assert loaded_token == "test-token-789"

    def test_delete_token(self, config):
        """Should delete token file"""
        config.save_token("test-token")
        assert config.token_file.exists()

        config.delete_token()
        assert not config.token_file.exists()

    def test_delete_token_when_not_exists(self, config):
        """Should not error when deleting non-existent token"""
        assert not config.token_file.exists()

        # Should not raise exception
        config.delete_token()

    def test_has_token_true(self, config):
        """Should return True when token exists"""
        config.save_token("test-token")
        assert config.has_token() is True

    def test_has_token_false_when_not_exists(self, config):
        """Should return False when token doesn't exist"""
        assert config.has_token() is False

    def test_has_token_false_when_empty(self, config):
        """Should return False when token file is empty"""
        config.token_file.write_text("")
        assert config.has_token() is False
