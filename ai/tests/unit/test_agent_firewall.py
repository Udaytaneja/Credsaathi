"""Unit tests for CredSaathi Agent Firewall and Tool Permission Layer."""
import asyncio
import pytest
from ai.gateway.errors import AIFirewallException, AIRateLimitException, AITimeoutException, AIValidationException
from ai.guardrails.agent_firewall import AgentFirewall
from ai.guardrails.firewall_schemas import AgentPermissionPolicy, ToolExecutionRequest


# Dummy Tool Functions for Testing
def dummy_read_profile(user_id: str):
    return {"user_id": user_id, "name": "Ramesh"}


def dummy_modify_loan_status(application_id: str, new_status: str):
    return {"status": new_status}


async def dummy_slow_tool():
    await asyncio.sleep(2.0)
    return "done"


@pytest.fixture
def firewall():
    fw = AgentFirewall()
    fw.register_tool("read_own_profile", dummy_read_profile)
    fw.register_tool("modify_loan_status", dummy_modify_loan_status)
    fw.register_tool("slow_tool", dummy_slow_tool)
    return fw


@pytest.mark.asyncio
async def test_1_permitted_tool_call(firewall):
    req = ToolExecutionRequest(
        agent_name="Customer Assistant",
        tool_name="read_own_profile",
        user_id="user_123",
        target_user_id="user_123",
        arguments={"user_id": "user_123"}
    )

    res = await firewall.execute_tool(req)
    assert res.success is True
    assert res.tool_name == "read_own_profile"
    assert res.result_data["name"] == "Ramesh"


@pytest.mark.asyncio
async def test_2_denied_tool_call(firewall):
    # Customer Assistant attempting prohibited modify_loan_status tool
    req = ToolExecutionRequest(
        agent_name="Customer Assistant",
        tool_name="modify_loan_status",
        user_id="user_123",
        arguments={"application_id": "APP_01", "new_status": "APPROVED"}
    )

    with pytest.raises(AIFirewallException) as exc_info:
        await firewall.execute_tool(req)

    assert "NOT permitted" in exc_info.value.message
    denied_logs = firewall.get_denied_action_logs()
    assert len(denied_logs) >= 1
    assert denied_logs[-1]["denial_reason"] == "UNAUTHORIZED_TOOL_DISPATCH"


@pytest.mark.asyncio
async def test_3_wrong_user_cross_tenant_mismatch(firewall):
    req = ToolExecutionRequest(
        agent_name="Customer Assistant",
        tool_name="read_own_profile",
        user_id="user_123",
        target_user_id="user_victim_999",
        arguments={"user_id": "user_victim_999"}
    )

    with pytest.raises(AIFirewallException) as exc_info:
        await firewall.execute_tool(req)

    assert "Scope Violation" in exc_info.value.message


@pytest.mark.asyncio
async def test_4_missing_authorization(firewall):
    req = ToolExecutionRequest(
        agent_name="Customer Assistant",
        tool_name="read_own_profile",
        user_id="",
        arguments={}
    )

    with pytest.raises(AIFirewallException) as exc_info:
        await firewall.execute_tool(req)

    assert "User authorization context is missing" in exc_info.value.message


@pytest.mark.asyncio
async def test_5_excessive_calls_rate_limit(firewall):
    policy = AgentPermissionPolicy(
        agent_name="Test Agent",
        allowed_tools=["read_own_profile"],
        max_requests_per_minute=2,
        timeout_seconds=5.0
    )
    firewall.register_policy(policy)

    req = ToolExecutionRequest(
        agent_name="Test Agent",
        tool_name="read_own_profile",
        user_id="user_rate_limit",
        arguments={"user_id": "user_rate_limit"}
    )

    # First 2 calls succeed
    await firewall.execute_tool(req)
    await firewall.execute_tool(req)

    # 3rd call exceeds rate limit
    with pytest.raises(AIRateLimitException):
        await firewall.execute_tool(req)


@pytest.mark.asyncio
async def test_6_tool_execution_timeout(firewall):
    policy = AgentPermissionPolicy(
        agent_name="Test Fast Agent",
        allowed_tools=["slow_tool"],
        timeout_seconds=0.1
    )
    firewall.register_policy(policy)

    req = ToolExecutionRequest(
        agent_name="Test Fast Agent",
        tool_name="slow_tool",
        user_id="user_123"
    )

    with pytest.raises(AITimeoutException):
        await firewall.execute_tool(req)


@pytest.mark.asyncio
async def test_7_malformed_tool_arguments(firewall):
    req = ToolExecutionRequest(
        agent_name="Customer Assistant",
        tool_name="read_own_profile",
        user_id="user_123",
        arguments={"invalid_param": "wrong"}
    )

    with pytest.raises(AIValidationException) as exc_info:
        await firewall.execute_tool(req)

    assert "Malformed arguments" in exc_info.value.message


@pytest.mark.asyncio
async def test_8_prompt_injection_tool_escalation(firewall):
    # Prompt injection attempting to invoke unauthorized direct_db_write / approve_application
    req = ToolExecutionRequest(
        agent_name="Customer Assistant",
        tool_name="approve_application",
        user_id="attacker_user",
        arguments={"application_id": "APP_888"}
    )

    with pytest.raises(AIFirewallException) as exc_info:
        await firewall.execute_tool(req)

    assert "NOT permitted" in exc_info.value.message
    assert exc_info.value.code == "AGENT_FIREWALL_VIOLATION"


@pytest.mark.asyncio
async def test_9_audit_trail_and_registry(firewall):
    registered = firewall.get_registered_tools()
    assert "read_own_profile" in registered
    assert "modify_loan_status" in registered

    req = ToolExecutionRequest(
        agent_name="Customer Assistant",
        tool_name="read_own_profile",
        user_id="user_123",
        arguments={"user_id": "user_123"}
    )
    await firewall.execute_tool(req)

    audit_logs = firewall.get_audit_logs()
    assert isinstance(audit_logs, list)
    assert len(audit_logs) == 1
    assert audit_logs[0]["status"] == "PERMITTED"
    assert audit_logs[0]["tool_name"] == "read_own_profile"


