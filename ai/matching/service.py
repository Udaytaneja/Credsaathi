"""Scheme Matching Orchestration Service combining ranker, explainer, and guardrails."""
from ai.guardrails.matching_guardrails import matching_guardrail
from ai.matching.explainer import explainer
from ai.matching.ranker import ranker
from ai.schemas.matching import SchemeMatchRequest, SchemeMatchResponseData


class SchemeMatchingService:
    """Orchestrates candidate scheme ranking, natural language explanations, missing info detection, and safety guardrails."""

    async def match_schemes(self, request: SchemeMatchRequest) -> SchemeMatchResponseData:
        # 1. Deterministic/Semantic Ranking
        ranked_candidates = ranker.rank_candidates(
            applicant=request.applicant_context,
            candidates=request.candidate_schemes
        )

        # 2. Explanation Generation & Missing Information Identification
        raw_results = await explainer.generate_explanations(
            applicant=request.applicant_context,
            ranked_candidates=ranked_candidates,
            language=request.language
        )

        # 3. Guardrail & Compliance Enforcement
        guarded_results = matching_guardrail.validate_and_guard_results(
            candidate_schemes=request.candidate_schemes,
            results=raw_results
        )

        return SchemeMatchResponseData(matches=guarded_results)


scheme_matching_service = SchemeMatchingService()
