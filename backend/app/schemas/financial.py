from decimal import Decimal
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EMICalculationRequest(BaseModel):
    principal: Decimal = Field(..., gt=0, description="Principal loan amount in Currency (e.g. 2500000)")
    annual_interest_rate: Decimal = Field(..., ge=0, le=100, description="Annual interest rate in percent (e.g. 10.5)")
    tenure_months: int = Field(..., gt=0, description="Loan tenure in months")


class EMICalculationResponse(BaseModel):
    principal: Decimal
    annual_interest_rate: Decimal
    tenure_months: int
    monthly_emi: Decimal
    total_repayment: Decimal
    total_interest: Decimal
    emi_label: str
    total_repayment_label: str
    total_interest_label: str


class AmortizationYearRow(BaseModel):
    year: int
    principal_paid: Decimal
    interest_paid: Decimal
    balance_remaining: Decimal
    principal_paid_label: str
    interest_paid_label: str
    balance_remaining_label: str


class AmortizationScheduleResponse(BaseModel):
    principal: Decimal
    annual_interest_rate: Decimal
    tenure_months: int
    monthly_emi: Decimal
    total_repayment: Decimal
    total_interest: Decimal
    yearly_breakdown: list[AmortizationYearRow]


class FinancialSnapshotRequest(BaseModel):
    monthly_income: Decimal = Field(..., gt=0, description="Gross monthly income")
    monthly_expenses: Decimal = Field(default=Decimal("0.00"), ge=0, description="Monthly living / operational expenses")
    existing_debt_monthly_obligation: Decimal = Field(default=Decimal("0.00"), ge=0, description="Existing EMI obligations")
    proposed_emi: Decimal = Field(default=Decimal("0.00"), ge=0, description="Proposed new loan EMI")
    total_assets: Decimal | None = Field(default=None, ge=0, description="Total asset value")
    total_liabilities: Decimal | None = Field(default=None, ge=0, description="Total liability value")


class FinancialSnapshotMetrics(BaseModel):
    monthly_income: Decimal
    monthly_expenses: Decimal
    existing_debt_monthly_obligation: Decimal
    proposed_emi: Decimal
    total_monthly_obligations: Decimal
    net_monthly_cash_flow: Decimal
    remaining_cash_flow_post_emi: Decimal
    cash_flow_impact_percentage: Decimal
    debt_service_coverage_ratio: Decimal | None
    total_assets: Decimal | None
    total_liabilities: Decimal | None
    net_worth: Decimal | None
    monthly_income_label: str
    monthly_expenses_label: str
    existing_debt_label: str
    remaining_cash_flow_post_emi_label: str
    cash_flow_impact_label: str
    dscr_label: str | None


class LoanScenarioRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Loan principal amount in Lakhs (e.g. 25 for ₹25,00,000) or raw currency")
    tenure_years: int = Field(..., gt=0, description="Loan tenure in years")
    interest_rate: Decimal = Field(default=Decimal("10.5"), ge=0, le=100, description="Annual interest rate in % p.a.")
    is_amount_in_lakhs: bool = Field(default=True, description="True if amount is provided in Lakhs")
    monthly_income: Decimal | None = Field(default=Decimal("180000.00"), ge=0)
    monthly_expenses: Decimal | None = Field(default=Decimal("92000.00"), ge=0)
    existing_debt: Decimal | None = Field(default=Decimal("24000.00"), ge=0)

    @field_validator("tenure_years")
    @classmethod
    def validate_tenure_years(cls, v: int) -> int:
        if v <= 0 or v > 40:
            raise ValueError("Tenure years must be between 1 and 40 years")
        return v


class LoanScenarioResponse(BaseModel):
    emi_label: str = Field(..., alias="emiLabel")
    total_repayment_label: str = Field(..., alias="totalRepaymentLabel")
    total_interest_label: str = Field(..., alias="totalInterestLabel")
    monthly_debt_obligations_label: str = Field(..., alias="monthlyDebtObligationsLabel")
    remaining_cash_flow_post_emi_label: str = Field(..., alias="remainingCashFlowPostEmiLabel")
    cash_flow_impact_percentage: str = Field(..., alias="cashFlowImpactPercentage")
    interest_rate_applied: str = Field(..., alias="interestRateApplied")
    amortization_breakdown: list[dict[str, Any]] = Field(..., alias="amortizationBreakdown")
    disclaimer: str = Field(...)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
