"""Prefix-only source candidates for proposed arguments, never maliciousness labels.

The engine consumes saved v1 events in order. Its inputs are the actual outbound
messages plus verified exposure references, not runtime metadata or evaluator
results. The same consume API can be connected to a future live observer; this
release exports offline prefix replays and makes no pre-execution timing claim.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Iterator

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

from agentdojo_lab.lexical import exact_spans, lcs_evidence


def pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def argument_leaves(value, path="") -> Iterator[tuple[str, object]]:
    """Keep array indices, JSON Pointer escaping and empty containers explicit."""
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from argument_leaves(child, f"{path}/{pointer_token(key)}")
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from argument_leaves(child, f"{path}/{index}")
    else:
        yield path, value


def _text(value) -> str | None:
    if isinstance(value, str):
        return value
    if value is None or type(value) in (int, float, bool):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    return None


def _identity(*parts) -> str:
    raw = json.dumps(parts, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def _message_parts(message: dict) -> Iterator[tuple[str, str]]:
    """Only actual request text; call metadata is included only for assistant role."""
    content = message.get("content")
    if isinstance(content, str):
        yield "/content", content
    elif isinstance(content, list):
        for index, part in enumerate(content):
            if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str):
                yield f"/content/{index}/text", part["text"]
    if message.get("role") == "assistant":
        for index, call in enumerate(message.get("tool_calls") or []):
            args = call.get("function", {}).get("arguments")
            if isinstance(args, str):
                yield f"/tool_calls/{index}/function/arguments", args


def structured_scalars(text: str) -> dict:
    """Locate scalars in JSON/YAML message text without constructing Python objects.

    BaseLoader compose does not execute tags or coerce dates. Reject aliases,
    duplicate mapping keys and excessive structure; use raw text matching as a
    separately labelled fallback. Offsets index the original Unicode string.
    """
    limits = {"max_codepoints": 65536, "max_nodes": 4096, "max_depth": 32}
    if len(text) > limits["max_codepoints"]:
        return {"status": "budget_exceeded", "scalars": [], "limits": limits}
    try:
        root = yaml.compose(text, Loader=yaml.BaseLoader)
        if not isinstance(root, (MappingNode, SequenceNode)):
            return {"status": "plain_text", "scalars": [], "limits": limits}
        leaves, seen = [], set()

        def walk(node, path, depth):
            if id(node) in seen or len(seen) >= limits["max_nodes"] or depth > limits["max_depth"]:
                raise ValueError("unsupported aliases or structure budget")
            seen.add(id(node))
            if isinstance(node, ScalarNode):
                leaves.append(
                    {
                        "field_path": path,
                        "value": node.value,
                        "start": node.start_mark.index,
                        "end": node.end_mark.index,
                    }
                )
            elif isinstance(node, SequenceNode):
                for index, child in enumerate(node.value):
                    walk(child, f"{path}/{index}", depth + 1)
            elif isinstance(node, MappingNode):
                keys = set()
                for key, child in node.value:
                    if not isinstance(key, ScalarNode) or key.value in keys:
                        raise ValueError("non-scalar or duplicate key")
                    keys.add(key.value)
                    walk(child, f"{path}/{pointer_token(key.value)}", depth + 1)

        walk(root, "", 0)
        return {"status": "parsed", "scalars": leaves, "limits": limits}
    except (yaml.YAMLError, ValueError, RecursionError):
        return {"status": "unsupported_structure", "scalars": [], "limits": limits}


class ProvenanceTracker:
    """Incremental, deterministic candidate generation over one event stream."""

    def __init__(self, semantic_matcher=None):
        self.semantic_matcher = semantic_matcher
        self.run_id = None
        self.sequence = 0
        self.seen = set()
        self.results = {}
        self.requests = {}
        self.sources = {}
        self.calls = []

    def _register(self, request, index, message, exposure=None):
        for part_path, text in _message_parts(message):
            role = message["role"]
            source_event = exposure["data"]["source_result_event_id"] if exposure else None
            key = _identity(
                self.run_id, request["episode_id"], role, source_event or f"message:{index}", part_path, text
            )
            source_id = f"source:{key}"
            if source_id not in self.sources:
                self.sources[source_id] = {
                    "source_id": source_id,
                    "run_id": self.run_id,
                    "episode_id": request["episode_id"],
                    "kind": role,
                    "source_event_id": source_event or request["event_id"],
                    "first_observed_sequence": exposure["event_sequence"]
                    if exposure
                    else request["sequence"],
                    "text": text,
                    "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "structure": structured_scalars(text),
                }
            request["sources"].append(
                {
                    "source_id": source_id,
                    "message_index": index,
                    "request_pointer": f"/data/body/messages/{index}{part_path}",
                    "exposure_event_id": exposure["event_id"] if exposure else None,
                }
            )

    def consume(self, event: dict) -> dict | None:
        """Return one frozen call analysis at a proposal; never consult later events."""
        event = copy.deepcopy(event)
        if event.get("schema_version") != 1:
            raise ValueError("Unsupported observation schema")
        if type(event.get("event_sequence")) is not int or event["event_sequence"] != self.sequence + 1:
            raise ValueError("Provenance requires consecutive event order")
        if not event.get("event_id") or event["event_id"] in self.seen:
            raise ValueError("Missing or duplicate event ID")
        if self.run_id is None:
            self.run_id = event.get("run_id")
        if not self.run_id or event.get("run_id") != self.run_id:
            raise ValueError("A tracker consumes exactly one run")
        self.sequence = event["event_sequence"]
        self.seen.add(event["event_id"])
        kind, data = event["event_type"], event["data"]
        if kind == "TOOL_RESULT":
            # Identity only: data.message.tool_call.args is NOT exposed content.
            self.results[event["event_id"]] = {
                "episode_id": event["episode_id"],
                "call_ref": event.get("call_ref"),
                "sequence": self.sequence,
                "tool_call_id": event.get("tool_call_id"),
            }
        elif kind == "MODEL_REQUEST":
            request_id = event["model_request_id"]
            if request_id in self.requests:
                raise ValueError("Duplicate model request ID")
            request = {
                "event_id": event["event_id"],
                "sequence": self.sequence,
                "episode_id": event["episode_id"],
                "messages": data["body"].get("messages", []),
                "sources": [],
                "exposed_indices": set(),
                "proposed": False,
            }
            self.requests[request_id] = request
            for index, message in enumerate(request["messages"]):
                if message.get("role") in {"user", "assistant", "system", "developer"}:
                    self._register(request, index, message)
        elif kind == "TOOL_OUTPUT_EXPOSED":
            request = self.requests[event["model_request_id"]]
            index = data["message_index"]
            source = self.results.get(data.get("source_result_event_id"))
            if request["proposed"]:
                raise ValueError("Exposure arrived after a proposal using its request")
            if (
                type(index) is not int
                or index < 0
                or index >= len(request["messages"])
                or index in request["exposed_indices"]
            ):
                raise ValueError("Invalid or duplicate exposure position")
            message = request["messages"][index]
            if (
                message.get("role") != "tool"
                or message != data["message"]
                or source is None
                or source["episode_id"] != request["episode_id"]
                or event["episode_id"] != request["episode_id"]
                or source["call_ref"] != event.get("call_ref")
                or source["sequence"] >= request["sequence"]
                or source["tool_call_id"] != message.get("tool_call_id")
                or event.get("tool_call_id") != message.get("tool_call_id")
            ):
                raise ValueError("Exposure does not match its actual request and source")
            request["exposed_indices"].add(index)
            self._register(request, index, message, event)
        elif kind == "TOOL_CALL_PROPOSED":
            request = self.requests[event["model_request_id"]]
            expected = {i for i, m in enumerate(request["messages"]) if m.get("role") == "tool"}
            if expected != request["exposed_indices"] or request["episode_id"] != event["episode_id"]:
                raise ValueError("Proposal lacks its complete request exposure mapping")
            request["proposed"] = True
            call = self._analyze(event, request)
            self.calls.append(copy.deepcopy(call))
            return copy.deepcopy(call)
        return None

    def _analyze(self, event, request):
        fields = []
        for path, value in argument_leaves(event["data"]["arguments"]):
            # A zero-argument call has no argument attribution target.
            if path == "" and value == {}:
                continue
            text = _text(value)
            exact, lexical, semantic = [], [], []
            for occurrence in request["sources"]:
                source = self.sources[occurrence["source_id"]]
                base = {**occurrence, "kind": source["kind"], "source_event_id": source["source_event_id"]}
                if text is not None and text:
                    equal = [x for x in source["structure"]["scalars"] if x["value"] == text]
                    if equal:
                        for scalar in equal:
                            exact.append(
                                {
                                    **base,
                                    "evidence_type": "structured_scalar_equal",
                                    "source_field_path": scalar["field_path"],
                                    "start": scalar["start"],
                                    "end": scalar["end"],
                                }
                            )
                    else:
                        for start, end in exact_spans(source["text"], text):
                            exact.append(
                                {
                                    **base,
                                    "evidence_type": "bounded_exact_text",
                                    "source_field_path": None,
                                    "start": start,
                                    "end": end,
                                }
                            )
                score = lcs_evidence(source["text"], text or "")
                lexical.append({**base, **score})
                if self.semantic_matcher is not None:
                    # The scorer sees only this request's visible source and current argument.
                    semantic.append(
                        {**base, **copy.deepcopy(self.semantic_matcher.compare(source["text"], text or ""))}
                    )
            distinct = {x["source_id"] for x in exact}
            fields.append(
                {
                    "item_id": "item:" + _identity(self.run_id, event["episode_id"], event["event_id"], path),
                    "argument_path": path,
                    "value": value,
                    "exact_status": (
                        "multiple_source_candidates"
                        if len(distinct) > 1
                        else "single_source_candidate"
                        if distinct
                        else "no_exact_evidence"
                    ),
                    "exact_candidates": exact,
                    "nt_style_lcs": lexical,
                    **({"nt_style_semantic": semantic} if self.semantic_matcher is not None else {}),
                    "provenance_verdict": "unreviewed",
                    "maliciousness": "not_assessed",
                    "causal_influence": "not_assessed",
                }
            )
        visible = []
        for occurrence in request["sources"]:
            source = self.sources[occurrence["source_id"]]
            visible.append({**source, **occurrence})
        return {
            "run_id": self.run_id,
            "task_id": event.get("task_id"),
            "episode_id": event["episode_id"],
            "proposal_event_id": event["event_id"],
            "proposal_sequence": event["event_sequence"],
            "model_request_id": event["model_request_id"],
            "request_event_id": request["event_id"],
            "request_sequence": request["sequence"],
            "cutoff_event_id": event["event_id"],
            "function": event["data"]["function"],
            "arguments": event["data"]["arguments"],
            "request_messages": request["messages"],
            "visible_sources": visible,
            "fields": fields,
            "availability": "offline_prefix_replay; pre-execution latency not measured",
        }


METHODS = {
    "exact_v1": {
        "description": "Structured scalar equality; otherwise bounded case-sensitive literal text",
        "raw_min_codepoints": 3,
        "short_values": "structured scalar equality only",
        "source_types": ["user", "tool", "assistant", "system", "developer"],
        "normalization": "none for raw text; YAML/JSON scalar decoding is explicitly labelled",
    },
    "nt_style_lcs_v1": {
        "paper": "https://arxiv.org/html/2604.23374v1#S4.SS2",
        "formula": "longest_common_subsequence_length / min(source_length, argument_length)",
        "threshold": 0.15,
        "unit": "unicode_codepoint",
        "case_sensitive": True,
        "source_unit": "actual outbound message text part; no chunking",
        "argument_unit": "JSON leaf; scalar JSON rendering for non-string values",
        "source_types": ["user", "tool", "assistant", "system", "developer"],
        "scope": "paper-based Tier 2 component adaptation; not full NeuroTaint reproduction",
        "assumptions": [
            "paper does not specify character/token unit or serialization",
            "no canary, embeddings, memory lineage, causal judge or policy-based thresholds",
            "user/assistant/system controls are labelled separately from tool sources",
            "threshold hits are candidates, not verified provenance or maliciousness",
        ],
    },
}
