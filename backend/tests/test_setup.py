"""
TDD Cycle 1: Django Project Setup Tests
Test that Django project exists and is configured correctly
"""
import pytest
from django.conf import settings


def test_django_settings_exist():
    """
    RED: Test that Django settings are configured
    Should FAIL - no Django project exists yet
    """
    assert settings.configured, "Django settings should be configured"


def test_installed_apps_include_rest_framework():
    """
    RED: Test that DRF is in INSTALLED_APPS
    Should FAIL - DRF not configured yet
    """
    assert 'rest_framework' in settings.INSTALLED_APPS, "DRF should be installed"


def test_installed_apps_include_corsheaders():
    """
    RED: Test that CORS headers is in INSTALLED_APPS
    Should FAIL - CORS not configured yet
    """
    assert 'corsheaders' in settings.INSTALLED_APPS, "CORS headers should be installed"


def test_lms_app_in_installed_apps():
    """
    RED: Test that our LMS app is in INSTALLED_APPS
    Should FAIL - LMS app doesn't exist yet
    """
    assert 'lms' in settings.INSTALLED_APPS, "LMS app should be in INSTALLED_APPS"
