"""Audit service manager for recording, routing, and querying AI operations."""
import time
from typing import Any, Dict, List, Optional
from ai.audit.schemas import AIAuditRecord
from ai.audit.sink import AuditSink, CompositeAuditSink, InMemoryAuditSink, LoggerAuditSink
from ai.utils.logging import logger


class AuditService:
    """Orchestrates AI operation auditing and routes audit events to configured sinks."""

    def __init__(self, sinks: Optional[List[AuditSink]] = None):
        self.in_memory_sink = InMemoryAuditSink()
        self.logger_sink = LoggerAuditSink()
        default_sinks = sinks if sinks is not None else [self.in_memory_sink, self.logger_sink]
        self._composite_sink = CompositeAuditSink(default_sinks)

    def add_sink(self, sink: AuditSink) -> None:
        """Adds a new audit sink to the active composite sink."""
        self._composite_sink.sinks.append(sink)

    async def record_event(self, record: AIAuditRecord) -> None:
        """Asynchronously records an AI audit event."""
        logger.info(
            f"[AUDIT_RECORD] Task='{record.task_type}' ReqID='{record.request_id}' "
            f"User='{record.user_id}' Latency={record.latency_ms}ms Status='{record.output_validation_status}'"
        )
        await self._composite_sink.record_audit_event(record)

    def create_record(
        self,
        request_id: str,
        task_type: str,
        user_id: Optional[str] = None,
        application_id: Optional[str] = None,
        model_provider: Optional[str] = None,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        prompt_template_version: Optional[str] = None,
        retrieval_source_ids: Optional[List[str]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        latency_ms: float = 0.0,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_cost_usd: Optional[float] = None,
        output_validation_status: str = "PASSED",
        guardrail_events: Optional[List[Dict[str, Any]]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        human_review_required: bool = False,
    ) -> AIAuditRecord:
        """Factory helper method for constructing AIAuditRecord instances."""
        return AIAuditRecord(
            request_id=request_id,
            user_id=user_id,
            application_id=application_id,
            task_type=task_type,
            model_provider=model_provider,
            model_name=model_name,
            model_version=model_version,
            prompt_template_version=prompt_template_version,
            retrieval_source_ids=retrieval_source_ids or [],
            tool_calls=tool_calls or [],
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost_usd=total_cost_usd,
            output_validation_status=output_validation_status,
            guardrail_events=guardrail_events or [],
            errors=errors or [],
            human_review_required=human_review_required,
        )

    def get_in_memory_records(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> List[AIAuditRecord]:
        """Retrieves audit records captured by the internal memory sink."""
        return self.in_memory_sink.get_records(request_id=request_id, user_id=user_id, task_type=task_type)

    def clear_in_memory_records(self) -> None:
        """Clears records in memory sink."""
        self.in_memory_sink.clear()


audit_service = AuditService()
