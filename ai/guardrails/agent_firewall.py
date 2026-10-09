"""CredSaathi Agent Firewall and Tool Permission Layer."""
import asyncio
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from ai.gateway.errors import AIFirewallException, AIRateLimitException, AITimeoutException, AIValidationException
from ai.guardrails.firewall_schemas import AgentPermissionPolicy, ToolExecutionRequest, ToolExecutionResult
from ai.utils.logging import logger


class AgentFirewall:
    """Firewall intercepting all agent tool calls, validating scopes, enforcing allowlists, timeouts, and rate limits."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._policies: Dict[str, AgentPermissionPolicy] = {}
        self._execution_timestamps: Dict[str, List[float]] = {}
        self._denied_action_logs: List[Dict[str, Any]] = []
        self._audit_logs: List[Dict[str, Any]] = []
        self._setup_default_policies()

    def _setup_default_policies(self):
        """Registers default agent permission policies."""
        # 1. Customer Assistant Policy
        self._policies["Customer Assistant"] = AgentPermissionPolicy(
            agent_name="Customer Assistant",
            allowed_tools=[
                "read_own_profile",
                "read_own_application_status",
                "search_approved_knowledge",
                "explain_scheme_information"
            ],
            allowed_scopes=["own_data_only"],
            max_requests_per_minute=20,
            timeout_seconds=5.0
        )

        # 2. Scheme Matching Assistant Policy
        self._policies["Scheme Matching Assistant"] = AgentPermissionPolicy(
            agent_name="Scheme Matching Assistant",
            allowed_tools=[
                "search_approved_knowledge",
                "explain_scheme_information",
                "rank_candidate_schemes"
            ],
            allowed_scopes=["candidate_schemes_only"],
            max_requests_per_minute=30,
            timeout_seconds=5.0
        )

        # 3. Document Extraction Assistant Policy
        self._policies["Document Extraction Assistant"] = AgentPermissionPolicy(
            agent_name="Document Extraction Assistant",
            allowed_tools=[
                "extract_document_fields",
                "normalize_document_text"
            ],
            allowed_scopes=["document_bytes_only"],
            max_requests_per_minute=30,
            timeout_seconds=5.0
        )

    def register_tool(self, tool_name: str, func: Callable) -> None:
        """Register an executable tool function in the Tool Registry."""
        self._tools[tool_name] = func
        logger.info(f"Agent Firewall registered tool '{tool_name}' in Tool Registry.")

    def register_policy(self, policy: AgentPermissionPolicy) -> None:
        """Register or update an agent's permission policy."""
        self._policies[policy.agent_name] = policy

    def get_registered_tools(self) -> List[str]:
        """Return names of all tools registered in the Tool Registry."""
        return list(self._tools.keys())

    async def execute_tool(self, req: ToolExecutionRequest) -> ToolExecutionResult:
        """Executes tool through firewall with allowlist, scope, timeout, and rate-limit checks."""
        start_time = time.time()
        trace_id = f"trace_{uuid.uuid4().hex[:12]}"

        # 1. Check Missing Authorization / Empty User Context
        if not req.user_id or not req.user_id.strip():
            self._log_denied_action(req, "MISSING_USER_CONTEXT", trace_id)
            raise AIFirewallException("User authorization context is missing or empty.", tool_name=req.tool_name)

        # 2. Check Agent Policy
        policy = self._policies.get(req.agent_name)
        if not policy:
            self._log_denied_action(req, "UNKNOWN_AGENT", trace_id)
            raise AIFirewallException(f"Agent '{req.agent_name}' is not registered with firewall policy.", req.tool_name)

        # 3. Check Tool Allowlist
        if req.tool_name not in policy.allowed_tools:
            self._log_denied_action(req, "UNAUTHORIZED_TOOL_DISPATCH", trace_id)
            raise AIFirewallException(
                f"Tool '{req.tool_name}' is NOT permitted for agent '{req.agent_name}'. Action denied.",
                tool_name=req.tool_name
            )

        # 4. Check Target User Scope (Tenant Isolation)
        if req.target_user_id and req.target_user_id != req.user_id:
            self._log_denied_action(req, "CROSS_TENANT_SCOPE_VIOLATION", trace_id)
            raise AIFirewallException(
                f"Scope Violation: Agent cannot access target_user_id '{req.target_user_id}' on behalf of user '{req.user_id}'.",
                tool_name=req.tool_name
            )

        # 5. Check Rate Limit
        rate_key = f"{req.agent_name}:{req.user_id}"
        self._check_rate_limit(rate_key, policy.max_requests_per_minute, req, trace_id)

        # 6. Check Tool Function Existence in Registry
        tool_func = self._tools.get(req.tool_name)
        if not tool_func:
            self._log_denied_action(req, "UNREGISTERED_TOOL_FUNCTION", trace_id)
            raise AIFirewallException(f"Tool function '{req.tool_name}' is not registered in Tool Registry.", req.tool_name)

        # 7. Execute with Timeout & Argument Validation
        try:
            if asyncio.iscoroutinefunction(tool_func):
                res = await asyncio.wait_for(tool_func(**req.arguments), timeout=policy.timeout_seconds)
            else:
                # Wrap sync call in asyncio timeout check
                res = await asyncio.wait_for(asyncio.to_thread(tool_func, **req.arguments), timeout=policy.timeout_seconds)
        except TypeError as e:
            self._log_denied_action(req, "MALFORMED_TOOL_ARGUMENTS", trace_id)
            raise AIValidationException(f"Malformed arguments for tool '{req.tool_name}': {str(e)}", field="arguments")
        except asyncio.TimeoutError:
            self._log_denied_action(req, "TOOL_EXECUTION_TIMEOUT", trace_id)
            raise AITimeoutException(f"Tool '{req.tool_name}' execution timed out after {policy.timeout_seconds}s.")

        exec_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"[FIREWALL_PERMIT] Agent='{req.agent_name}' Tool='{req.tool_name}' Trace={trace_id} ({exec_ms}ms)")

        # Log audit event for successful execution
        self._log_audit_event(req, status="PERMITTED", trace_id=trace_id, execution_time_ms=exec_ms)

        return ToolExecutionResult(
            success=True,
            tool_name=req.tool_name,
            result_data=res,
            execution_time_ms=exec_ms,
            audit_trace_id=trace_id
        )

    def _check_rate_limit(self, key: str, max_per_min: int, req: ToolExecutionRequest, trace_id: str) -> None:
        """Enforces sliding window rate limit for tool calls."""
        now = time.time()
        window_start = now - 60.0
        timestamps = [ts for ts in self._execution_timestamps.get(key, []) if ts > window_start]

        if len(timestamps) >= max_per_min:
            self._log_denied_action(req, "RATE_LIMIT_EXCEEDED", trace_id)
            raise AIRateLimitException(f"Agent tool execution rate limit exceeded ({max_per_min}/min).")

        timestamps.append(now)
        self._execution_timestamps[key] = timestamps

    def _log_denied_action(self, req: ToolExecutionRequest, reason: str, trace_id: str) -> None:
        """Logs denied action event to audit trail."""
        denied_entry = {
            "agent_name": req.agent_name,
            "tool_name": req.tool_name,
            "user_id": req.user_id,
            "target_user_id": req.target_user_id,
            "denial_reason": reason,
            "trace_id": trace_id,
            "timestamp": int(time.time())
        }
        self._denied_action_logs.append(denied_entry)
        self._log_audit_event(req, status=f"DENIED:{reason}", trace_id=trace_id)
        logger.warning(f"[FIREWALL_DENIED] [{reason}] Agent='{req.agent_name}' Tool='{req.tool_name}' User='{req.user_id}' Trace={trace_id}")

    def _log_audit_event(self, req: ToolExecutionRequest, status: str, trace_id: str, execution_time_ms: float = 0.0) -> None:
        """Records structured audit event for tool invocation."""
        audit_entry = {
            "trace_id": trace_id,
            "agent_name": req.agent_name,
            "tool_name": req.tool_name,
            "user_id": req.user_id,
            "target_user_id": req.target_user_id,
            "status": status,
            "execution_time_ms": execution_time_ms,
            "timestamp": int(time.time()),
        }
        self._audit_logs.append(audit_entry)

    def get_denied_action_logs(self) -> List[Dict[str, Any]]:
        """Returns log entries of denied tool executions for security audit."""
        return self._denied_action_logs

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        """Returns complete audit log of tool execution attempts."""
        return self._audit_logs


agent_firewall = AgentFirewall()
