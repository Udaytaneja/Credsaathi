"""Grounded Financial Explanation Generator adhering to compliance safety rules."""
import re
from typing import List
from ai.financial.schemas.financial import FinancialProfileInput, FinancialSummaryResponseData
from ai.financial.summarizer.summarizer import summarizer
from ai.schemas.model_gateway import ModelRequest, TaskType
from ai.utils.logging import logger

PROHIBITED_FINANCIAL_CLAIMS = [
    r"credit approval",
    r"loan rejection",
    r"approval probability",
    r"credit score",
    r"risk score",
    r"guaranteed approval",
    r"approved for loan",
    r"rejected for loan",
]


class FinancialExplanationGenerator:
    """Generates human-readable financial profile summaries grounded in backend metrics."""

    async def generate_explanation(self, profile: FinancialProfileInput) -> FinancialSummaryResponseData:
        key_facts = summarizer.extract_key_facts(profile)
        data_gaps = summarizer.identify_data_gaps(profile)
        observations, prep_guidance = summarizer.generate_observations(profile)

        # Build LLM Prompt with preserved numeric facts
        prompt = (
            f"Validated Financial Facts:\n" + "\n".join(f"- {f}" for f in key_facts) + "\n"
            f"Observations:\n" + "\n".join(f"- {o}" for o in observations) + "\n"
            f"Task: Generate a 3-sentence narrative summary explaining the applicant's financial profile overview."
        )

        sys_prompt = (
            "You are a financial profile summarizer for CredSaathi. Summarize provided metrics accurately. "
            "Do NOT issue credit approvals, loan rejections, credit scores, risk scores, or approval probabilities."
        )

        model_req = ModelRequest(
            task_type=TaskType.FINANCIAL_EXPLANATION,
            prompt=prompt,
            system_prompt=sys_prompt,
            temperature=0.2
        )

        try:
            from ai.model_router.gateway import model_gateway
            res = await model_gateway.invoke(model_req)
            summary_text = res.content.strip()
        except Exception as e:
            logger.warning(f"Gateway financial explanation note: {str(e)}, using fallback summary.")
            summary_text = (
                f"Financial profile overview based on {len(key_facts)} verified backend metrics. "
                f"Income/Turnover and reported liabilities have been logged."
            )

        # Sanitize summary text against prohibited decisioning claims
        clean_summary = self._sanitize_summary(summary_text)

        from ai.model_router.registry import model_registry
        model_meta = model_registry.get_metadata("default")

        return FinancialSummaryResponseData(
            summary=clean_summary,
            key_facts=key_facts,
            observations=observations,
            data_gaps=data_gaps,
            preparation_guidance=prep_guidance,
            source="backend_validated_data",
            model=model_meta
        )

    def _sanitize_summary(self, text: str) -> str:
        """Strips or replaces prohibited financial decisioning terms."""
        sanitized = text
        for pattern in PROHIBITED_FINANCIAL_CLAIMS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Financial Guardrail caught prohibited claim pattern '{pattern}'.")
                sanitized = re.sub(pattern, "financial summary metric", sanitized, flags=re.IGNORECASE)
        return sanitized


explanation_generator = FinancialExplanationGenerator()
