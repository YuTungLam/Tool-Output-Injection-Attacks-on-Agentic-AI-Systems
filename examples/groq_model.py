import json
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from boundary_agent import build_graph
from boundary_agent.tools import mock_web_search
from boundary_agent.tracing import create_trace_event, serialize_message

MODEL_NAME = "openai/gpt-oss-20b"

model = ChatGroq(model=MODEL_NAME)
tools = [mock_web_search]
graph = build_graph(model, tools)

inputs = {
    "messages": [
        SystemMessage(content="You are a concise assistant."),
        HumanMessage(
            content="Use mock_web_search to find information about LangGraph."
        ),
    ]
}

run_id = str(uuid4())
sequence = 1

run_started = create_trace_event(
    run_id=run_id,
    sequence=sequence,
    event_type="run_started",
    data={
        "model": MODEL_NAME,
        "tools": [tool.name for tool in tools],
    },
)
print(json.dumps(run_started, ensure_ascii=False))
sequence += 1

input_received = create_trace_event(
    run_id=run_id,
    sequence=sequence,
    event_type="input_received",
    data={
        "messages": [
            serialize_message(message)
            for message in inputs["messages"]
        ]
    },
)
print(json.dumps(input_received, ensure_ascii=False))
sequence += 1

for event in graph.stream(
        inputs,
        stream_mode="updates",
        version="v2",
):
    if event["type"] != "updates":
        continue

    for node_name, update in event["data"].items():
        for message in update.get("messages", []):
            trace_event = create_trace_event(
                run_id=run_id,
                sequence=sequence,
                event_type="node_message",
                data={
                    "node": node_name,
                    "message": serialize_message(message),
                },
            )
            print(json.dumps(trace_event, ensure_ascii=False))
            sequence += 1