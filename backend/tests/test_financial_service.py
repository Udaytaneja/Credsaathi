from decimal import Decimal
import pytest
from pydantic import ValidationError

from app.schemas.financial import (
    EMICalculationRequest,
    FinancialSnapshotRequest,
    LoanScenarioRequest,
)
from app.services.financial_service import FinancialEngineService, format_inr


def test_format_inr():
    """Verify Indian Rupee currency formatting helper."""
    assert format_inr(Decimal("2500000")) == "₹25,00,000"
    assert format_inr(Decimal("180000")) == "₹1,80,000"
    assert format_inr(Decimal("53682")) == "₹53,682"
    assert format_inr(Decimal("0")) == "₹0"
    assert format_inr(Decimal("-5000")) == "-₹5,000"


def test_normal_emi_calculation():
    """Test standard EMI calculation with known expected values."""
    # Principal: ₹25,00,000 (25 Lakhs), Tenure: 5 Years (60 Months), Rate: 10.5% p.a.
    principal = Decimal("2500000.00")
    rate = Decimal("10.50")
    tenure_months = 60

    emi = FinancialEngineService.calculate_emi(principal, rate, tenure_months)
    assert emi == Decimal("53734.75")

    total_repayment = FinancialEngineService.calculate_total_repayment(emi, tenure_months)
    assert total_repayment == Decimal("3224085.00")

    total_interest = FinancialEngineService.calculate_total_interest(total_repayment, principal)
    assert total_interest == Decimal("724085.00")


def test_zero_or_invalid_principal():
    """Test zero and negative principal handling."""
    with pytest.raises(ValueError, match="Principal amount must be greater than zero"):
        FinancialEngineService.calculate_emi(Decimal("0.00"), Decimal("10.0"), 12)

    with pytest.raises(ValueError, match="Principal amount must be greater than zero"):
        FinancialEngineService.calculate_emi(Decimal("-1000.00"), Decimal("10.0"), 12)

    with pytest.raises(ValidationError):
        EMICalculationRequest(principal=Decimal("0.00"), annual_interest_rate=Decimal("10.0"), tenure_months=12)


def test_invalid_interest_rate():
    """Test negative interest rate and rate > 100%."""
    with pytest.raises(ValueError, match="Annual interest rate must be between 0 and 100 percent"):
        FinancialEngineService.calculate_emi(Decimal("100000.00"), Decimal("-1.0"), 12)

    with pytest.raises(ValueError, match="Annual interest rate must be between 0 and 100 percent"):
        FinancialEngineService.calculate_emi(Decimal("100000.00"), Decimal("150.0"), 12)

    with pytest.raises(ValidationError):
        EMICalculationRequest(principal=Decimal("100000.00"), annual_interest_rate=Decimal("-5.0"), tenure_months=12)


def test_invalid_tenure():
    """Test zero or negative tenure in months."""
    with pytest.raises(ValueError, match="Tenure months must be greater than zero"):
        FinancialEngineService.calculate_emi(Decimal("100000.00"), Decimal("10.0"), 0)

    with pytest.raises(ValueError, match="Tenure months must be greater than zero"):
        FinancialEngineService.calculate_emi(Decimal("100000.00"), Decimal("10.0"), -12)

    with pytest.raises(ValidationError):
        EMICalculationRequest(principal=Decimal("100000.00"), annual_interest_rate=Decimal("10.0"), tenure_months=0)


def test_zero_interest_rate_boundary():
    """Boundary test: 0% interest rate loan (simple linear principal division)."""
    principal = Decimal("120000.00")
    rate = Decimal("0.00")
    tenure_months = 12

    emi = FinancialEngineService.calculate_emi(principal, rate, tenure_months)
    assert emi == Decimal("10000.00")

    total_repayment = FinancialEngineService.calculate_total_repayment(emi, tenure_months)
    assert total_repayment == Decimal("120000.00")

    total_interest = FinancialEngineService.calculate_total_interest(total_repayment, principal)
    assert total_interest == Decimal("0.00")


