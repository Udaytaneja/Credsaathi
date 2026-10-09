"""Document Type Classifier classifying raw OCR text into document categories."""
from ai.extraction.schemas import SupportedDocumentType


class DocumentClassifier:
    """Classifies document text into supported document types."""

    def classify(self, text: str, hint_type: SupportedDocumentType = None) -> SupportedDocumentType:
        if hint_type and hint_type != SupportedDocumentType.GENERIC:
            return hint_type

        text_lower = text.lower()
        if "salary" in text_lower or "income" in text_lower or "pay slip" in text_lower:
            return SupportedDocumentType.INCOME_PROOF
        elif "bank" in text_lower or "statement" in text_lower or "balance" in text_lower:
            return SupportedDocumentType.BANK_STATEMENT
        elif "gst" in text_lower or "registration" in text_lower or "udyam" in text_lower or "trade" in text_lower:
            return SupportedDocumentType.BUSINESS_REGISTRATION
        elif "aadhaar" in text_lower or "identity" in text_lower or "passport" in text_lower:
            return SupportedDocumentType.IDENTITY_PROOF

        return SupportedDocumentType.GENERIC


classifier = DocumentClassifier()
