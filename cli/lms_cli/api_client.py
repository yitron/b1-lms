"""
API Client for B1 LMS Backend

Handles all HTTP requests to the Django REST API
"""
import requests
from typing import Dict, Any, Optional


class APIClientError(Exception):
    """Custom exception for API client errors"""
    pass


class APIClient:
    """Client for communicating with B1 LMS API"""

    def __init__(self, base_url: str = "http://localhost:8000/api/", token: Optional[str] = None):
        """
        Initialize API client

        Args:
            base_url: Base URL for the API (default: http://localhost:8000/api/)
            token: Authentication token (optional)
        """
        # Ensure base_url ends with /
        if not base_url.endswith('/'):
            base_url += '/'

        self.base_url = base_url
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers including auth token if present

        Returns:
            dict: Headers dictionary
        """
        headers = {}
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        return headers

    def get(self, endpoint: str) -> Dict[str, Any]:
        """
        Make GET request to API

        Args:
            endpoint: API endpoint (e.g., "lessons/", "progress/")

        Returns:
            dict: JSON response from API

        Raises:
            APIClientError: If request fails (non-200 status code)
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                # Try to get error message from response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = response.text or 'Unknown error'

                raise Exception(f"GET request failed with status {response.status_code}: {error_msg}")

            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIClientError(f"Network error: {str(e)}")

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make POST request to API

        Args:
            endpoint: API endpoint (e.g., "auth/login/")
            data: Data to send in request body (dict)

        Returns:
            dict: JSON response from API

        Raises:
            APIClientError: If request fails (non-200/201 status code)
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.post(url, json=data, headers=headers)

            if response.status_code not in [200, 201]:
                # Try to get error message from response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Unknown error')
                except:
                    error_msg = response.text or 'Unknown error'

                raise Exception(f"POST request failed with status {response.status_code}: {error_msg}")

            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIClientError(f"Network error: {str(e)}")

    def set_token(self, token: str) -> None:
        """
        Set authentication token

        Args:
            token: Authentication token string
        """
        self.token = token

    def clear_token(self) -> None:
        """Clear authentication token"""
        self.token = None
