"""Source citation builder mapping retrieved chunks to traceable references."""
from typing import List, Tuple
from ai.rag.schemas import DocumentChunk, SourceCitation


class CitationBuilder:
    """Builds structured, traceable citations from retrieved document chunks."""

    def build_citations(
        self, retrieved_chunks: List[Tuple[DocumentChunk, float]]
    ) -> List[SourceCitation]:
        citations: List[SourceCitation] = []
        for idx, (chunk, score) in enumerate(retrieved_chunks, start=1):
            cit = SourceCitation(
                citation_id=f"[{idx}]",
                source_id=chunk.source.source_id,
                title=chunk.source.title,
                source_type=chunk.source.source_type.value,
                snippet=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                retrieval_score=score,
                verification_date=chunk.source.verification_date
            )
            citations.append(cit)
        return citations


citation_builder = CitationBuilder()
