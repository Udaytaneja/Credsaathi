"""Text Chunker for splitting knowledge sources into overlap chunks with metadata."""
from typing import List
from ai.rag.embeddings.generator import embedding_generator
from ai.rag.schemas import DocumentChunk, KnowledgeSource


class TextChunker:
    """Splits knowledge source text into chunk objects with embedded vectors."""

    def chunk_document(
        self, source: KnowledgeSource, full_text: str, chunk_size: int = 300, overlap: int = 50
    ) -> List[DocumentChunk]:
        """Splits full document text into overlapping chunks."""
        words = full_text.split()
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        i = 0
        while i < len(words):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words)

            chunk_id = f"{source.source_id}_chk_{chunk_idx}"
            embedding = embedding_generator.generate_embedding(chunk_text)

            chunk_obj = DocumentChunk(
                chunk_id=chunk_id,
                source=source,
                content=chunk_text,
                embedding=embedding,
                metadata={"chunk_index": chunk_idx, "word_count": len(chunk_words)}
            )
            chunks.append(chunk_obj)

            chunk_idx += 1
            i += max(chunk_size - overlap, 1)

        return chunks


text_chunker = TextChunker()
