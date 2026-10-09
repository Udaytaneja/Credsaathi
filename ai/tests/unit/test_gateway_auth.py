from unittest.mock import MagicMock, patch
from fastapi import Request, status
import pytest

from ai.configs.settings import AISettings, settings
from ai.gateway.auth import verify_api_key
from ai.gateway.errors import AIServiceException


def test_verify_api_key_valid_header():
    request = MagicMock(spec=Request)
    request.state = MagicMock()
    request.state.user_id = "test_user_123"

    user_id = verify_api_key(request, x_api_key="credsaathi_secret_api_key_v1")
    assert user_id == "test_user_123"


def test_verify_api_key_valid_bearer_token():
    request = Request(scope={"type": "http"})

    user_id = verify_api_key(request, authorization="Bearer credsaathi_test_api_key")
    assert user_id == "authenticated_user"


def test_verify_api_key_missing_header():
    request = Request(scope={"type": "http"})

    with pytest.raises(AIServiceException) as exc_info:
        verify_api_key(request, x_api_key=None, authorization=None)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.code == "UNAUTHORIZED"
    assert "Missing X-API-Key" in exc_info.value.message


def test_verify_api_key_invalid_credentials():
    request = Request(scope={"type": "http"})

    with pytest.raises(AIServiceException) as exc_info:
        verify_api_key(request, x_api_key="invalid_attacker_key")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid authentication key" in exc_info.value.message


def test_verify_api_key_empty_configured_keys():
    request = Request(scope={"type": "http"})

    with patch.object(settings, "API_KEYS", ""):
        with pytest.raises(AIServiceException) as exc_info:
            verify_api_key(request, x_api_key="some_key")

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "No service credentials configured" in exc_info.value.message


def test_cors_origins_configuration():
    # Production environment with empty CORS_ORIGINS -> empty list
    prod_settings = AISettings(ENVIRONMENT="production", CORS_ORIGINS="")
    assert prod_settings.cors_origins_list == []

    # Configured CORS_ORIGINS -> parsed list
    custom_settings = AISettings(CORS_ORIGINS="https://app.credsaathi.in, https://admin.credsaathi.in")
    assert custom_settings.cors_origins_list == [
        "https://app.credsaathi.in",
        "https://admin.credsaathi.in",
    ]
