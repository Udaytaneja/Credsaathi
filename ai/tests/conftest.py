"""Pytest fixtures for CredSaathi AI Layer tests."""
import pytest
from fastapi.testclient import TestClient
from ai.main import app


@pytest.fixture
def client():
    """Provides a TestClient for FastAPI endpoints with default authenticated API key header."""
    with TestClient(app, headers={"X-API-Key": "credsaathi_secret_api_key_v1"}) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    """Provides valid authentication headers for API tests."""
    return {"X-API-Key": "credsaathi_secret_api_key_v1"}
