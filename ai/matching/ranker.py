"""Deterministic & Semantic Ranking Engine for candidate schemes."""
import re
from typing import List, Tuple
from ai.schemas.matching import ApplicantContext, CandidateScheme


class SchemeRanker:
    """Computes semantic relevance scores (0.0 to 1.0) for pre-filtered candidate schemes."""

    def compute_relevance_score(
        self, applicant: ApplicantContext, candidate: CandidateScheme
    ) -> float:
        """Computes semantic relevance score between applicant context and candidate scheme.

        NOTE: This relevance_score reflects text/attribute match fit, NOT credit score,
        approval probability, or guaranteed approval.
        """
        score = 0.5  # Base candidate score (since pre-filtered as candidate by backend)

        # 1. Purpose match bonus
        if applicant.purpose:
            purpose_tokens = set(re.findall(r"\w+", applicant.purpose.lower()))
            scheme_text = (candidate.scheme_name + " " + candidate.description).lower()
            scheme_tokens = set(re.findall(r"\w+", scheme_text))
            intersection = purpose_tokens.intersection(scheme_tokens)
            if intersection:
                match_ratio = len(intersection) / max(len(purpose_tokens), 1)
                score += min(match_ratio * 0.25, 0.25)

        # 2. Category / Target demographic match
        if applicant.category and candidate.category:
            if applicant.category.lower() in candidate.category.lower() or candidate.category.lower() == "general":
                score += 0.1

        # 3. Backend status weighting (Backend status is source of truth)
        status_upper = candidate.backend_eligibility_status.upper()
        if status_upper == "ELIGIBLE":
            score += 0.15
        elif status_upper == "PARTIAL":
            score += 0.05
        elif status_upper == "NEEDS_INFO":
            score += 0.0

        # Cap score between 0.05 and 0.99 (Never 1.0 / guarantee)
        final_score = round(min(max(score, 0.05), 0.99), 2)
        return final_score

    def rank_candidates(
        self, applicant: ApplicantContext, candidates: List[CandidateScheme]
    ) -> List[Tuple[CandidateScheme, float]]:
        """Ranks candidates in descending order of semantic relevance score."""
        scored_candidates = []
        for candidate in candidates:
            rel_score = self.compute_relevance_score(applicant, candidate)
            scored_candidates.append((candidate, rel_score))

        # Sort by relevance score descending
        scored_candidates.sort(key=lambda item: item[1], reverse=True)
        return scored_candidates


ranker = SchemeRanker()
