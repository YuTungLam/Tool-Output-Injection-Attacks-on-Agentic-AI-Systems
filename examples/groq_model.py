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

last_message = result["messages"][-1]

print(last_message.content)
print(last_message.tool_calls)