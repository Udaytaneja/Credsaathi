"""Document extraction safety and extraction quality guardrail."""
from typing import Any, Dict, List, Optional, Tuple
from ai.utils.logging import logger

FALLBACK_HUMAN_REVIEW = "Human review required."
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/webp",
]
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB


class DocumentSecurityGuardrail:
    """Validates document extraction quality, file types, size limits, and security payloads."""

    def __init__(self, min_confidence_threshold: float = 0.70):
        self.min_confidence_threshold = min_confidence_threshold

    def validate_extraction_confidence(
        self, confidence_score: float, extracted_fields: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Validates that document extraction confidence meets minimum threshold."""
        if confidence_score < self.min_confidence_threshold:
            logger.warning(
                f"[DOCUMENT_GUARDRAIL] Extraction confidence ({confidence_score}) below threshold ({self.min_confidence_threshold})."
            )
            return False, FALLBACK_HUMAN_REVIEW

        if extracted_fields is not None and len(extracted_fields) == 0:
            logger.warning("[DOCUMENT_GUARDRAIL] Zero fields extracted from document.")
            return False, FALLBACK_HUMAN_REVIEW

        return True, "Confidence passed"

    def get_extraction_result_or_fallback(
        self, confidence_score: float, extracted_fields: Dict[str, Any]
    ) -> Tuple[bool, Any, str]:
        """Returns extracted fields if confidence is sufficient, or human review fallback."""
        is_valid, msg = self.validate_extraction_confidence(confidence_score, extracted_fields)
        if not is_valid:
            return False, None, FALLBACK_HUMAN_REVIEW
        return True, extracted_fields, "Extraction successful"

    def validate_document_file(
        self, mime_type: str, file_size_bytes: int, filename: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Validates document file metadata for size limits and allowed mime types."""
        if mime_type.lower() not in ALLOWED_MIME_TYPES:
            logger.warning(f"[DOCUMENT_GUARDRAIL] Rejected unallowed mime type: {mime_type}")
            return False, f"Unsupported file type: {mime_type}"

        if file_size_bytes > MAX_FILE_SIZE_BYTES:
            logger.warning(f"[DOCUMENT_GUARDRAIL] File size ({file_size_bytes} bytes) exceeds limit.")
            return False, f"File size exceeds maximum limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."

        if filename:
            forbidden_extensions = [".exe", ".bat", ".cmd", ".vbs", ".js", ".ps1", ".sh", ".php", ".py"]
            for ext in forbidden_extensions:
                if filename.lower().endswith(ext):
                    logger.warning(f"[DOCUMENT_GUARDRAIL] Forbidden executable extension detected: {filename}")
                    return False, f"Executable file types are strictly prohibited: {ext}"

        return True, "Document file is valid"


document_security_guardrail = DocumentSecurityGuardrail()
