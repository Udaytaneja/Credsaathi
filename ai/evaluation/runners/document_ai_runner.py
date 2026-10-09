"""Runner for Document AI evaluation suite."""
import json
import os
from typing import Any, Dict
from ai.evaluation.configs.thresholds import EvaluationThresholds
from ai.evaluation.metrics.text_accuracy import (
    calculate_character_error_rate,
    calculate_expected_calibration_error,
    calculate_field_extraction_accuracy,
)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "synthetic_document_ai.json")


def run_document_ai_eval(
    dataset_path: str = DATASET_PATH,
    thresholds: EvaluationThresholds = None,
) -> Dict[str, Any]:
    """Runs Document AI evaluation against benchmark dataset."""
    thresholds = thresholds or EvaluationThresholds.load_from_json()
    cfg = thresholds.document_ai

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    acc_sum = 0.0
    cer_sum = 0.0
    confidences = []
    accuracies = []

    for item in dataset:
        acc = calculate_field_extraction_accuracy(item["model_extracted_fields"], item["expected_extracted_fields"])
        cer = calculate_character_error_rate(item["expected_ocr_text"], item["raw_ocr_text"])

        acc_sum += acc
        cer_sum += cer

        conf = item.get("model_confidence", 0.90)
        confidences.append(conf)
        accuracies.append(acc)

    avg_acc = round(acc_sum / total, 4) if total > 0 else 0.0
    avg_cer = round(cer_sum / total, 4) if total > 0 else 0.0
    ece = calculate_expected_calibration_error(confidences, accuracies)

    passed = (
        avg_acc >= cfg.field_extraction_accuracy
        and avg_cer <= cfg.character_error_rate_max
        and ece <= cfg.confidence_calibration_ece_max
    )

    return {
        "suite": "DOCUMENT_AI",
        "sample_count": total,
        "metrics": {
            "field_extraction_accuracy": avg_acc,
            "ocr_quality": round(1.0 - avg_cer, 4),
            "character_error_rate": avg_cer,
            "validation_accuracy": avg_acc,
            "confidence_calibration_ece": ece,
        },
        "thresholds": cfg.model_dump(),
        "passed": passed,
    }
