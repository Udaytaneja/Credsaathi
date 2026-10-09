"""API endpoint for Saakshi - CredSaathi Applicant Assistant."""
import time
from fastapi import APIRouter, Depends, Request, status
from ai.agents.saakshi import saakshi_assistant
from ai.audit import audit_service
from ai.gateway.auth import verify_api_key
from ai.model_router.registry import model_registry
from ai.schemas.assistant import AssistantQueryRequest, AssistantQueryResponseData
from ai.schemas.common import ResponseEnvelope

router = APIRouter()


@router.post(
    "/assistant/query",
    response_model=ResponseEnvelope[AssistantQueryResponseData],
    summary="Query Saakshi Applicant Assistant",
    description="Saakshi Applicant Assistant endpoint for scheme guidance, navigation, application status, and FAQs.",
    status_code=status.HTTP_200_OK,
)
async def assistant_query_endpoint(
    request: Request,
    body: AssistantQueryRequest,
    authenticated_user: str = Depends(verify_api_key),
):
    """Saakshi Applicant Assistant endpoint.

    NOTE: Saakshi does NOT issue credit approvals, loan rejections, or credit scores. Saakshi cannot access another user's data.
    """
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown_req")
    user_id = body.authenticated_user_id or authenticated_user

    try:
        response_data = await saakshi_assistant.handle_query(body)
        model_meta = model_registry.get_metadata("default")
        latency_ms = round((time.time() - start_time) * 1000, 2)

        audit_rec = audit_service.create_record(
            request_id=request_id,
            task_type="ASSISTANT_QUERY",
            user_id=user_id,
            application_id=body.application_id,
            model_provider=model_meta.provider if model_meta else "CredSaathi-Internal",
            model_name=model_meta.model if model_meta else "saakshi-assistant",
            model_version=model_meta.version if model_meta else "v1.0",
            retrieval_source_ids=[c.citation_id for c in response_data.citations],
            latency_ms=latency_ms,
            output_validation_status="PASSED",
            guardrail_events=[
                {"event": "prompt_injection_detected", "val": response_data.safety_flags.prompt_injection_detected},
                {"event": "unauthorized_access_attempt", "val": response_data.safety_flags.unauthorized_access_attempt},
            ],
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
            task_type="ASSISTANT_QUERY",
            user_id=user_id,
            latency_ms=latency_ms,
            output_validation_status="FAILED",
            errors=[{"code": "ASSISTANT_ERROR", "message": str(e)}],
        )
        await audit_service.record_event(audit_rec)
        raise
