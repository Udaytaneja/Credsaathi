"""Evaluation harness and synthetic dataset runner for Scheme Matching AI."""
import math
from typing import Any, Dict, List
from ai.matching.service import scheme_matching_service
from ai.schemas.matching import ApplicantContext, CandidateScheme, SchemeMatchRequest, SchemeMatchResult

# Synthetic Evaluation Dataset with Ground Truth (Dummy Data - Zero Real PII)
SYNTHETIC_EVAL_DATASET = [
    {
        "eval_id": "eval_001",
        "description": "Women Entrepreneur Business Scheme Match Test",
        "request": SchemeMatchRequest(
            applicant_context=ApplicantContext(
                applicant_id="dummy_anon_01",
                category="Women",
                state="Maharashtra",
                income_annual=350000.0,
                purpose="Micro business expansion for tailoring shop",
            ),
            candidate_schemes=[
                CandidateScheme(
                    scheme_id="SCH_WOMEN_BIZ_01",
                    scheme_name="Stree Shakti Udyam Scheme",
                    category="Women",
                    description="Financial assistance and micro loans for women entrepreneurs.",
                    eligibility_criteria=["Must be female business owner", "Annual income under 5 Lakhs"],
                    required_documents=["Business Registration", "Aadhaar Card", "Income Certificate"],
                    backend_eligibility_status="ELIGIBLE"
                ),
                CandidateScheme(
                    scheme_id="SCH_AGRI_02",
                    scheme_name="Kisan Tractor Loan Subsidy",
                    category="General",
                    description="Agricultural machinery purchasing subsidy.",
                    eligibility_criteria=["Must own agricultural land"],
                    required_documents=["Land Record Document"],
                    backend_eligibility_status="PARTIAL"
                )
            ]
        ),
        "expected_top_scheme_id": "SCH_WOMEN_BIZ_01",
        "expected_eligible_count": 1
    }
]


class SchemeMatchingEvaluator:
    """Calculates evaluation metrics: Precision@K, Recall@K, Ranking Correctness, Eligibility Consistency."""

    async def evaluate_dataset(
        self, dataset: List[Dict[str, Any]] = SYNTHETIC_EVAL_DATASET, k: int = 1
    ) -> Dict[str, float]:
        """Runs evaluation over the benchmark dataset and returns summary metric scores."""
        total_evals = len(dataset)
        precision_sum = 0.0
        recall_sum = 0.0
        ranking_correct = 0
        eligibility_consistent = 0
        prohibited_claim_violations = 0

        for item in dataset:
            req: SchemeMatchRequest = item["request"]
            expected_top_id: str = item["expected_top_scheme_id"]

            res = await scheme_matching_service.match_schemes(req)
            matches: List[SchemeMatchResult] = res.matches

            if not matches:
                continue

            top_k_ids = [m.scheme_id for m in matches[:k]]

            # Precision@K
            hits = 1.0 if expected_top_id in top_k_ids else 0.0
            precision_sum += hits / k

            # Recall@K
            recall_sum += hits

            # Ranking Correctness (Is expected top candidate ranked first?)
            if matches[0].scheme_id == expected_top_id:
                ranking_correct += 1

            # Eligibility Consistency Check (AI eligibility status matches backend status)
            backend_map = {c.scheme_id: c.backend_eligibility_status for c in req.candidate_schemes}
            consistent = all(m.eligibility_status == backend_map.get(m.scheme_id) for m in matches)
            if consistent:
                eligibility_consistent += 1

            # Check for prohibited terms in explanations
            for m in matches:
                exp_lower = m.explanation.lower()
                if "approval probability" in exp_lower or "guaranteed eligibility" in exp_lower:
                    prohibited_claim_violations += 1

        metrics = {
            f"precision@{k}": round(precision_sum / total_evals, 4),
            f"recall@{k}": round(recall_sum / total_evals, 4),
            "ranking_correctness_pct": round((ranking_correct / total_evals) * 100.0, 2),
            "eligibility_consistency_pct": round((eligibility_consistent / total_evals) * 100.0, 2),
            "prohibited_claim_violations_count": float(prohibited_claim_violations),
        }
        return metrics


evaluator = SchemeMatchingEvaluator()
