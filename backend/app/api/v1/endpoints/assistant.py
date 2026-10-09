import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.ai_client import ai_service_client
from app.services.application_service import ApplicationService

router = APIRouter()


class AssistantQueryInput(BaseModel):
    query: str = Field(..., min_length=1, description="User question or query text")
    language: str = Field(default="en", description="Preferred language ('en', 'hi', 'hinglish')")
    application_id: str | None = Field(default=None, description="Optional application context ID")


@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    summary="Query Saakshi AI Assistant with authenticated identity",
)
async def query_saakshi_assistant(
    body: AssistantQueryInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # CRITICAL: Sourcing identity strictly from authenticated JWT token, NOT from request body!
    authenticated_user_id = str(current_user.id)

    # Validate application context access if application_id is provided
    validated_app_id = body.application_id
    if body.application_id:
        try:
            app_uuid = uuid.UUID(body.application_id)
            ApplicationService.get_application_by_id(db, current_user, app_uuid)
        except HTTPException as he:
            if he.status_code == status.HTTP_403_FORBIDDEN or he.status_code == status.HTTP_404_NOT_FOUND:
                return {
                    "answer": "Access Denied: You do not have authorization to view this application or user data.",
                    "citations": [],
                    "suggested_actions": ["View My Applications"],
                    "safety_flags": {
                        "prompt_injection_detected": False,
                        "unauthorized_access_attempt": True,
                        "evidence_found": False,
                    },
                    "disclaimer": "Saakshi is an informational assistant. Saakshi does not issue credit approvals.",
                }
            raise he
        except ValueError:
            # If application_id is not a valid UUID string, treat as unauthorized or invalid
            pass

    try:
        response = await ai_service_client.query_assistant(
            query=body.query,
            authenticated_user_id=authenticated_user_id,
            application_id=validated_app_id,
            language=body.language,
        )
        return response
    except Exception:
        return {
            "answer": "I am unable to reach the AI assistant right now. Please try again shortly.",
            "citations": [],
            "suggested_actions": ["Check Application Status", "View Scheme Options"],
            "safety_flags": {
                "prompt_injection_detected": False,
                "unauthorized_access_attempt": False,
                "evidence_found": False,
            },
            "disclaimer": "Saakshi is an informational assistant. Saakshi does not issue credit approvals.",
        }

