import json

from langchain_core.messages import AIMessage, ToolMessage

from boundary_agent.tracing import serialize_message


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