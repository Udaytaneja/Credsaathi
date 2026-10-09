from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.financial import (
    FinancialSnapshotMetrics,
    FinancialSnapshotRequest,
    LoanScenarioRequest,
    LoanScenarioResponse,
)
from app.services.ai_client import ai_service_client
from app.services.financial_service import FinancialEngineService

router = APIRouter()


@router.post(
    "/loan-scenarios",
    response_model=LoanScenarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate loan scenario and EMI",
)
def calculate_loan_scenario(body: LoanScenarioRequest):
    return FinancialEngineService.calculate_loan_scenario(body)


@router.post(
    "/snapshot",
    response_model=FinancialSnapshotMetrics,
    status_code=status.HTTP_200_OK,
    summary="Derive financial snapshot metrics",
)
def calculate_snapshot(body: FinancialSnapshotRequest):
    return FinancialEngineService.calculate_financial_snapshot(body)


@router.post(
    "/explanation",
    status_code=status.HTTP_200_OK,
    summary="Generate grounded AI financial profile narrative",
)
async def generate_financial_explanation(
    body: FinancialSnapshotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Authoritative backend calculation
    snapshot = FinancialEngineService.calculate_financial_snapshot(body)

    # 2. Build payload for AI explanation generator
    ai_payload: dict[str, Any] = {
        "validated_income": float(snapshot.monthly_income * 12),
        "expenses": float(snapshot.monthly_expenses * 12),
        "existing_liabilities": float(snapshot.existing_debt_monthly_obligation * 12),
        "cash_flow_information": f"Post-EMI remaining monthly cash flow: {snapshot.remaining_cash_flow_post_emi_label}, Impact: {snapshot.cash_flow_impact_label}",
        "currency": "INR",
    }

    try:
        ai_narrative = await ai_service_client.generate_financial_explanation(ai_payload)
    except Exception as e:
        ai_narrative = {
            "summary": f"Financial profile validated: Net Cash Flow {snapshot.remaining_cash_flow_post_emi_label}/month. (AI fallback: {str(e)})",
            "key_facts": [f"Income: {snapshot.monthly_income_label}", f"Expenses: {snapshot.monthly_expenses_label}"],
            "observations": [f"DSCR: {snapshot.dscr_label or 'N/A'}"],
            "data_gaps": [],
            "preparation_guidance": [],
            "disclaimer": "Narrative generated from backend-validated metrics.",
        }

    return {
        "authoritative_metrics": snapshot,
        "ai_explanation": ai_narrative,
    }
