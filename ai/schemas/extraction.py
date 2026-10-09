"""Alias to Document AI schemas for API routing consistency."""
from ai.extraction.schemas import (
    DocumentExtractionRequest,
    DocumentExtractionResponseData,
    ProcessingMetadata,
    SupportedDocumentType,
)

__all__ = [
    "SupportedDocumentType",
    "ProcessingMetadata",
    "DocumentExtractionRequest",
    "DocumentExtractionResponseData",
]
