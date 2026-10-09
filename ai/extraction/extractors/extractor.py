"""Field Extractor for Document AI using Model Gateway and regex parsing."""
import re
from typing import Any, Dict, Tuple
from ai.model_router.gateway import model_gateway
from ai.schemas.model_gateway import ModelRequest, TaskType
from ai.utils.logging import logger


class FieldExtractor:
    """Extracts key document fields from OCR text."""

    async def extract_fields(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Invokes Model Gateway or regex fallback to extract raw field dictionary."""
        prompt = f"Document Type: {doc_type}\nText Content:\n{text}\nTask: Extract key fields (applicant_name, gross_monthly_income, employer_name, issue_date, document_ref) into JSON."
        sys_prompt = "You are a Document AI extractor. Extract fields accurately without inventing data."

        req = ModelRequest(
            task_type=TaskType.EXTRACTION,
            prompt=prompt,
            system_prompt=sys_prompt,
            temperature=0.1
        )

        try:
            res = await model_gateway.invoke(req)
            if res.structured_output:
                return res.structured_output
        except Exception as e:
            logger.warning(f"Gateway extraction call note: {str(e)}, using fallback regex extractor.")

        # Fallback regex extraction engine
        extracted = {}

        name_match = re.search(r"(?:Applicant Name|Name):\s*([A-Za-z\s]+)", text, re.IGNORECASE)
        if name_match:
            extracted["applicant_name"] = name_match.group(1).strip()

        income_match = re.search(r"(?:Income|Salary|Gross):\s*(?:INR|Rs\.?)?\s*([\d,]+)", text, re.IGNORECASE)
        if income_match:
            extracted["gross_monthly_income"] = income_match.group(1).replace(",", "")

        employer_match = re.search(r"(?:Employer Name|Company|Employer):\s*([A-Za-z0-9\s]+)", text, re.IGNORECASE)
        if employer_match:
            extracted["employer_name"] = employer_match.group(1).strip()

        ref_match = re.search(r"(?:Document Ref|Ref No|Ref):\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        if ref_match:
            extracted["document_ref"] = ref_match.group(1).strip()

        return extracted


extractor = FieldExtractor()
