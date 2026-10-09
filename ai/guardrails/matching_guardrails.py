"""Guardrails and safety checks for Scheme Matching AI outputs."""
import re
from typing import List
from ai.schemas.matching import CandidateScheme, SchemeMatchResult
from ai.utils.logging import logger

PROHIBITED_TERMS = [
    r"approval probability",
    r"credit score",
    r"risk score",
    r"guaranteed eligibility",
    r"guaranteed approval",
    r"100% approval",
    r"100% eligible",
    r"guarantee approval",
]


class SchemeMatchingGuardrail:
    """Enforces financial compliance and grounding on scheme match results."""

    def sanitize_explanation(self, text: str) -> str:
        """Removes or replaces non-compliant financial claim phrases from explanation text."""
        sanitized = text
        for pattern in PROHIBITED_TERMS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Guardrail caught prohibited term pattern '{pattern}' in explanation text.")
                sanitized = re.sub(
                    pattern,
                    "compatibility score",
                    sanitized,
                    flags=re.IGNORECASE
                )

        return sanitized

    def validate_and_guard_results(
        self, candidate_schemes: List[CandidateScheme], results: List[SchemeMatchResult]
    ) -> List[SchemeMatchResult]:
        """Validates that match results align strictly with ground-truth candidate schemes."""
        allowed_ids = {c.scheme_id for c in candidate_schemes}
        guarded_results: List[SchemeMatchResult] = []

        for result in results:
            # 1. Verification: Ensure scheme_id belongs to candidate list (no hallucinated schemes)
            if result.scheme_id not in allowed_ids:
                logger.error(f"Guardrail rejected hallucinated scheme ID: {result.scheme_id}")
                continue

            # 2. Sanitize explanation
            clean_exp = self.sanitize_explanation(result.explanation)

            # 3. Sanitize match reasons
            clean_reasons = [self.sanitize_explanation(r) for r in result.match_reasons]

            # 4. Enforce relevance_score bounds (0.0 to 0.99)
            bounded_score = round(min(max(result.relevance_score, 0.0), 0.99), 2)

            result.explanation = clean_exp
            result.match_reasons = clean_reasons
            result.relevance_score = bounded_score
            guarded_results.append(result)

        return guarded_results


matching_guardrail = SchemeMatchingGuardrail()
