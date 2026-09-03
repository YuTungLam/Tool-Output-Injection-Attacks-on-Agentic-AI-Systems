"""Minimal LangGraph runtime."""

from langgraph.graph import END, START, MessagesState, StateGraph


def mock_model_node(
    state: MessagesState,
) -> dict[str, list[dict[str, str]]]:
    """Read the latest user message and append one assistant message."""

    latest_message = state["messages"][-1]
    return {
        "messages": [
            {
                "role": "assistant",
                "content": f"Received: {latest_message.content}",
            }
        ]
    }


def build_graph():
    """Build and compile the graph."""

    builder = StateGraph(MessagesState)
    builder.add_node("model", mock_model_node)
    builder.add_edge(START, "model")
    builder.add_edge("model", END)
    return builder.compile()
