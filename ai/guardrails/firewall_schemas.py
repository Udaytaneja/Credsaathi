"""Pydantic schemas and policies for Agent Firewall and Tool Permission Layer."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentPermissionPolicy(BaseModel):
    """Permission policy defining allowed tools, scopes, and execution limits for an agent."""
    agent_name: str = Field(..., description="Unique agent name e.g. Customer Assistant")
    allowed_tools: List[str] = Field(..., description="Explicit allowlist of tool names")
    allowed_scopes: List[str] = Field(default_factory=lambda: ["own_data_only"], description="Allowed data access scopes")
    max_requests_per_minute: int = Field(default=30, description="Max tool executions per minute per user")
    timeout_seconds: float = Field(default=10.0, description="Max execution duration in seconds")


class ToolExecutionRequest(BaseModel):
    """Payload for invoking a tool through the Agent Firewall."""
    agent_name: str = Field(..., description="Calling agent name")
    tool_name: str = Field(..., description="Target tool name")
    user_id: str = Field(..., description="Authenticated user ID scope")
    target_user_id: Optional[str] = Field(default=None, description="Target user ID if accessing user data")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool execution keyword arguments")


class ToolExecutionResult(BaseModel):
    """Standardized response returned by Agent Firewall after tool execution."""
    success: bool = Field(..., description="Indicates if tool execution succeeded")
    tool_name: str = Field(..., description="Executed tool name")
    result_data: Optional[Any] = Field(default=None, description="Output payload from tool")
    execution_time_ms: float = Field(..., ge=0.0, description="Execution time in milliseconds")
    audit_trace_id: str = Field(..., description="Audit trace identifier")
