"""Schema validator and mandatory field checker for Document AI."""
from typing import Any, Dict, List, Tuple


class DocumentValidator:
    """Validates extracted document fields against mandatory schemas."""

    MANDATORY_FIELDS = {
        "income_proof": ["applicant_name", "gross_monthly_income"],
        "bank_statement": ["applicant_name"],
        "business_registration": ["employer_name"],
        "generic": []
    }

    def validate(self, doc_type: str, fields: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Returns warnings list and missing mandatory fields list."""
        warnings: List[str] = []
        missing_mandatory: List[str] = []

        required = self.MANDATORY_FIELDS.get(doc_type, [])
        for req_field in required:
            if req_field not in fields or fields[req_field] is None or fields[req_field] == "":
                missing_mandatory.append(req_field)
                warnings.append(f"Missing mandatory field '{req_field}' for document type '{doc_type}'.")

        return warnings, missing_mandatory


validator = DocumentValidator()
