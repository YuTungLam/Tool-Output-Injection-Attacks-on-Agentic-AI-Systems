# Project context: Tool Output Injection Attacks

Last updated: 2026-09-15. This is the durable project brief for the researcher,
supervisor, and future Codex sessions. It records the user's initial idea and
supervisor guidance, followed by a separately identified repository assessment.
Update the current-state sections as work progresses; preserve the original intent.

## Original idea supplied by the researcher

Working title: **Idea 2 — Tool Output Injection Attacks**.

### Motivation

Agentic AI systems increasingly rely on external tools such as web search, APIs,
and file systems. Their outputs directly influence agent reasoning,
decision-making, and actions. In practice, tools may return manipulated content,
hidden instructions, or misleading data, and agents may give that material more
authority than it should have.

The initial proposal contrasted this with user-side attacks and identified a gap
in understanding what happens when tool outputs become adversarial inputs. That
is the project's original motivation, not an established claim that prior work
ignores indirect prompt injection. The eventual novelty claim must be narrower
and supported by experiments and a current literature comparison.

**Research question:** How can malicious or manipulated tool outputs influence
agent behavior, and what security risks do they introduce?

### Objectives

1. Investigate how agents process and trust tool outputs.
2. Analyze how malicious outputs alter observable decisions and trigger
   unintended actions, including contamination of tool arguments.
3. Evaluate effects on decision accuracy, task utility, and system safety.
4. Explain propagation from the adversarial source to the security consequence.

Tools participate in the agent's decision-making loop and are a critical attack
surface. Compromised outputs may lead to sensitive data leakage, unsafe actions,
or deviation from the user's intended goal. The longer-term aim is more reliable
interaction between agents and external systems.

### Starting point and move to NeSI

The researcher initially developed this repository on a personal computer, using
Groq's free API. The `codex/agentdojo-lab` branch contains an AgentDojo reproduction
and an independent implementation of NeuroTaint's described methodology, built
with Codex because author code was unavailable to the researcher at that time.
It generates HTML reports to help inspect individual experiments.

Further implementation is to take place on NeSI HPC. The requested first local
model candidate is
[meta-llama/Llama-4-Scout-17B-16E-Instruct](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct).
Local inference is intended to remove dependence on the previous free API quota;
it is a new experimental backend, not a continuation of the same Groq model runs.

## Supervisor guidance after the demonstration

The next useful step is to **stress-test the existing NeuroTaint implementation
and identify failure cases**, with a small set of concrete examples for the next
meeting. Reproducing another approach or building another large system is not
the immediate objective.

Priority dimensions:

- Multiple sources influencing one action, including sources needed jointly and
  redundant sources for which removing one does not resolve responsibility.
- Argument-level influence: the intended tool can remain unchanged while a
  sensitive value, such as an email recipient, changes.
- Longer propagation chains through several tools.
- Provenance lost through summarization, rewriting, or paraphrasing.
- Information persisted in memory and used by a later session.
- Ambiguous influence judgments and inconsistent conclusions across repeated runs.

For a successful attack, reconstruct the complete path:

> Source → entry point → first divergence → intermediate propagation →
> memory/tool interactions → final sink/action.

The supervisor's motivating example is a malicious document or tool output
entering an observation, changing an argument, being written to memory, surviving
into a later session, and influencing a sensitive call or data disclosure.
Likewise, conceptually `send_email(to=user, ...)` may become
`send_email(to=attacker, ...)`: the research must explain where the new value
originated and how it reached the call. The actual AgentDojo schema uses a
`recipients` list; bind analysis to its real argument paths.

For each meeting example, show the clean and attacked executions, where they
first diverge, how influence propagates, the final consequence, and whether the
independent NeuroTaint implementation identifies the complete path. Provide a
flowchart/attack trace with links to supporting events.

**The central question is:**

> “What important propagation or influence pattern is not reliably captured by
> existing approaches, and why?”

A systematic, reproducible failure pattern could establish a more specific
research gap and later motivate a method or defense. A single failed run, an
unexposed source, or a transport/parser issue is insufficient.

## Implementation and evidence boundaries

