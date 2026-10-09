"""RAG evaluation metrics: Retrieval Relevance, Groundedness, Citation Correctness, and Hallucination Rate."""
from typing import List


def calculate_retrieval_relevance(retrieved_chunk_ids: List[str], relevant_chunk_ids: List[str]) -> float:
    """Calculates retrieval relevance ratio of retrieved chunks against ground truth relevant chunks."""
    if not retrieved_chunk_ids:
        return 0.0
    if not relevant_chunk_ids:
        return 1.0

    relevant_retrieved = sum(1 for cid in retrieved_chunk_ids if cid in relevant_chunk_ids)
    return round(relevant_retrieved / len(retrieved_chunk_ids), 4)


def calculate_groundedness(answer_claims: List[str], retrieved_contexts: List[str]) -> float:
    """Calculates groundedness score (ratio of answer claims backed by retrieved context)."""
    if not answer_claims:
        return 1.0
    if not retrieved_contexts:
        return 0.0

    combined_context = " ".join(retrieved_contexts).lower()
    grounded_claims = 0

    for claim in answer_claims:
        # Check substring keywords presence
        keywords = [w.lower() for w in claim.split() if len(w) > 3]
        if not keywords or any(kw in combined_context for kw in keywords):
            grounded_claims += 1

    return round(grounded_claims / len(answer_claims), 4)


def calculate_citation_correctness(citations: List[str], valid_source_ids: List[str]) -> float:
    """Calculates citation correctness ratio for generated citations."""
    if not citations:
        return 1.0
    if not valid_source_ids:
        return 0.0

    valid_count = sum(1 for c in citations if c in valid_source_ids)
    return round(valid_count / len(citations), 4)


def calculate_hallucination_rate(groundedness_score: float) -> float:
    """Calculates hallucination rate as inverse of groundedness score."""
    return round(max(0.0, 1.0 - groundedness_score), 4)
