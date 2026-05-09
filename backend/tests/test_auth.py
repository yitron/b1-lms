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


@pytest.mark.django_db
class TestAuthLogin:
    """Tests for user login endpoint"""

    def test_login_with_valid_credentials_returns_token(self):
        """
        RED: Test POST /api/auth/login/ with valid credentials
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create user first
        User.objects.create_user(username='testuser', password='testpass123')

        # Try to login
        response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        assert response.status_code == 200, "Should return 200 OK"
        assert 'token' in response.data, "Should return authentication token"
        assert 'user' in response.data, "Should return user data"

    def test_login_with_invalid_password_fails(self):
        """
        RED: Test login with wrong password returns 400
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create user
        User.objects.create_user(username='testuser', password='testpass123')

        # Try to login with wrong password
        response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        assert response.status_code == 400, "Should return 400 Bad Request"

    def test_login_with_nonexistent_user_fails(self):
        """
        RED: Test login with non-existent user returns 400
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        response = client.post('/api/auth/login/', {
            'username': 'nonexistent',
            'password': 'testpass123'
        })

        assert response.status_code == 400, "Should return 400 Bad Request"

    def test_login_without_username_fails(self):
        """
        RED: Test login without username returns 400
        Should FAIL - validation not implemented yet
        """
        client = APIClient()

        response = client.post('/api/auth/login/', {
            'password': 'testpass123'
        })

        assert response.status_code == 400, "Should return 400 Bad Request"

    def test_login_without_password_fails(self):
        """
        RED: Test login without password returns 400
        Should FAIL - validation not implemented yet
        """
        client = APIClient()

        response = client.post('/api/auth/login/', {
            'username': 'testuser'
        })

        assert response.status_code == 400, "Should return 400 Bad Request"

    def test_login_returns_same_token_for_same_user(self):
        """
        RED: Test that login returns existing token
        Should FAIL - token reuse not implemented yet
        """
        client = APIClient()

        # Create user and get token via signup
        user = User.objects.create_user(username='testuser', password='testpass123')
        token1 = Token.objects.create(user=user)

        # Login should return same token
        response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        assert response.data['token'] == token1.key, "Should return existing token"


@pytest.mark.django_db
class TestAuthLogout:
    """Tests for user logout endpoint"""

    def test_logout_deletes_token(self):
        """
        RED: Test POST /api/auth/logout/ deletes token
        Should FAIL - endpoint doesn't exist yet
        """
        client = APIClient()

        # Create user and token
        user = User.objects.create_user(username='testuser', password='testpass123')
        token = Token.objects.create(user=user)

        # Logout
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = client.post('/api/auth/logout/')

        assert response.status_code == 200, "Should return 200 OK"

        # Verify token was deleted
        assert not Token.objects.filter(key=token.key).exists(), "Token should be deleted"

    def test_logout_without_token_fails(self):
        """
        RED: Test logout without authentication returns 401
        Should FAIL - authentication check not implemented yet
        """
        client = APIClient()

        response = client.post('/api/auth/logout/')

        assert response.status_code == 401, "Should return 401 Unauthorized"

    def test_logout_with_invalid_token_fails(self):
        """
        RED: Test logout with invalid token returns 401
        Should FAIL - validation not implemented yet
        """
        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = client.post('/api/auth/logout/')

        assert response.status_code == 401, "Should return 401 Unauthorized"
