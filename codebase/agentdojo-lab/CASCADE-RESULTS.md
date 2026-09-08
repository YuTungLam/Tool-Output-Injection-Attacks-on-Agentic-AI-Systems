# Policy and ordered cascade validation — 2026-09-08

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: paper-based implementation and prospective integration validation
- Origin Date: 2026-09-08
- Verification Status: gate 4 accepted within the disclosed ordinary passive condition
- Version Label: workspace-ordered-cascade-validation-v1

## Implemented scope

The observer now supports a frozen source/sink policy and ordered, per-source/argument comparisons.
The workspace registry covers all 24 native tools: 13 source roles, 11 sink roles and one neutral role.
`get_unread_emails` has both source and sink roles because it returns messages and changes their read state.
The normalized policy SHA-256 is
`5e2fe7a0bfe5297c41ecc03a0bd7701138afa214aa212b7f30b80b6f7f51636c`.

The route explicitly records disabled Tier 1, then LCS, whole-text MiniLM and chunk coverage. A hit stops
only that pair's later stages. Other eligible sources still receive their own comparisons. Missing scores,
excluded roles/arguments, unknown tools, empty arguments and no-argument sinks retain separate statuses.
The exact baseline remains independent. Saved reports include the normalized policy document; live
verification restores that snapshot rather than reloading a potentially changed policy filename.

The primary agent still receives its original requests and tool outputs. No canary, action interception,
parameter update, attack trial or causal probe is introduced. The fixed protocol and paper-to-adapter
choices are in [CASCADE.md](CASCADE.md).

## Ten saved real traces

| Measurement | Observation |
| --- | ---: |
| Recorded runs / proposed calls / leaf arguments | 10 / 21 / 54 |
| Selected sink proposals / selected leaf arguments | 9 / 38 |
| Eligible source/argument pairs | 43 |
| First hit at Tier 2 | 43 |
| Tier 3 / Tier 4 skipped after a hit | 43 / 43 |
| Actual semantic encoder entry calls | 0 |
| Unclassified proposal / source occurrences | 0 / 0 |
| Incomplete applicable pairs | 0 |

Two replays with separately constructed pinned local encoders produced identical call analyses. The
54-item blank annotation package is byte-identical to the earlier independent-scoring package. The old
exact-baseline counts remain 27 single-source candidates, four multiple-source candidates and 23 fields
without exact evidence. These counts are descriptions of algorithm output, not independent labels.

All 43 eligible pairs meet the fixed LCS threshold. Their LCS scores range from 0.1875 to 1.0, with median
1.0. This observation demonstrates actual early stopping, and it also motivates later checks of candidate
specificity. A long tool result can share a short subsequence with many arguments. Without independent
source judgments, these matches cannot be called correct attribution, false positives or a demonstrated
research gap. No threshold was changed after observing this result.

Encoder entry was instrumented before its cache boundary. Zero calls therefore means the semantic stages
were not invoked, rather than merely served from a warm cache. Model forward counts and comparative
latency benefit were not measured. The earlier 214 independent comparisons use a different source/sink
denominator and must not be treated as a paired speedup baseline.

## Fresh real-agent integration and controls

One new Groq `openai/gpt-oss-120b` execution of `workspace/user_task_20` passed native utility, exiting with
code 0. All three proposals had analysis and flush receipts before runtime entry. All saved call analyses
match replay exactly except for the explicitly different availability label.

| Measurement | Observation |
| --- | ---: |
| Real trials / model requests / recorded events | 1 / 4 / 35 |
| Proposed / executed calls | 3 / 3 |
| Analyses / flush receipts / runtime timing records | 3 / 3 / 3 |
| Policy sink proposals / selected sink fields | 1 / 5 |
| All argument fields / eligible cascade pairs | 7 / 10 |
| First hit at Tier 2 / incomplete pairs | 10 / 0 |
| API input / output tokens | 8,135 / 282 |
| Agent elapsed / quota pacing wait | 198.315 s / 194.958 s |
| Synchronous consumer time across all 35 events | 175.031 ms |

