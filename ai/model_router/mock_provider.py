"""Mock Model Provider implementation for unit testing and local execution without external API keys."""
import asyncio
import time
from typing import Any, Dict, Optional
from ai.gateway.errors import AIModelException, AITimeoutException
from ai.model_router.base_provider import BaseModelProvider
from ai.schemas.common import ModelMetadata
from ai.schemas.model_gateway import CostMetadata, ModelRequest, ModelResponse, TaskType


class MockModelProvider(BaseModelProvider):
    """Mock model provider with controllable behavior for testing timeouts, errors, and task responses."""

    def __init__(
        self,
        provider_name: str = "mock-provider",
        model_name: str = "mock-llm-v1",
        version: str = "1.0.0",
        delay_seconds: float = 0.0,
        should_fail: bool = False,
        should_timeout: bool = False,
        should_return_malformed: bool = False,
        failure_message: str = "Simulated provider error",
    ):
        self.provider_name = provider_name
        self.model_name = model_name
        self.version = version
        self.delay_seconds = delay_seconds
        self.should_fail = should_fail
        self.should_timeout = should_timeout
        self.should_return_malformed = should_return_malformed
        self.failure_message = failure_message

    def get_metadata(self) -> ModelMetadata:
        return ModelMetadata(
            provider=self.provider_name,
            model=self.model_name,
            version=self.version
        )

    async def invoke(self, request: ModelRequest) -> ModelResponse:
        start_time = time.time()

        if self.should_timeout:
            await asyncio.sleep(self.delay_seconds + 5.0)
            raise AITimeoutException(message="Mock execution timed out")

        if self.delay_seconds > 0:
            await asyncio.sleep(self.delay_seconds)

        if self.should_fail:
            raise AIModelException(
                message=self.failure_message,
                model_metadata=self.get_metadata()
            )

        if self.should_return_malformed:
            # Returns content that fails downstream JSON parsing or structured schema validation
            return ModelResponse(
                content="INVALID_JSON_{{{bad_syntax",
                structured_output=None,
                metadata=self.get_metadata(),
                cost=CostMetadata(prompt_tokens=10, completion_tokens=5, total_tokens=15),
                request_id=request.request_id,
                execution_time_ms=(time.time() - start_time) * 1000,
                audit_metadata={"task_type": request.task_type.value, "mock": True}
            )

        # Generate task-specific response content
        content, structured = self._generate_task_output(request)
        execution_time_ms = (time.time() - start_time) * 1000

        prompt_len = len(request.prompt.split())
        completion_len = len(content.split())
        cost = CostMetadata(
            prompt_tokens=prompt_len,
            completion_tokens=completion_len,
            total_tokens=prompt_len + completion_len,
            estimated_cost_usd=(prompt_len + completion_len) * 0.000002
        )

        return ModelResponse(
            content=content,
            structured_output=structured,
            metadata=self.get_metadata(),
            cost=cost,
            request_id=request.request_id,
            execution_time_ms=execution_time_ms,
            audit_metadata={
                "task_type": request.task_type.value,
                "user_id": request.user_id,
                "mock": True
            }
        )

    def _generate_task_output(self, request: ModelRequest) -> tuple[str, Optional[Dict[str, Any]]]:
        """Generates mock output based on task type."""
        tt = request.task_type
        if tt == TaskType.CLASSIFICATION:
            return "ELIGIBLE", {"category": "ELIGIBLE", "confidence": 0.95}
        elif tt == TaskType.EXTRACTION:
            import re
            name_m = re.search(r"Applicant Name:\s*([^\n]+)", request.prompt)
            name = name_m.group(1).strip() if name_m else None
            inc_m = re.search(r"Gross Monthly Income:\s*(?:INR)?\s*(\d+)", request.prompt)
            inc = float(inc_m.group(1)) if inc_m else None
            emp_m = re.search(r"Employer Name:\s*([^\n]+)", request.prompt)
            emp = emp_m.group(1).strip() if emp_m else None
            fields = {}
            if name:
                fields["applicant_name"] = name
            if inc:
                fields["gross_monthly_income"] = inc
            if emp:
                fields["employer_name"] = emp
            return '{"extracted": "mock_data"}', fields if fields else None
        elif tt == TaskType.SUMMARIZATION:
            return f"Summary of input: {request.prompt[:50]}...", {"summary": request.prompt[:50]}
        elif tt == TaskType.SCHEME_MATCHING:
            return "Scheme match evaluation completed.", {"matched_schemes": ["SCHEME_001"], "score": 0.88}
        elif tt == TaskType.FINANCIAL_EXPLANATION:
            return "Financial narrative explanation.", {"explanation": "Debt-to-income ratio is healthy."}
        else:
            return f"Mock response for task '{tt.value}': {request.prompt}", {"result": "ok"}
