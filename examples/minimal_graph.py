"""Run the minimal graph without an API key or network connection."""

from boundary_agent import build_graph


graph = build_graph()
result = graph.invoke(
    {"messages": [{"role": "user", "content": "What is an agent?"}]}
)

for message in result["messages"]:
    print(f"{message.type}: {message.content}")
