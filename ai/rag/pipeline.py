"""Grounded RAG Pipeline Service with citation mapping and hallucination controls."""
from ai.rag.citations.builder import citation_builder
from ai.rag.retrieval.retriever import retriever
from ai.rag.schemas import RAGQueryRequest, RAGQueryResponseData
from ai.rag.validation.checker import rag_validator
from ai.schemas.model_gateway import ModelRequest, TaskType
from ai.utils.logging import logger

REFUSAL_MESSAGES = {
    "en": "I could not find verified evidence in the CredSaathi knowledge base to answer your question. I cannot fabricate unverified information.",
    "hi": "क्रेडसाथी ज्ञान कोष में आपके प्रश्न का उत्तर देने के लिए सत्यापित प्रमाण नहीं मिला।",
    "hinglish": "CredSaathi verified database me is query ka verified answer nahi mila. Main unverified info generate nahi kar sakta."
}


class RAGPipelineService:
    """Orchestrates grounded RAG retrieval, evidence validation, citation building, and refusal handling."""

    async def query(self, req: RAGQueryRequest) -> RAGQueryResponseData:
        lang = req.language.lower()
        refusal_txt = REFUSAL_MESSAGES.get(lang, REFUSAL_MESSAGES["en"])

        # 1. Prompt Injection Shield
        if rag_validator.check_prompt_injection(req.query):
            logger.warning(f"Prompt injection attempt blocked: {req.query}")
            return RAGQueryResponseData(
                answer="Security Warning: Prompt injection pattern detected. Query blocked.",
                citations=[],
                evidence_found=False,
                query_language=req.language
            )

        # 2. Vector Retrieval & Source Filtering
        retrieved = retriever.retrieve(
            query=req.query,
            top_k=req.top_k,
            filter_source_type=req.filter_source_type,
            min_score=req.min_score_threshold
        )

        # 3. Evidence Sufficiency & Refusal Check
        if not rag_validator.is_evidence_sufficient(retrieved, min_required_score=req.min_score_threshold):
            logger.info(f"Insufficient grounding evidence for query: {req.query}")
            return RAGQueryResponseData(
                answer=refusal_txt,
                citations=[],
                evidence_found=False,
                query_language=req.language
            )

        # 4. Build Citations
        citations = citation_builder.build_citations(retrieved)

        # 5. Build Grounded Prompt for Model Gateway
        context_snippets = "\n".join([f"{cit.citation_id} {cit.snippet}" for cit in citations])

        prompt = (
            f"User Query: {req.query}\n"
            f"Target Language: {req.language}\n"
            f"Verified Evidence Snippets:\n{context_snippets}\n"
            f"Task: Answer the user query using ONLY the verified evidence snippets above. "
            f"Include citation tags like [1] inline corresponding to facts."
        )

        sys_prompt = (
            "You are CredSaathi Grounded Assistant. Rely strictly on provided evidence snippets. "
            "Do NOT invent facts, rates, or eligibility rules not present in snippets."
        )

        model_req = ModelRequest(
            task_type=TaskType.RAG,
            prompt=prompt,
            system_prompt=sys_prompt,
            temperature=0.1
        )

        try:
            from ai.model_router.gateway import model_gateway
            model_res = await model_gateway.invoke(model_req)
            answer_text = model_res.content.strip()
        except Exception as e:
            logger.warning(f"Gateway RAG note: {str(e)}, using direct snippet summary.")
            answer_text = f"Based on verified records {citations[0].citation_id}: {citations[0].snippet}"

        return RAGQueryResponseData(
            answer=answer_text,
            citations=citations,
            evidence_found=True,
            query_language=req.language
        )


rag_pipeline_service = RAGPipelineService()
