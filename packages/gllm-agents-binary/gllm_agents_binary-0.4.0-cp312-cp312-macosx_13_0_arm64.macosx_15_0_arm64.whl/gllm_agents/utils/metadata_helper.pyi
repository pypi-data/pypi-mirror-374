from _typeshed import Incomplete
from enum import StrEnum
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from gllm_agents.utils.token_usage_helper import STEP_USAGE_KEY as STEP_USAGE_KEY, TOTAL_USAGE_KEY as TOTAL_USAGE_KEY
from typing import Any

logger: Incomplete
DEFAULT_STEP_INDICATOR_MESSAGE: str
FINAL_AGENT_THINKING_FINISHED_CONTENT: str
FINAL_THINKING_AND_ACTIVITY_INFO: Incomplete
DEFAULT_THINKING_AND_ACTIVITY_INFO: Incomplete

class Kind(StrEnum):
    """Constants for metadata kind values."""
    AGENT_STEP = 'agent_step'
    AGENT_THINKING_STEP = 'agent_thinking_step'
    FINAL_RESPONSE = 'final_response'
    FINAL_THINKING_STEP = 'final_agent_thinking_step'
    AGENT_DEFAULT = 'agent_default'

class Status(StrEnum):
    """Constants for metadata status values."""
    RUNNING = 'running'
    FINISHED = 'finished'
    STOPPED = 'stopped'

class MetadataFieldKeys(StrEnum):
    """Enumeration of standard metadata field keys used in A2A events."""
    KIND = 'kind'
    STATUS = 'status'
    TIME = 'time'
    MESSAGE = 'message'
    TOOL_INFO = 'tool_info'
    REFERENCES = 'references'
    THINKING_AND_ACTIVITY_INFO = 'thinking_and_activity_info'
    STEP_USAGE = STEP_USAGE_KEY
    TOTAL_USAGE = TOTAL_USAGE_KEY

class MetadataTimeTracker:
    """Tracks cumulative execution time across agent steps for final response metadata.

    This class provides a clean way to accumulate execution times from individual
    agent steps and apply the total time to final response metadata.
    """
    def __init__(self) -> None:
        """Initialize the time tracker with zero accumulated time."""
    def update_response_metadata(self, response: dict[str, Any]) -> dict[str, Any]:
        """Update response metadata with accumulated time tracking.

        Args:
            response: Response dictionary containing metadata

        Returns:
            Response with updated metadata for final responses. If any error occurs,
            returns the original response unchanged.
        """

def detect_agent_step_content(content: str, default_kind: str, tool_calls: Any | None = None) -> str:
    """Detect if content corresponds to agent step patterns from LangGraph.

    Args:
        content: The content to detect.
        default_kind: The default kind to return if the content does not match any of the patterns.
        tool_calls: The tool calls to detect.

    Returns:
        The kind of the content.
    """
def create_metadata(content: str = '', kind: Kind = ..., status: Status = ..., tool_calls: Any | None = None, is_final: bool = False, time: float | None = None, existing_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create metadata for A2A responses with content-based message.

    Args:
        content: The content to create metadata for.
        kind: The kind of the content.
        status: The status of the content.
        tool_calls: The tool calls to create metadata for.
        is_final: Whether the content is final.
        time: The time of the content.
        existing_metadata: Optional existing metadata to merge with. Existing metadata
            takes precedence over generated metadata for conflicting keys.

    Returns:
        The metadata for the content, merged with existing metadata if provided.
    """
def create_tool_processing_metadata(original_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create metadata for tool processing events (tool_call and tool_result).

    Args:
        original_metadata: Optional original metadata to merge with.

    Returns:
        Metadata dictionary with agent_thinking_step kind and no message/time/status.
    """
def create_status_update_metadata(content: str, custom_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create metadata for status update events with content-based rules.

    Args:
        content: The content of the status update.
        custom_metadata: Optional custom metadata to merge with.

    Returns:
        Metadata dictionary following the specific rules for different content types.
    """
