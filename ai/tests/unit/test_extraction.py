"""Unit tests for Document AI pipeline."""
import base64
import pytest
from ai.extraction.loaders.loader import document_loader
from ai.extraction.schemas import DocumentExtractionRequest, SupportedDocumentType
from ai.extraction.service import document_ai_service
from ai.gateway.errors import AIValidationException


@pytest.mark.asyncio
async def test_valid_document_extraction():
    req = DocumentExtractionRequest(
        document_type=SupportedDocumentType.INCOME_PROOF,
        file_name="salary_slip.pdf",
        file_text_override="Applicant Name: Ramesh Kumar\nGross Monthly Income: INR 55000\nEmployer Name: Acme Tech"
    )

    resp = await document_ai_service.process_document(req)

    assert resp.document_type == "income_proof"
    assert resp.fields["applicant_name"] == "Ramesh Kumar"
    assert resp.fields["gross_monthly_income"] == 55000.0
    assert resp.fields["employer_name"] == "Acme Tech"
    assert resp.field_confidence["applicant_name"] > 0.8
    assert "authenticity" in resp.disclaimer.lower()


def test_unsupported_file_format():
    with pytest.raises(AIValidationException) as exc_info:
        document_loader.validate_and_load("exe_file.exe", base64.b64encode(b"dummy").decode())

    assert "Unsupported file format" in exc_info.value.message


def test_corrupted_base64_document():
    with pytest.raises(AIValidationException) as exc_info:
        document_loader.validate_and_load("corrupted.pdf", "invalid_base64_content_!@#$")

    assert "Corrupted or malformed base64" in exc_info.value.message


@pytest.mark.asyncio
async def test_low_quality_ocr_triggers_review():
    req = DocumentExtractionRequest(
        document_type=SupportedDocumentType.GENERIC,
        file_name="blurry_doc.png",
        file_text_override="LOW_QUALITY_OCR Unreadable text snippet"
    )

    resp = await document_ai_service.process_document(req)

    assert resp.review_required is True
    assert any("low overall OCR confidence" in w for w in resp.warnings)


@pytest.mark.asyncio
async def test_missing_mandatory_fields_triggers_review():
    req = DocumentExtractionRequest(
        document_type=SupportedDocumentType.INCOME_PROOF,
        file_name="incomplete.pdf",
        file_text_override="Random Document text without name or income"
    )

    resp = await document_ai_service.process_document(req)

    assert resp.review_required is True
    assert any("Missing mandatory field" in w for w in resp.warnings)


def test_malicious_path_traversal_sanitization():
    # Dangerous path attempts should be stripped to base filename
    raw, mime = document_loader.validate_and_load(
        "../../../etc/passwd/malicious.pdf",
        base64.b64encode(b"valid pdf header content").decode()
    )
    assert mime == "application/pdf"
    assert len(raw) > 0