def test_single_month_tenure_boundary():
    """Boundary test: 1 month tenure."""
    principal = Decimal("100000.00")
    rate = Decimal("12.00")  # 1% per month
    tenure_months = 1

    emi = FinancialEngineService.calculate_emi(principal, rate, tenure_months)
    assert emi == Decimal("101000.00")

    total_repayment = FinancialEngineService.calculate_total_repayment(emi, tenure_months)
    assert total_repayment == Decimal("101000.00")

    total_interest = FinancialEngineService.calculate_total_interest(total_repayment, principal)
    assert total_interest == Decimal("1000.00")


def test_rounding_precision():
    """Verify precision-safe rounding behavior across calculations."""
    principal = Decimal("333333.33")
    rate = Decimal("7.75")
    tenure_months = 37

    req = EMICalculationRequest(principal=principal, annual_interest_rate=rate, tenure_months=tenure_months)
    res = FinancialEngineService.calculate_emi_summary(req)

    assert isinstance(res.monthly_emi, Decimal)
    assert res.monthly_emi == Decimal("10157.15")
    assert res.total_repayment == Decimal("375814.55")
    assert res.total_interest == Decimal("42481.22")


def test_large_monetary_values():
    """Test calculations with large values (e.g. ₹100 Crore / 1 Billion principal)."""
    principal = Decimal("1000000000.00")  # 100 Crore
    rate = Decimal("9.50")
    tenure_months = 240  # 20 years

    emi = FinancialEngineService.calculate_emi(principal, rate, tenure_months)
    assert emi > Decimal("0")
    total_repayment = FinancialEngineService.calculate_total_repayment(emi, tenure_months)
    total_interest = FinancialEngineService.calculate_total_interest(total_repayment, principal)

    assert total_repayment > principal
    assert total_interest == total_repayment - principal


def test_amortization_schedule_generation():
    """Test complete yearly amortization schedule generation."""
    principal = Decimal("1200000.00")  # 12 Lakhs
    rate = Decimal("10.00")
    tenure_months = 24  # 2 Years

    schedule = FinancialEngineService.generate_amortization_schedule(principal, rate, tenure_months)

    assert len(schedule.yearly_breakdown) == 2
    assert schedule.yearly_breakdown[0].year == 1
    assert schedule.yearly_breakdown[1].year == 2
    assert schedule.yearly_breakdown[1].balance_remaining == Decimal("0.00")

    # Sum of principal paid across years must equal initial principal
    total_principal_paid = sum((row.principal_paid for row in schedule.yearly_breakdown), Decimal("0.00"))
    assert total_principal_paid == principal


def test_financial_snapshot_derivation():
    """Test financial snapshot, cash flow, debt service coverage ratio (DSCR), and net worth metrics."""
    req = FinancialSnapshotRequest(
        monthly_income=Decimal("200000.00"),
        monthly_expenses=Decimal("80000.00"),
        existing_debt_monthly_obligation=Decimal("20000.00"),
        proposed_emi=Decimal("40000.00"),
        total_assets=Decimal("5000000.00"),
        total_liabilities=Decimal("1500000.00"),
    )

    metrics = FinancialEngineService.calculate_financial_snapshot(req)

    assert metrics.net_monthly_cash_flow == Decimal("100000.00")
    assert metrics.total_monthly_obligations == Decimal("60000.00")
    assert metrics.remaining_cash_flow_post_emi == Decimal("60000.00")
    assert metrics.cash_flow_impact_percentage == Decimal("30.0")
    assert metrics.debt_service_coverage_ratio == Decimal("2.00")
    assert metrics.dscr_label == "2.00x (Healthy DSCR)"
    assert metrics.net_worth == Decimal("3500000.00")


def test_loan_scenario_response_compatibility():
    """Verify loan scenario calculation response formatting for frontend consumption."""
    req = LoanScenarioRequest(
        amount=Decimal("25"),  # 25 Lakhs
        tenure_years=5,
        interest_rate=Decimal("10.5"),
        is_amount_in_lakhs=True,
    )

    res = FinancialEngineService.calculate_loan_scenario(req)

    assert "₹53,735 / month" in res.emi_label
    assert "₹32,24,085" in res.total_repayment_label
    assert "₹7,24,085" in res.total_interest_label
    assert "10.5% p.a." in res.interest_rate_applied
    assert len(res.amortization_breakdown) == 5
    assert res.amortization_breakdown[0]["year"] == 1
    assert "Official interest rates" in res.disclaimer
