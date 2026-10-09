"""Source grounding, hallucination prevention, and untrusted source guardrails."""
from typing import Any, Dict, List, Optional
from ai.utils.logging import logger

FALLBACK_INSUFFICIENT_EVIDENCE = "Insufficient verified information to answer this."


class GroundingGuardrail:
    """Enforces evidence grounding, source trust verification, and hallucination guardrails."""

    def __init__(self, approved_domains: Optional[List[str]] = None):
        self.approved_domains = approved_domains or [
            "gov.in",
            "nic.in",
            "credsaathi.in",
            "rbi.org.in",
            "nabard.org",
            "psbloansin59minutes.com",
            "standupmitra.in",
        ]

    def validate_grounding(
        self,
        query: str,
        retrieved_contexts: List[str],
        confidence_score: float = 1.0,
        min_context_count: int = 1,
        min_confidence: float = 0.5,
    ) -> bool:
        """Validates that query has sufficient ground-truth context to answer safely."""
        if not retrieved_contexts or len(retrieved_contexts) < min_context_count:
            logger.warning("[GROUNDING_GUARDRAIL] Insufficient context count retrieved for query.")
            return False

        if confidence_score < min_confidence:
            logger.warning(
                f"[GROUNDING_GUARDRAIL] Context retrieval confidence ({confidence_score}) below threshold ({min_confidence})."
            )
            return False

        # Ensure retrieved context is not empty or white space
        valid_contexts = [c for c in retrieved_contexts if c and c.strip()]
        if not valid_contexts:
            logger.warning("[GROUNDING_GUARDRAIL] All retrieved contexts were empty.")
            return False

        return True

    def get_grounded_response_or_fallback(
        self,
        response_text: str,
        retrieved_contexts: List[str],
        confidence_score: float = 1.0,
    ) -> str:
        """Returns model response if properly grounded, or the standard insufficient evidence fallback."""
        if not self.validate_grounding(query="", retrieved_contexts=retrieved_contexts, confidence_score=confidence_score):
            return FALLBACK_INSUFFICIENT_EVIDENCE

        return response_text

    def is_source_trusted(self, source_url_or_domain: str) -> bool:
        """Checks if a source URI or domain is in the approved trust list."""
        if not source_url_or_domain:
            return False

        lower_src = source_url_or_domain.lower()
        for domain in self.approved_domains:
            if domain in lower_src:
                return True

        logger.warning(f"[GROUNDING_GUARDRAIL] Untrusted source detected: '{source_url_or_domain}'")
        return False

    def filter_untrusted_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters out citations or sources from untrusted origins."""
        trusted_sources = []
        for src in sources:
            uri = src.get("uri", "") or src.get("source_url", "") or src.get("title", "")
            if self.is_source_trusted(uri):
                trusted_sources.append(src)
            else:
                logger.info(f"[GROUNDING_GUARDRAIL] Filtered out untrusted source entry: {src}")

        return trusted_sources


grounding_guardrail = GroundingGuardrail()
