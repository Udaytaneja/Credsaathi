"""Pydantic schemas package for CredSaathi AI Layer."""
from ai.schemas.assistant import AssistantQueryRequest, AssistantQueryResponseData, SafetyFlags
from ai.schemas.common import ErrorDetail, ModelMetadata, ResponseEnvelope
from ai.schemas.financial import FinancialProfileInput, FinancialSummaryResponseData
from ai.schemas.matching import (
    ApplicantContext,
    CandidateScheme,
    SchemeMatchRequest,
    SchemeMatchResponseData,
    SchemeMatchResult,
)
from ai.schemas.model_gateway import CostMetadata, ModelRequest, ModelResponse, TaskType
from ai.schemas.rag import DocumentChunk, KnowledgeSource, RAGQueryRequest, RAGQueryResponseData, SourceCitation, SourceType

__all__ = [
    "ModelMetadata",
    "ErrorDetail",
    "ResponseEnvelope",
    "TaskType",
    "ModelRequest",
    "CostMetadata",
    "ModelResponse",
    "ApplicantContext",
    "CandidateScheme",
    "SchemeMatchRequest",
    "SchemeMatchResult",
    "SchemeMatchResponseData",
    "FinancialProfileInput",
    "FinancialSummaryResponseData",
    "SourceType",
    "KnowledgeSource",
    "DocumentChunk",
    "SourceCitation",
    "RAGQueryRequest",
    "RAGQueryResponseData",
    "AssistantQueryRequest",
    "AssistantQueryResponseData",
    "SafetyFlags",
]
