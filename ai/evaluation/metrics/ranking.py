"""Ranking metrics: Precision@K, Recall@K, and Ranking Correctness."""
from typing import List


def calculate_precision_at_k(actual_rankings: List[str], expected_ids: List[str], k: int = 1) -> float:
    """Calculates Precision@K for candidate rankings against expected IDs."""
    if not actual_rankings or k <= 0:
        return 0.0

    top_k = actual_rankings[:k]
    hits = sum(1 for item in top_k if item in expected_ids)
    return round(hits / k, 4)


def calculate_recall_at_k(actual_rankings: List[str], expected_ids: List[str], k: int = 1) -> float:
    """Calculates Recall@K for candidate rankings against expected IDs."""
    if not expected_ids or k <= 0:
        return 0.0

    top_k = actual_rankings[:k]
    hits = sum(1 for item in top_k if item in expected_ids)
    return round(hits / len(expected_ids), 4)


def calculate_ranking_correctness(actual_top: str, expected_top: str) -> bool:
    """Checks if top ranked item matches expected top ground-truth ID."""
    if not actual_top or not expected_top:
        return False
    return actual_top == expected_top
