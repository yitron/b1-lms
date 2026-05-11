"""
Tests for API client

TDD Cycle 9: CLI Setup & API Client
RED Phase - Write failing tests first
"""
from unittest.mock import Mock, patch

import pytest

from lms_cli.api_client import APIClient


class TestAPIClientInit:
    """Test API client initialization"""

    def test_init_with_default_url(self):
        """Should initialize with default base URL"""
        client = APIClient()
        assert client.base_url == "http://localhost:8000/api/"

    def test_init_with_custom_url(self):
        """Should initialize with custom base URL"""
        client = APIClient(base_url="http://example.com/api/")
        assert client.base_url == "http://example.com/api/"

    def test_init_adds_trailing_slash(self):
        """Should add trailing slash to base URL if missing"""
        client = APIClient(base_url="http://example.com/api")
        assert client.base_url == "http://example.com/api/"

    def test_init_without_token(self):
        """Should initialize without token"""
        client = APIClient()
        assert client.token is None


class TestAPIClientGetRequest:
    """Test API client GET requests"""

    @patch('lms_cli.api_client.requests.get')
    def test_get_lessons_success(self, mock_get):
        """Should successfully GET lessons"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lessons": [
                {"lesson_id": "module-00", "title": "Test Lesson"}
            ]
        }
        mock_get.return_value = mock_response

        # Make request
        client = APIClient()
        response = client.get("lessons/")

        # Assertions
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/lessons/",
            headers={}
        )
        assert response == {"lessons": [{"lesson_id": "module-00", "title": "Test Lesson"}]}

    @patch('lms_cli.api_client.requests.get')
    def test_get_with_token(self, mock_get):
        """Should include Authorization header when token is set"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"progress": []}
        mock_get.return_value = mock_response

        # Make request with token
        client = APIClient(token="test-token-123")
        response = client.get("progress/")

        # Assertions
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/progress/",
            headers={"Authorization": "Token test-token-123"}
        )
        assert response == {"progress": []}

    @patch('lms_cli.api_client.requests.get')
    def test_get_404_error(self, mock_get):
        """Should raise exception on 404"""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_get.return_value = mock_response

        # Should raise exception
        client = APIClient()
        with pytest.raises(Exception) as exc_info:
            client.get("lessons/invalid/")

        assert "404" in str(exc_info.value)


class TestAPIClientPostRequest:
    """Test API client POST requests"""

    @patch('lms_cli.api_client.requests.post')
    def test_post_login_success(self, mock_post):
        """Should successfully POST login"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "token": "abc123",
            "user": {"username": "testuser"}
        }
        mock_post.return_value = mock_response

        # Make request
        client = APIClient()
        response = client.post("auth/login/", {
            "username": "testuser",
            "password": "testpass"
        })

        # Assertions
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/auth/login/",
            json={"username": "testuser", "password": "testpass"},
            headers={}
        )
        assert response == {"token": "abc123", "user": {"username": "testuser"}}

    @patch('lms_cli.api_client.requests.post')
    def test_post_with_token(self, mock_post):
        """Should include Authorization header when token is set"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Logged out"}
        mock_post.return_value = mock_response

        # Make request with token
        client = APIClient(token="test-token-123")
        client.post("auth/logout/", {})

        # Assertions
        mock_post.assert_called_once_with(
            "http://localhost:8000/api/auth/logout/",
            json={},
            headers={"Authorization": "Token test-token-123"}
        )

    @patch('lms_cli.api_client.requests.post')
    def test_post_400_error(self, mock_post):
        """Should raise exception on 400 error"""
        # Mock 400 response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid data"}
        mock_post.return_value = mock_response

        # Should raise exception
        client = APIClient()
        with pytest.raises(Exception) as exc_info:
            client.post("auth/login/", {"username": "test"})

        assert "400" in str(exc_info.value)


class TestAPIClientTokenManagement:
    """Test token management"""

    def test_set_token(self):
        """Should be able to set token"""
        client = APIClient()
        assert client.token is None

        client.set_token("new-token-123")
        assert client.token == "new-token-123"

    def test_clear_token(self):
        """Should be able to clear token"""
        client = APIClient(token="test-token")
        assert client.token == "test-token"

        client.clear_token()
        assert client.token is None

    @patch('lms_cli.api_client.requests.get')
    def test_token_updates_headers(self, mock_get):
        """Should update headers when token is set"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        client = APIClient()

        # First request without token
        client.get("test/")
        mock_get.assert_called_with(
            "http://localhost:8000/api/test/",
            headers={}
        )

        # Set token
        client.set_token("new-token")

        # Second request with token
        client.get("test/")
        mock_get.assert_called_with(
            "http://localhost:8000/api/test/",
            headers={"Authorization": "Token new-token"}
        )
