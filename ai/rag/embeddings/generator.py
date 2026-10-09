"""Lightweight Embedding Generator for in-memory vector retrieval."""
import math
import re
from typing import List

EMBEDDING_DIM = 64


class EmbeddingGenerator:
    """Generates normalized dense vector embeddings for text queries and document chunks."""

    def generate_embedding(self, text: str) -> List[float]:
        """Generates normalized vector embedding based on hashed token frequencies."""
        vec = [0.0] * EMBEDDING_DIM
        tokens = re.findall(r"\w+", text.lower())

        if not tokens:
            return vec

        for token in tokens:
            # Deterministic hash to bucket
            idx = abs(hash(token)) % EMBEDDING_DIM
            vec[idx] += 1.0

        # L2 Normalize
        magnitude = math.sqrt(sum(v * v for v in vec))
        if magnitude > 0:
            vec = [round(v / magnitude, 4) for v in vec]

        return vec

    def cosine_similarity(self, vec1: List[float], vec2: List[float], query_text: str = "", chunk_text: str = "") -> float:
        """Calculates cosine similarity with keyword matching bonus."""
        sim = 0.0
        if vec1 and vec2 and len(vec1) == len(vec2):
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            sim = dot_product

        if query_text and chunk_text:
            STOP_WORDS = {"is", "in", "the", "a", "an", "what", "of", "to", "for", "and", "or", "on", "at", "by", "this", "that", "rate"}
            q_tokens = set(re.findall(r"\w+", query_text.lower())) - STOP_WORDS
            c_tokens = set(re.findall(r"\w+", chunk_text.lower())) - STOP_WORDS
            common = q_tokens.intersection(c_tokens)
            if not common:
                return 0.0
            overlap_ratio = len(common) / max(len(q_tokens), 1)
            sim = max(sim, overlap_ratio)

        return round(max(min(sim, 1.0), 0.0), 4)


embedding_generator = EmbeddingGenerator()
