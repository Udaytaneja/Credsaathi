"""Pydantic schemas for CredSaathi Document AI."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SupportedDocumentType(str, Enum):
    """Supported document categories for MVP."""
    INCOME_PROOF = "income_proof"
    BANK_STATEMENT = "bank_statement"
    BUSINESS_REGISTRATION = "business_registration"
    IDENTITY_PROOF = "identity_proof"
    GENERIC = "generic"


class ProcessingMetadata(BaseModel):
    """Metadata describing Document AI OCR engine and model execution."""
    ocr_engine: str = Field(default="mock-ocr-v1", description="OCR engine identifier")
    model_version: str = Field(default="1.0.0", description="Model / extractor version")
    file_size_bytes: int = Field(default=0, ge=0, description="Input document file size in bytes")
    file_type: str = Field(default="application/pdf", description="MIME type or file extension")


class DocumentExtractionRequest(BaseModel):
    """Request model for document extraction."""
    document_type: Optional[SupportedDocumentType] = Field(
        default=SupportedDocumentType.GENERIC,
        description="Target document category or GENERIC for auto-classification"
    )
    file_name: str = Field(default="document.pdf", description="Original filename")
    file_bytes_base64: Optional[str] = Field(default=None, description="Base64 encoded file content")
    file_text_override: Optional[str] = Field(default=None, description="Direct text input override for testing/OCR pass-through")


class DocumentExtractionResponseData(BaseModel):
    """Structured extraction response returned by Document AI pipeline."""
    document_type: str = Field(..., description="Classified or specified document type")
    fields: Dict[str, Any] = Field(default_factory=dict, description="Extracted and normalized document fields")
    field_confidence: Dict[str, float] = Field(default_factory=dict, description="Per-field confidence scores (0.0 to 1.0)")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings or low confidence alerts")
    review_required: bool = Field(default=True, description="Indicates if human review is required")
    processing_metadata: ProcessingMetadata = Field(..., description="Processing metadata")
    disclaimer: str = Field(
        default="OCR extraction does NOT prove document authenticity, legal validity, or identity verification. Human review required.",
        description="Mandatory Document AI safety disclaimer"
    )
