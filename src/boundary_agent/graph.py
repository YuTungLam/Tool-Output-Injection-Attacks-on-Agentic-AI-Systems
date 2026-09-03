"""Minimal LangGraph runtime."""

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, MessagesState, StateGraph


def build_graph(model: BaseChatModel):
    """Build and compile the graph."""
    def model_node(state: MessagesState):
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", model_node)
    builder.add_edge(START, "model")
    builder.add_edge("model", END)

    return builder.compile()
