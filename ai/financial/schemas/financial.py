"""Pydantic schemas for CredSaathi Financial Intelligence MVP."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ai.schemas.common import ModelMetadata


class FinancialProfileInput(BaseModel):
    """Validated financial data payload originating from core backend."""
    validated_income: Optional[float] = Field(default=None, ge=0.0, description="Annual/Monthly income validated by backend")
    turnover: Optional[float] = Field(default=None, ge=0.0, description="Annual business turnover")
    revenue: Optional[float] = Field(default=None, ge=0.0, description="Annual revenue")
    expenses: Optional[float] = Field(default=None, ge=0.0, description="Annual/Monthly operational or personal expenses")
    existing_liabilities: Optional[float] = Field(default=None, ge=0.0, description="Total outstanding debt / liabilities")
    existing_loans: List[Dict[str, Any]] = Field(default_factory=list, description="Details of existing active loans")
    repayment_information: Optional[str] = Field(default=None, description="Repayment track record / history summary")
    cash_flow_information: Optional[str] = Field(default=None, description="Net cash flow status summary")
    loan_requirement: Optional[float] = Field(default=None, ge=0.0, description="Requested loan amount")
    currency: str = Field(default="INR", description="Currency unit")


class FinancialSummaryResponseData(BaseModel):
    """Structured response payload for financial profile narrative explanations."""
    summary: str = Field(..., description="Human-readable plain-language financial summary")
    key_facts: List[str] = Field(default_factory=list, description="Preserved numeric financial facts from backend")
    observations: List[str] = Field(default_factory=list, description="Objective financial observations without decisioning claims")
    data_gaps: List[str] = Field(default_factory=list, description="Identified missing financial attributes required for full context")
    preparation_guidance: List[str] = Field(default_factory=list, description="Guidance steps for document/profile preparation")
    source: str = Field(default="backend_validated_data", description="Source indicator enforcing backend source of truth")
    model: Optional[ModelMetadata] = Field(default=None, description="Model metadata used for explanation generation")
    disclaimer: str = Field(
        default="Financial summaries present narrative explanations of backend-validated metrics. This summary is NOT a credit score, risk score, credit approval, or loan rejection decision.",
        description="Mandatory financial compliance disclaimer"
    )
