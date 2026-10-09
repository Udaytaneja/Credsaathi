"""Audit sink abstraction layer for persisting AI audit records."""
import abc
import json
from typing import List, Optional
from ai.audit.schemas import AIAuditRecord
from ai.utils.logging import logger


class AuditSink(abc.ABC):
    """Abstract base class for AI audit record sinks."""

    @abc.abstractmethod
    async def record_audit_event(self, record: AIAuditRecord) -> None:
        """Persists or emits an AI audit record."""
        pass


class InMemoryAuditSink(AuditSink):
    """In-memory audit sink storing audit events for testing and in-process queries."""

    def __init__(self):
        self._records: List[AIAuditRecord] = []

    async def record_audit_event(self, record: AIAuditRecord) -> None:
        self._records.append(record)

    def get_records(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> List[AIAuditRecord]:
        """Filters in-memory audit records by criteria."""
        results = self._records
        if request_id:
            results = [r for r in results if r.request_id == request_id]
        if user_id:
            results = [r for r in results if r.user_id == user_id]
        if task_type:
            results = [r for r in results if r.task_type == task_type]
        return results

    def clear(self) -> None:
        self._records.clear()


class LoggerAuditSink(AuditSink):
    """Logs structured JSON audit records to standard application logs."""

    async def record_audit_event(self, record: AIAuditRecord) -> None:
        logger.info(f"[AI_AUDIT_EVENT] {record.model_dump_json()}")


class CompositeAuditSink(AuditSink):
    """Dispatches audit records to multiple sinks simultaneously."""

    def __init__(self, sinks: List[AuditSink]):
        self.sinks = sinks

    async def record_audit_event(self, record: AIAuditRecord) -> None:
        for sink in self.sinks:
            try:
                await sink.record_audit_event(record)
            except Exception as e:
                logger.error(f"Failed to record audit event in sink {sink.__class__.__name__}: {str(e)}")
