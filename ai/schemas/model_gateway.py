"""Schemas for AI Model Gateway requests, responses, task routing, and cost metadata."""
import uuid
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from ai.schemas.common import ModelMetadata


class TaskType(str, Enum):
    """Supported task types for task-based model routing."""
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    SUMMARIZATION = "summarization"
    SCHEME_MATCHING = "scheme_matching"
    TRANSLATION = "translation"
    RAG = "rag"
    FINANCIAL_EXPLANATION = "financial_explanation"
    ASSISTANT = "assistant"


class ModelRequest(BaseModel):
    """Standard request payload for invoking a model through the Model Gateway."""
    task_type: TaskType = Field(..., description="Task type driving route & system prompt selection")
    prompt: str = Field(..., min_length=1, description="Primary user input or prompt string")
    system_prompt: Optional[str] = Field(default=None, description="Optional system instruction override")
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured contextual input data")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=1000, gt=0, description="Maximum token generation limit")
    timeout_seconds: Optional[float] = Field(default=None, gt=0.0, description="Optional per-request timeout override")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Correlation ID")
    user_id: Optional[str] = Field(default=None, description="Optional user identifier for auditing")
    model_override: Optional[str] = Field(default=None, description="Optional specific model alias override")

    @field_validator("prompt")
    @classmethod
    def validate_prompt_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v


class CostMetadata(BaseModel):
    """Token usage and estimated cost metadata."""
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: Optional[float] = Field(default=0.0, ge=0.0)


class ModelResponse(BaseModel):
    """Standardized output returned by Model Gateway for any provider execution."""
    content: str = Field(..., description="Generated raw text response")
    structured_output: Optional[Dict[str, Any]] = Field(default=None, description="Parsed structured JSON output")
    metadata: ModelMetadata = Field(..., description="Provider, model name and version metadata")
    cost: Optional[CostMetadata] = Field(default_factory=CostMetadata, description="Token cost accounting")
    request_id: str = Field(..., description="Correlation ID matching request")
    execution_time_ms: float = Field(..., ge=0.0, description="Execution duration in milliseconds")
    audit_metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit trace telemetry")
