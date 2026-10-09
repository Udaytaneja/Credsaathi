import io
import pytest

from app.schemas.document import MAX_FILE_SIZE_BYTES


@pytest.fixture
def auth_applicant(client):
    """Register and return auth headers + user_id for an applicant."""
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Doc Applicant",
            "email": "doc.applicant@credsaathi.in",
            "password": "Password123!",
            "role": "APPLICANT",
        },
    ).json()
    return {"Authorization": f"Bearer {reg['access_token']}"}, reg["user"]["id"]


def test_valid_document_upload_and_metadata(client, auth_applicant):
    headers, user_id = auth_applicant
    file_content = b"%PDF-1.4 Mock PDF Document Content"
    file_obj = io.BytesIO(file_content)

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("bank_statement.pdf", file_obj, "application/pdf")},
        data={"document_type": "BANK_STATEMENT"},
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "bank_statement.pdf"
    assert data["mime_type"] == "application/pdf"
    assert data["document_type"] == "BANK_STATEMENT"
    assert data["file_size_bytes"] == len(file_content)
    assert data["status"] == "VALID"
    assert data["extracted_data"] is not None
    assert data["user_id"] == user_id
    # Storage path must use internal safe UUID identifier, not user filename
    assert "bank_statement.pdf" not in data["storage_path"]


def test_invalid_mime_type_rejection(client, auth_applicant):
    headers, _ = auth_applicant
    file_content = b"<html><script>alert('malicious')</script></html>"
    file_obj = io.BytesIO(file_content)

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("malicious.html", file_obj, "text/html")},
        data={"document_type": "BANK_STATEMENT"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_oversized_file_rejection(client, auth_applicant):
    headers, _ = auth_applicant
    # Create file slightly exceeding 10 MB limit
    oversized_content = b"A" * (MAX_FILE_SIZE_BYTES + 1024)
    file_obj = io.BytesIO(oversized_content)

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("large_file.pdf", file_obj, "application/pdf")},
        data={"document_type": "BANK_STATEMENT"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "exceeds maximum limit" in response.json()["detail"]


def test_document_ownership_authorization(client, auth_applicant):
    h1, _ = auth_applicant

    # Upload document as User 1
    doc_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("id_proof.jpg", io.BytesIO(b"\xff\xd8\xff\xe0 Mock JPEG Data"), "image/jpeg")},
        data={"document_type": "IDENTITY_PROOF"},
        headers=h1,
    ).json()
    doc_id = doc_res["id"]

    # Register User 2
    reg2 = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Doc User 2",
            "email": "doc.user2@credsaathi.in",
            "password": "Password123!",
            "role": "APPLICANT",
        },
    ).json()
    h2 = {"Authorization": f"Bearer {reg2['access_token']}"}

    # User 1 accesses own document -> HTTP 200
    res1 = client.get(f"/api/v1/documents/{doc_id}", headers=h1)
    assert res1.status_code == 200

    # User 2 attempts to access User 1's document -> HTTP 403 Forbidden
    res2 = client.get(f"/api/v1/documents/{doc_id}", headers=h2)
    assert res2.status_code == 403
    assert "Access denied" in res2.json()["detail"]
