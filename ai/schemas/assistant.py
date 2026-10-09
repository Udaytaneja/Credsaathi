"""Pydantic schemas for Saakshi - CredSaathi Applicant Assistant."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ai.rag.schemas import SourceCitation
from ai.schemas.common import ModelMetadata


class AssistantQueryRequest(BaseModel):
    """Request model for Saakshi Applicant Assistant."""
    query: str = Field(..., min_length=1, description="User question or query text")
    language: str = Field(default="en", description="Preferred response language: 'en', 'hi', 'hinglish'")
    authenticated_user_id: str = Field(..., description="ID of the authenticated user making request")
    application_id: Optional[str] = Field(default=None, description="Optional application ID to query context for")


class SafetyFlags(BaseModel):
    """Safety and security flags associated with the assistant execution."""
    prompt_injection_detected: bool = False
    unauthorized_access_attempt: bool = False
    evidence_found: bool = True
    prohibited_term_redacted: bool = False


class AssistantQueryResponseData(BaseModel):
    """Response payload for Saakshi Applicant Assistant."""
    answer: str = Field(..., description="Grounded natural language answer")
    citations: List[SourceCitation] = Field(default_factory=list, description="Traceable citations list")
    suggested_actions: List[str] = Field(default_factory=list, description="Contextual suggested UI/navigation actions")
    safety_flags: SafetyFlags = Field(default_factory=SafetyFlags, description="Security and safety flags")
    disclaimer: str = Field(
        default="Saakshi is an informational assistant. Saakshi does not issue credit approvals, loan rejections, or credit scores.",
        description="Mandatory Saakshi assistant disclaimer"
    )
