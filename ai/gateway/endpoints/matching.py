"""API endpoint for CredSaathi Scheme Matching AI."""
import time
from fastapi import APIRouter, Depends, Request, status
from ai.audit import audit_service
from ai.gateway.auth import verify_api_key
from ai.matching.service import scheme_matching_service
from ai.model_router.registry import model_registry
from ai.schemas.common import ResponseEnvelope
from ai.schemas.matching import SchemeMatchRequest, SchemeMatchResponseData

router = APIRouter()


@router.post(
    "/scheme-match",
    response_model=ResponseEnvelope[SchemeMatchResponseData],
    summary="Match & Rank Candidate Government/Financial Schemes",
    description="Ranks, explains, and identifies missing information for candidate schemes provided by backend.",
    status_code=status.HTTP_200_OK,
)
async def match_schemes_endpoint(
    request: Request,
    body: SchemeMatchRequest,
    authenticated_user: str = Depends(verify_api_key),
):
    """Ranks, explains, and identifies missing information for candidate schemes.

    NOTE: relevance_score represents semantic match relevance, NOT credit score, approval probability,
    or guaranteed eligibility.
    """
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown_req")
    user_id = body.applicant_context.applicant_id or authenticated_user

    try:
        match_response = await scheme_matching_service.match_schemes(body)
        model_meta = model_registry.get_metadata("default")
        latency_ms = round((time.time() - start_time) * 1000, 2)

        audit_rec = audit_service.create_record(
            request_id=request_id,
            task_type="SCHEME_MATCHING",
            user_id=user_id,
            model_provider=model_meta.provider if model_meta else "CredSaathi-Internal",
            model_name=model_meta.model if model_meta else "scheme-matcher",
            model_version=model_meta.version if model_meta else "v1.0",
            latency_ms=latency_ms,
            output_validation_status="PASSED",
        )
        await audit_service.record_event(audit_rec)

        return ResponseEnvelope.success_response(
            data=match_response,
            model_metadata=model_meta,
            request_id=request_id
        )
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        audit_rec = audit_service.create_record(
            request_id=request_id,
            task_type="SCHEME_MATCHING",
            user_id=user_id,
            latency_ms=latency_ms,
            output_validation_status="FAILED",
            errors=[{"code": "EXECUTION_ERROR", "message": str(e)}],
        )
        await audit_service.record_event(audit_rec)
        raise
