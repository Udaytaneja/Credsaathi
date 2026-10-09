"""Unit tests for CredSaathi AI Auditability & Telemetry Package."""
import pytest
from ai.audit import (
    AIAuditRecord,
    AuditService,
    CompositeAuditSink,
    InMemoryAuditSink,
    LoggerAuditSink,
    audit_service,
)


@pytest.mark.asyncio
async def test_1_create_and_record_ai_audit_event():
    svc = AuditService()
    svc.clear_in_memory_records()

    record = svc.create_record(
        request_id="req_test_100",
        task_type="SCHEME_MATCHING",
        user_id="user_abc",
        application_id="app_555",
        model_provider="CredSaathi-Internal",
        model_name="scheme-matcher",
        model_version="v2.1",
        prompt_template_version="pt_v1.0",
        retrieval_source_ids=["doc_chunk_1", "doc_chunk_2"],
        tool_calls=[{"tool": "rank_candidate_schemes", "status": "SUCCESS"}],
        latency_ms=145.2,
        prompt_tokens=350,
        completion_tokens=120,
        total_cost_usd=0.002,
        output_validation_status="PASSED",
        guardrail_events=[{"guardrail": "financial_compliance", "status": "CLEAN"}],
        human_review_required=False,
    )

    await svc.record_event(record)

    records = svc.get_in_memory_records(request_id="req_test_100")
    assert len(records) == 1
    rec = records[0]
    assert rec.request_id == "req_test_100"
    assert rec.task_type == "SCHEME_MATCHING"
    assert rec.user_id == "user_abc"
    assert rec.model_name == "scheme-matcher"
    assert len(rec.retrieval_source_ids) == 2
    assert rec.latency_ms == 145.2
    assert rec.human_review_required is False


@pytest.mark.asyncio
async def test_2_in_memory_sink_filtering():
    sink = InMemoryAuditSink()

    rec1 = AIAuditRecord(request_id="req_1", user_id="user_a", task_type="TASK_A")
    rec2 = AIAuditRecord(request_id="req_2", user_id="user_b", task_type="TASK_B")
    rec3 = AIAuditRecord(request_id="req_3", user_id="user_a", task_type="TASK_B")

    await sink.record_audit_event(rec1)
    await sink.record_audit_event(rec2)
    await sink.record_audit_event(rec3)

    assert len(sink.get_records(user_id="user_a")) == 2
    assert len(sink.get_records(task_type="TASK_B")) == 2
    assert len(sink.get_records(request_id="req_2")) == 1


@pytest.mark.asyncio
async def test_3_data_minimization():
    rec = AIAuditRecord(
        request_id="req_min",
        user_id="user_min",
        task_type="DOCUMENT_EXTRACTION",
        guardrail_events=[{"event": "pii_redacted"}],
    )

    # Ensure model dump has metadata but no raw sensitive prompt or output fields
    dump = rec.model_dump()
    assert "request_id" in dump
    assert "user_id" in dump
    assert "raw_prompt" not in dump
    assert "raw_output" not in dump
    assert "document_bytes" not in dump


@pytest.mark.asyncio
async def test_4_composite_sink_resilience():
    memory_sink = InMemoryAuditSink()
    logger_sink = LoggerAuditSink()
    composite = CompositeAuditSink([memory_sink, logger_sink])

    rec = AIAuditRecord(request_id="req_comp", task_type="TEST_TASK")
    await composite.record_audit_event(rec)

    assert len(memory_sink.get_records()) == 1
