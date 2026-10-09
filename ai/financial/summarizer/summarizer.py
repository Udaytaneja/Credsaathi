"""Financial Summarizer preserving backend numeric data without recalculation."""
from typing import List, Tuple
from ai.financial.schemas.financial import FinancialProfileInput


class FinancialSummarizer:
    """Extracts facts, data gaps, and objective observations while preserving numeric values."""

    def extract_key_facts(self, profile: FinancialProfileInput) -> List[str]:
        """Preserves exact numeric values provided by backend."""
        facts = []
        if profile.validated_income is not None:
            facts.append(f"Validated Income: {profile.currency} {profile.validated_income:,.2f}")
        if profile.turnover is not None:
            facts.append(f"Business Turnover: {profile.currency} {profile.turnover:,.2f}")
        if profile.revenue is not None:
            facts.append(f"Annual Revenue: {profile.currency} {profile.revenue:,.2f}")
        if profile.expenses is not None:
            facts.append(f"Reported Expenses: {profile.currency} {profile.expenses:,.2f}")
        if profile.existing_liabilities is not None:
            facts.append(f"Existing Debt/Liabilities: {profile.currency} {profile.existing_liabilities:,.2f}")
        if profile.loan_requirement is not None:
            facts.append(f"Requested Loan Requirement: {profile.currency} {profile.loan_requirement:,.2f}")
        if profile.existing_loans:
            facts.append(f"Active Loans Count: {len(profile.existing_loans)}")
        return facts

    def identify_data_gaps(self, profile: FinancialProfileInput) -> List[str]:
        """Identifies missing financial profile attributes."""
        gaps = []
        if profile.validated_income is None and profile.turnover is None:
            gaps.append("Missing verified income or business turnover data.")
        if profile.expenses is None:
            gaps.append("Missing annual/monthly expenses data.")
        if profile.repayment_information is None:
            gaps.append("Missing historical repayment track record.")
        if profile.cash_flow_information is None:
            gaps.append("Missing cash flow summary data.")
        return gaps

    def generate_observations(self, profile: FinancialProfileInput) -> Tuple[List[str], List[str]]:
        """Generates objective observations and preparation steps without making decisioning claims."""
        observations = []
        prep_guidance = []

        if profile.validated_income and profile.existing_liabilities:
            observations.append(
                f"Outstanding liabilities represent {profile.currency} {profile.existing_liabilities:,.2f} "
                f"against annual validated income of {profile.currency} {profile.validated_income:,.2f}."
            )

        if profile.cash_flow_information:
            observations.append(f"Cash flow track record: {profile.cash_flow_information}")
        else:
            prep_guidance.append("Provide 6-month bank account statement to establish cash flow history.")

        if profile.loan_requirement and profile.validated_income:
            prep_guidance.append("Prepare proof of income and tax returns matching the requested loan amount.")

        return observations, prep_guidance


summarizer = FinancialSummarizer()
