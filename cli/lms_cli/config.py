"""
Configuration management for B1 LMS CLI

Handles storing and retrieving authentication tokens
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Manages CLI configuration including token storage"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration

        Args:
            config_dir: Directory for storing config (default: ~/.lms/)
        """
        if config_dir is None:
            config_dir = Path.home() / '.lms'

        self.config_dir = config_dir
        self.token_file = self.config_dir / 'token'

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_token(self, token: str) -> None:
        """
        Save authentication token to disk

        Args:
            token: Authentication token string
        """
        self.token_file.write_text(token)
        # Set file permissions to 600 (owner read/write only)
        os.chmod(self.token_file, 0o600)

    def load_token(self) -> Optional[str]:
        """
        Load authentication token from disk

        Returns:
            str: Token if exists, None otherwise
        """
        if not self.token_file.exists():
            return None

        token = self.token_file.read_text().strip()
        return token if token else None

    def delete_token(self) -> None:
        """Delete saved authentication token"""
        if self.token_file.exists():
            self.token_file.unlink()

    def has_token(self) -> bool:
        """
        Check if token exists

        Returns:
            bool: True if token file exists and is not empty
        """
        return self.token_file.exists() and bool(self.load_token())
