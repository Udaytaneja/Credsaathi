"""Pydantic schemas for AI Auditability and Telemetry events."""
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIAuditRecord(BaseModel):
    """Structured audit record representing a single traceable AI operation."""

    audit_id: str = Field(
        default_factory=lambda: f"audit_{uuid.uuid4().hex[:16]}",
        description="Unique identifier for this audit event record"
    )
    request_id: str = Field(..., description="Correlation request ID across service calls")
    user_id: Optional[str] = Field(default=None, description="Authenticated user ID scope")
    application_id: Optional[str] = Field(default=None, description="Loan or scheme application ID context")
    task_type: str = Field(..., description="Task type classification (e.g. SCHEME_MATCHING, DOCUMENT_EXTRACTION)")
    model_provider: Optional[str] = Field(default=None, description="Model provider (e.g. OpenAI, Anthropic, Internal)")
    model_name: Optional[str] = Field(default=None, description="Model name or architecture ID")
    model_version: Optional[str] = Field(default=None, description="Model version tag")
    prompt_template_version: Optional[str] = Field(default=None, description="Version of prompt template utilized")
    retrieval_source_ids: List[str] = Field(default_factory=list, description="IDs of retrieved knowledge chunks/sources")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool execution traces through Firewall")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Total execution latency in milliseconds")
    prompt_tokens: Optional[int] = Field(default=None, ge=0, description="Input prompt token count")
    completion_tokens: Optional[int] = Field(default=None, ge=0, description="Output completion token count")
    total_cost_usd: Optional[float] = Field(default=None, ge=0.0, description="Estimated API usage cost in USD")
    output_validation_status: str = Field(default="PASSED", description="Validation status: PASSED, REPAIRED, REJECTED")
    guardrail_events: List[Dict[str, Any]] = Field(default_factory=list, description="Events emitted by Guardrails layer")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error codes and messages if failure occurred")
    human_review_required: bool = Field(default=False, description="Flag indicating if human review is needed")
    timestamp: float = Field(default_factory=time.time, description="POSIX timestamp of operation execution")