The method reference is
[Ghost in the Agent: Redefining Information Flow Tracking for LLM Agents, arXiv v1](https://arxiv.org/abs/2604.23374v1).
Its stated scope already includes semantic transformation, causal influence, and
cross-session persistence. These are therefore dimensions to stress-test, rather
than automatically novel capabilities. See the repository's
[reproduction contract](codebase/agentdojo-lab/REPRODUCTION-CONTRACT.md) for the
declared adaptation and underspecified choices.

The repository records M1–M7 as implemented: policy/exposure bindings, explicit
and semantic cascade, file-memory lineage, isolated single/pair judges,
completed-trace composition, integrations, and the online observer. This is an
independent paper-method implementation under an AgentDojo adapter. It is not
proof of equivalence to author code, original datasets, or original numerical
results. Test coverage and detector accuracy are different claims.

Current evaluation keeps the tracer observational. SafeTool, CTTA, weight
updates, action blocking, and new defenses are outside the immediate pilot.
Experiments use the existing native simulated tools and synthetic sensitive data.

## Repository map

Paths in the table are relative to `codebase/agentdojo-lab/` unless stated otherwise.

| Area | Where to look | What it provides |
| --- | --- | --- |
| Runtime/configuration | `src/agentdojo_lab/runner.py`, `providers.py`, `groq_adapter.py`, `cli.py` | Native AgentDojo execution; Groq and explicit OpenAI-compatible endpoints |
| Version pins | `upstream.json`, `pyproject.toml`, `uv.lock`, `scripts/bootstrap.py` | Python 3.12, AgentDojo 0.1.35 at a fixed commit, locked dependencies |
| Observations | `recording.py`, `observation.py`, `online.py` in `src/agentdojo_lab/` | Requests, exposures, proposals, tool execution, and observer receipts |
| Sources and argument fields | `provenance.py`, `policy.py`, `configs/workspace_policy_v1.yaml` | Source bindings and recursive argument leaves with JSON Pointers |
| Detection | `canary.py`, `lexical.py`, `semantic.py`, `cascade.py`, `profiles.py` | Registered Canary, LCS, embeddings, chunk coverage, and fixed profiles |
| Memory/path graph | `lineage.py`, `scripts/run_memory_pair.py` | Typed paths and content-bound file persistence across separate sessions |
| Influence checks | `causal_v2.py`, `causal_v2_audit.py`, `causal_replay.py` | Single/pair interventions, no-tools judge predictions, one-step replays |
| Joined audit | `paper_audit.py`, `online_causal.py` | Completed-trace composition and online proposal-boundary integration |
| Presentation | `html_report.py`, `provenance_report.py`, `templates/` | Interactive per-run timelines and graphs |
| Prior experiments | `ATTACK-VALIDATION-RESULTS.md`, `METHOD-COMPLETION-RESULTS.md`, `NEUROTAINT_EVAL_PROGRESS.json` | Historical outcomes and bounded claims |
| Regression coverage | `tests/` | Historical coverage plus new local-provider regression tests; see current verification below |
| Older separate harness | root `codebase/tool_output_lab/` | Earlier experiment harness; different event schema, not the active lab |

Bare module filenames in this map refer to `src/agentdojo_lab/`.

## Current state on NeSI — 2026-09-15

This continuation began from clean source checkpoint `3c71025` on
`codex/agentdojo-lab`. The current hardened execution and propagation checkpoint
is `84fe7cc`, pushed to `origin/codex/agentdojo-lab`. Recheck these facts on a
later visit.

| Item | Observed state |
| --- | --- |
| Source/configuration/test files | Present in Git |
| Previous raw runs and generated HTML | Historical bundles absent; new setup receipts/offline smoke exist locally |
| Lab environment and AgentDojo checkout | Restored on NeSI; `doctor` verifies the pinned clean upstream |
| Semantic weights | Pinned MiniLM snapshot downloaded and file hashes verified; locked semantic dependencies installed and 53 dependent regressions passed |
| Default Python / lab Python | System 3.9.25; restored lab `.venv` 3.12.14 |
| Local LLM integration | Explicit primary, online, deferred, joint-audit and one-step replay endpoints plus provider-aware doctor coverage implemented; legacy defaults remain unchanged |
| Scout weights/server | All 63 pinned files verified. First container 9029215 FAILED and GPU 9029415 CANCELLED. CPU retry 9039259 COMPLETED in 6m 49s. GPU smoke 9039289 then COMPLETED `0:0` in 9m 54s on `mg15` with four A100 80 GB GPUs; synthetic 4/4 and all nine benign-native checks passed |
| Hugging Face access | Browser login complete; saved identity and authenticated pinned Scout config download verified |
| Model storage | Private scratch root `/nesi/nobackup/uoa04799/dyu848/tool-output-lab`; 10 TiB project scratch allocation |
| NeSI offline smoke | Completed native fixture with a valid 15-event recording and HTML; no real LLM calls |
| Git transport | SSH push and pull tested successfully on this device earlier in the session |
| Scout Case A runner | Hardened 85-source v4 plan prepared with zero requests. First submitted wrapper job 9043206 was cancelled before allocation after audit found a Slurm helper-path defect; zero live Case A requests |
| New case-study pilot | Planned in RESEARCH_PLAN.md; zero new trajectories |

The read-only scheduler assessment found project association `uoa04799` and GPU
nodes; see [HPC_SETUP.md](HPC_SETUP.md) for the dated inventory and feasibility
limits. Scheduler visibility is not proof of a current allocation or available
project GPU-hour balance.

Historical result notes describe successful two-source constructed attacks,
an exact-copy cross-session pilot, and possible early LCS overmatching. Those
are useful leads, but their ignored raw artifacts are not locally available to
reverify. Do not regenerate missing evidence by silently rerunning the models.
The memory copy pilot is not evidence of an actual memory-persistence attack.

The old NT-AgentDojo-Eval-v1 document proposes 120 native trajectories. Its
checked-in ledger records no frozen native plan and zero started trajectories,
despite the older README calling the matrix frozen. The 2026-09-14 guidance
**defers that larger phase** in favor of the small case-study pilot. Original
ledgers and result notes retain their historical values.

## Next actions and unresolved inputs

1. Use [the supervisor checklist](RESEARCH_PLAN.md#supervisor-checklist--checked-2026-09-15)
   to track delivered results separately from existing code and preparation.
2. Finish the corrected Case A helper-path binding, freeze a v2 bundle/site and
   submit one replacement job. Preserve cancelled job `9043206`, which used no
   GPU time or requests.
3. When the replacement becomes terminal, verify its same-allocation synthetic/native
   smoke chain, request accounting and clean/attacked evidence before interpreting
   any recipient or sink result.
4. Use the offline single-episode paired report for changed tool arguments,
   proposal divergence and configured sensitive-field divergence. The separate
   `offline-cross-session-propagation-v2` exporter validates eight typed path
   segments in each existing offline control. The joint auditor and one-step
   replay accept explicit configured OpenAI-compatible endpoints while preserving
   their legacy defaults. Causal influence remains unassessed and attack success
   unknown for the offline controls.
5. Freeze the prepared Case B v2 plan into a same-allocation bundle/site, then
   submit it after review. The strict four-arm runner and wrapper are implemented
   but unsubmitted; they have made no live request. Case C still needs a frozen
   transformed-memory live protocol.

The first 2026-09-15 Case A implementation subagent was stopped by a platform
security-risk flag. Its four unfinished files remain preserved byte-for-byte in
`codebase/agentdojo-lab/reports/20260915-scout-continuation-v2/quarantined-case-a-draft/`
with a hash manifest. A later Daybreak Blue worker, available in this Codex
workspace, verified those hashes, independently reviewed the bounded simulated-tool
design, restored the files and completed the active runner. Root verification
passed 84 selected tests, Ruff and Python compilation; `prepare` records
`prepared_not_executed` and makes zero model requests. This resolves the tooling
restriction for this bounded implementation on the current Codex surface only;
it does not establish access in a separate API project or product. The original
flag and quarantine remain historical evidence. No live Case A request was made,
so this is not a Scout refusal or an experimental finding.

Continuation checkpoint `7b5f1eb` added the separate two-hour smoke-plus-Case-A
wrapper without changing the then-pending smoke job. It requires current-job
Slurm time evidence, at least 3,900 seconds remaining, a live authenticated
loopback server, the exact plan-bound runner, and a recomputed preflight → smoke →
native → execution → terminal evidence chain. The combined ceiling is 24 generation
attempts: 4 synthetic, at most 4 benign native, and at most 16 Case A. Root's final
selection passed **109 tests plus 16 subtests**, Ruff, Bash syntax and Python
compilation. Later source changes correctly invalidated the first three
zero-request preparations. The v3 audit specifically found a missing runtime-read
MiniLM revision pin in its source inventory. The current ignored preparation is
`codebase/agentdojo-lab/runs/scout-case-a-prepared-v4`; it binds 85 source files,
has plan SHA-256
`5e3b9aa67767e2bf0b5c1275dac14742ee02f596efff84f0d6fe2cd4c95b5d31`
and records zero model requests. After smoke `9039289` passed, the exact source at
pushed checkpoint `84fe7cc` was copied into immutable bundle
`evidence/scout-case-a-submission-20260915-v1`, with private site file
`/nesi/project/uoa04799/dyu848/tools/scout-case-a-site-20260915-v1.env`.
Case A job `9043206` was submitted at 15:36 NZST, then cancelled at 15:47 before
allocation when audit found a relative helper path that would resolve from
Slurm's spool directory. Accounting records 00:00:00 elapsed, zero GPU time and
zero requests. Preserve that failed submission record. A corrected v2 bundle and
replacement job are pending; the limits remain 24 requests and eight GPU-hours.

The 2026-09-15 checklist review read Slurm accounting and retained job artifacts.
It did not rerun tests or launch replacement jobs. Container failure and GPU
cancellation are infrastructure outcomes, not research attack trials. Detailed
states and evidence paths are in HPC_SETUP.md.

The user confirms Hugging Face approval, has signed in successfully on NeSI,
and has delegated storage choices. No further authentication input is needed.
Previous run/report bundle locations remain unknown.

Continuation on 2026-09-15: [RESEARCH_PROGRESS.md](RESEARCH_PROGRESS.md) now
provides progress bars and per-run explanations. The first supervisor checklist
is **10/25 complete (40%)**, including preparation; its 13 new experimental
deliverables remain **0/13**. This counts completed items, not elapsed time or
detector accuracy. The new CPU/GPU attempt uses private, separately named
evidence and site files described in HPC_SETUP.md.

The NeSI bootstrap and offline smoke have run. The smoke is
`codebase/agentdojo-lab/runs/20260914-nesi-offline-smoke-v1`; setup receipts are
in `codebase/agentdojo-lab/reports/20260914-nesi-setup-v1`. These are new setup
artifacts, not restored historical experiments or new attack evidence. The final
full verification passed **2,056 repository tests** and **26 HPC tests** (plus
25 HPC subtests), with Ruff, shell syntax and documentation link checks passing.
Logs are `pytest-full-final.txt` and `pytest-hpc.txt` in the setup receipt directory.
The initial full run's six failures are retained in `pytest-full.txt`: four were
missing plotting dependencies; two exposed a plan-only auditor guard bug, which
was fixed without changing frozen protocols. The final full rerun passes.
Live Scout integration inference has now succeeded, but no new research
trajectory has completed. Preparation and smoke evidence is retained in
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/` outside Git.

New 2026-09-15 verification passed **28 HPC tests plus 25 subtests**, and **38
paired/report tests including 14 new tests**; Ruff and shell syntax also passed.
The benign paired fixture has 25 valid events per arm, two successful simulated
tool calls and one file-state change per arm, with zero real model calls. Its
report is `reports/20260915-paired-report-fixture-v2/index.html` in the lab.
This demonstrates the exporter, not a Scout attack. It compares tool proposals
within a single episode; assistant prose and cross-session alignment are outside
that component. Detailed receipts and limitations are in RESEARCH_PROGRESS.md.

The separate bounded cross-session exporter was hardened on 2026-09-15 for Case C
preparation. The new `reports/20260915-cross-session-propagation-v2` report
validates all eight recorded/candidate path segments in both existing offline
controls, including the source read, memory write/version, checkpoint, fresh
session-B restoration and proposed/runtime/result/native sink chain. A 74-test
selection passed, and independent review exercised 22 mutation classes; every
mutation was rejected or downgraded. This is derived engineering-control evidence
with zero live calls. Causal influence was not assessed and attack success remains
unknown.

The joint no-tools auditor and observed one-step replay now have separately named
configured OpenAI-compatible protocols and `--endpoint-config`. They require
explicit `--live`, an environment-only key, zero SDK retries and truthful endpoint/
model receipts; replay preserves the recorded request and rejects a model mismatch.
The earlier 217-test combined selection remains historical verification. The
current ignored report is `reports/20260915-cross-session-propagation-v2`; both
session alignments and graph halves are validated against content-derived IDs and
strict input hashes. The earlier v1 report remains preserved.

The completed Case A runner and its report/provider regressions passed **84
selected tests** on 2026-09-15. Its execution gate requires successful synthetic
and benign native smoke receipts from the same four-A100 serving job before either
clean or attacked slot can make a request. The first submitted job, `9043206`, was
cancelled before allocation after the helper-path audit; it made zero requests
and does not increase the experimental-deliverable count.

The later same-allocation batch validation passed **109 tests and 16 subtests**.
Checkpoint `84fe7cc` strengthens exact runtime, tool-result, native-state and
serving bindings and is pushed. This validates orchestration and evidence
integrity; it is not a Case A result.

After the submission audit, the corrected helper-path and preflight-envelope
selection passed **108 tests plus 16 subtests**, Ruff, Python compilation, Bash
syntax and diff checks. ShellCheck was unavailable. This remediation invalidated
v3 and produced the 85-source v4 plan above; no replacement job is claimed yet.

The Case B four-arm runner is strict about distinct worker processes and exact
proposal → runtime start → runtime return → visible tool result → native state
change evidence. Its reviewed `nesi-scout-smoke-case-b-v1` wrapper requests at
most two hours on four A100s and permits at most 24 total requests: four synthetic,
four benign-native and 16 Case B. The independent final Case A/B selection passed
191 tests plus 16 subtests; root's broader selection passed 214 tests plus 16
subtests. Ruff, Bash syntax, compilation and diff checks passed.
The prepared v2 design inventory has 163 source files, including 113 pinned
AgentDojo runtime/package-metadata files, and a nine-entry launch manifest.
`runs/scout-case-b-prepared-v2` contains exactly `plan.json` and
`preparation.json`; their SHA-256 values are
`69b0b0c2a77bff5057789719ae76a4a05c757a1acc511e3f66f14bd13dff60ff`
and `ba663d561892b614f7320be36a8fc9c4bf363c946c15837ac52e905fa1b45906`.
It records zero model calls. Preserved v1 is source-invalidated. No v2 bundle,
submission or research request is claimed here.

Git synchronization: this continuation started from clean checkpoint **`3c71025`**,
matching `origin/codex/agentdojo-lab`. SSH push and pull were already verified for
repository owner `YuTungLam`. The Case A implementation checkpoint **`6071eb0`**,
batch-preparation checkpoint **`7b5f1eb`**, and hardened execution/propagation
checkpoint **`84fe7cc`** were subsequently pushed to that branch. Git
synchronization does not imply that a corrected Case A job has been submitted;
inspect scheduler and submission receipts separately.

## Moving between devices

Git syncs tracked code, configurations, and these context files on the selected
branch. It ignores `.env`, lab `runs/`, `reports/`, `.venv/`, `.model-cache/`, and
`vendor/`. Root `/docs/` and `/CODEX_HANDOFF.md` are also ignored, which is why
the durable context lives in these root files instead.

For old experiments, transfer selected complete batch directories and their
linked derived report directories through the researcher's normal file-transfer
route. Preserve relative paths, original bytes, failed/quarantined artifacts,
and manifests. Record the source device, batch IDs, destination, and SHA-256
checks; reverify before analysis. Do not copy credentials with the bundle.
Model and semantic-encoder caches can be separately restored or downloaded at
their recorded revisions. Missing bundles remain missing, not recreated runs.

At the end of a work session, update this status and the research plan, commit
the intended tracked changes, and record whether they were pushed. On the next
device, pull the same branch and let AGENTS.md route Codex to these notes. The
new device still needs its own Git/Hugging Face authentication and environment.
