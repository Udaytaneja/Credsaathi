"""Confidence scoring engine and human-review flag logic."""
from typing import Any, Dict, List, Tuple


class ConfidenceScorer:
    """Calculates per-field confidence scores and determines if human review is required."""

    CONFIDENCE_THRESHOLD = 0.85

    def calculate_confidence(
        self, ocr_doc_confidence: float, fields: Dict[str, Any], missing_mandatory: List[str]
    ) -> Tuple[Dict[str, float], bool, List[str]]:
        """Calculates per-field confidence dictionary and review_required flag."""
        field_conf: Dict[str, float] = {}
        warnings: List[str] = []

        for field_name, value in fields.items():
            if value is not None and value != "":
                # Field confidence is combination of OCR engine score and value quality
                conf = round(min(ocr_doc_confidence * 0.98, 0.99), 2)
            else:
                conf = 0.0

            field_conf[field_name] = conf
            if conf < self.CONFIDENCE_THRESHOLD:
                warnings.append(f"Field '{field_name}' confidence ({conf}) is below threshold ({self.CONFIDENCE_THRESHOLD}).")

        # Determine human review flag
        review_required = False

        if missing_mandatory:
            review_required = True
            warnings.append("Human review required due to missing mandatory document fields.")

        if ocr_doc_confidence < 0.70:
            review_required = True
            warnings.append("Human review required due to low overall OCR confidence.")

        if any(c < self.CONFIDENCE_THRESHOLD for c in field_conf.values()):
            review_required = True

        return field_conf, review_required, warnings


confidence_scorer = ConfidenceScorer()
