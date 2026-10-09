"""Unit tests for Scheme Matching AI (ranker, explainer, guardrails, evaluation)."""
import pytest
from ai.evaluation.matching_eval import evaluator
from ai.guardrails.matching_guardrails import matching_guardrail
from ai.matching.ranker import ranker
from ai.matching.service import scheme_matching_service
from ai.schemas.matching import ApplicantContext, CandidateScheme, SchemeMatchRequest, SchemeMatchResult


def test_scheme_ranker_relevance_score_bounds():
    applicant = ApplicantContext(purpose="Higher Education Abroad", category="General")
    candidate = CandidateScheme(
        scheme_id="SCH_EDU_01",
        scheme_name="Global Education Scholar Loan",
        description="Education loans for studying abroad",
        backend_eligibility_status="ELIGIBLE"
    )

    score = ranker.compute_relevance_score(applicant, candidate)

    assert 0.0 <= score <= 0.99
    # Score should be elevated due to purpose match and backend ELIGIBLE status
    assert score >= 0.70


def test_guardrails_prohibited_terms_redaction():
    text_with_prohibited = "This scheme guarantees 100% approval and improves your credit score."
    clean_text = matching_guardrail.sanitize_explanation(text_with_prohibited)

    assert "100% approval" not in clean_text
    assert "credit score" not in clean_text
    assert "compatibility score" in clean_text


def test_guardrail_filters_hallucinated_schemes():
    valid_candidates = [
        CandidateScheme(scheme_id="VALID_01", scheme_name="Valid Scheme", description="Desc")
    ]
    raw_results = [
        SchemeMatchResult(
            scheme_id="VALID_01",
            scheme_name="Valid Scheme",
            relevance_score=0.8,
            eligibility_status="ELIGIBLE",
            source_reference="Ref",
            last_verified="2026-10-01",
            explanation="Exp"
        ),
        SchemeMatchResult(
            scheme_id="HALLUCINATED_99",
            scheme_name="Fake Scheme",
            relevance_score=0.95,
            eligibility_status="ELIGIBLE",
            source_reference="Fake",
            last_verified="2026-10-01",
            explanation="Fake Exp"
        )
    ]

    guarded = matching_guardrail.validate_and_guard_results(valid_candidates, raw_results)
    assert len(guarded) == 1
    assert guarded[0].scheme_id == "VALID_01"


@pytest.mark.asyncio
async def test_matching_service_execution():
    req = SchemeMatchRequest(
        applicant_context=ApplicantContext(purpose="Business Growth", category="General"),
        candidate_schemes=[
            CandidateScheme(
                scheme_id="BIZ_01",
                scheme_name="Mudra Business Loan",
                description="Loans for small businesses",
                backend_eligibility_status="ELIGIBLE",
                required_documents=["GST Certificate"]
            )
        ]
    )

    resp = await scheme_matching_service.match_schemes(req)
    assert len(resp.matches) == 1
    m = resp.matches[0]
    assert m.scheme_id == "BIZ_01"
    assert m.relevance_score > 0.5
    assert len(m.missing_information) >= 1
    assert "Upload document: GST Certificate" in m.missing_information[0]


@pytest.mark.asyncio
async def test_matching_evaluator_harness():
    metrics = await evaluator.evaluate_dataset()
    assert "precision@1" in metrics
    assert metrics["precision@1"] == 1.0
    assert metrics["eligibility_consistency_pct"] == 100.0
    assert metrics["prohibited_claim_violations_count"] == 0.0
