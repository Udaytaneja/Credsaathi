"""Runner for Financial AI evaluation suite."""
import json
import os
from typing import Any, Dict
from ai.evaluation.configs.thresholds import EvaluationThresholds
from ai.evaluation.metrics.financial_metrics import calculate_backend_consistency

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "synthetic_financial_ai.json")


def run_financial_ai_eval(
    dataset_path: str = DATASET_PATH,
    thresholds: EvaluationThresholds = None,
) -> Dict[str, Any]:
    """Runs Financial AI consistency evaluation against deterministic reference values."""
    thresholds = thresholds or EvaluationThresholds.load_from_json()
    cfg = thresholds.financial_ai

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    consistency_sum = 0.0

    for item in dataset:
        c_score = calculate_backend_consistency(item["ai_calculated_values"], item["reference_values"])
        consistency_sum += c_score

    avg_consistency = round(consistency_sum / total, 4) if total > 0 else 0.0
    passed = avg_consistency >= cfg.backend_consistency_rate

    return {
        "suite": "FINANCIAL_AI",
        "sample_count": total,
        "metrics": {
            "backend_consistency_rate": avg_consistency,
        },
        "thresholds": cfg.model_dump(),
        "passed": passed,
    }
