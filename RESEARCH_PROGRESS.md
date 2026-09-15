# Research progress and run results

Status date: 2026-09-15 (NeSI local date). This is a checked snapshot, not a live scheduler display.
The [supervisor checklist](RESEARCH_PLAN.md#supervisor-checklist--checked-2026-09-15)
is the source of the completion count. Historical ledgers keep their own scope.

| Scope | Progress | Completed / total |
| --- | --- | ---: |
| Current checklist | **40%** `████████░░░░░░░░░░░░` | 10 / 25 |
| Preparation and remaining prerequisites | **83%** `█████████████████░░░` | 10 / 12 |
| Supervisor's new experimental deliverables | **0%** `░░░░░░░░░░░░░░░░░░░░` | 0 / 13 |

Percentages count completed checkboxes equally; they are not estimates of time
remaining, model-download progress, attack success rate, or detector accuracy.
The denominator is the first checklist's 10 completed preparation/prerequisite
items, 13 experimental deliverables, and 2 unfinished prerequisites. It excludes
the older checklist later in the plan. A partial item remains unchecked. Recovering old
raw artifacts is listed but does not block new named experiments.

The earlier M1–M7 independent method implementation is complete within
[its declared contract](codebase/agentdojo-lab/REPRODUCTION-CONTRACT.md).
That does not complete the supervisor's new experimental deliverables.

## Current work

- CPU container retry **9039259 passed** on Genoa with local SSD, preserving
  the failed first attempt and reusing the verified Scout model.
- GPU smoke **9039289 passed** in 9m 54s on four A100 80 GB GPUs. Its four
  synthetic requests and three-request benign native task all passed.
- The offline single-episode comparison and bounded Case A runner are implemented
  and verified. The first Case A attempt's platform flag and quarantined draft
  remain preserved; Daybreak Blue completed the retry on this Codex surface. The
  current 85-source Case A plan is prepared. The first immutable
  same-allocation bundle/site produced job **9043206**, which was cancelled before
  allocation after an audit found a Slurm helper-path defect. The corrected v2
  bundle passed request-free validation and a GO audit; replacement job **9050478**
  is pending for Priority with zero runtime, no allocation and no model requests.
  Configured joint/replay transport and the cross-session exporter are also
  verified offline. Proposed payloads and offline fixtures are not live results.
- The strict Case B four-arm runner and same-allocation wrapper are reviewed and
  test-clean. Its v2 plan and immutable bundle passed offline validation. Job
  **9052477** is pending for Priority with zero runtime, no allocation and no
  model calls. Case A job **9050478** also remains pending for Priority.

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

The later replacement used a fresh evidence directory and the recovered container.
Its four synthetic requests and at-most-four-request benign native scope remained
within one hour on four A100s. No attack trial was included.

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
`████████████████████`. GPU runtime and tool behavior were subsequently verified
by the smoke below.

A later start predicted by the scheduler's test-only query was superseded by
immediate backfilling. The successful retry supports this recovery setup; because
storage, compression level and deadline changed together, it does not isolate
which change caused the improvement. The old failure remains recorded.

Evidence: `evidence/container-prep-20260915-v2/`, plus the frozen helper bundle
and submission records in `evidence/scout-recovery-submission-20260915-v2/`.

### GPU smoke attempt 2 — job 9039289 — passed

Slurm started the job automatically after its dependency and scheduling wait. It
ran on `mg15` with **four A100 SXM4 80 GB GPUs**, 96 allocated logical CPUs and
320 GiB host RAM. It completed in **9m 54s** with exit `0:0`. vLLM
`0.29.0+cu129` loaded 50 model shards across four workers; the slowest worker took
375.30 seconds and reported 52.72 GiB loaded per worker. The loopback server was
ready at 14:54:38 NZST.

All **4 / 4 synthetic requests passed**:

| Check | Result | Elapsed |
| --- | --- | ---: |
| One typed tool call | Exact Unicode array and null arguments | 2.024 s |
| Tool-result round trip | Matching call ID and final receipt ID | 1.460 s |
| Parallel tools | Exactly two integer-argument calls | 2.220 s |
| No-tools judge | Valid JSON and different-recipient judgment | 3.455 s |

The benign native `user_task_0` then passed with **3 requests**, 24 recorded
events and two successful simulated tool round trips. All nine required checks
passed: framework completion, task utility, one evaluable task, request cap,
complete recording, valid links, native tool round trip, HTML export, and no
online auditors. The total was **7 / 8 allowed generation requests**. Prompt and
completion usage for the native run was 14,021 and 89 tokens respectively.

This verifies the pinned Scout container, four-GPU load, typed tool protocol,
JSON response path and one benign AgentDojo loop. It does not test an attack or
NeuroTaint attribution. Evidence is under
`evidence/scout-smoke-20260915-v2/`; SHA-256 values are
`cf6ac029df212ce19a9ab171b0e841e26b13423fa9d86a29588d2ff3c79465ea`
(`preflight.json`),
`f239a98ceb184be2ff63eaafe68f5e40f46965b38b17b9cb49749d9237bd3f34`
(`container-runtime.json`),
`d7c2b167ab7c1ebd014b16c6fb0cb195323535db2620a5ae921376dd2a287a48`
(`smoke.json`),
`283361a3e17c8e98f0d71a28fc624be6910243f92e7b01cad5d7c7ac2c8d3192`
(`native-smoke.json`) and
`9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
(`job-exit-code.txt`). The scheduler log hash is
`31cf94502677f83157cfb228ec7ba7cb0dd33623d2aa0975b0ba844c2311fcca`.

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
the successful build, input preflight and later GPU smoke are recorded separately
above.

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
cross-session alignment and causal attribution remain outside its scope. The later
cross-session exporter handles ordered session pairs separately; it does not alter
this component or infer causal influence.

### Case A implementation attempt — stopped by platform

The first implementation subagent ended with the platform message **“This content was
flagged for possible cybersecurity risk.”** This is a Codex/platform tooling
restriction, not a Hugging Face authentication failure, Scout refusal, detector
prediction, or research attack result. No research model requests were made.

Four incomplete draft files were moved byte-for-byte out of active source into
`codebase/agentdojo-lab/reports/20260915-scout-continuation-v2/quarantined-case-a-draft/`.
`quarantine.json` records their original paths and SHA-256 hashes. The root agent
did not finish or execute that stopped draft. At that checkpoint it was not an
accepted runnable protocol. The unaffected container recovery and offline
comparison continued.

### Case A Daybreak Blue retry — offline implementation passed

A Daybreak Blue worker started successfully in the current Codex workspace,
confirming access for this product surface. It first matched all four preserved
files against `quarantine.json`, independently reviewed the bounded simulated-tool
scope, restored them as active source, and completed the runner, tests and protocol.
This does not establish Daybreak access for a separate API organization, project,
or product surface.

Root verification passed **84 selected Case A, paired-report, runner and local-provider
tests** in 21.67 seconds. Ruff and Python compilation passed. The CLI `prepare`
path returned `prepared_not_executed` with **0 model requests**. Outcome extraction
requires a unique, ordered proposal → runtime start → runtime return chain with
matching function and arguments, explicit null error fields, and an identical new
native sent-email object. Malformed, return-only and duplicate evidence remains
unconfirmed. Native attachment `19` serializes as `attachments: ["19"]`.

The active protocol is [CASE-A-SCOUT-V1.md](codebase/agentdojo-lab/CASE-A-SCOUT-V1.md),
and implementation checkpoint **`6071eb0`** is pushed to
`origin/codex/agentdojo-lab`. The original quarantine was not altered. At this
historical implementation checkpoint, no live call or Slurm submission had
occurred. The later smoke and submission are recorded below.

### Case A same-allocation preparation — passed offline

The preparations at `runs/scout-case-a-prepared-v1`,
`runs/scout-case-a-prepared-v2` and `runs/scout-case-a-prepared-v3` remain
preserved. Later source changes made each old snapshot fail verification as
designed; v3 specifically omitted the runtime-read MiniLM revision pin from its
source inventory. The current canonical preparation is
`codebase/agentdojo-lab/runs/scout-case-a-prepared-v4`. Its `preparation.json`
status is `prepared_not_executed`, its `real_llm_requests_started` value is zero,
and its 85-file `plan.json` has SHA-256
`5e3b9aa67767e2bf0b5c1275dac14742ee02f596efff84f0d6fe2cd4c95b5d31`.
The directory contains exactly `plan.json` and `preparation.json`; the latter has
SHA-256
`b315d3ee67a338124a5b9c35825824dd058e89e25a56a077134fbd9456f3dbd4`.
The clean-then-attacked order, one repetition per slot and 16-attempt Case A
ceiling are unchanged. Later bound-source drift must fail verification again.

Checkpoint **`7b5f1eb`** added `hpc/scout-smoke-case-a.sbatch` as a separate
two-hour wrapper. It cannot reuse job `9039289` receipts because that job's
frozen script shut its server down. Its fresh allocation must repeat
four synthetic requests and the at-most-four-request benign native smoke before
the at-most-16-request Case A pair, for a 24-attempt combined ceiling. It also
requires the exact plan-bound runner, an authenticated loopback server, matching
Slurm and receipt chains, and at least 3,900 seconds of scheduler-reported time.

After two independent Daybreak reviews and fixes, root verification passed **109
tests plus 16 subtests**. Ruff, Bash syntax, Python compilation, source-plan
verification and `git diff --check` passed. Subsequent hardening at pushed
checkpoint **`84fe7cc`** tightened same-allocation serving and exact
proposal/runtime/result/native-state bindings before the v4 plan was frozen.

### Case A submission attempt 1 — job 9043206 — cancelled before allocation

The immutable helper bundle is
`evidence/scout-case-a-submission-20260915-v1`, and its private site file is
`/nesi/project/uoa04799/dyu848/tools/scout-case-a-site-20260915-v1.env`.
Input preflight passed. Job **9043206** was submitted at **15:36 NZST** with a
two-hour limit, four A100s, 48 requested CPUs and 320 GiB host RAM. Audit then
found that one relative helper path would resolve from Slurm's spool directory,
so the job was cancelled at **15:47 NZST before allocation**. Slurm records
00:00:00 elapsed; it used zero GPU time and made zero requests. Preserve the v1
bundle and cancellation record. The maximum allocation remains eight GPU-hours
and the combined cap remains 24 generation requests.

The read-only cancellation receipt is
`evidence/scout-case-a-submission-20260915-v1/cancelled.json`, SHA-256
`35bfde30958b8ecb49aafcb31c448e69c0c0e71fe57ce8387f8c535b6d6a9e5a`.
It records `CANCELLED by 200426`, exit `0:0`, 00:00:00 elapsed and no assigned
node.

The corrected helper-path and Case A preflight-envelope selection passed **108
tests plus 16 subtests**, Ruff, Python compilation, Bash syntax and diff checks.
ShellCheck was unavailable. The smoke preflight now reports its smoke-only limits
separately from the enclosing 7,200-second, 24-total-request, 16-Case-A-request
and zero-online-auditor envelope.

### Case A submission attempt 2 — job 9050478 — pending

The corrected source checkpoint
`228f7c2ce4255a8587921ef955c633868b1fb10d` is pushed. Its immutable bundle is
`evidence/scout-case-a-submission-20260915-v2`, and the private site file is
`/nesi/project/uoa04799/dyu848/tools/scout-case-a-site-20260915-v2.env`.
The site file, helper manifest and offline preflight SHA-256 values are
`985c5f97ca5ce6141b5d6c04a8abaef797251f900eccce51676f0bfce1ca905d`,
`5cc8195c816e43c1c2ec22237cbadc9cacd4503f5beca75ae5e4a243014a6451`
and `6a8b2f5e3ba7da0f61c7dd9b0723135cdf7b12d15b97fe37492852c004f54aab`.
Request-free validation passed. An independent audit returned **GO**, with no
P1/P2 findings; its focused selection passed **81 tests plus 16 subtests**.

Job **9050478** was submitted at the scheduler's **Sep 15 17:08** display. At
this snapshot it is **PENDING** for **Priority**, with zero runtime, no allocation
and zero observed model requests. Slurm displays a prospective `mg14` node and
an estimated **Sep 15 22:35 NZST** start; these are scheduling projections, not
guarantees or evidence of allocation. The job starts automatically, so no manual
command is required. Its terminal results are not yet available. The
`submitted.json` receipt has SHA-256
`770b8e9fc66590f968d1e0f6bbc7e731b70ff7db66c1c197366955b25a4744c9`.
Monitor this job, then analyze all smoke, request-accounting, Case A and report
artifacts after it becomes terminal.

### Configured causal/replay and cross-session preparation — passed offline

The joint no-tools auditor and observed one-step replay now accept an explicit
credential-free `--endpoint-config` with separately named OpenAI-compatible
protocols. Both require `--live` and an environment-only key, construct a client
with zero SDK retries, record provider/model/URL metadata and refuse a configured
endpoint mixed with an injected client. The auditor sends no tools and omits the
unsupported reasoning-effort field. Replay preserves the recorded messages,
tools and request settings, rejects an endpoint model different from the recorded
primary request, and treats a missing or different response model as invalid.
Legacy Groq defaults and protocols remain unchanged. Independent review found and
verified fixes for transport/receipt mismatch, unhashed provider code and the
configured punctuation-report identity.

The hardened offline cross-session exporter compares two ordered A/B run pairs. It
aligns actions independently in each session and keeps insertions, omissions and
ambiguous alignments visible. Its boundary record separately types process/run
identity, fresh first-request history, A native-state and lineage hashes, the A
created-file ID versus the successful B read, actual B exposure, the versioned
write row and the restored read. The checkpoint row is bound to the successful
proposal, runtime return and visible tool-result content. Its canonical state
digest and content-derived graph IDs are verified. It reports eight explicit
segments from the session-A source read through the session-B native sink state.

The named control source at
`runs/20260915-cross-session-report-source-v1` completed four separate offline
processes and 12 MockTransport requests, with **zero real model requests**. The
marker branch retained its marker through session B; the neutralized branch did
not. Both A and B cross-condition alignments were unique under the documented
rule. Both branches recorded distinct process/run IDs, empty prior assistant/tool
history, matching checkpoint hashes, successful created-ID/read-ID correspondence,
source exposure and restored-read evidence. This is exact-copy control evidence,
not a transformed attack, causal effect or Scout result.

The current v2 selection passed **74 tests**. Independent review exercised **22
mutation classes** covering forged or contradictory source, graph, checkpoint,
history, request, runtime, tool-result and native-state evidence; all were rejected
or downgraded. Ruff, Python compilation and `git diff --check` passed. The ignored
report is `reports/20260915-cross-session-propagation-v2`, with report SHA-256
`e5986b24c126641617ff1c7d95e412d401bea5a51f9019d7a4e06e021c6660df`
and HTML SHA-256
`1af7fd7d367d910b914c2268ccc63b7f86f11d9b1bac294d246eb79d84f01423`.
Both controls cover all **8 / 8** segments. This is an offline exact-copy
engineering control: causal influence is `not_assessed`, attack success is
`unknown`, and zero real model requests ran. The earlier v1 report remains
preserved.

### Case B joint-source runner — reviewed offline

The four fixed arms are both sources, A only, B only and neither, each in a
separate process with fresh environment and history. Outcome extraction requires
an exact proposal → runtime start → runtime return → visible tool result → native
state-change chain. Source exposure, exact answer utility, native outcome and
joint-necessity interpretation remain separate fields.

The `nesi-scout-smoke-case-b-v1` same-allocation wrapper is now implemented. It
requests four A100s for at most two hours; the fixed request ceiling is four
synthetic, four benign-native and 16 Case B attempts. It requires at least 3,900
seconds remaining before the Case B phase, enforces a 3,600-second process-group
watchdog, binds the server PID and cleanup phase, and reruns the full request-free
source verifier at terminal close. The launch manifest has exactly nine entries.

The independent final Case A/B suite passed **191 tests plus 16 subtests in 77.01
seconds**; root's broader selection passed **214 tests plus 16 subtests**. Ruff,
Bash syntax, Python compilation and diff whitespace checks passed; 70 focused
Case B tests are included. The prepared v2 design
inventory has **163 source files**, including all 113 required AgentDojo runtime
and package-metadata files from pinned upstream commit
`089ed468cf3ed0322acc66b0211f26d9d90dbf60`. The upstream runtime-tree SHA-256 is
`4c58924aeb917f1daf29a4fcb11d79e716af8baf7266b73c592b39aa93a4edd7`.
Final SHA-256 values for the shared smoke, Case A wrapper, Case B wrapper, Case B
batch helper and Case B runner are respectively
`1e2caa7bd21310f7ce04af46607ad0e077abb56f2ba117691f5ee466a584ee1a`,
`4a4199dc8489224b842eaefc1d2e20ac3faccf906ec0d20a6e3fe49d97731c7e`,
`542ed12f3e62141fcff4b7861a31eace2498639d6ce28b889bcbc7f9e80258fa`,
`9f47c7d329ec300300da7b2e8346b1ec428b5d9d1bef4223d4ea865bed221934`
and `b685a83c10f3cbcb5decfff4df133fd449132ee9d34676de228d1ba38e86ada7`.
The preserved v1 plan has 41 sources, zero model calls and SHA-256
`4b8bc845437ce557fe6bbe589dd90d6ccc5b083d92955ef0fb1324f4df52c036`;
request-free verification now rejects it because later source/wrapper additions
changed the protocol inventory. The canonical v2 directory is
`runs/scout-case-b-prepared-v2`; it contains exactly `plan.json` and
`preparation.json`. Their SHA-256 values are
`69b0b0c2a77bff5057789719ae76a4a05c757a1acc511e3f66f14bd13dff60ff`
and `ba663d561892b614f7320be36a8fc9c4bf363c946c15837ac52e905fa1b45906`.
The preparation status is `prepared_not_executed` and records zero model calls.

### Case B submission — job 9052477 — pending

The immutable bundle is
`evidence/scout-case-b-submission-20260915-v1`; the private site file is
`/nesi/project/uoa04799/dyu848/tools/scout-case-b-site-20260915-v1.env`.
All **163 / 163** plan-bound sources are physical mode-0400 files. Fifty bind
pushed parent checkpoint `228f7c2ce4255a8587921ef955c633868b1fb10d`; 113 bind
pinned AgentDojo checkpoint `089ed468cf3ed0322acc66b0211f26d9d90dbf60`.
The combined physical source-tree SHA-256 is
`8ecf7918e814b30989d5a4b94514895093998c897ad3fe2f4adcdaf64e147884`.
The plan and preparation SHA-256 values remain
`69b0b0c2a77bff5057789719ae76a4a05c757a1acc511e3f66f14bd13dff60ff`
and `ba663d561892b614f7320be36a8fc9c4bf363c946c15837ac52e905fa1b45906`.

The site, nine-entry root manifest, offline preflight, request-free validation
and submission-plan SHA-256 values are, respectively,
`38c6ab9d6441cc55672efcccd434b4442e0dc12e5c0f4357aee26b6a567e5980`,
`951a00e2cf1d00b255ee390feeebc43a35321cc7162363651bd6d9509b092eac`,
`6c3b6b501733595985df9872fcca2eeca590e773176ca8333a5a866f3df1ea60`,
`4e7748b77e204c5fcebfa95512b3a8b7df114e7607ce1942ca4965921440a424`
and `938cb660d45586a3c5330ae105cbc139228dc567412f8ea715d065d619b9566e`.
Offline native/Case B preflight, request-free verification, import isolation,
runner binding and fixed-limit checks passed. Independent audit returned **GO**
with no P1/P2 findings.

Job **9052477** was submitted at scheduler display **Sep 15 17:30**. It is
**PENDING** for **Priority**, with runtime zero, no allocation and no observed
model calls. Its displayed **Sep 16 00:40 NZST** start and prospective `mg14`
node are scheduler projections, not guarantees or allocation evidence. It will
start automatically. The `submitted.json` SHA-256 is
`88b00e37fa87aa45755de4749aeaa6ae0a2ee81d62c84c9c36bd2c1bb3812408`.
No Case B result exists yet.

The checklist is now **10/25 (40%)**, preparation/prerequisites are **10/12
(83%)**, and live experimental deliverables remain **0/13**.

## Evidence locations and continuing work

External evidence paths above are relative to
`/nesi/project/uoa04799/dyu848/tool-output-lab/`. They stay outside Git; tracked
notes and source code provide the cross-device handoff. Generated lab `runs/`
and `reports/` are also ignored. A missing bundle on another device is not a
new failed experiment.

Inspect live jobs with `squeue -u dyu848`; inspect terminal outcomes with `sacct`.
Update this snapshot from receipts and accounting after each terminal attempt.
A current next action is to monitor Case A `9050478` and Case B `9052477`, then
analyze every terminal smoke, request-accounting, case and report artifact.
A running or queued job has no percentage estimate unless its own instrumentation
provides a measurable denominator. See [HPC_SETUP.md](HPC_SETUP.md) for pins,
resources, current job IDs, and the next deployment gate.

Synchronization: hardened execution and propagation checkpoint **`84fe7cc`** and
current Case A launch checkpoint
**`228f7c2ce4255a8587921ef955c633868b1fb10d`** are pushed to
`origin/codex/agentdojo-lab`. Git excludes the ignored canonical plans, fixture
runs, reports and external submission bundles. The cancelled job record and
pending replacement must be checked separately from Git state.
