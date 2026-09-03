import json
from uuid import uuid4

from langchain_groq import ChatGroq

from boundary_agent import build_graph
from boundary_agent.tools import mock_web_search
from boundary_agent.tracing import create_trace_event


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

run_id = str(uuid4())
sequence = 1

for event in graph.stream(
        inputs,
        stream_mode="updates",
        version="v2",
):
    for node_name, update in event["data"].items():
        for message in update.get("messages", []):
            record = create_trace_event(
                run_id=run_id,
                sequence=sequence,
                node=node_name,
                message=message,
            )

            print(
                json.dumps(
                    record,
                    indent=2,
                    ensure_ascii=False,
                )
            )

            sequence += 1