"""Runner for RAG evaluation suite."""
import json
import os
from typing import Any, Dict
from ai.evaluation.configs.thresholds import EvaluationThresholds
from ai.evaluation.metrics.rag_metrics import (
    calculate_citation_correctness,
    calculate_groundedness,
    calculate_hallucination_rate,
    calculate_retrieval_relevance,
)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "synthetic_rag.json")


def run_rag_eval(
    dataset_path: str = DATASET_PATH,
    thresholds: EvaluationThresholds = None,
) -> Dict[str, Any]:
    """Runs RAG evaluation against benchmark dataset."""
    thresholds = thresholds or EvaluationThresholds.load_from_json()
    cfg = thresholds.rag

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    rel_sum = 0.0
    ground_sum = 0.0
    cite_sum = 0.0

    for item in dataset:
        rel = calculate_retrieval_relevance(item["retrieved_chunk_ids"], item["expected_relevant_chunk_ids"])
        ground = calculate_groundedness(item["model_answer_claims"], item["retrieved_contexts"])
        cite = calculate_citation_correctness(item["generated_citations"], item["valid_source_ids"])

        rel_sum += rel
        ground_sum += ground
        cite_sum += cite

    avg_rel = round(rel_sum / total, 4) if total > 0 else 0.0
    avg_ground = round(ground_sum / total, 4) if total > 0 else 0.0
    avg_cite = round(cite_sum / total, 4) if total > 0 else 0.0
    hallucination_rate = calculate_hallucination_rate(avg_ground)

    passed = (
        avg_rel >= cfg.retrieval_relevance
        and avg_ground >= cfg.groundedness_rate
        and avg_cite >= cfg.citation_correctness
        and hallucination_rate <= cfg.hallucination_rate_max
    )

    return {
        "suite": "RAG",
        "sample_count": total,
        "metrics": {
            "retrieval_relevance": avg_rel,
            "groundedness_rate": avg_ground,
            "citation_correctness": avg_cite,
            "hallucination_rate": hallucination_rate,
        },
        "thresholds": cfg.model_dump(),
        "passed": passed,
    }
