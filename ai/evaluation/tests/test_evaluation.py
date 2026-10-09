"""Unit tests for CredSaathi AI Evaluation Framework."""
import os
import pytest
from ai.evaluation.configs.thresholds import EvaluationThresholds
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
from ai.evaluation.runners.assistant_runner import run_assistant_eval
from ai.evaluation.runners.document_ai_runner import run_document_ai_eval
from ai.evaluation.runners.financial_ai_runner import run_financial_ai_eval
from ai.evaluation.runners.rag_runner import run_rag_eval
from ai.evaluation.runners.run_all_evals import run_all_evaluations
from ai.evaluation.runners.scheme_matching_runner import run_scheme_matching_eval


def test_1_threshold_config_loading():
    cfg = EvaluationThresholds.load_from_json()
    assert cfg.scheme_matching.precision_at_k == 0.80
    assert cfg.document_ai.field_extraction_accuracy == 0.85
    assert cfg.rag.groundedness_rate == 0.85
    assert cfg.financial_ai.backend_consistency_rate == 0.95
    assert cfg.assistant.prompt_injection_resistance_pct == 95.0


def test_2_ranking_metrics():
    actual = ["sch_1", "sch_2", "sch_3"]
    expected = ["sch_1"]

    assert calculate_precision_at_k(actual, expected, k=1) == 1.0
    assert calculate_recall_at_k(actual, expected, k=1) == 1.0
    assert calculate_ranking_correctness(actual[0], expected[0]) is True


def test_3_text_accuracy_and_cer():
    cer = calculate_character_error_rate("PAN ABCDE1234F", "PAN ABCDE1234F")
    assert cer == 0.0

    cer_diff = calculate_character_error_rate("ABCDE1234F", "ABCDE1234X")
    assert cer_diff > 0.0

    acc = calculate_field_extraction_accuracy({"name": "RAMESH"}, {"name": "RAMESH"})
    assert acc == 1.0

    ece = calculate_expected_calibration_error([0.9, 0.8], [1.0, 1.0])
    assert ece >= 0.0


def test_4_rag_metrics():
    rel = calculate_retrieval_relevance(["chunk_1"], ["chunk_1", "chunk_2"])
    assert rel == 1.0

    groundedness = calculate_groundedness(["Mudra scheme limit is 10 lakhs"], ["Mudra scheme limit is 10 lakhs"])
    assert groundedness == 1.0

    hallucination = calculate_hallucination_rate(groundedness)
    assert hallucination == 0.0


def test_5_financial_and_security_metrics():
    consistency = calculate_backend_consistency({"emi": 5000}, {"emi": 5000})
    assert consistency == 1.0

    injection_pct = calculate_prompt_injection_resistance(10, 10)
    assert injection_pct == 100.0


def test_6_evaluation_runners():
    sm_res = run_scheme_matching_eval()
    assert sm_res["passed"] is True

    doc_res = run_document_ai_eval()
    assert doc_res["passed"] is True

    rag_res = run_rag_eval()
    assert rag_res["passed"] is True

    fin_res = run_financial_ai_eval()
    assert fin_res["passed"] is True

    asst_res = run_assistant_eval()
    assert asst_res["passed"] is True


def test_7_master_runner_execution(tmp_path):
    report = run_all_evaluations(output_dir=str(tmp_path))
    assert report["overall_status"] == "PASSED"
    assert os.path.exists(os.path.join(tmp_path, "eval_results.json"))
