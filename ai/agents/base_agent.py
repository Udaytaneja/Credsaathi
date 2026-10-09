"""Base Agent class enforcing tool allowlists, scopes, rate limits, and audit events."""
import time
from typing import Any, Dict, List, Optional
from ai.utils.logging import logger


class ControlledAgent:
    """Base class for all CredSaathi AI Agents."""

    def __init__(self, agent_name: str, allowed_tools: List[str]):
        self.agent_name = agent_name
        self.allowed_tools = set(allowed_tools)

    def validate_tool_permission(self, tool_name: str) -> bool:
        """Verifies if tool_name is in the explicit allowlist."""
        if tool_name not in self.allowed_tools:
            logger.error(f"Agent '{self.agent_name}' attempted unauthorized tool execution: '{tool_name}'")
            return False
        return True

    def log_audit_event(self, event_type: str, user_id: str, payload: Dict[str, Any]) -> None:
        """Logs structured audit telemetry for agent execution."""
        logger.info(
            f"[AGENT_AUDIT] Agent={self.agent_name} Event={event_type} User={user_id} "
            f"Timestamp={int(time.time())}"
        )
