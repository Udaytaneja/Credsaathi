"""API endpoint for CredSaathi Document AI extraction."""
import time
from fastapi import APIRouter, Depends, Request, status
from ai.audit import audit_service
from ai.gateway.auth import verify_api_key
from ai.extraction.service import document_ai_service
from ai.model_router.registry import model_registry
from ai.schemas.common import ResponseEnvelope
from ai.schemas.extraction import DocumentExtractionRequest, DocumentExtractionResponseData

router = APIRouter()


@router.post(
    "/extract-document",
    response_model=ResponseEnvelope[DocumentExtractionResponseData],
    summary="Extract & Validate Document Fields",
    description="Extracts, normalizes, and validates document fields from uploaded document text or bytes.",
    status_code=status.HTTP_200_OK,
)
async def extract_document_endpoint(
    request: Request,
    body: DocumentExtractionRequest,
    authenticated_user: str = Depends(verify_api_key),
):
    """Extracts, normalizes, and validates document fields.

    NOTE: OCR extraction does NOT prove document authenticity, identity verification, or legal validity.
    """
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown_req")

    try:
        response_data = await document_ai_service.process_document(body)
        model_meta = model_registry.get_metadata("default")
        latency_ms = round((time.time() - start_time) * 1000, 2)

        audit_rec = audit_service.create_record(
            request_id=request_id,
            task_type="DOCUMENT_EXTRACTION",
            user_id=authenticated_user,
            model_provider=model_meta.provider if model_meta else "CredSaathi-Internal",
            model_name=model_meta.model if model_meta else "doc-extractor",
            model_version=model_meta.version if model_meta else "v1.0",
            latency_ms=latency_ms,
            output_validation_status="PASSED" if not response_data.review_required else "REPAIRED",
            human_review_required=response_data.review_required,
        )
        await audit_service.record_event(audit_rec)

        return ResponseEnvelope.success_response(
            data=response_data,
            model_metadata=model_meta,
            request_id=request_id
        )
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        audit_rec = audit_service.create_record(
            request_id=request_id,
            task_type="DOCUMENT_EXTRACTION",
            user_id=authenticated_user,
            latency_ms=latency_ms,
            output_validation_status="FAILED",
            errors=[{"code": "EXTRACTION_ERROR", "message": str(e)}],
        )
        await audit_service.record_event(audit_rec)
        raise
