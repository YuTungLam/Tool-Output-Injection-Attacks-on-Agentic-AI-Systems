from langchain_core.language_models.fake_chat_models import (
    FakeMessagesListChatModel,
)
from langchain_core.messages import AIMessage

from boundary_agent import build_graph


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