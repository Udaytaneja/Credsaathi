"""Repeatable Master Evaluation Runner for CredSaathi AI Layer."""
import json
import os
import sys
import time
from typing import Any, Dict
from ai.evaluation.configs.thresholds import EvaluationThresholds
from ai.evaluation.runners.assistant_runner import run_assistant_eval
from ai.evaluation.runners.document_ai_runner import run_document_ai_eval
from ai.evaluation.runners.financial_ai_runner import run_financial_ai_eval
from ai.evaluation.runners.rag_runner import run_rag_eval
from ai.evaluation.runners.scheme_matching_runner import run_scheme_matching_eval
from ai.utils.logging import logger

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")


def run_all_evaluations(output_dir: str = REPORTS_DIR) -> Dict[str, Any]:
    """Runs all AI evaluation suites and saves machine-readable report."""
    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()
    thresholds = EvaluationThresholds.load_from_json()

    suite_results = {
        "SCHEME_MATCHING": run_scheme_matching_eval(thresholds=thresholds),
        "DOCUMENT_AI": run_document_ai_eval(thresholds=thresholds),
        "RAG": run_rag_eval(thresholds=thresholds),
        "FINANCIAL_AI": run_financial_ai_eval(thresholds=thresholds),
        "ASSISTANT": run_assistant_eval(thresholds=thresholds),
    }

    all_passed = all(s["passed"] for s in suite_results.values())
    total_duration_ms = round((time.time() - start_time) * 1000, 2)

    master_report = {
        "timestamp": int(time.time()),
        "total_duration_ms": total_duration_ms,
        "overall_status": "PASSED" if all_passed else "FAILED",
        "dataset_notice": "Evaluation executed on synthetic benchmark datasets. Do not claim production readiness based on synthetic data alone.",
        "suites": suite_results,
    }

    report_path = os.path.join(output_dir, "eval_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(master_report, f, indent=2)

    print_human_readable_summary(master_report)
    logger.info(f"[EVALUATION_FINISHED] Saved machine-readable evaluation report to '{report_path}'")
    return master_report


def print_human_readable_summary(report: Dict[str, Any]) -> None:
    """Prints formatted ASCII summary table of evaluation results to stdout."""
    print("\n" + "=" * 70)
    print("           CredSaathi AI Quality Evaluation Summary")
    print("=" * 70)
    print(f"Overall Status   : {report['overall_status']}")
    print(f"Total Latency    : {report['total_duration_ms']} ms")
    print(f"Notice           : {report['dataset_notice']}")
    print("-" * 70)
    print(f"{'Suite Name':<20} | {'Status':<8} | {'Key Metric Summary'}")
    print("-" * 70)

    for suite_name, data in report["suites"].items():
        status = "PASSED" if data["passed"] else "FAILED"
        metrics_summary = ", ".join(f"{k}={v}" for k, v in list(data["metrics"].items())[:2])
        print(f"{suite_name:<20} | {status:<8} | {metrics_summary}")

    print("=" * 70 + "\n")


if __name__ == "__main__":
    report = run_all_evaluations()
    if report["overall_status"] != "PASSED":
        sys.exit(1)
