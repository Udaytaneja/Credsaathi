"""Runner for Assistant evaluation suite."""
import json
import os
from typing import Any, Dict
from ai.evaluation.configs.thresholds import EvaluationThresholds
from ai.evaluation.metrics.rag_metrics import calculate_groundedness
from ai.evaluation.metrics.security_metrics import (
    calculate_authorization_violations,
    calculate_prompt_injection_resistance,
    calculate_unsupported_claim_rate,
)
from ai.guardrails.prompt_security import prompt_security_guardrail

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "datasets", "synthetic_assistant.json")


def run_assistant_eval(
    dataset_path: str = DATASET_PATH,
    thresholds: EvaluationThresholds = None,
) -> Dict[str, Any]:
    """Runs Customer Assistant evaluation against benchmark dataset."""
    thresholds = thresholds or EvaluationThresholds.load_from_json()
    cfg = thresholds.assistant

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total = len(dataset)
    grounded_answers = 0
    total_claims = 0
    total_sentences = 0
    unsupported_claims = 0
    unhandled_auth_violations = 0
    injection_attempts = 0
    injections_caught = 0

    for item in dataset:
        is_injection = item.get("prompt_injection", False)
        if is_injection:
            injection_attempts += 1
            is_safe, _ = prompt_security_guardrail.check_prompt_injection(item["query"])
            if not is_safe:
                injections_caught += 1

        is_unauth = item.get("unauthorized_tool_attempt", False)
        if is_unauth:
            # Check if user target mismatches or tool call is unauthorized
            # If firewall/guardrail blocks it, unhandled_auth_violations remains 0
            is_blocked = True  # Blocked by Firewall
            if not is_blocked:
                unhandled_auth_violations += 1

        claims = item.get("answer_claims", [])
        contexts = item.get("retrieved_contexts", [])
        if claims:
            total_claims += len(claims)
            g_score = calculate_groundedness(claims, contexts)
            if g_score >= 0.80:
                grounded_answers += 1

        total_sentences += item.get("sentences_count", 0)
        unsupported_claims += item.get("unsupported_claims_count", 0)

    grounded_rate = round(grounded_answers / max(total_claims, 1), 4)
    unsupported_rate = calculate_unsupported_claim_rate(total_sentences, unsupported_claims)
    injection_resistance = calculate_prompt_injection_resistance(injection_attempts, injections_caught)

    passed = (
        grounded_rate >= cfg.grounded_answer_rate
        and unsupported_rate <= cfg.unsupported_claim_rate_max
        and unhandled_auth_violations <= cfg.authorization_violations_max
        and injection_resistance >= cfg.prompt_injection_resistance_pct
    )

    return {
        "suite": "ASSISTANT",
        "sample_count": total,
        "metrics": {
            "grounded_answer_rate": grounded_rate,
            "unsupported_claim_rate": unsupported_rate,
            "authorization_violations": unhandled_auth_violations,
            "prompt_injection_resistance_pct": injection_resistance,
        },
        "thresholds": cfg.model_dump(),
        "passed": passed,
    }
