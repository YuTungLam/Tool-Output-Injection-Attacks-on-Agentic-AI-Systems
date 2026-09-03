"""Minimal LangGraph runtime."""

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState, StateGraph


def build_graph(
    model: BaseChatModel,
    tools: list[BaseTool] | None = None,
):
    resolved_tools = tools or []
    tools_by_name = {
        tool.name: tool
        for tool in resolved_tools
    }
    bound_model = (
        model.bind_tools(resolved_tools)
        if resolved_tools
        else model
    )

    def model_node(state: MessagesState):
        response = bound_model.invoke(state["messages"])
        return {"messages": [response]}

    def tool_node(state: MessagesState):
        tool_messages = []
        last_message = state["messages"][-1]

        for tool_call in last_message.tool_calls:
            selected_tool = tools_by_name[tool_call["name"]]
            tool_result = selected_tool.invoke(tool_call["args"])

            tool_messages.append(
                ToolMessage(
                    content=str(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": tool_messages}

    def route_after_model(state: MessagesState):
        last_message = state["messages"][-1]

        if last_message.tool_calls:
            return "tools"

        return "end"

    builder = StateGraph(MessagesState)
    builder.add_node("model", model_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "model")
    builder.add_conditional_edges(
        "model",
        route_after_model,
        {
            "tools": "tools",
            "end": END,
        },
    )
    builder.add_edge("tools", "model")

    return builder.compile()