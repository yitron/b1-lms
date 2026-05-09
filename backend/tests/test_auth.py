"""
TDD Cycle 4: Authentication API Tests
Test signup, login, and logout endpoints
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


@pytest.mark.django_db
class TestAuthSignup:
    """Tests for user signup endpoint"""

    def test_signup_creates_user_and_returns_token(self):
        """
        RED: Test POST /api/auth/signup/ creates user and returns token
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        response = client.post('/api/auth/signup/', {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        })

        assert response.status_code == 201, "Should return 201 Created"
        assert 'token' in response.data, "Should return authentication token"
        assert 'user' in response.data, "Should return user data"
        assert response.data['user']['username'] == 'testuser', "Username should match"

        # Verify user was created
        user = User.objects.get(username='testuser')
        assert user is not None, "User should be created in database"
        assert user.email == 'test@example.com', "Email should match"

    def test_signup_without_username_fails(self):
        """
        RED: Test signup without username returns 400
        Should FAIL - validation not implemented yet
        """
        client = APIClient()

        response = client.post('/api/auth/signup/', {
            'password': 'testpass123'
        })

        assert response.status_code == 400, "Should return 400 Bad Request"

    def test_signup_without_password_fails(self):
        """
        RED: Test signup without password returns 400
        Should FAIL - validation not implemented yet
        """
        client = APIClient()

        response = client.post('/api/auth/signup/', {
            'username': 'testuser'
        })

        assert response.status_code == 400, "Should return 400 Bad Request"

    def test_signup_with_duplicate_username_fails(self):
        """
        RED: Test signup with existing username returns 400
        Should FAIL - duplicate check not implemented yet
        """
        client = APIClient()

        # Create first user
        User.objects.create_user(username='testuser', password='pass123')

        # Try to create duplicate
        response = client.post('/api/auth/signup/', {
            'username': 'testuser',
            'password': 'newpass123'
        })

        assert response.status_code == 400, "Should return 400 Bad Request for duplicate username"

    def test_signup_email_is_optional(self):
        """
        RED: Test signup works without email
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        response = client.post('/api/auth/signup/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        assert response.status_code == 201, "Should return 201 Created even without email"
        assert 'token' in response.data, "Should return token"

    def test_signup_token_is_valid(self):
        """
        RED: Test that returned token can be used for authentication
        Should FAIL - token generation not implemented yet
        """
        client = APIClient()

        response = client.post('/api/auth/signup/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        token = response.data['token']

        # Try to use the token
        client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        # Verify token is associated with user
        token_obj = Token.objects.get(key=token)
        assert token_obj.user.username == 'testuser', "Token should be associated with correct user"
