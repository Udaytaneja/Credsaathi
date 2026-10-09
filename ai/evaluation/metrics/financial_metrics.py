"""Financial metrics: Consistency checks against deterministic backend reference calculations."""
from typing import Any, Dict


def calculate_backend_consistency(ai_values: Dict[str, Any], reference_values: Dict[str, Any], tolerance: float = 0.01) -> float:
    """Calculates consistency score comparing AI financial calculations against backend reference values."""
    if not reference_values:
        return 1.0

    consistent_count = 0
    for key, expected_val in reference_values.items():
        actual_val = ai_values.get(key)
        if actual_val is None:
            continue

        if isinstance(expected_val, (int, float)) and isinstance(actual_val, (int, float)):
            delta = abs(float(expected_val) - float(actual_val))
            denom = max(abs(float(expected_val)), 1.0)
            if (delta / denom) <= tolerance:
                consistent_count += 1
        elif str(actual_val).strip().lower() == str(expected_val).strip().lower():
            consistent_count += 1

    return round(consistent_count / len(reference_values), 4)
