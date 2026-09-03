"""Minimal LangGraph runtime."""

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState, StateGraph

def build_graph(
    model: BaseChatModel,
    tools: list[BaseTool] | None = None,
):
    bound_model = model.bind_tools(tools) if tools else model

    def model_node(state: MessagesState):
        response = bound_model.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", model_node)
    builder.add_edge(START, "model")
    builder.add_edge("model", END)

    return builder.compile()
