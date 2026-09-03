from boundary_agent import build_graph
from boundary_agent.tools import mock_web_search
from langchain_groq import ChatGroq


model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=2,
)

graph = build_graph(
    model,
    tools=[mock_web_search],
)

result = graph.invoke(
    {
        "messages": [
            ("system", "You are a concise assistant."),
            (
                "user",
                "Use mock_web_search to find information about LangGraph.",
            ),
        ]
    }
)

for message in result["messages"]:
    print(f"{message.type}: {message.content}")

    if getattr(message, "tool_calls", None):
        print(f"tool_calls: {message.tool_calls}")