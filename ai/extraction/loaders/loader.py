"""Safe temporary document loader, validation, and format checking."""
import base64
from typing import Tuple
from ai.gateway.errors import AIValidationException

ALLOWED_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/jpg"}
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class DocumentLoader:
    """Safely validates, sanitizes, and unpacks document uploads."""

    def validate_and_load(
        self, file_name: str, base64_content: str
    ) -> Tuple[bytes, str]:
        """Validates extension, size, base64 decoding, and returns binary payload and detected mime type."""
        # 1. Extension check & Path Traversal Sanitization
        clean_name = file_name.replace("\\", "/").split("/")[-1]
        ext = "." + clean_name.split(".")[-1].lower() if "." in clean_name else ""

        if ext not in ALLOWED_EXTENSIONS:
            raise AIValidationException(
                f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}",
                field="file_name"
            )

        # 2. Base64 Decoding & Corrupted payload check
        try:
            raw_bytes = base64.b64decode(base64_content, validate=True)
        except Exception:
            raise AIValidationException("Corrupted or malformed base64 document content.", field="file_bytes_base64")

        if not raw_bytes or len(raw_bytes) == 0:
            raise AIValidationException("Empty document content provided.", field="file_bytes_base64")

        # 3. File Size Validation
        if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
            raise AIValidationException(
                f"File size exceeds maximum allowed limit of 10MB ({len(raw_bytes)} bytes).",
                field="file_bytes_base64"
            )

        # 4. MIME Type detection
        mime_type = "application/pdf" if ext == ".pdf" else f"image/{ext.replace('.', '')}"
        return raw_bytes, mime_type


document_loader = DocumentLoader()
