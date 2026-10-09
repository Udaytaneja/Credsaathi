"""Vector Store and Synthetic Knowledge Base for CredSaathi Grounded RAG."""
from typing import List, Optional, Tuple
from ai.rag.chunking.chunker import text_chunker
from ai.rag.embeddings.generator import embedding_generator
from ai.rag.schemas import DocumentChunk, KnowledgeSource, SourceType

SYNTHETIC_KNOWLEDGE_DOCUMENTS = [
    {
        "source": KnowledgeSource(
            source_id="SRC_SCHEME_PMEGP",
            title="Prime Minister Employment Generation Programme (PMEGP)",
            source_type=SourceType.GOVERNMENT_SCHEME,
            verification_status="VERIFIED",
            verification_date="2026-10-01",
            effective_date="2026-01-01",
            url_or_ref="https://kviconline.gov.in/pmegp"
        ),
        "content": (
            "PMEGP is a credit linked subsidy scheme for setting up micro enterprises in non-farm sector. "
            "Maximum project cost eligible for manufacturing sector is INR 50 Lakhs and for business/service sector is INR 20 Lakhs. "
            "General category beneficiaries receive 15% subsidy in urban areas and 25% in rural areas. "
            "Special categories including SC, ST, OBC, Minorities, Women, Ex-servicemen receive 25% in urban and 35% in rural areas."
        )
    },
    {
        "source": KnowledgeSource(
            source_id="SRC_FAQ_ELIGIBILITY",
            title="CredSaathi Scheme Matching FAQ",
            source_type=SourceType.FAQ,
            verification_status="VERIFIED",
            verification_date="2026-10-01",
            effective_date="2026-01-01",
            url_or_ref="https://credsaathi.in/faq/eligibility"
        ),
        "content": (
            "CredSaathi calculates deterministic eligibility based on applicant category, state, income, and age. "
            "Relevance scores indicate match suitability and do not guarantee loan approval or represent credit scores. "
            "Applicants must provide verified income proofs and Aadhaar/PAN documents for complete scheme verification."
        )
    },
    {
        "source": KnowledgeSource(
            source_id="SRC_LENDER_MUDRA",
            title="MUDRA Loan Operational Guidelines",
            source_type=SourceType.LENDER_INFO,
            verification_status="VERIFIED",
            verification_date="2026-10-01",
            effective_date="2026-01-01",
            url_or_ref="https://mudra.org.in/guidelines"
        ),
        "content": (
            "MUDRA loans are divided into three categories: Shishu (loans up to INR 50,000), "
            "Kishore (loans above INR 50,000 and up to INR 5 Lakhs), and Tarun (loans above INR 5 Lakhs and up to INR 10 Lakhs). "
            "No collateral is required for MUDRA loans under government directives."
        )
    }
]


class VectorKnowledgeStore:
    """In-memory vector store indexing verified document chunks."""

    def __init__(self):
        self._chunks: List[DocumentChunk] = []
        self._load_synthetic_knowledge_base()

    def _load_synthetic_knowledge_base(self):
        for doc in SYNTHETIC_KNOWLEDGE_DOCUMENTS:
            src: KnowledgeSource = doc["source"]
            content: str = doc["content"]
            doc_chunks = text_chunker.chunk_document(src, content)
            self._chunks.extend(doc_chunks)

    def search(
        self,
        query_text: str,
        top_k: int = 3,
        filter_source_type: Optional[SourceType] = None,
        min_score: float = 0.15
    ) -> List[Tuple[DocumentChunk, float]]:
        """Searches vector store using query text and optional source filter."""
        query_vec = embedding_generator.generate_embedding(query_text)
        results: List[Tuple[DocumentChunk, float]] = []

        for chunk in self._chunks:
            if filter_source_type and chunk.source.source_type != filter_source_type:
                continue

            score = embedding_generator.cosine_similarity(
                query_vec, chunk.embedding or [], query_text=query_text, chunk_text=chunk.content
            )
            if score >= min_score:
                results.append((chunk, score))

        # Sort descending by score
        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]


vector_store = VectorKnowledgeStore()
