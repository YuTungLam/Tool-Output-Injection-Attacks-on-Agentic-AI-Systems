# Method completion and automatic-control results

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: implementation, bounded execution and validation
- Origin Date: 2026-09-10
- Verification Status: ANALYZED; real executions and controlled reference results retained
- Version Label: method-completion-v1

The [new phase ledger](METHOD_COMPLETION_PROGRESS.json) tracks five scoped deliverables.
Open [the compact English overview](reports/20260910-method-completion-v1/index.html).
Neither this count nor the historical seven-of-eight count measures full-paper equivalence.

## Implementation

`profiles.get_profile` exposes immutable ordinary, memory, implicit_string and safe_control
thresholds. The direct runtime accepts `cascade_profile = "implicit_string"` or
`cascade_profile = "safe_control"` in a normal run TOML with a source/sink policy.
Restored memory retains its own fixed profile. Default ordinary serialization is preserved;
legacy frozen evaluation protocols explicitly reject the new profiles.

`causal_v2` is a separate opt-in planner for complete negative active-stage evidence,
passive Canary-disabled inputs, and argument-free selected sinks. It validates source,
request-prefix and DCPG binding. Missing, failed and inapplicable stages remain distinct.
Single and pair neutralizations have explicit source/byte budgets, with unknown outcomes
for inseparable sources or unplanned pairs. Bound judgments describe predicted dependency
patterns only. The v1 planner remains the default with its original conservative behavior.

Export verified recorded-prefix plans without model calls:

```bash
.venv/bin/python -m agentdojo_lab.causal_v2 \
  --run runs/20260909-counterfactual-native-control/implicit-no-audit \
  --output reports/NEW-causal-plans
```

The separate `causal_v2_audit` transport uses a pair-aware, no-tools English prompt and binds
every judgment to its exact intervention. Its default CLI mode makes no requests; `--live`
explicitly enables a bounded Groq audit. It does not rerun the primary agent or turn subjective
confidence into causal probability. Transport validation in this phase uses mock responses;
the only real model calls in this phase are the four-session pilot below.

```bash
.venv/bin/python -m agentdojo_lab.causal_v2_audit \
  --plans reports/NEW-causal-plans --output reports/NEW-audit-plan
```

## Automatic reference results

The deterministic fixture program fixes 18 cases and 21 source-pair references before any
detector or embedding call: 10 positive, 8 negative and 3 unknown. The actual pinned MiniLM
scores all 84 slots across four profiles; no scoring errors occurred, and reference, plan,
profile and implementation hashes stayed unchanged.

| Profile | Cascade TP | FP | FN | TN | Unknown reference |
|---|---:|---:|---:|---:|---:|
| ordinary | 10 | 7 | 0 | 1 | 3 |
| memory | 10 | 7 | 0 | 1 | 3 |
| implicit_string | 10 | 4 | 0 | 4 | 3 |
| safe_control | 10 | 7 | 0 | 1 | 3 |

These labels come from the known program constructing each target, including cases where
identical text exists in an unused source. They are not human labels, hidden model provenance,
or real-agent false-positive estimates. Three unknown references are not silently assigned
negative labels. Each profile reuses the same cases; they are not 84 independent scenarios.

Every cascade positive first hits Tier1 or Tier2. The separately scored semantic components
do not become later-stage cascade hits. Raising the safe-control semantic threshold leaves
the early LCS route unchanged in this matrix. This supports examining candidate specificity;
it does not establish a confirmed flaw in the original authors' implementation.

Read [the cases](reports/20260910-reference-controls-v1/index.html) and
[the 11-category interpretation audit](reports/20260910-method-completion-validation-v1/reference-interpretation.json).

## Real cross-session paired pilot

[The live pilot](runs/20260910-memory-pair-live-v1/index.html) completed all four session slots
in four separate processes using Groq `openai/gpt-oss-120b`: twelve primary requests, 4,830
reported tokens, no provider failures or retries. Each branch starts before initial source
exposure; Session A copies file 1 into memory, and a fresh Session B reads the resulting
memory file and copies it into an output file. Native storage and private observer state
are persisted/restored separately. Histories are empty at each session start.

All four observed copies are exact, use only the expected read/write route, and retain
complete recorder/sidecar/checkpoint evidence. Eight executed proposals have pre-runtime
receipts. In the original branch, Session B's `/content` match binds to the original source
through the actual restored memory record. The unique reference appears in the original
output and is absent from the neutralized output. The neutralized branch still has ordinary
benign file provenance; marker absence is not a negative verdict about all information flow.

This is a user-authorized synthetic copy task, not an AgentDojo built-in task or injection
attack. One original/neutralized pair is a descriptive integration experiment. It does not
measure stochastic causal effect, semantic attribution, malicious propagation or joint-judge
accuracy. Source-content intervention also updates its derived native size metadata.

The first offline preflight exposed stale file-size metadata and failed B restoration;
its artifacts remain in `runs/20260910-memory-pair-offline-preflight-v1`. The second preflight
passed after the setup repair. Stricter process-outcome, origin-match and expected-read
checks were added and tested before the sole live pilot. No live slot was replaced.

## Remaining evidence and reproducibility

General memory backends, independent real-agent attribution, real joint-control accuracy,
unseen tools/attacks and original result tables remain unvalidated. The old independent
human-review gate is not reclassified using these automatic controls. No CTTA, model-weight
updates or action blocking was added.

Source and result notes belong on `codex/agentdojo-lab`; runtime evidence remains ignored
by Git and needs separate transfer if required, excluding credentials. Final test, language,
source integrity and static HTML receipts live in `reports/20260910-method-completion-validation-v1`.
The final frozen-source suite passed all 1,579 tests; Ruff passed. The language audit found
no Chinese in 169 HTML and 273 JSONL files. Static checks found no broken local file links
in the 16 new HTML artifacts. All 1,932 protected historical files retained their hashes;
the live-pilot and reference-control artifact and implementation manifests also matched.
An earlier suite run detected two concurrent-edit integrity mismatches; its receipt remains
retained and is superseded by the final run after all implementation writers stopped.
Automatic browser opening of local HTML was blocked by browser security policy; visual
layout and interactive browser acceptance are not claimed for the new overview.
