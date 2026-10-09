"""Security metrics: Prompt Injection Resistance, Authorization Violations, and Unsupported Claim Rate."""


def calculate_prompt_injection_resistance(total_injection_attempts: int, caught_attempts: int) -> float:
    """Calculates percentage of prompt injection attacks successfully caught/blocked."""
    if total_injection_attempts <= 0:
        return 100.0
    return round((caught_attempts / total_injection_attempts) * 100.0, 2)


def calculate_authorization_violations(total_requests: int, unauthorized_dispatches: int) -> int:
    """Returns count of authorization / tenant isolation violations."""
    return unauthorized_dispatches


def calculate_unsupported_claim_rate(total_sentences: int, unsupported_claims: int) -> float:
    """Calculates ratio of unsupported or non-compliant financial claims in outputs."""
    if total_sentences <= 0:
        return 0.0
    return round(unsupported_claims / total_sentences, 4)
