"""Prompt injection, input sanitization, and malicious payload security guardrails."""
import re
from typing import Tuple
from ai.gateway.errors import AIGuardrailViolationException
from ai.utils.logging import logger

INJECTION_PATTERNS = [
    r"ignore\s+((all|previous|above|system)\s+)*(instructions|prompts|rules)",
    r"override\s+(system|security|rules|guardrails)",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"forget\s+all\s+(your\s+)?rules",
    r"bypass\s+(firewall|auth|permission)",
    r"disregard\s+prior\s+directives",
    r"system_prompt_override",
    r"eval\(|exec\(|import\s+os|subprocess\.",
]

MALICIOUS_DOC_PATTERNS = [
    r"<script\b[^>]*>(.*?)</script>",
    r"javascript:",
    r"<\?php",
    r"SELECT\s+.*\s+FROM\s+information_schema",
    r"DROP\s+TABLE",
    r"UNION\s+SELECT",
]


class PromptSecurityGuardrail:
    """Detects prompt injection attempts, malicious payload injections, and sanitizes input prompts."""

    def sanitize_input_prompt(self, text: str) -> str:
        """Sanitizes control characters and whitespace from input text."""
        if not text:
            return ""
        # Remove null bytes and non-printable control characters (except standard whitespace)
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        return sanitized.strip()

    def check_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """Checks for prompt injection patterns. Returns (is_safe, reason)."""
        if not text:
            return True, "Empty input"

        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"[GUARDRAIL_PROMPT_INJECTION] Caught suspicious pattern: '{pattern}'")
                return False, f"Prompt injection detected matching pattern: '{pattern}'"

        return True, "Input is clean"

    def validate_input_prompt(self, text: str) -> str:
        """Sanitizes prompt and raises AIGuardrailViolationException if prompt injection is detected."""
        clean_text = self.sanitize_input_prompt(text)
        is_safe, reason = self.check_prompt_injection(clean_text)
        if not is_safe:
            raise AIGuardrailViolationException(message=f"Access denied: {reason}", guardrail_name="prompt_security")
        return clean_text

    def check_malicious_document_content(self, content: str) -> Tuple[bool, str]:
        """Checks document content for embedded malicious scripts or injection strings."""
        if not content:
            return True, "Empty content"

        for pattern in MALICIOUS_DOC_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning(f"[GUARDRAIL_MALICIOUS_DOC] Caught malicious content pattern: '{pattern}'")
                return False, f"Malicious document content detected: '{pattern}'"

        return True, "Document content is clean"


prompt_security_guardrail = PromptSecurityGuardrail()
