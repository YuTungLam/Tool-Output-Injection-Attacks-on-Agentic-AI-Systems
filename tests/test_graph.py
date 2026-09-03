from langchain_core.language_models.fake_chat_models import (
    FakeMessagesListChatModel,
)
from langchain_core.messages import AIMessage

from boundary_agent import build_graph
from boundary_agent.tools import mock_web_search

class ToolCallingFakeModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

def test_graph_appends_model_response() -> None:
    model = FakeMessagesListChatModel(
        responses=[AIMessage(content="Test response")]
    )
    graph = build_graph(model)

    result = graph.invoke(
        {"messages": [{"role": "user", "content": "hello"}]}
    )

    assert len(result["messages"]) == 2
    assert result["messages"][0].type == "human"
    assert result["messages"][0].content == "hello"
    assert result["messages"][1].type == "ai"
    assert result["messages"][1].content == "Test response"

def test_graph_executes_tool_and_returns_to_model() -> None:
    model = ToolCallingFakeModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "mock_web_search",
                        "args": {"query": "LangGraph"},
                        "id": "call-1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(
                content="LangGraph is a stateful agent framework."
            ),
        ]
    )
    graph = build_graph(
        model,
        tools=[mock_web_search],
    )

    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Search for LangGraph"}]}
    )

    messages = result["messages"]
    tool_message = messages[-2]
    final_message = messages[-1]

    assert [message.type for message in messages] == [
        "human",
        "ai",
        "tool",
        "ai",
    ]
    assert tool_message.name == "mock_web_search"
    assert tool_message.tool_call_id == "call-1"
    assert tool_message.content == (
        "LangGraph is a framework for building stateful agent workflows."
    )
    assert final_message.content == (
        "LangGraph is a stateful agent framework."
    )