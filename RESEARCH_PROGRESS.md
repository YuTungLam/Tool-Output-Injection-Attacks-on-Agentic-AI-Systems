# Research progress and run results

Status date: 2026-09-15 (NeSI local date). This is a checked snapshot, not a live scheduler display.
The [supervisor checklist](RESEARCH_PLAN.md#supervisor-checklist--checked-2026-09-15)
is the source of the completion count. Historical ledgers keep their own scope.

| Scope | Progress | Completed / total |
| --- | --- | ---: |
| Current checklist | **32%** `██████░░░░░░░░░░░░░░` | 8 / 25 |
| Preparation and remaining prerequisites | **67%** `█████████████░░░░░░░` | 8 / 12 |
| Supervisor's new experimental deliverables | **0%** `░░░░░░░░░░░░░░░░░░░░` | 0 / 13 |

Percentages count completed checkboxes equally; they are not estimates of time
remaining, model-download progress, attack success rate, or detector accuracy.
The denominator is the first checklist's 8 completed preparation items, 13
experimental deliverables, and 4 remaining prerequisites. It excludes the older
checklist later in the plan. A partial item remains unchecked. Recovering old
raw artifacts is listed but does not block new named experiments.

The earlier M1–M7 independent method implementation is complete within
[its declared contract](codebase/agentdojo-lab/REPRODUCTION-CONTRACT.md).
That does not complete the supervisor's new experimental deliverables.

## Current work

- CPU container retry **9039259 passed** on Genoa with local SSD, preserving
  the failed first attempt and reusing the verified Scout model.
- GPU smoke **9039289 is waiting for scheduling priority**, with preparation complete. It checks
  synthetic function calls and one benign native AgentDojo task before research.
- The offline single-episode comparison is implemented and verified. Case A implementation was stopped
  by a platform security flag; its incomplete draft is preserved outside active
  source. Proposed payloads and offline fixtures are not live results.

## Run-by-run results

### Model download — job 9029207 — passed

The CPU job completed in **27m 05s**, with scheduler exit `0:0`. All **63 / 63**
selected model files passed checks against the pinned Hugging Face revision,
including **50 safetensors shards totaling 217,283,738,720 bytes** (about
202.4 GiB). The snapshot can be reused; another model download is unnecessary.

This establishes file integrity and gated-model access. It does not demonstrate
that Scout fits the GPUs, starts successfully, or produces valid tool calls.

Evidence: `evidence/scout-download-20260914-v1/model-integrity.json` and the
separate model-preflight receipt in `reports/20260914-nesi-setup-v1/` in the lab.

### Serving container attempt 1 — job 9029215 — failed

The CPU job ran for **50m 31s** and stopped during SIF creation. Slurm records
exit `9:0`; the wrapper records `137`. There is no successful finalization
receipt or completed SIF. The 3,000-second timeout plus 30-second kill grace
matches the elapsed time, so timeout is a plausible explanation; the retained
logs do not conclusively identify the kill reason.

This is an infrastructure failure, not an attack result or evidence about
NeuroTaint. Retain the failed attempt. The recovery uses a separately named
protocol and evidence directory; it must produce a verified SIF before inference.

Evidence: `evidence/container-prep-20260914-v1/{plan.json,build.log,job-exit-code.txt}`
and `evidence/prep-logs/container-9029215.log`.

### GPU smoke attempt 1 — job 9029415 — cancelled before starting

This job required successful model and container preparation. The container
failed, so the GPU job was cancelled with **zero runtime and no start time**.
There were **zero inference requests** and no native task result. This is neither
a passed nor a failed Scout capability test: the test did not execute.

The replacement must use a fresh evidence directory and the recovered container.
Its planned checks are four synthetic requests and at most four benign native
requests, on four A100s for at most one hour. No attack trial is included.

### Serving container attempt 2 — job 9039259 — passed

This separately named retry started on **Genoa g01 at 2026-09-14 22:20 UTC**
(15 September NeSI time). It uses the same pinned OCI software, with node-local
SSD temporary files, gzip level 1, and a 6,600-second build deadline within a
two-hour CPU allocation. It requests eight CPUs and 32 GiB; Slurm allocates
16 logical CPUs. The old incomplete rootfs is preserved and not reused; the
content-addressed OCI cache and verified model are reusable.

The build completed in **391.20 seconds**, followed by **10.15 seconds** for
hashing/publication: about **6m 42s** inside the wrapper. Slurm records **6m 49s**
for the complete job, exit `0:0`. The inspected SIF
is **11,042,500,608 bytes**, SHA-256
`2e34131f9ef3257b67e628e735fa76dee506449152f3882bf50204c92e38b6c2`.
The private site file now contains that checksum. **Container preparation: 100%**
`████████████████████`. GPU runtime compatibility and tool behavior remain untested.

A later start predicted by the scheduler's test-only query was superseded by
immediate backfilling. The successful retry supports this recovery setup; because
storage, compression level and deadline changed together, it does not isolate
which change caused the improvement. The old failure remains recorded.

Evidence: `evidence/container-prep-20260915-v2/`, plus the frozen helper bundle
and submission records in `evidence/scout-recovery-submission-20260915-v2/`.

### GPU smoke attempt 2 — job 9039289 — waiting for scheduling priority

The job's `afterok:9039259` dependency is fulfilled. It is now pending for
scheduling priority. The ceiling is **four A100s for one hour**, 48 requested CPUs and 320 GiB
host RAM, with **at most eight generation requests**. Four synthetic requests
check typed arguments, tool-result IDs, parallel calls and JSON judgments. Only
if those pass will one benign native task use up to four more requests.

This is a scheduled integration check. There are no GPU results or research
outcomes yet. The new evidence directory, `evidence/scout-smoke-20260915-v2/`,
will be created when the job starts. The server stops when the bounded job ends.

### Offline native integration fixture — passed on 2026-09-14

The fixture completed **one simulated tool execution and two mocked model
requests**, produced **15 valid events**, passed native task utility, and generated
per-run HTML. It verifies the recording/runtime/report integration with prescribed
responses. It does not measure Scout behavior or attack success.

Evidence: [offline fixture report](codebase/agentdojo-lab/runs/20260914-nesi-offline-smoke-v1/report.html).

### Software verification — passed after fixes on 2026-09-14

The first full suite had **2,050 passes and 6 failures**: four required missing
plotting dependencies and two exposed a plan-only auditor guard defect. After
restoring the locked dependencies and fixing that guard, the complete rerun
passed **2,056 tests**. A separate HPC suite passed **26 tests plus 25 subtests**.
The original failed log remains alongside the passing logs.

These are software regression results. Test counts are not experimental samples,
and historical passes must not be presented as new runs on a later date.

Evidence: `codebase/agentdojo-lab/reports/20260914-nesi-setup-v1/`:
`pytest-full.txt`, `pytest-full-final.txt`, `pytest-hpc.txt`.

### Recovery tooling verification — passed on 2026-09-15

The updated HPC suite passed **28 tests and 25 subtests**, including finalizer
checks for preserving the original protocol and recording the new retry protocol.
Shell syntax and Ruff checks also pass. This validates the preparation code;
the successful build and input preflight are recorded separately above. Actual
GPU runtime/tool behavior still requires the queued smoke.

Evidence: `codebase/agentdojo-lab/reports/20260915-scout-continuation-v2/pytest-hpc.txt`.

### New Scout research trials — not started

**0 native research sessions started.** No observed clean/attacked recipient
change, new joint-source result, transformed-memory attack, repeated-judgment
estimate, or new supported systematic-failure claim is available yet.

For each future slot, record the condition, fixed request budget, source exposure,
actual calls and changed arguments, successful or failed simulated sink, task
utility, trace/report links, detector evidence, and remaining unknowns. Preserve
failed and incomplete slots; do not replace them or add unplanned trials to obtain
a successful attack.

### Offline paired-report verification — passed on 2026-09-15

The new exporter passed **38 selected tests, including 14 new tests**. It records
input hashes, aligns tool proposals, shows changed argument JSON Pointers,
preserves ambiguous alignments and missing calls, and separates successful runtime
returns from proposals. It links source exposures, observed native state changes,
and existing per-run graphs. Initial environment differences remain explicit;
matching settings and prompt do not prove a controlled experiment.

In the benign scripted fixture, each arm recorded **25 valid events, two tool
proposals, two successful native returns and one file-state change**. The first
changed tool proposal was the second call: the agent copied the different fixture
document into a new file. The report correctly identifies the changed content
argument. The arm label `attacked` is only a comparator label for this fixture;
no malicious research outcome or real model behavior is established.

Open the [paired fixture report](codebase/agentdojo-lab/reports/20260915-paired-report-fixture-v2/index.html).
Its `pair.json`, `validation.json` and `pytest.txt` retain the comparison, source
hashes and test evidence. All 22 in-page evidence links resolve. The source runs
remain unchanged in `runs/20260915-paired-report-fixture-v1/{clean,attacked}`.
The first report/test attempt exposed incorrectly encoded event-fragment IDs;
that defect was fixed before the passing report was exported to a new directory.

This component handles single-episode tool-proposal comparisons. Assistant prose,
cross-session alignment and causal attribution remain outside its scope. The
combined exporter/local-case-runner prerequisite is therefore still unchecked;
the selected local runners and joint/replay support are unfinished.

### Case A implementation attempt — stopped by platform

The implementation subagent ended with the platform message **“This content was
flagged for possible cybersecurity risk.”** This is a Codex/platform tooling
restriction, not a Hugging Face authentication failure, Scout refusal, detector
prediction, or research attack result. No research model requests were made.

Four incomplete draft files were moved byte-for-byte out of active source into
`codebase/agentdojo-lab/reports/20260915-scout-continuation-v2/quarantined-case-a-draft/`.
`quarantine.json` records their original paths and SHA-256 hashes. The root agent
did not finish or execute the stopped draft. It is not an accepted runnable
protocol, and the Case A preparation checkbox remains incomplete. The unaffected
container recovery and offline comparison continued. Resolving this platform
restriction is required before continuing that stopped implementation task.

## Evidence locations and continuing work

External evidence paths above are relative to
`/nesi/project/uoa04799/dyu848/tool-output-lab/`. They stay outside Git; tracked
notes and source code provide the cross-device handoff. Generated lab `runs/`
and `reports/` are also ignored. A missing bundle on another device is not a
new failed experiment.

Inspect live jobs with `squeue -u dyu848`; inspect terminal outcomes with `sacct`.
Update this snapshot from receipts and accounting after each terminal attempt.
A running or queued job has no percentage estimate unless its own instrumentation
provides a measurable denominator. See [HPC_SETUP.md](HPC_SETUP.md) for pins,
resources, current job IDs, and the next deployment gate.
