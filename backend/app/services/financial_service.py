from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Any

from app.schemas.financial import (
    AmortizationScheduleResponse,
    AmortizationYearRow,
    EMICalculationRequest,
    EMICalculationResponse,
    FinancialSnapshotMetrics,
    FinancialSnapshotRequest,
    LoanScenarioRequest,
    LoanScenarioResponse,
)

# Set global decimal precision to 28 decimal places for financial calculations
getcontext().prec = 28


def format_inr(amount: Decimal | int | float) -> str:
    """
    Format monetary Decimal into Indian Rupee currency string.
    Example: 2500000 -> "₹25,00,000", 53682.45 -> "₹53,682"
    """
    dec_val = Decimal(str(amount)) if not isinstance(amount, Decimal) else amount
    is_negative = dec_val < Decimal("0")
    abs_val = abs(dec_val)

    rounded_val = int(abs_val.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    s = str(rounded_val)

    if len(s) <= 3:
        formatted_num = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        groups: list[str] = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted_num = ",".join(groups) + "," + last3

    prefix = "-₹" if is_negative else "₹"
    return f"{prefix}{formatted_num}"


class FinancialEngineService:
    """
    Authoritative, deterministic backend financial calculation service.
    
    All calculations are performed strictly using Decimal precision arithmetic.
    """

    @staticmethod
    def calculate_emi(
        principal: Decimal,
        annual_interest_rate: Decimal,
        tenure_months: int,
    ) -> Decimal:
        """
        Calculate Equated Monthly Installment (EMI) using Decimal precision.
        Formula: EMI = [P x r x (1+r)^n] / [(1+r)^n - 1]
        """
        if principal <= Decimal("0"):
            raise ValueError("Principal amount must be greater than zero.")
        if annual_interest_rate < Decimal("0") or annual_interest_rate > Decimal("100"):
            raise ValueError("Annual interest rate must be between 0 and 100 percent.")
        if tenure_months <= 0:
            raise ValueError("Tenure months must be greater than zero.")

        # Zero interest rate case
        if annual_interest_rate == Decimal("0"):
            raw_emi = principal / Decimal(tenure_months)
            return raw_emi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Monthly interest rate r = R / (12 * 100)
        r = annual_interest_rate / Decimal("1200")

        # (1 + r)^n using pure Decimal arithmetic
        one_plus_r = Decimal("1") + r
        factor = one_plus_r ** tenure_months

        numerator = principal * r * factor
        denominator = factor - Decimal("1")

        if denominator == Decimal("0"):
            raw_emi = principal / Decimal(tenure_months)
        else:
            raw_emi = numerator / denominator

        return raw_emi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_total_repayment(emi: Decimal, tenure_months: int) -> Decimal:
        """Calculate total repayment over loan tenure."""
        if emi < Decimal("0"):
            raise ValueError("EMI amount cannot be negative.")
        if tenure_months <= 0:
            raise ValueError("Tenure months must be greater than zero.")

        total = emi * Decimal(tenure_months)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_total_interest(total_repayment: Decimal, principal: Decimal) -> Decimal:
        """Calculate total interest cost."""
        if principal < Decimal("0") or total_repayment < Decimal("0"):
            raise ValueError("Principal and total repayment must be non-negative.")

        interest = total_repayment - principal
        return max(Decimal("0.00"), interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @classmethod
    def calculate_emi_summary(cls, request: EMICalculationRequest) -> EMICalculationResponse:
        """Compute EMI, total repayment, and total interest with labels."""
        emi = cls.calculate_emi(
            principal=request.principal,
            annual_interest_rate=request.annual_interest_rate,
            tenure_months=request.tenure_months,
        )
        total_repayment = cls.calculate_total_repayment(
            emi=emi,
            tenure_months=request.tenure_months,
        )
        total_interest = cls.calculate_total_interest(
            total_repayment=total_repayment,
            principal=request.principal,
        )

        return EMICalculationResponse(
            principal=request.principal,
            annual_interest_rate=request.annual_interest_rate,
            tenure_months=request.tenure_months,
            monthly_emi=emi,
            total_repayment=total_repayment,
            total_interest=total_interest,
            emi_label=f"{format_inr(emi)} / month",
            total_repayment_label=format_inr(total_repayment),
            total_interest_label=format_inr(total_interest),
        )

    @classmethod
    def generate_amortization_schedule(
        cls,
        principal: Decimal,
        annual_interest_rate: Decimal,
        tenure_months: int,
    ) -> AmortizationScheduleResponse:
        """
        Generate detailed yearly amortization breakdown table.
        """
        emi = cls.calculate_emi(principal, annual_interest_rate, tenure_months)
        total_repayment = cls.calculate_total_repayment(emi, tenure_months)
        total_interest = cls.calculate_total_interest(total_repayment, principal)

        r = annual_interest_rate / Decimal("1200")
        current_balance = principal
        yearly_rows: list[AmortizationYearRow] = []

        total_years = (tenure_months + 11) // 12
        month_counter = 0

        for yr in range(1, total_years + 1):
            yr_principal_paid = Decimal("0.00")
            yr_interest_paid = Decimal("0.00")

            months_in_this_year = min(12, tenure_months - month_counter)

            for _ in range(months_in_this_year):
                month_counter += 1
                if annual_interest_rate > Decimal("0"):
                    monthly_interest = (current_balance * r).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                else:
                    monthly_interest = Decimal("0.00")

                monthly_principal = emi - monthly_interest

                # Cap principal payment to remaining balance
                if monthly_principal > current_balance or month_counter == tenure_months:
                    monthly_principal = current_balance

                yr_interest_paid += monthly_interest
                yr_principal_paid += monthly_principal
                current_balance = max(Decimal("0.00"), current_balance - monthly_principal)

            yearly_rows.append(
                AmortizationYearRow(
                    year=yr,
                    principal_paid=yr_principal_paid.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    interest_paid=yr_interest_paid.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    balance_remaining=current_balance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    principal_paid_label=format_inr(yr_principal_paid),
                    interest_paid_label=format_inr(yr_interest_paid),
                    balance_remaining_label=format_inr(current_balance),
                )
            )

        return AmortizationScheduleResponse(
            principal=principal,
            annual_interest_rate=annual_interest_rate,
            tenure_months=tenure_months,
            monthly_emi=emi,
            total_repayment=total_repayment,
            total_interest=total_interest,
            yearly_breakdown=yearly_rows,
        )

    @staticmethod
    def calculate_financial_snapshot(request: FinancialSnapshotRequest) -> FinancialSnapshotMetrics:
        """
        Derive financial snapshot metrics including cash flow, debt obligations, DSCR, and net worth.
        """
        if request.monthly_income <= Decimal("0"):
            raise ValueError("Monthly income must be greater than zero.")

        net_monthly_cash_flow = (
            request.monthly_income - request.monthly_expenses - request.existing_debt_monthly_obligation
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total_monthly_obligations = (
            request.existing_debt_monthly_obligation + request.proposed_emi
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        remaining_cash_flow_post_emi = (
            request.monthly_income - request.monthly_expenses - total_monthly_obligations
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Cash flow impact % = (total_monthly_obligations / monthly_income) * 100
        impact_pct_raw = (total_monthly_obligations / request.monthly_income) * Decimal("100")
        cash_flow_impact_percentage = min(
            Decimal("100.0"),
            impact_pct_raw.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
        )

        # Debt Service Coverage Ratio (DSCR) = (Income - Expenses) / Total Obligations
        available_for_debt = request.monthly_income - request.monthly_expenses
        if total_monthly_obligations > Decimal("0") and available_for_debt > Decimal("0"):
            dscr = (available_for_debt / total_monthly_obligations).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            dscr_label = f"{dscr}x ({'Healthy' if dscr >= Decimal('1.25') else 'Moderate' if dscr >= Decimal('1.0') else 'Strained'} DSCR)"
        else:
            dscr = None
            dscr_label = None

        # Net worth = Assets - Liabilities
        if request.total_assets is not None and request.total_liabilities is not None:
            net_worth = (request.total_assets - request.total_liabilities).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            net_worth = None

        return FinancialSnapshotMetrics(
            monthly_income=request.monthly_income,
            monthly_expenses=request.monthly_expenses,
            existing_debt_monthly_obligation=request.existing_debt_monthly_obligation,
            proposed_emi=request.proposed_emi,
            total_monthly_obligations=total_monthly_obligations,
            net_monthly_cash_flow=net_monthly_cash_flow,
            remaining_cash_flow_post_emi=remaining_cash_flow_post_emi,
            cash_flow_impact_percentage=cash_flow_impact_percentage,
            debt_service_coverage_ratio=dscr,
            total_assets=request.total_assets,
            total_liabilities=request.total_liabilities,
            net_worth=net_worth,
            monthly_income_label=format_inr(request.monthly_income),
            monthly_expenses_label=format_inr(request.monthly_expenses),
            existing_debt_label=format_inr(request.existing_debt_monthly_obligation),
            remaining_cash_flow_post_emi_label=format_inr(remaining_cash_flow_post_emi),
            cash_flow_impact_label=f"{cash_flow_impact_percentage}%",
            dscr_label=dscr_label,
        )

    @classmethod
    def calculate_loan_scenario(cls, req: LoanScenarioRequest) -> LoanScenarioResponse:
        """
        Calculate complete loan scenario matching the frontend component expectations.
        """
        # Convert Lakhs to raw currency if specified
        if req.is_amount_in_lakhs:
            principal = (req.amount * Decimal("100000")).quantize(Decimal("0.01"))
        else:
            principal = req.amount.quantize(Decimal("0.01"))

        tenure_months = req.tenure_years * 12
        rate = req.interest_rate

        # 1. Compute EMI & Repayment
        emi = cls.calculate_emi(principal, rate, tenure_months)
        total_payment = cls.calculate_total_repayment(emi, tenure_months)
        total_interest = cls.calculate_total_interest(total_payment, principal)

        # 2. Derive cash flow impact
        monthly_inc = req.monthly_income if req.monthly_income is not None else Decimal("180000.00")
        monthly_exp = req.monthly_expenses if req.monthly_expenses is not None else Decimal("92000.00")
        existing_d = req.existing_debt if req.existing_debt is not None else Decimal("24000.00")

        snapshot_req = FinancialSnapshotRequest(
            monthly_income=monthly_inc,
            monthly_expenses=monthly_exp,
            existing_debt_monthly_obligation=existing_d,
            proposed_emi=emi,
        )
        snapshot = cls.calculate_financial_snapshot(snapshot_req)

        # 3. Generate Amortization schedule
        amort_res = cls.generate_amortization_schedule(principal, rate, tenure_months)
        amortization_breakdown: list[dict[str, Any]] = [
            {
                "year": row.year,
                "principalPaid": row.principal_paid_label,
                "interestPaid": row.interest_paid_label,
                "balanceRemaining": row.balance_remaining_label,
            }
            for row in amort_res.yearly_breakdown
        ]

        return LoanScenarioResponse(
            emi_label=f"{format_inr(emi)} / month",
            total_repayment_label=format_inr(total_payment),
            total_interest_label=format_inr(total_interest),
            monthly_debt_obligations_label=f"{format_inr(snapshot.total_monthly_obligations)} / month",
            remaining_cash_flow_post_emi_label=format_inr(snapshot.remaining_cash_flow_post_emi),
            cash_flow_impact_percentage=f"{snapshot.cash_flow_impact_percentage}%",
            interest_rate_applied=f"{rate.quantize(Decimal('0.1'))}% p.a. (Indicative)",
            amortization_breakdown=amortization_breakdown,
            disclaimer=(
                "Official interest rates, processing fees, and EMI schedules are subject to "
                "final bank underwriting."
            ),
        )
