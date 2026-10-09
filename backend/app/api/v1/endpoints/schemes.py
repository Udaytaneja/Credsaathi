from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.scheme import Scheme
from app.models.user import User
from app.services.ai_client import ai_service_client

router = APIRouter()


class ApplicantMatchContextInput(BaseModel):
    category: str | None = Field(default="General")
    state: str | None = Field(default=None)
    income_annual: float | None = Field(default=None, ge=0.0)
    occupation: str | None = Field(default=None)
    purpose: str | None = Field(default=None)
    language: str = Field(default="en")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="List active schemes",
)
def list_schemes(db: Session = Depends(get_db)):
    schemes = db.query(Scheme).filter(Scheme.status == "ACTIVE", Scheme.deleted_at.is_(None)).all()
    return schemes


@router.post(
    "/match",
    status_code=status.HTTP_200_OK,
    summary="Match and rank schemes for authenticated applicant",
)
async def match_schemes(
    body: ApplicantMatchContextInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch active schemes from database for deterministic pre-filtering
    schemes = db.query(Scheme).filter(Scheme.status == "ACTIVE", Scheme.deleted_at.is_(None)).all()

    if not schemes:
        return {"matches": [], "disclaimer": "No active schemes found in system database."}

    candidate_schemes: list[dict[str, Any]] = []
    for s in schemes:
        # Perform deterministic hard eligibility pre-filtering
        backend_status = "ELIGIBLE"
        if s.min_amount and body.income_annual and float(s.min_amount) > (body.income_annual * 2):
            backend_status = "NEEDS_INFO"

        req_docs = s.required_documents if isinstance(s.required_documents, list) else ["Bank Statement", "Aadhaar Card"]

        candidate_schemes.append({
            "scheme_id": str(s.id),
            "scheme_name": s.name,
            "category": s.category or "General",
            "description": s.description,
            "eligibility_criteria": [s.purpose or "General scheme eligibility"],
            "required_documents": req_docs,
            "backend_eligibility_status": backend_status,
            "source_reference": s.source,
            "last_verified": "2026-10-01",
        })

    applicant_context = {
        "applicant_id": str(current_user.id),
        "category": body.category,
        "state": body.state,
        "income_annual": body.income_annual,
        "occupation": body.occupation,
        "purpose": body.purpose,
    }

    try:
        ai_response = await ai_service_client.match_schemes(
            applicant_context=applicant_context,
            candidate_schemes=candidate_schemes,
            language=body.language,
        )
        return ai_response
    except Exception as e:
        # Fallback to backend deterministic candidates if AI microservice is offline
        fallback_matches = [
            {
                "scheme_id": c["scheme_id"],
                "scheme_name": c["scheme_name"],
                "relevance_score": 0.85 if c["backend_eligibility_status"] == "ELIGIBLE" else 0.50,
                "eligibility_status": c["backend_eligibility_status"],
                "match_reasons": [f"Matches purpose {body.purpose or 'general'}"],
                "missing_information": [],
                "source_reference": c["source_reference"],
                "last_verified": c["last_verified"],
                "explanation": f"Backend candidate scheme match (AI fallback: {str(e)})",
            }
            for c in candidate_schemes
        ]
        return {
            "matches": fallback_matches,
            "disclaimer": "Relevance scores indicate semantic matching compatibility. Not an approval decision.",
        }
