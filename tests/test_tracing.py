import json

from langchain_core.messages import AIMessage, ToolMessage

from boundary_agent.tracing import (
    TRACE_SCHEMA_VERSION,
    create_trace_event,
    serialize_message,
)
from datetime import datetime, timezone

def test_serialize_ai_message_with_tool_call() -> None:
    message = AIMessage(
        content="",
        id="message-1",
        tool_calls=[
            {
                "name": "mock_web_search",
                "args": {"query": "LangGraph"},
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )

    record = serialize_message(message)

    assert record["message_type"] == "ai"
    assert record["message_id"] == "message-1"
    assert record["tool_calls"][0]["name"] == "mock_web_search"
    assert record["tool_calls"][0]["args"] == {"query": "LangGraph"}
    assert json.loads(json.dumps(record)) == record


def test_serialize_tool_message() -> None:
    message = ToolMessage(
        content="Search result",
        name="mock_web_search",
        tool_call_id="call-1",
    )

    record = serialize_message(message)

    assert record["message_type"] == "tool"
    assert record["name"] == "mock_web_search"
    assert record["tool_call_id"] == "call-1"
    assert record["content"] == "Search result"
    assert json.loads(json.dumps(record)) == record

def test_create_trace_event() -> None:
    message = AIMessage(
        content="Final answer",
        id="message-1",
    )

    event = create_trace_event(
        run_id="run-1",
        sequence=1,
        node="model",
        message=message,
    )

    assert event["schema_version"] == TRACE_SCHEMA_VERSION
    assert event["run_id"] == "run-1"
    assert event["sequence"] == 1
    assert event["event_type"] == "node_message"
    assert event["node"] == "model"
    assert event["message"]["content"] == "Final answer"

    timestamp = datetime.fromisoformat(event["timestamp_utc"])
    assert timestamp.tzinfo == timezone.utc
    assert json.loads(json.dumps(event)) == event