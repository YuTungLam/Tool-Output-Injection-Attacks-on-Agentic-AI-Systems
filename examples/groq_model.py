from boundary_agent import build_graph
from langchain_groq import ChatGroq


model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=2,
)

graph = build_graph(model)

result = graph.invoke(
    {
        "messages": [
            ("system", "You are a concise assistant."),
            ("user", "Explain what an AI agent is in one sentence."),
        ]
    }
)

print(type(graph))
print(type(result))

for message in result["messages"]:
    print(f"{message.type}: {message.content}")