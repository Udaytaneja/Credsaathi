"""OCR Abstraction Engine for CredSaathi Document AI."""
from typing import Dict, Tuple


class OCREngine:
    """OCR Engine Abstraction providing text extraction and OCR segment confidence."""

    def __init__(self, engine_name: str = "mock-ocr-v1"):
        self.engine_name = engine_name

    def extract_text(self, raw_bytes: bytes, mime_type: str, text_override: str = None) -> Tuple[str, float]:
        """Extracts text and overall document OCR confidence from raw bytes or text override."""
        if text_override is not None:
            # Check for simulated low quality text
            if "LOW_QUALITY_OCR" in text_override:
                return text_override, 0.45
            return text_override, 0.95

        # Fallback text extraction simulation from raw bytes content
        try:
            decoded_str = raw_bytes.decode("utf-8", errors="ignore")
            if decoded_str and len(decoded_str.strip()) > 5:
                if "LOW_QUALITY" in decoded_str:
                    return decoded_str, 0.40
                return decoded_str, 0.92
        except Exception:
            pass

        # Simulated OCR text extraction output for mock binaries
        default_ocr_text = (
            "Salary Slip / Income Certificate\n"
            "Applicant Name: Ramesh Kumar\n"
            "Employer Name: Apex Tech Solutions Pvt Ltd\n"
            "Gross Monthly Income: INR 45,000\n"
            "Date of Issue: 15-09-2026\n"
            "Document Ref: INC-2026-8891"
        )
        return default_ocr_text, 0.90


ocr_engine = OCREngine()
