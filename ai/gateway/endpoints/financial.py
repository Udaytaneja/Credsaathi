"""API endpoint for CredSaathi Financial Intelligence MVP."""
import time
from fastapi import APIRouter, Depends, Request, status
from ai.audit import audit_service
from ai.gateway.auth import verify_api_key
from ai.financial.explanation.generator import explanation_generator
from ai.financial.schemas.financial import FinancialProfileInput, FinancialSummaryResponseData
from ai.schemas.common import ResponseEnvelope

router = APIRouter()


@router.post(
    "/financial-explanation",
    response_model=ResponseEnvelope[FinancialSummaryResponseData],
    summary="Generate Grounded Financial Profile Narrative",
    description="Generates narrative summaries and financial observations grounded in backend metrics.",
    status_code=status.HTTP_200_OK,
)
async def financial_explanation_endpoint(
    request: Request,
    body: FinancialProfileInput,
    authenticated_user: str = Depends(verify_api_key),
):
    """Generates narrative summaries and financial observations grounded in backend metrics.

    NOTE: AI does NOT issue credit approvals, loan rejections, credit scores, or approval probabilities.
    """
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown_req")
    user_id = getattr(body, "applicant_id", None) or authenticated_user

    try:
        summary_data = await explanation_generator.generate_explanation(body)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        audit_rec = audit_service.create_record(
            request_id=request_id,
            task_type="FINANCIAL_EXPLANATION",
            user_id=user_id,
            model_provider=summary_data.model.provider if summary_data.model else "CredSaathi-Internal",
            model_name=summary_data.model.model if summary_data.model else "financial-summarizer",
            model_version=summary_data.model.version if summary_data.model else "v1.0",
            latency_ms=latency_ms,
            output_validation_status="PASSED",
        )
        await audit_service.record_event(audit_rec)

        return ResponseEnvelope.success_response(
            data=summary_data,
            model_metadata=summary_data.model,
            request_id=request_id
        )
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        audit_rec = audit_service.create_record(
            request_id=request_id,
            task_type="FINANCIAL_EXPLANATION",
            user_id=user_id,
            latency_ms=latency_ms,
            output_validation_status="FAILED",
            errors=[{"code": "FINANCIAL_EXPLANATION_ERROR", "message": str(e)}],
        )
        await audit_service.record_event(audit_rec)
        raise
