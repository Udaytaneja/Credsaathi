from datetime import timedelta
import uuid

from fastapi import Depends
import pytest

from app.api.v1.router import api_v1_router
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user, require_role, verify_organization_access, verify_user_access
from app.models.organization import Organization
from app.models.user import User

# Mount test endpoints to verify RBAC & user isolation dependencies
@api_v1_router.get("/test/applicant-only")
def applicant_only_endpoint(current_user: User = Depends(require_role(["APPLICANT"]))):
    return {"message": "Success", "user_id": str(current_user.id)}


@api_v1_router.get("/test/banker-only")
def banker_only_endpoint(current_user: User = Depends(require_role(["BANKER", "BANK_ADMIN"]))):
    return {"message": "Success", "user_id": str(current_user.id)}


@api_v1_router.get("/test/user/{target_user_id}")
def user_data_endpoint(
    target_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    verify_user_access(current_user, target_user_id)
    return {"message": "Access Granted", "target_user_id": str(target_user_id)}


@api_v1_router.get("/test/org/{target_org_id}")
def org_data_endpoint(
    target_org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    verify_organization_access(current_user, target_org_id)
    return {"message": "Access Granted", "target_org_id": str(target_org_id)}


def test_registration_success(client):
    payload = {
        "name": "Kashvi Jain",
        "email": "kashvi@credsaathi.in",
        "password": "SecurePassword123",
        "role": "APPLICANT",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "kashvi@credsaathi.in"
    assert data["user"]["name"] == "Kashvi Jain"
    assert data["user"]["role"] == "APPLICANT"
    assert "password_hash" not in data


def test_registration_with_full_name_alias(client):
    payload = {
        "full_name": "Diagnostic Test User",
        "email": "diagnostic.alias@credsaathi.in",
        "password": "SecurePassword123!",
        "role": "APPLICANT",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["name"] == "Diagnostic Test User"


def test_registration_missing_name_fails_422(client):
    payload = {
        "email": "noname@credsaathi.in",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    details = response.json()["detail"]
    assert any("name" in str(err["loc"]) for err in details)


def test_duplicate_registration_fails(client):
    payload = {
        "name": "Kashvi Jain",
        "email": "duplicate@credsaathi.in",
        "password": "SecurePassword123",
        "role": "APPLICANT",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_valid_login(client):
    reg_payload = {
        "name": "Uday Taneja",
        "email": "uday@credsaathi.in",
        "password": "MySecretPassword!23",
        "role": "BANKER",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "uday@credsaathi.in",
        "password": "MySecretPassword!23",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "uday@credsaathi.in"
    assert data["user"]["role"] == "BANKER"


def test_invalid_login_credentials(client):
    login_payload = {
        "email": "nonexistent@credsaathi.in",
        "password": "WrongPassword",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_expired_or_invalid_token(client):
    # Invalid token
    res1 = client.get(
        "/api/v1/test/applicant-only",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )
    assert res1.status_code == 401

    # Expired token
    expired_token = create_access_token(
        subject=str(uuid.uuid4()),
        email="test@expired.com",
        role="APPLICANT",
        expires_delta=timedelta(seconds=-10),
    )
    res2 = client.get(
        "/api/v1/test/applicant-only",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res2.status_code == 401


def test_applicant_role_authorization(client):
    reg_payload = {
        "name": "Applicant User",
        "email": "applicant@credsaathi.in",
        "password": "Password123!",
        "role": "APPLICANT",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Applicant accessing applicant endpoint -> HTTP 200
    res1 = client.get("/api/v1/test/applicant-only", headers=headers)
    assert res1.status_code == 200

    # Applicant accessing banker endpoint -> HTTP 403 Forbidden
    res2 = client.get("/api/v1/test/banker-only", headers=headers)
    assert res2.status_code == 403


def test_banker_role_authorization(client):
    reg_payload = {
        "name": "Banker User",
        "email": "banker@credsaathi.in",
        "password": "Password123!",
        "role": "BANKER",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Banker accessing banker endpoint -> HTTP 200
    res1 = client.get("/api/v1/test/banker-only", headers=headers)
    assert res1.status_code == 200

    # Banker accessing applicant endpoint -> HTTP 403 Forbidden
    res2 = client.get("/api/v1/test/applicant-only", headers=headers)
    assert res2.status_code == 403


def test_cross_user_access_rejection(client):
    # Register Applicant 1
    u1_res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "User One",
            "email": "user1@credsaathi.in",
            "password": "Password123!",
            "role": "APPLICANT",
        },
    ).json()
    u1_id = u1_res["user"]["id"]
    u1_token = u1_res["access_token"]

    # Register Applicant 2
    u2_res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "User Two",
            "email": "user2@credsaathi.in",
            "password": "Password123!",
            "role": "APPLICANT",
        },
    ).json()
    u2_id = u2_res["user"]["id"]

    # Applicant 1 accesses own user data -> HTTP 200
    res1 = client.get(
        f"/api/v1/test/user/{u1_id}",
        headers={"Authorization": f"Bearer {u1_token}"},
    )
    assert res1.status_code == 200

    # Applicant 1 attempts to access Applicant 2 data -> HTTP 403 Forbidden
    res2 = client.get(
        f"/api/v1/test/user/{u2_id}",
        headers={"Authorization": f"Bearer {u1_token}"},
    )
    assert res2.status_code == 403


def test_organization_scoping_rejection(client, db_session):
    # Create two organizations
    org1 = Organization(name="Bank A", code="BANK_A")
    org2 = Organization(name="Bank B", code="BANK_B")
    db_session.add(org1)
    db_session.add(org2)
    db_session.commit()

    # Register Banker with Org 1
    banker_res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Banker Org1",
            "email": "banker_org1@credsaathi.in",
            "password": "Password123!",
            "role": "BANKER",
            "organization_id": str(org1.id),
        },
    ).json()
    token = banker_res["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Banker accesses Org 1 data -> HTTP 200
    res1 = client.get(f"/api/v1/test/org/{org1.id}", headers=headers)
    assert res1.status_code == 200

    # Banker accesses Org 2 data -> HTTP 403 Forbidden
    res2 = client.get(f"/api/v1/test/org/{org2.id}", headers=headers)
    assert res2.status_code == 403

