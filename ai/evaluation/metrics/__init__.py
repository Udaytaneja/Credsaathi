"""Evaluation metrics package."""
from ai.evaluation.metrics.financial_metrics import calculate_backend_consistency
from ai.evaluation.metrics.rag_metrics import (
    calculate_citation_correctness,
    calculate_groundedness,
    calculate_hallucination_rate,
    calculate_retrieval_relevance,
)
from ai.evaluation.metrics.ranking import (
    calculate_precision_at_k,
    calculate_ranking_correctness,
    calculate_recall_at_k,
)
from ai.evaluation.metrics.security_metrics import (
    calculate_authorization_violations,
    calculate_prompt_injection_resistance,
    calculate_unsupported_claim_rate,
)
from ai.evaluation.metrics.text_accuracy import (
    calculate_character_error_rate,
    calculate_expected_calibration_error,
    calculate_field_extraction_accuracy,
)

__all__ = [
    "calculate_precision_at_k",
    "calculate_recall_at_k",
    "calculate_ranking_correctness",
    "calculate_character_error_rate",
    "calculate_field_extraction_accuracy",
    "calculate_expected_calibration_error",
    "calculate_retrieval_relevance",
    "calculate_groundedness",
    "calculate_citation_correctness",
    "calculate_hallucination_rate",
    "calculate_backend_consistency",
    "calculate_prompt_injection_resistance",
    "calculate_authorization_violations",
    "calculate_unsupported_claim_rate",
]
