"""Unified CredSaathi AI Guardrail Manager and Orchestrator."""
from typing import Any, Dict, List, Optional
from ai.gateway.errors import AIFirewallException, AIGuardrailViolationException
from ai.guardrails.agent_firewall import AgentFirewall, agent_firewall
from ai.guardrails.document_security import FALLBACK_HUMAN_REVIEW, DocumentSecurityGuardrail, document_security_guardrail
from ai.guardrails.financial_compliance import FinancialComplianceGuardrail, financial_compliance_guardrail
from ai.guardrails.grounding import FALLBACK_INSUFFICIENT_EVIDENCE, GroundingGuardrail, grounding_guardrail
from ai.guardrails.privacy import PrivacyGuardrail, privacy_guardrail
from ai.guardrails.prompt_security import PromptSecurityGuardrail, prompt_security_guardrail
from ai.utils.logging import logger

FALLBACK_ACCESS_DENIED = "Access denied."


class AIGuardrailManager:
    """Orchestrates modular guardrails across input sanitization, privacy, grounding, compliance, and tool execution."""

    def __init__(
        self,
        prompt_security: Optional[PromptSecurityGuardrail] = None,
        privacy: Optional[PrivacyGuardrail] = None,
        grounding: Optional[GroundingGuardrail] = None,
        financial_compliance: Optional[FinancialComplianceGuardrail] = None,
        document_security: Optional[DocumentSecurityGuardrail] = None,
        firewall: Optional[AgentFirewall] = None,
    ):
        self.prompt_security = prompt_security or prompt_security_guardrail
        self.privacy = privacy or privacy_guardrail
        self.grounding = grounding or grounding_guardrail
        self.financial_compliance = financial_compliance or financial_compliance_guardrail
        self.document_security = document_security or document_security_guardrail
        self.firewall = firewall or agent_firewall

    def validate_input_query(
        self, query: str, user_id: str, target_user_id: Optional[str] = None
    ) -> str:
        """Validates input query against user scope, prompt injection, and sanitizes input."""
        # 1. User scope check
        self.privacy.validate_user_scope(current_user_id=user_id, target_user_id=target_user_id)

        # 2. Prompt injection & sanitization check
        clean_query = self.prompt_security.validate_input_prompt(query)

        return clean_query

    def process_output_response(
        self,
        response_text: str,
        retrieved_contexts: Optional[List[str]] = None,
        confidence_score: float = 1.0,
        preserve_pii: bool = False,
    ) -> str:
        """Processes model output response with PII redaction, grounding verification, and financial claim compliance."""
        if not response_text:
            return ""

        processed_text = response_text

        # 1. Grounding check if contexts provided
        if retrieved_contexts is not None:
            if not self.grounding.validate_grounding(
                query="", retrieved_contexts=retrieved_contexts, confidence_score=confidence_score
            ):
                return FALLBACK_INSUFFICIENT_EVIDENCE

        # 2. Financial compliance repair
        processed_text = self.financial_compliance.sanitize_financial_claims(processed_text)

        # 3. PII redaction
        if not preserve_pii:
            processed_text = self.privacy.redact_pii(processed_text)

        return processed_text


guardrail_manager = AIGuardrailManager()
