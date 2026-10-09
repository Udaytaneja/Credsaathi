"""Retriever module enforcing source filters and score thresholds."""
from typing import List, Optional, Tuple
from ai.rag.ingestion.store import vector_store
from ai.rag.schemas import DocumentChunk, SourceType


class RAGRetriever:
    """Retrieves top matching knowledge chunks from vector store."""

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        filter_source_type: Optional[SourceType] = None,
        min_score: float = 0.20
    ) -> List[Tuple[DocumentChunk, float]]:
        """Performs vector search with filtering and threshold validation."""
        return vector_store.search(
            query_text=query,
            top_k=top_k,
            filter_source_type=filter_source_type,
            min_score=min_score
        )


retriever = RAGRetriever()