The selected sink is `create_calendar_event`; two prior retrieval sources are compared with each of its
five supplied fields. The two retrieval proposals still receive sidecar records with their policy scope.
Timing is diagnostic under shared desktop activity, excluding model loading and report generation; it
does not establish a speedup against the prior live trial or a hard analysis deadline.

Five native SDK/runtime controls use the actual semantic matcher with an instrumented deterministic
encoder. They test LCS stopping before any encoding, whole-text stopping before chunk encoding, a chunk
hit, exhausted comparisons and competing sources. Actual requests, actions, native history, environment
and SDK statistics agree with the corresponding uninstrumented controls, and receipts are persisted at
the runtime entry boundary. These fixtures validate routing, not semantic quality.

A supplementary local control with the real pinned MiniLM uses a fixed benign multi-sentence source and
the literal target `ZZZZ` to reach the semantic stages. Both stages execute, make two encoder-entry calls,
and agree with independent component scores within a predeclared absolute tolerance of 1e-6; coverage
also agrees. The input specification is saved before its execution. This added consistency control is
separate from the frozen ten-trace replay and does not use task labels.

The full suite passes **552 tests** in 11.81 seconds; Ruff passes. Static HTML/data checks and Node script
syntax checks pass; browser visual testing was not performed. The language audit finds no Chinese text
in **37 HTML files and 68 decoded JSONL files**. Runtime, policy, model-pin and protocol hashes remain
unchanged from preflight; all 124 protected old-batch files and the new run's source records are unchanged.

## Evidence and commands

- [Saved-trace cascade viewer](reports/20260908-cascade-pilot-v1/index.html)
- [Replay equality and encoder-entry observations](reports/20260908-cascade-validation/replay-verification.json)
- [Frozen code, policy, protocol and input hashes](reports/20260908-cascade-validation/preflight.json)
- [Fresh-run configuration](configs/groq_cascade.toml)
- [Fresh run and interactive timeline](runs/20260908-cascade-groq-task20/report.html)
- [Fresh-run cascade evidence viewer](reports/20260908-cascade-task20-prefix-replay/index.html)
- [Live timing, policy and replay verification](reports/20260908-cascade-validation/live-verification.json)
- [Real MiniLM staged control](reports/20260908-cascade-validation/staged-encoder-control.json)
- [Execution record](reports/20260908-cascade-validation/execution.json) and [quality checks](reports/20260908-cascade-validation/quality.json)

From `agentdojo-lab`, use a new output directory for every experiment. This replays the fixed old traces
without API calls:

```bash
.venv/bin/dojo-lab provenance \
  --batch runs/20260907T025045Z-clean-pilot-b93eae95 \
  --policy configs/workspace_policy_v1.yaml \
  --semantic-model .model-cache/all-MiniLM-L6-v2-1110a243 \
  --semantic-revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 \
  --output reports/cascade-replay-new
```

For another real integration trial:

```bash
.venv/bin/dojo-lab run --config configs/groq_cascade.toml
```

The recorded replay operation additionally repeats analysis with a new encoder and checks the blank
annotation bytes. Its exact script and hash are saved with the preflight record. Runs, derived reports
and local model weights remain Git-ignored and must be synchronized separately when changing machines.
Do not resume the old frozen pilot with the modified runtime.

## Remaining scope

This gate is the ordinary, direct-visible-source policy and active Tier 2–4 route. It is not the complete
paper method. The separate canary condition, DCPG lineage/memory restoration, isolated counterfactual
analysis and independent clean/injected evaluation remain pending. There are no independent attribution
accuracy, malicious-propagation or causal results yet.

The next implementation gate is DCPG lineage and memory restoration, including the distinction between
an observed tool boundary and a candidate information-flow edge. A sink-only output such as a newly
created file ID is currently excluded by the retrieval-source policy; the report preserves that coverage
limitation. Zero-argument mutation/control effects likewise have no explicit argument target. Neither
case is evidence of a safe action or absent influence.
