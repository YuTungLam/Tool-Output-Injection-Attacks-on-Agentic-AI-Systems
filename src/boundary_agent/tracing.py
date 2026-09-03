"""Trace normalization utilities."""

from datetime import datetime, timezone
from typing import Any

from langchain_core.messages import BaseMessage

TRACE_SCHEMA_VERSION = "1.0"


def serialize_message(message: BaseMessage) -> dict[str, Any]:
    return {
        "message_type": message.type,
        "content": message.content,
        "message_id": message.id,
        "name": message.name,
        "tool_calls": getattr(message, "tool_calls", []),
        "tool_call_id": getattr(message, "tool_call_id", None),
    }


def create_trace_event(
        *,
        run_id: str,
        sequence: int,
        event_type: str,
        data: dict[str, Any],
) -> dict[str, Any]:
    if not run_id:
        raise ValueError("run_id must not be empty")

    if sequence < 1:
        raise ValueError("sequence must be at least 1")

    if not event_type:
        raise ValueError("event_type must not be empty")

    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "run_id": run_id,
        "sequence": sequence,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "data": data,
    }