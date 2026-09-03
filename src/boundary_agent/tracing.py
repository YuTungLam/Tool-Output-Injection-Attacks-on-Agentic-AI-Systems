"""Trace normalization utilities."""

from typing import Any

from langchain_core.messages import BaseMessage


def serialize_message(message: BaseMessage) -> dict[str, Any]:
    return {
        "message_type": message.type,
        "content": message.content,
        "message_id": message.id,
        "name": message.name,
        "tool_calls": getattr(message, "tool_calls", []),
        "tool_call_id": getattr(message, "tool_call_id", None),
    }