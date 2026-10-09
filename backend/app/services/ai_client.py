import logging
import uuid
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger("credsaathi.ai_client")


class AIServiceError(Exception):
    """Base exception for AI microservice communication errors."""
    def __init__(self, message: str, status_code: int = 502, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class AIServiceTimeoutError(AIServiceError):
    """Exception raised when AI microservice call times out."""
    def __init__(self, message: str = "AI service request timed out"):
        super().__init__(message, status_code=504)


class AIServiceConnectionError(AIServiceError):
    """Exception raised when AI microservice connection fails."""
    def __init__(self, message: str = "AI microservice is unavailable"):
        super().__init__(message, status_code=503)


class AIServiceResponseError(AIServiceError):
    """Exception raised when AI microservice returns non-200 response or invalid payload."""
    pass


class AIServiceClient:
    """
    HTTP Client for backend integration with CredSaathi AI microservice.
    
    Handles headers, timeouts, correlation IDs, error mapping, and safe logging.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
    ):
        self.base_url = (base_url or settings.ai_service_url).rstrip("/")
        self.api_key = api_key or settings.ai_api_key
        self.timeout = timeout or settings.ai_service_timeout

    def _get_headers(self, correlation_id: str | None = None) -> dict[str, str]:
        cid = correlation_id or uuid.uuid4().hex
        return {
            "X-API-Key": self.api_key,
            "X-Correlation-ID": cid,
            "Content-Type": "application/json",
        }

    async def _post(
        self,
        endpoint: str,
        payload: dict[str, Any],
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        cid = correlation_id or uuid.uuid4().hex
        headers = self._get_headers(cid)

        # Safe logging: log endpoint, cid, payload keys (no API keys)
        logger.info(
            "Sending request to AI microservice endpoint=%s correlation_id=%s keys=%s",
            endpoint,
            cid,
            list(payload.keys()),
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                logger.info(
                    "Received response from AI microservice endpoint=%s status=%d correlation_id=%s",
                    endpoint,
                    response.status_code,
                    cid,
                )

                if response.status_code != 200:
                    try:
                        err_json = response.json()
                    except Exception:
                        err_json = response.text
                    raise AIServiceResponseError(
                        message=f"AI service returned HTTP {response.status_code}",
                        status_code=response.status_code,
                        details=err_json,
                    )

                data = response.json()
                if isinstance(data, dict) and "data" in data:
                    return data["data"]
                return data

        except httpx.TimeoutException as e:
            logger.error("AI service timeout endpoint=%s correlation_id=%s error=%s", endpoint, cid, str(e))
            raise AIServiceTimeoutError(f"AI microservice request to '{endpoint}' timed out.") from e

        except (httpx.ConnectError, httpx.RequestError) as e:
            logger.error("AI service connection failure endpoint=%s correlation_id=%s error=%s", endpoint, cid, str(e))
            raise AIServiceConnectionError(f"Failed to connect to AI microservice at '{url}'.") from e

    async def match_schemes(
        self,
        applicant_context: dict[str, Any],
        candidate_schemes: list[dict[str, Any]],
        language: str = "en",
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Call AI scheme matching microservice."""
        if not candidate_schemes:
            raise ValueError("Candidate schemes list cannot be empty.")

        payload = {
            "applicant_context": applicant_context,
            "candidate_schemes": candidate_schemes,
            "language": language,
        }
        return await self._post("/scheme-match", payload, correlation_id)

    async def extract_document(
        self,
        file_name: str,
        document_type: str = "generic",
        file_bytes_base64: str | None = None,
        file_text_override: str | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Call AI document extraction microservice."""
        payload = {
            "document_type": document_type.lower(),
            "file_name": file_name,
            "file_bytes_base64": file_bytes_base64,
            "file_text_override": file_text_override,
        }
        return await self._post("/extract-document", payload, correlation_id)

    async def generate_financial_explanation(
        self,
        financial_profile: dict[str, Any],
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Call AI financial explanation microservice."""
        return await self._post("/financial-explanation", financial_profile, correlation_id)

    async def query_assistant(
        self,
        query: str,
        authenticated_user_id: str,
        application_id: str | None = None,
        language: str = "en",
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Call Saakshi assistant AI microservice."""
        payload = {
            "query": query,
            "language": language,
            "authenticated_user_id": authenticated_user_id,
            "application_id": application_id,
        }
        return await self._post("/assistant/query", payload, correlation_id)


ai_service_client = AIServiceClient()
