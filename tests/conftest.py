"""
Pytest configuration and fixtures for the FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """
    Fixture that provides a sample email for testing.
    """
    return "newstudent@mergington.edu"


@pytest.fixture
def existing_activity():
    """
    Fixture that provides an existing activity name for testing.
    """
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """
    Fixture that provides a nonexistent activity name for testing.
    """
    return "Nonexistent Club"
