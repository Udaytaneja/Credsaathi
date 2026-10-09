"""Unit tests for CredSaathi Financial Intelligence MVP."""
import pytest
from ai.financial.explanation.generator import explanation_generator
from ai.financial.schemas.financial import FinancialProfileInput
from ai.financial.summarizer.summarizer import summarizer


def test_numeric_preservation():
    profile = FinancialProfileInput(
        validated_income=600000.0,
        turnover=1500000.0,
        revenue=1400000.0,
        expenses=400000.0,
        existing_liabilities=200000.0,
        loan_requirement=500000.0,
        currency="INR"
    )

    facts = summarizer.extract_key_facts(profile)

    assert any("600,000.00" in f for f in facts)
    assert any("1,500,000.00" in f for f in facts)
    assert any("200,000.00" in f for f in facts)


def test_data_gap_detection():
    profile = FinancialProfileInput(
        validated_income=500000.0,
        # Missing expenses, repayment history, cash flow
    )

    gaps = summarizer.identify_data_gaps(profile)

    assert any("expenses" in g for g in gaps)
    assert any("repayment track record" in g for g in gaps)
    assert any("cash flow" in g for g in gaps)


@pytest.mark.asyncio
async def test_financial_explanation_consistency_and_guardrails():
    profile = FinancialProfileInput(
        validated_income=750000.0,
        existing_liabilities=150000.0,
        loan_requirement=300000.0
    )

    res1 = await explanation_generator.generate_explanation(profile)
    res2 = await explanation_generator.generate_explanation(profile)

    # Identical backend inputs produce consistent outputs
    assert res1.key_facts == res2.key_facts
    assert res1.source == "backend_validated_data"
    assert res1.source == res2.source

    # Check guardrails: zero credit score or credit approval decision claims
    summary_lower = res1.summary.lower()
    assert "credit score" not in summary_lower
    assert "credit approval" not in summary_lower
    assert "loan rejection" not in summary_lower
