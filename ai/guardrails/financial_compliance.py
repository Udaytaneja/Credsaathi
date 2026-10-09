"""Financial compliance and unsupported claim guardrail."""
import re
from typing import Tuple
from ai.utils.logging import logger

UNSUPPORTED_FINANCIAL_CLAIMS = [
    (r"\b100%\s+approval\b", "compatibility match"),
    (r"\bguaranteed\s+approval\b", "high compatibility"),
    (r"\bguaranteed\s+eligibility\b", "indicative eligibility"),
    (r"\bguarantee\s+loan\b", "facilitate scheme application"),
    (r"\brisk-free\s+loan\b", "standard loan terms apply"),
    (r"\bno\s+repayment\s+required\b", "repayment as per scheme terms"),
    (r"\binstant\s+approval\s+without\s+verification\b", "approval subject to bank verification"),
    (r"\bcredit\s+score\s+boost\b", "financial profile assessment"),
]


class FinancialComplianceGuardrail:
    """Enforces financial regulatory compliance, repairing or rejecting unsupported financial claims."""

    def sanitize_financial_claims(self, text: str) -> str:
        """Repairs non-compliant or unsupported financial claim phrases with compliant language."""
        if not text:
            return ""

        sanitized = text
        for pattern, replacement in UNSUPPORTED_FINANCIAL_CLAIMS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"[FINANCIAL_GUARDRAIL] Replacing non-compliant phrase matching '{pattern}' with '{replacement}'")
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    def check_unsupported_claims(self, text: str) -> Tuple[bool, str]:
        """Checks if text contains unsupported or non-compliant financial claims. Returns (is_compliant, phrase_found)."""
        if not text:
            return True, ""

        for pattern, _ in UNSUPPORTED_FINANCIAL_CLAIMS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.warning(f"[FINANCIAL_GUARDRAIL] Unsupported claim detected: '{match.group(0)}'")
                return False, match.group(0)

        return True, ""


financial_compliance_guardrail = FinancialComplianceGuardrail()
