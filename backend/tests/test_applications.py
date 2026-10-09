import uuid
from decimal import Decimal
import pytest

from app.models.organization import Organization
from app.models.scheme import Scheme


@pytest.fixture
def test_scheme(db_session):
    """Fixture providing a test scheme in database."""
    scheme = Scheme(
        name="PM Mudra Yojana",
        code="PMMY_01",
        purpose="Business Expansion",
        description="Collateral free loan for micro enterprises",
        category="MSME",
        min_amount=Decimal("50000.00"),
        max_amount=Decimal("1000000.00"),
        interest_rate_min=Decimal("8.50"),
        interest_rate_max=Decimal("12.00"),
        source="Ministry of MSME",
        status="ACTIVE",
    )
    db_session.add(scheme)
    db_session.commit()
    db_session.refresh(scheme)
    return scheme


@pytest.fixture
def applicant_headers(client):
    """Register and return auth headers for an applicant user."""
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Applicant User",
            "email": "applicant.app@credsaathi.in",
            "password": "Password123!",
            "role": "APPLICANT",
        },
    ).json()
    return {"Authorization": f"Bearer {reg['access_token']}"}, reg["user"]["id"]


@pytest.fixture
def banker_headers(client, db_session):
    """Register and return auth headers for a banker user belonging to Org A."""
    org = Organization(name="State Bank", code="SBI_01")
    db_session.add(org)
    db_session.commit()

    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Banker User",
            "email": "banker.app@credsaathi.in",
            "password": "Password123!",
            "role": "BANKER",
            "organization_id": str(org.id),
        },
    ).json()
    return {"Authorization": f"Bearer {reg['access_token']}"}, reg["user"]["id"], org.id


def test_create_application_success(client, test_scheme, applicant_headers):
    headers, user_id = applicant_headers
    payload = {
        "scheme_id": str(test_scheme.id),
        "requested_amount": 500000.0,
    }
    response = client.post("/api/v1/applications", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "application_number" in data
    assert data["user_id"] == user_id
    assert data["scheme_id"] == str(test_scheme.id)
    assert data["status"] == "DRAFT"
    assert Decimal(str(data["requested_amount"])) == Decimal("500000.0")


def test_application_ownership_authorization(client, test_scheme, applicant_headers):
    # Applicant 1 creates application
    h1, u1_id = applicant_headers
    app_res = client.post(
        "/api/v1/applications",
        json={"scheme_id": str(test_scheme.id), "requested_amount": 200000.0},
        headers=h1,
    ).json()
    app_id = app_res["id"]

    # Register Applicant 2
    h2 = {"Authorization": f"Bearer {client.post('/api/v1/auth/register', json={'name': 'User 2', 'email': 'user2.app@credsaathi.in', 'password': 'Password123!', 'role': 'APPLICANT'}).json()['access_token']}"}

    # Applicant 1 accesses application -> HTTP 200
    res1 = client.get(f"/api/v1/applications/{app_id}", headers=h1)
    assert res1.status_code == 200

    # Applicant 2 attempts to access Applicant 1's application -> HTTP 403 Forbidden
    res2 = client.get(f"/api/v1/applications/{app_id}", headers=h2)
    assert res2.status_code == 403
    assert "Access denied" in res2.json()["detail"]


def test_list_applications_scoped_by_role(client, test_scheme, applicant_headers, banker_headers):
    app_headers, app_user_id = applicant_headers
    bank_headers, banker_user_id, org_id = banker_headers

    # Applicant creates an application with banker's organization_id
    client.post(
        "/api/v1/applications",
        json={
            "scheme_id": str(test_scheme.id),
            "organization_id": str(org_id),
            "requested_amount": 300000.0,
        },
        headers=app_headers,
    )

    # Applicant lists applications -> sees 1 application
    app_list = client.get("/api/v1/applications", headers=app_headers).json()
    assert len(app_list) == 1
    assert app_list[0]["user_id"] == app_user_id

    # Banker lists applications -> sees application assigned to their organization
    banker_list = client.get("/api/v1/applications", headers=bank_headers).json()
    assert len(banker_list) == 1
    assert banker_list[0]["organization_id"] == str(org_id)


def test_valid_and_invalid_application_status_transitions(client, test_scheme, applicant_headers, banker_headers):
    app_headers, _ = applicant_headers
    bank_headers, _, org_id = banker_headers

    # Create draft application
    app_res = client.post(
        "/api/v1/applications",
        json={
            "scheme_id": str(test_scheme.id),
            "organization_id": str(org_id),
            "requested_amount": 100000.0,
        },
        headers=app_headers,
    ).json()
    app_id = app_res["id"]

    # 1. Invalid status value -> HTTP 422 Unprocessable Entity
    bad_val_res = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "SUPER_APPROVED"},
        headers=app_headers,
    )
    assert bad_val_res.status_code == 422

    # 2. Invalid state machine transition: DRAFT -> ACCEPTED directly (must go DRAFT -> SUBMITTED) -> HTTP 400
    invalid_trans_res = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "ACCEPTED"},
        headers=bank_headers,
    )
    assert invalid_trans_res.status_code == 400

    # 3. Applicant transitions DRAFT -> SUBMITTED -> HTTP 200
    sub_res = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "SUBMITTED"},
        headers=app_headers,
    )
    assert sub_res.status_code == 200
    assert sub_res.json()["status"] == "SUBMITTED"
    assert sub_res.json()["submitted_at"] is not None

    # 4. Applicant tries to mark SUBMITTED application UNDER_REVIEW -> HTTP 403 Forbidden
    app_accept_res = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "UNDER_REVIEW"},
        headers=app_headers,
    )
    assert app_accept_res.status_code == 403

    # 5. Banker transitions SUBMITTED -> UNDER_REVIEW -> HTTP 200
    review_res = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "UNDER_REVIEW"},
        headers=bank_headers,
    )
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "UNDER_REVIEW"

    # 6. Banker transitions UNDER_REVIEW -> ACCEPTED -> HTTP 200
    accept_res = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "ACCEPTED"},
        headers=bank_headers,
    )
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "ACCEPTED"
