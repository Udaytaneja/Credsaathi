"""LLM-assisted Explanation and Missing Information Generator grounded in candidate schemes."""
import json
from typing import List, Tuple
from ai.model_router.gateway import model_gateway
from ai.schemas.matching import ApplicantContext, CandidateScheme, SchemeMatchResult
from ai.schemas.model_gateway import ModelRequest, TaskType
from ai.utils.logging import logger


class SchemeExplainer:
    """Generates natural language match explanations and missing-information lists using Model Gateway."""

    async def generate_explanations(
        self,
        applicant: ApplicantContext,
        ranked_candidates: List[Tuple[CandidateScheme, float]],
        language: str = "en"
    ) -> List[SchemeMatchResult]:
        """Generates grounded explanations for ranked scheme candidates."""
        results: List[SchemeMatchResult] = []

        for candidate, relevance_score in ranked_candidates:
            # Build missing information list deterministically from required documents & missing attributes
            missing_info = self._identify_missing_information(applicant, candidate)

            # Build grounded prompt for explanation generation
            prompt = (
                f"Applicant Profile: Category={applicant.category}, State={applicant.state}, "
                f"Income={applicant.income_annual}, Purpose={applicant.purpose}\n"
                f"Scheme Name: {candidate.scheme_name}\n"
                f"Scheme Description: {candidate.description}\n"
                f"Eligibility Criteria: {', '.join(candidate.eligibility_criteria)}\n"
                f"Required Documents: {', '.join(candidate.required_documents)}\n"
                f"Backend Status: {candidate.backend_eligibility_status}\n"
                f"Language: {language}\n"
                f"Task: Generate a grounded, 2-sentence match explanation and list key match reasons."
            )

            sys_prompt = (
                "You are an AI assistant for CredSaathi. Explain why the applicant matches the candidate scheme based ONLY on provided facts. "
                "Do NOT promise guaranteed approval, credit scores, risk scores, or loan approval probabilities."
            )

            model_req = ModelRequest(
                task_type=TaskType.SCHEME_MATCHING,
                prompt=prompt,
                system_prompt=sys_prompt,
                temperature=0.3
            )

            try:
                response = await model_gateway.invoke(model_req)
                explanation_text = response.content.strip()
            except Exception as e:
                logger.warning(f"Fallback explanation used due to gateway invocation note: {str(e)}")
                explanation_text = (
                    f"{candidate.scheme_name} matches your profile based on {applicant.purpose or 'your requirements'}. "
                    f"Verified status: {candidate.backend_eligibility_status}."
                )

            # Default grounded match reasons
            match_reasons = [
                f"Matches profile purpose: '{applicant.purpose}'" if applicant.purpose else "Matches general category criteria",
                f"Deterministic backend eligibility verified as {candidate.backend_eligibility_status}"
            ]

            result = SchemeMatchResult(
                scheme_id=candidate.scheme_id,
                scheme_name=candidate.scheme_name,
                relevance_score=relevance_score,
                eligibility_status=candidate.backend_eligibility_status,
                match_reasons=match_reasons,
                missing_information=missing_info,
                source_reference=candidate.source_reference,
                last_verified=candidate.last_verified,
                explanation=explanation_text
            )
            results.append(result)

        return results

    def _identify_missing_information(
        self, applicant: ApplicantContext, candidate: CandidateScheme
    ) -> List[str]:
        """Identifies missing attributes or required documents deterministically."""
        missing = []
        if candidate.required_documents:
            for doc in candidate.required_documents:
                missing.append(f"Upload document: {doc}")

        if not applicant.income_annual:
            missing.append("Provide annual income details for verification")

        if not applicant.state:
            missing.append("Provide state of residence")

        return missing


explainer = SchemeExplainer()
