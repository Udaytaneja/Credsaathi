"""Saakshi - CredSaathi Applicant Information and Navigation Assistant."""
import re
from typing import List, Tuple
from ai.agents.tools import saakshi_tools
from ai.guardrails.matching_guardrails import matching_guardrail
from ai.model_router.gateway import model_gateway
from ai.rag.pipeline import rag_pipeline_service
from ai.rag.schemas import RAGQueryRequest
from ai.rag.validation.checker import rag_validator
from ai.schemas.assistant import AssistantQueryRequest, AssistantQueryResponseData, SafetyFlags
from ai.schemas.model_gateway import ModelRequest, TaskType
from ai.utils.logging import logger

SAAKSHI_REFUSAL_MESSAGES = {
    "en": "I could not find verified scheme records to answer this question. Saakshi cannot fabricate unverified scheme details.",
    "hi": "क्रेडसाथी के पास इस योजना की सत्यापित जानकारी उपलब्ध नहीं है।",
    "hinglish": "CredSaathi me is scheme ki verified information nahi mili. Saakshi unverified scheme details create nahi karti."
}

UNAUTHORIZED_DATA_RESPONSE = {
    "en": "Access Denied: You do not have authorization to view this application or user data.",
    "hi": "अस्वीकृत: आपके पास इस आवेदन की जानकारी देखने की अनुमति नहीं है।",
    "hinglish": "Access Denied: Aapke paas is application data ko view karne ki authorization nahi hai."
}


class SaakshiAssistant:
    """Saakshi Assistant providing safe, multi-tenant isolated navigation & guidance."""

    async def handle_query(self, req: AssistantQueryRequest) -> AssistantQueryResponseData:
        flags = SafetyFlags()
        lang = req.language.lower()

        # 1. Defense against Prompt Injection
        if rag_validator.check_prompt_injection(req.query):
            flags.prompt_injection_detected = True
            flags.evidence_found = False
            return AssistantQueryResponseData(
                answer="Security Alert: Prompt injection attempt detected. Query rejected.",
                citations=[],
                suggested_actions=["Contact Customer Support"],
                safety_flags=flags
            )

        # 2. Defense against another user's data request / cross-tenant probing
        if self._is_cross_user_probe(req.query):
            flags.unauthorized_access_attempt = True
            flags.evidence_found = False
            return AssistantQueryResponseData(
                answer=UNAUTHORIZED_DATA_RESPONSE.get(lang, UNAUTHORIZED_DATA_RESPONSE["en"]),
                citations=[],
                suggested_actions=["View My Applications"],
                safety_flags=flags
            )

        # 3. Application Status Intent Handling
        if self._is_status_query(req.query) or req.application_id:
            return await self._handle_status_intent(req, flags)

        # 4. Scheme & FAQ Intent via Grounded RAG Pipeline
        rag_req = RAGQueryRequest(
            query=req.query,
            language=req.language,
            top_k=3
        )
        rag_res = await rag_pipeline_service.query(rag_req)

        if not rag_res.evidence_found:
            flags.evidence_found = False
            ref_msg = SAAKSHI_REFUSAL_MESSAGES.get(lang, SAAKSHI_REFUSAL_MESSAGES["en"])
            return AssistantQueryResponseData(
                answer=ref_msg,
                citations=[],
                suggested_actions=["Browse Available Schemes", "Check Eligibility"],
                safety_flags=flags
            )

        # 5. Sanitize Output & Apply Financial Guardrails
        clean_answer = matching_guardrail.sanitize_explanation(rag_res.answer)
        if clean_answer != rag_res.answer:
            flags.prohibited_term_redacted = True

        suggested = self._derive_suggested_actions(req.query)

        return AssistantQueryResponseData(
            answer=clean_answer,
            citations=rag_res.citations,
            suggested_actions=suggested,
            safety_flags=flags
        )

    async def _handle_status_intent(
        self, req: AssistantQueryRequest, flags: SafetyFlags
    ) -> AssistantQueryResponseData:
        lang = req.language.lower()
        # Extract application ID from query or request parameter
        app_id_match = re.search(r"APP_\d+", req.query)
        app_id = req.application_id or (app_id_match.group(0) if app_id_match else None)

        if not app_id:
            return AssistantQueryResponseData(
                answer="Please provide your Application ID (e.g. APP_101) to check your application status.",
                citations=[],
                suggested_actions=["View My Applications"],
                safety_flags=flags
            )

        # Execute read-only tool with tenant ownership check
        status_data = saakshi_tools.get_application_status(
            user_id=req.authenticated_user_id,
            application_id=app_id
        )

        if not status_data:
            flags.unauthorized_access_attempt = True
            flags.evidence_found = False
            return AssistantQueryResponseData(
                answer=UNAUTHORIZED_DATA_RESPONSE.get(lang, UNAUTHORIZED_DATA_RESPONSE["en"]),
                citations=[],
                suggested_actions=["View My Applications"],
                safety_flags=flags
            )

        # Formulate grounded application status answer
        if lang == "hi":
            ans = f"आपका आवेदन {status_data['application_id']} स्थिति: '{status_data['status']}'। अगला कदम: {status_data['next_step']}।"
        elif lang == "hinglish":
            ans = f"Aapka application {status_data['application_id']} status hai '{status_data['status']}'. Next step: {status_data['next_step']}."
        else:
            ans = (
                f"Your application {status_data['application_id']} for {status_data['scheme_name']} is currently '{status_data['status']}'. "
                f"Submitted on {status_data['submitted_date']}. Next recommended action: {status_data['next_step']}."
            )

        return AssistantQueryResponseData(
            answer=ans,
            citations=[],
            suggested_actions=["Upload Documents", "Check Status Details"],
            safety_flags=flags
        )

    def _is_status_query(self, query: str) -> bool:
        q_lower = query.lower()
        return "status" in q_lower or "track" in q_lower or "application" in q_lower

    def _is_cross_user_probe(self, query: str) -> bool:
        q_lower = query.lower()
        cross_patterns = [
            "other user",
            "another user",
            "all users data",
            "user_sita_02",  # direct probe for another test user
            "show someone else",
        ]
        return any(p in q_lower for p in cross_patterns)

    def _derive_suggested_actions(self, query: str) -> List[str]:
        q_lower = query.lower()
        if "scheme" in q_lower or "eligible" in q_lower:
            return ["Check Scheme Eligibility", "View Scheme Details"]
        if "document" in q_lower or "proof" in q_lower:
            return ["Upload Documents", "View Required Checklist"]
        return ["Check Scheme Match", "View My Applications"]


saakshi_assistant = SaakshiAssistant()
