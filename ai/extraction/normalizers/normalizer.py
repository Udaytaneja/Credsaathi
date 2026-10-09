"""Field Normalizer for cleaning currency, numbers, text, and dates."""
import re
from typing import Any, Dict


class FieldNormalizer:
    """Normalizes extracted raw field values into standard types (floats, strings, dates)."""

    def normalize(self, raw_fields: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        for key, val in raw_fields.items():
            if val is None:
                continue

            # Normalize income/currency fields
            if "income" in key or "salary" in key or "amount" in key:
                normalized[key] = self._normalize_float(val)
            elif "name" in key or "employer" in key:
                normalized[key] = str(val).strip().title()
            else:
                normalized[key] = str(val).strip()

        return normalized

    def _normalize_float(self, val: Any) -> float:
        """Parses numeric floats from string representation."""
        if isinstance(val, (int, float)):
            return float(val)
        val_str = str(val).replace(",", "").replace("INR", "").replace("Rs.", "").strip()
        match = re.search(r"[\d\.]+", val_str)
        if match:
            try:
                return float(match.group(0))
            except ValueError:
                pass
        return 0.0


normalizer = FieldNormalizer()
