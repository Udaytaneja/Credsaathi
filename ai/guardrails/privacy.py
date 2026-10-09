"""PII detection/redaction and cross-user information leakage guardrail."""
import re
from typing import Dict, List, Optional, Tuple
from ai.gateway.errors import AIGuardrailViolationException
from ai.utils.logging import logger

PII_PATTERNS: Dict[str, str] = {
    "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "AADHAAR": r"\b[2-9]{1}[0-9]{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b",
    "PHONE": r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
}


class PrivacyGuardrail:
    """Handles PII detection, redaction, and cross-user authorization scope verification."""

    def redact_pii(self, text: str, preserve_types: Optional[List[str]] = None) -> str:
        """Redacts PII instances from text replacing them with placeholders like [REDACTED_PAN]."""
        if not text:
            return ""

        preserve_types = preserve_types or []
        redacted = text

        for pii_type, pattern in PII_PATTERNS.items():
            if pii_type in preserve_types:
                continue

            matches = re.findall(pattern, redacted, re.IGNORECASE)
            if matches:
                logger.info(f"[PRIVACY_GUARDRAIL] Redacting {len(matches)} instance(s) of {pii_type}")
                redacted = re.sub(pattern, f"[REDACTED_{pii_type}]", redacted, flags=re.IGNORECASE)

        return redacted

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """Detects presence of PII and returns dictionary of detected types and matched strings."""
        if not text:
            return {}

        detected: Dict[str, List[str]] = {}
        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[pii_type] = matches

        return detected

    def validate_user_scope(self, current_user_id: str, target_user_id: Optional[str]) -> bool:
        """Enforces cross-user tenant boundary. Raises AIGuardrailViolationException if unauthorized access is attempted."""
        if not current_user_id or not current_user_id.strip():
            logger.warning("[PRIVACY_GUARDRAIL] Missing current_user_id context.")
            raise AIGuardrailViolationException("Access denied.", guardrail_name="privacy_user_scope")

        if target_user_id and target_user_id != current_user_id:
            logger.warning(
                f"[PRIVACY_GUARDRAIL] Cross-user access attempt blocked: user '{current_user_id}' requested target '{target_user_id}'."
            )
            raise AIGuardrailViolationException("Access denied.", guardrail_name="privacy_user_scope")

        return True


privacy_guardrail = PrivacyGuardrail()
