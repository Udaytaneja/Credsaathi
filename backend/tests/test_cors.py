import pytest
from app.core.config import Settings


def test_cors_origins_sanitization_and_defaults():
    """Verify cors_origins_list strips whitespace, trailing slashes, and provides defaults."""
    settings = Settings(cors_origins="https://credsaathi.vercel.app/, http://localhost:5173/ ")
    origins = settings.cors_origins_list
    assert origins == ["https://credsaathi.vercel.app", "http://localhost:5173"]

    # Verify default origins include Vercel production frontend when cors_origins is empty
    empty_settings = Settings(cors_origins="")
    assert "https://credsaathi.vercel.app" in empty_settings.cors_origins_list


def test_cors_preflight_allowed_origin(client):
    """Verify OPTIONS preflight request for allowed production origin returns correct headers."""
    response = client.options(
        "/api/v1/auth/register",
        headers={
            "Origin": "https://credsaathi.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://credsaathi.vercel.app"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_preflight_rejected_origin(client):
    """Verify OPTIONS preflight request for an unallowed origin is rejected."""
    response = client.options(
        "/api/v1/auth/register",
        headers={
            "Origin": "https://malicious-unauthorized-site.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "https://malicious-unauthorized-site.com"


def test_cors_actual_request_header(client):
    """Verify actual POST request from allowed origin includes access-control-allow-origin header."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "CORS Test User",
            "email": "cors.user@credsaathi.in",
            "password": "Password123!",
            "role": "APPLICANT",
        },
        headers={"Origin": "https://credsaathi.vercel.app"},
    )
    assert response.headers.get("access-control-allow-origin") == "https://credsaathi.vercel.app"


def test_production_safety_check_rejects_wildcard_cors():
    """Verify check_production_safety raises error if wildcard CORS is specified in production."""
    prod_settings = Settings(
        app_env="production",
        secret_key="a_very_secure_secret_key_for_production_use_12345",
        ai_api_key="a_very_secure_ai_api_key_for_production_use_12345",
        cors_origins="*",
    )
    with pytest.raises(ValueError, match=r"Wildcard '\*' CORS origin is not allowed in production"):
        prod_settings.check_production_safety()
