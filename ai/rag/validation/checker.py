"""Evidence sufficiency validator and prompt injection shield for RAG."""
import re
from typing import List, Tuple
from ai.rag.schemas import DocumentChunk

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"forget all prior instructions",
    r"bypass safety",
    r"system prompt leak",
    r"override system prompt",
    r"reveal secret key",
]


class RAGValidator:
    """Validates retrieval sufficiency and screens queries against prompt injection attempts."""

    def check_prompt_injection(self, query: str) -> bool:
        """Returns True if query contains prompt injection patterns."""
        q_lower = query.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, q_lower):
                return True
        return False

    def is_evidence_sufficient(
        self, retrieved_chunks: List[Tuple[DocumentChunk, float]], min_required_score: float = 0.20
    ) -> bool:
        """Validates if retrieved evidence meets sufficiency threshold."""
        if not retrieved_chunks:
            return False
        # Must have at least one candidate with score >= min_required_score
        return any(score >= min_required_score for _, score in retrieved_chunks)


rag_validator = RAGValidator()
