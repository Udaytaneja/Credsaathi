"""Subfolder test suite for Financial Intelligence module."""
import pytest
from ai.financial.explanation.generator import explanation_generator
from ai.financial.schemas.financial import FinancialProfileInput
from ai.financial.summarizer.summarizer import summarizer


def test_numeric_preservation_subfolder():
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


@pytest.mark.asyncio
async def test_financial_explanation_subfolder():
    profile = FinancialProfileInput(
        validated_income=750000.0,
        existing_liabilities=150000.0,
        loan_requirement=300000.0
    )

    res = await explanation_generator.generate_explanation(profile)
    assert res.source == "backend_validated_data"
    assert "credit score" not in res.summary.lower()
