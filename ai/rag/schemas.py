"""Pydantic schemas for CredSaathi Grounded RAG system."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    """Authorized knowledge source types."""
    GOVERNMENT_SCHEME = "government_scheme"
    LENDER_INFO = "lender_info"
    PRODUCT_INFO = "product_info"
    FAQ = "faq"
    DOCUMENTATION = "documentation"


class KnowledgeSource(BaseModel):
    """Metadata container for trusted knowledge documents."""
    source_id: str = Field(..., description="Unique source identifier")
    title: str = Field(..., description="Source document title")
    source_type: SourceType = Field(..., description="Authorized source category")
    verification_status: str = Field(default="VERIFIED", description="Verification status e.g. VERIFIED")
    verification_date: str = Field(default="2026-10-01", description="Date of last verification")
    effective_date: Optional[str] = Field(default="2026-01-01", description="Effective start date")
    url_or_ref: Optional[str] = Field(default=None, description="Official reference URL or portal ID")


class DocumentChunk(BaseModel):
    """Granular text chunk with vector embedding and source metadata."""
    chunk_id: str = Field(..., description="Unique chunk ID")
    source: KnowledgeSource = Field(..., description="Associated knowledge source")
    content: str = Field(..., description="Chunk text content")
    embedding: Optional[List[float]] = Field(default=None, description="Dense vector embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional chunk attributes")


class SourceCitation(BaseModel):
    """Traceable citation link attached to RAG outputs."""
    citation_id: str = Field(..., description="Citation marker e.g. [1]")
    source_id: str = Field(..., description="Source ID")
    title: str = Field(..., description="Source title")
    source_type: str = Field(..., description="Source type")
    snippet: str = Field(..., description="Exact grounding snippet quote")
    retrieval_score: float = Field(..., ge=0.0, le=1.0, description="Similarity retrieval score")
    verification_date: str = Field(..., description="Verification date")


class RAGQueryRequest(BaseModel):
    """Request payload for querying Grounded RAG."""
    query: str = Field(..., min_length=1, description="User query text")
    language: str = Field(default="en", description="Query language: 'en', 'hi', 'hinglish'")
    filter_source_type: Optional[SourceType] = Field(default=None, description="Optional source type filter")
    top_k: int = Field(default=3, gt=0, le=10, description="Max chunks to retrieve")
    min_score_threshold: float = Field(default=0.25, ge=0.0, le=1.0, description="Minimum relevance threshold")


class RAGQueryResponseData(BaseModel):
    """Response payload returned by Grounded RAG system."""
    answer: str = Field(..., description="Grounded natural language answer with citations")
    citations: List[SourceCitation] = Field(default_factory=list, description="Traceable citations list")
    evidence_found: bool = Field(default=True, description="Indicates if sufficient grounding evidence was retrieved")
    query_language: str = Field(default="en", description="Detected/specified language")
    disclaimer: str = Field(
        default="Answers are derived strictly from verified CredSaathi knowledge records and FAQs.",
        description="RAG safety disclaimer"
    )
