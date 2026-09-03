import json
from boundary_agent.tracing import serialize_message
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

inputs = {
    "messages": [
        ("system", "You are a concise assistant."),
        (
            "user",
            "Use mock_web_search to find information about LangGraph.",
        ),
    ]
}

for event in graph.stream(
        inputs,
        stream_mode="updates",
        version="v2",
):
    for node_name, update in event["data"].items():
        for message in update.get("messages", []):
            record = {
                "event_type": event["type"],
                "node": node_name,
                "message": serialize_message(message),
            }

            print(
                json.dumps(
                    record,
                    indent=2,
                    ensure_ascii=False,
                )
            )