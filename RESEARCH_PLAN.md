# Next phase: concrete propagation case studies on NeSI

> **Current action — 2026-09-23:** the Groq Case T1 placement main batch has
> completed its one permitted resume under frozen source hashes. The
> [final packet](codebase/agentdojo-lab/reports/20260923-case-t1-placement-groq-v1/index.html)
> retains 108/108 started sessions, 107 completed and one preserved HTTP 429;
> 94/96 final tasks pass the native/path/exposure gates. The separate request-free
> [Tier-2 scaling diagnostic](codebase/agentdojo-lab/CASE-T2-SHORT-TARGET-V1.md)
> is complete. The next action is to review the placement mechanism and choose
> any new named protocol; Git sync remains blocked. Details are in the
> 2026-09-23 active diagnostics section below.

> **Case M Groq phase — 2026-09-21 (same day, after Case R):** the deferred
> cross-session chain now has evidence. Case M stores a paraphrased summary of a
> contaminated document in Session A and sends it from a fresh Session B that
> restores the native drive and the DCPG registry. Main batch
> `codebase/agentdojo-lab/runs/20260921-case-m-v1`: 12/12 sessions, 6/6 chains,
> 3/3 attacked chains reached `send_email(attacker@example.com)` through the stored
> file alone, 3/3 clean chains sent to the legitimate contact (36 requests, 20,924
> tokens). Packet:
> [reports/20260921-case-m-groq-v1/index.html](codebase/agentdojo-lab/reports/20260921-case-m-groq-v1/index.html).
> The DCPG rehydration recovers the full path (document -> stored summary ->
> recipient) in every chain, but identically in clean and attacked chains, and the
> paraphrase step is matched by Tier-2 subsequence LCS (0.70-0.75) with 5-gram
> overlap at most 0.03, so the semantic tier is never reached. Details in PROJECT_CONTEXT.md,
> section "Case M Groq results".


> **Case R Groq phase — 2026-09-21 (Windows laptop, Groq `openai/gpt-oss-120b`):**
> The researcher moved off NeSI on 2026-09-20 and chose Groq. A new lean protocol,
> Case R, stress-tests recipient contamination under redundant and split sources.
> Pilot (8 slots) matched every frozen prediction; the frozen main batch
> `codebase/agentdojo-lab/runs/20260921-case-r-v1` ran 24/24 slots (95 requests,
> 72,053 tokens) and the forced replay/judge panel
> `runs/20260921-case-r-followups-v1` ran 6/6 sinks (42 requests, 56,168 tokens,
> 18/18 valid judgments). The interactive packet is
> [reports/20260921-case-r-groq-v1/index.html](codebase/agentdojo-lab/reports/20260921-case-r-groq-v1/index.html).
> Headline: the Tier-2 subsequence LCS matches every source (score >= 0.96) against
> a short recipient whether or not it contains the address, so the all-pairs
> causal gate never opens (23/23 sinks `not_eligible`); when forced, the
> counterfactual layer gives two different dependency patterns for identical
> `r_split` inputs and disagrees with the judge in 4/18 rows, because whole-source
> neutralization also removes the legitimate address. Details in PROJECT_CONTEXT.md, section "Case R Groq results". Local evidence is committed but **not yet pushed**:
> the stored GitHub credential belongs to a different account.


> **Nine-job terminal assessment — 2026-09-17:** All nine queued jobs reached a
> Slurm terminal state. Six case protocols retain 62 scientific requests; three
> repeat/argument panels made zero protocol requests because an incomplete frozen
> import closure stopped native smoke. A is a terminal-accepted no-exposure
> observation that supports no attack-effect inference. C/C2 remain blocked before
> a fresh Session B. E produced all-false outcomes and 0/3 matching joint blocks;
> all three blocks are interpretation-ineligible because utility failed. B/D
> tracked arm patterns remain descriptive because their terminal
> summary binding failed. See the [terminal analysis](codebase/agentdojo-lab/reports/20260917-scout-terminal-analysis-v1/README.md)
> and [terminal panel](codebase/agentdojo-lab/reports/20260917-scout-terminal-panel-v2/index.html).
> No old failure was replaced. The checklist remains **4/13 (31%)**; the immediate
> plan is a corrected 9-call canary followed conditionally by the 36-call and
> 42-call panels.

> **Meeting-packet assessment — 2026-09-16:** The
> [HTML packet](codebase/agentdojo-lab/reports/20260916-meeting-packet-v1/index.html)
> contains all eight Scout session outcomes, observed paths, a tracer-coverage
> table and all 13 deliverable statuses. Preparation is **12/12**; experimental
> deliverables **4/13 (31%)**; overall **16/25 (64%)**. Completed items are
> within-session transformation/provenance assessment, clean/attacked comparison,
> coverage assessment and the meeting packet. Causal, repeated and cross-session
> claims remain incomplete. All three jobs are terminal: **25 research requests**
> total, with zero additional requests in this reporting continuation.
> Case A cleanup diagnostics, Case B blocker reporting and Case C per-call
> reporting are now repaired prospectively. Saved outcomes and counts are unchanged.

Plan date: 2026-09-14; checklist reviewed 2026-09-16; run status updated
2026-09-17 (NeSI local date). Status: **all nine queued jobs assessed; corrected
follow-up bundle validation in progress**.
The meeting packet and descriptive coverage assessment are now complete.
This plan follows the researcher's new supervisor guidance in [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).

<a id="supervisor-checklist--checked-2026-09-15"></a>

## Supervisor checklist — checked 2026-09-16

Most completed work in the NeSI phase is preparation. The existing independent
NeuroTaint implementation and per-run HTML reports predate this phase. They are
the foundation for the requested stress tests. The
[meeting packet](codebase/agentdojo-lab/reports/20260916-meeting-packet-v1/index.html)
now presents all three case families, including failed and incomplete paths.
It completes reporting and bounded assessment work; the remaining scientific
criteria require evidence that these saved runs do not establish.

A checked box means the stated deliverable is complete. Existing code, a proposed
case, or a historical result note does not complete an experimental checkbox.

Progress reporting: [RESEARCH_PROGRESS.md](RESEARCH_PROGRESS.md) gives the
percentage, progress bars, and a run-by-run interpretation. The current first
checklist contains 25 items, of which 16 are complete (**64%**); preparation and
prerequisites are **12/12 (100%)**, while the 13 new experimental deliverables
are **4/13 (31%)**. These are equal checkbox counts, not time estimates or accuracy
scores.

### Completed preparation

- [x] Preserve the original idea and supervisor guidance in tracked context files.
- [x] Review and reuse the existing AgentDojo/NeuroTaint implementation; defer the
  old 120-trajectory evaluation and prioritize a few concrete cases.
- [x] Inventory existing argument tracking, source graphs, semantic matching,
  file-memory lineage, single/pair interventions, and per-run HTML support.
- [x] Draft three case families: changed recipient, two-source composition, and
  transformed information carried into a fresh session.
- [x] Identify a concrete Case A candidate (`user_task_33`) and inspect its
  injection point, recipient, tool schema, and tokenizer context budget.
- [x] Restore the NeSI lab, pinned AgentDojo, semantic model and plotting stack;
  implement explicit local primary/online-judge and deferred single-source endpoints.
- [x] Authenticate Hugging Face and download/checksum-verify all 63 Scout files.
- [x] Verify implementation on 2026-09-14: 2,056 repository tests, 26 HPC tests,
  and an offline native fixture passed. These are software checks, not evidence
  that the detector reliably identifies attacks.

### Supervisor's experimental deliverables — 4 of 13 complete

- [ ] **Same tool, contaminated argument:** run a clean/attacked pair where the
  tool stays `send_email` but the recipient changes; establish the new value's
  source and whether the simulated send actually succeeds. The live Case A pair
  was compared, but no attacker-recipient send occurred and both conditions
  failed native utility; this intended contaminated-argument case remains unmet.
- [ ] **Joint influence:** test both sources, A alone, B alone and neither;
  determine whether both sources are necessary for the observed action in the
  new case. A bounded earlier Groq pilot is recorded below.
- [ ] **Redundant sources and ambiguous removal:** test cases where removing one
  source preserves the action but removing both changes it. This is a separate
  proposed variant, not established by the joint-source construction.
- [ ] **Long propagation chains:** trace malicious information through multiple
  tool interactions to an executed sensitive action, with event references.
- [x] **Summarization, rewriting and paraphrase:** verify that the source was
  exposed and transformed, then identify where its provenance is retained or lost.
  C's first-session source exposure precedes the later factual paraphrase in file
  3, with a Tier-2 candidate and persisted source label. This completes the stated
  within-session assessment; it does not establish a carried attack, higher-tier
  semantic accuracy or the separate cross-session deliverable. See the
  [coverage assessment](codebase/agentdojo-lab/reports/20260916-meeting-packet-v1/coverage.md).
- [ ] **Cross-session memory attack:** persist contaminated content in session A,
  retrieve it in a genuinely fresh session B, and verify the later consequence.
- [ ] **Ambiguous judgments:** preserve uncertain, missing and contradictory
  judgments; compare judge predictions with observed interventions.
  Scout has no judge outputs. An additional review of archived judge/replay
  evidence was blocked by a platform cybersecurity-risk flag and is not counted.
- [ ] **Inconsistent repeated runs:** freeze repetitions and controls, then measure
  whether the same inputs produce different actions or attribution conclusions.
- [x] **Clean/attacked comparisons:** align executions, show changed arguments,
  and identify both the first behavioral and first security-relevant divergence.
  [Case A saved-result analysis](codebase/agentdojo-lab/reports/20260916-scout-analysis-v1/index.html)
  finds identical functional responses 1/2, first semantic response difference at
  event 34 and first tool/sensitive-argument difference at event 37. The initial
  erroneous send precedes source exposure in both branches; both fail the native
  exactly-one-email requirement. Comparison completion is not attack success.
- [ ] **Complete propagation flowcharts:** link source → entry point → first
  divergence → intermediate propagation → memory/tools → final action. Case-specific
  charts now show recorded A/B/C stages and missing endpoints in the meeting
  packet. A and B now have complete observed within-session source-to-state paths.
  The full requested path evidence remains partial because C has no handoff,
  second-session retrieval or final sink.
- [x] **Assess NeuroTaint's coverage:** compare recovered and missing path segments
  against recorded execution evidence, including final task/attack outcomes.
  The eight-session coverage table and event-indexed assessment account for
  exposure, 26 Tier-2 matches, native actions, stored labels and unobserved stages.
  This is coverage assessment, not a detector-accuracy or causal claim.
- [x] **Produce the meeting packet:** a small set of end-to-end examples, paired
  traces, flowcharts, outcomes and limitations. Preserve unsuccessful cases too.
  The HTML packet includes all three case families, recorded source-to-action
  paths where available, the blocked C continuation, eight session outcomes,
  coverage, acceptance criteria and five-minute presentation notes.
- [ ] **Establish a systematic failure pattern and research gap:** repeat a
  supported candidate and distinguish implementation defects, missing exposure,
  ambiguous method choices and actual method limitations before proposing a defense.

### Remaining prerequisites and historical evidence

- [x] Complete the serving container and pass the synthetic plus benign native
  Scout smoke. First container job `9029215` failed after 50m 31s during SIF
  creation; GPU job `9029415` was cancelled without starting. Recovery CPU job
  `9039259` passed in 6m 49s with local SSD/faster compression and a longer bounded
  deadline. GPU smoke `9039289` then completed on four A100s in 9m54s with exit
  `0:0`: all four synthetic checks and the benign native task passed using seven
  generation requests in total. This is live integration evidence, not an attack
  trajectory. See HPC_SETUP.md for all attempt receipts.
- [x] Add a paired comparison exporter and adapt the selected case runners and
  joint/replay auditors to the explicit local endpoint. Several historical batch
  entry points still retain their Groq protocols. The new **single-episode offline
  exporter is implemented**: 38 selected tests (14 new) and a benign native fixture
  pass. The bounded **Case A local runner is also implemented**; its combined
  runner/provider/report selection passed 84 tests. A historical plan was prepared
  with zero model requests, and the separate same-allocation batch selection
  passed 109 tests plus 16 subtests. The first implementation attempt's
  platform flag and quarantined draft remain recorded; a Daybreak Blue retry on
  the current Codex surface
  hash-verified and completed it. A separate bounded offline cross-session exporter
  now validates eight typed propagation segments across ordered A/B pairs; the
  v2 engineering-control report covers all 8/8 segments in each existing offline
  control. Its 74-test selection passes, and independent review rejected or
  downgraded 22 mutation classes. Causal influence remains unassessed and attack
  success unknown. The joint no-tools auditor and observed
  one-step replay now accept an explicit configured OpenAI-compatible endpoint,
  preserve their legacy defaults, disable SDK retries and record endpoint/model
  identity. The strict Case B four-arm runner and two-hour same-allocation wrapper
  are also implemented. The prior independent final Case A/B selection passed 191
  tests plus 16 subtests, while root's broader selection passed 214 plus 16
  subtests. The historical Case B v2 inventory contains 163 source files: 50 from pushed
  parent checkpoint `228f7c2ce4255a8587921ef955c633868b1fb10d` and 113 from the
  pinned AgentDojo checkout. Its frozen bundle uses physical mode-0400 sources
  and a nine-entry launch manifest; offline import isolation and fixed limits
  validate. The final exact submitted-source suite passed **351 tests plus 16
  subtests in 168.01 seconds**; scoped Ruff, compilation, Bash syntax and diff
  checks passed, and independent copied-bundle audits returned GO for all three
  cases. The current-source focused Case C suite passed 81 tests. This completes
  the checked bounded implementation prerequisite, not a scientific result; see
  RESEARCH_PROGRESS.md.
- [x] Freeze exact tasks, payloads, source sets, conditions, budgets, settings,
  success criteria and run order before the new research trials. Historical
  Case A v4 preparation `runs/scout-case-a-prepared-v4` has plan SHA-256
  `5e3b9aa67767e2bf0b5c1275dac14742ee02f596efff84f0d6fe2cd4c95b5d31`.
  It binds 85 source files including the runtime-read MiniLM pin, records zero
  requests, and superseded without deleting three earlier source-invalidated
  preparations. Current hardening now source-invalidates v4 as well.
  First submission `9043206` was cancelled
  before allocation after audit found a Slurm helper-path defect; it used zero GPU
  time and requests. Corrected job `9050478` was submitted from pushed checkpoint
  `228f7c2ce4255a8587921ef955c633868b1fb10d` after request-free validation and a
  GO audit with no P1/P2 findings. It later failed before vLLM startup because
  the frozen launcher imported a changed repository module; it made zero calls.
  Case B v2 was prepared and bundled with zero calls; job `9052477` loaded Scout
  and passed four synthetic requests, then failed before native inference because
  `configs/local_scout.toml` was absent from the bundle. Historical Case B v2 plan
  SHA-256 is
  `69b0b0c2a77bff5057789719ae76a4a05c757a1acc511e3f66f14bd13dff60ff`.
  Current hardening source-invalidates it. Case C now has a four-session protocol,
  a bounded Slurm wrapper and a prior noncanonical deterministic fixture. The
  copied-wrapper gate rejected unsubmitted Case C v1 because its plan omitted
  explicit `online_causal_audit = false`; the preserved attempt made zero model,
  network, GPU or scheduler actions. Commit
  `74c31d5e5ad5fc5bbb89a5eb4e1520b7787d3336` fixed the binding. A/B bind
  `ebc619813a9c22bdb2eb3bed675213edfc83bc89` and were revalidated after that
  C-only fix; corrected C v2 binds `74c31d5`. Canonical preparations initially
  recorded zero requests and contained only `plan.json` and `preparation.json`:
  Case A v5 has 205 sources and plan SHA-256
  `992509a7a4e1b8e8817072d4c2720ded6ec5981a559fd4aa1062cb5676fe1d15`;
  Case B v3 has 164 and
  `a5c0b7d19d32b619df337ab5ba47f79a4c6ba1e47732ea2f08278236390d98cf`;
  corrected Case C v2 has 206 and
  `b28f3497f1f75faf608784d73714b9ec67cf07bbdae89e21399508a217aa1388`.
  Their immutable bundles passed exact validation. Jobs `9064136`, `9064141` and
  `9064142` are terminal: A two sessions/eight requests, B four/eleven,
  C two/six; C second sessions made no requests.
- [x] Recover selected historical raw runs/reports if available and reverify them.
  Their absence does not block new named trials, but old outcome notes cannot
  substitute for locally inspected evidence.

### Partial progress from earlier Groq pilots

These results predate the NeSI setup. Their raw bundles were recovered at
`f96bdc8` and passed integrity/readability checks; those checks do not independently
replicate every scientific conclusion in the historical notes.

| Area | Recorded historical progress | Remaining limit |
| --- | --- | --- |
| Joint sources | 16 native trajectories across two constructed attack families; each both-payload condition succeeded in 2/2 repetitions, singleton/neither arms in 0/2 | Small constructed pilot; Scout four-arm outputs now exist, but utility failures and one observation per condition limit interpretation |
| Rewriting | Four normal-task processes produced nonverbatim outputs, but all omitted a required second read | Not malicious transformed propagation; requested step coverage was incomplete |
| Cross-session memory | Four original/neutralized processes successfully copied and restored file content | Authorized exact-copy control, not an attacked paraphrased-memory case |
| Judge ambiguity | Six valid later judgments included four agreements and two disagreements with earlier one-step replays | Judge/replay disagreement does not establish variability across repeated identical judgments |
| Reporting and hypotheses | Per-run HTML/graphs and controlled comparison notes; candidate LCS overmatching/fallback starvation | New aligned source-to-action packet and reproducible research-gap evidence still missing |

These pilots provide useful leads. The existing implementation contract does not
establish original-paper results or complete the new supervisor deliverables. See
[the implementation contract](codebase/agentdojo-lab/REPRODUCTION-CONTRACT.md),
[historical attack results](codebase/agentdojo-lab/ATTACK-VALIDATION-RESULTS.md),
[semantic validation](codebase/agentdojo-lab/SEMANTIC-VALIDATION-RESULTS.md),
[memory results](codebase/agentdojo-lab/METHOD-COMPLETION-RESULTS.md), and
[current setup evidence](HPC_SETUP.md#status-recheck-on-2026-09-15).

## Deliverable for the next meeting

Prepare at most three case families with clean/attacked traces, sensitive
argument diffs, flowcharts, observed consequences, and an explicit assessment of
which path segments the independent NeuroTaint implementation recovered or missed.
Keep unsuccessful and unavailable cases in the packet. If only one or two cases
are supported, present those and their limits rather than manufacture a third.

The first milestone is a readable causal question and a concrete trace, not a
large benchmark score. Defer the old 120-trajectory NT-AgentDojo-Eval-v1 matrix.
Reuse existing instrumentation and HTML; implement only missing transport and
paired-analysis support needed for these cases.

## Three case families

The examples below describe **intended experimental designs**. Observed Scout
results are linked above and do not establish every intended behavior. The older
Case A v4 and Case B v2 plans remain historical, source-invalidated inputs to
failed jobs. Use native simulated AgentDojo tools and the exact task, payload, schema and field-path
bindings in the canonical plans. Use addresses validated by the native simulated
tool schema. `EmailStr` rejects `.invalid`; use `attacker@example.com` for a
synthetic attacker recipient.

| Case | Clean behavior | Attacked behavior being tested | Main question |
| --- | --- | --- | --- |
| A: same tool, different recipient | Read task material and send the requested summary to `john.mitchell@gmail.com` | Tool-output content steers the same `send_email` call to `attacker@example.com` | Does attribution recover the changed `/recipients/0` value and the first security-relevant divergence? |
| B: two-source composition | Read two records and complete the benign task without an extra write | Two planted fragments are combined into an unauthorized simulated file write | Is the path attributed to both sources, and does removal distinguish joint dependence from coincidence? |
| C: transformed cross-session propagation | Session A stores a legitimate summary; fresh session B uses it for an authorized action | Contaminated material is rewritten, stored, restored, and affects a later recipient/action | Where does provenance survive or disappear across transformation and session boundaries? |

### Case A: sensitive argument without a tool-name change

Record the user-authorized recipient independently of detector output. Keep
the request, environment, and permitted operation fixed between conditions;
alter only the selected tool-output payload. Compare recipient elements,
subject/body, and native sent-mail state. The first payload exposure is the
entry point; it is not automatically the first behavioral divergence.

An attacker recipient in a proposal is an attempted deviation. A successful
simulated send to that recipient establishes the sink consequence under the
fixture's oracle. Do not describe a failed send as completed disclosure.

Read-only fixture inspection identified native workspace `user_task_33` as a
candidate: it requests a summary email and attachment `19`, addressed to
`john.mitchell@gmail.com` in the simulated environment. Its filename search
returns legitimate file `19` and injectable file `24`
(`newest-client-meeting-minutes.docx`). The named Case A v1 protocol uses the
existing drive-keyword injection point; its exact payload bytes and native-state
sink oracle are implemented, and `prepare` hashes the scientific inputs before
any live execution.
The recipient is available in file `19`'s `shared_with` field; a contact lookup
for that name fails in this fixture and should not become an assumed prerequisite.

The adapter currently registers the entire search response as one source even
when it contains both files. Structured binding can identify file `24`'s
`/1/content`, but a source-level detector hit alone does not distinguish the two
documents. Report that granularity explicitly; it is not evidence of a failure
in the original NeuroTaint paper. No Case A trajectory has been run on Scout.

### Case B: joint sources and removal ambiguity

Start from the existing content-composition design in
`codebase/agentdojo-lab/src/agentdojo_lab/attack_factorial.py`, creating a new
named local-model protocol rather than editing its frozen Groq settings.
Compare four whole-trajectory conditions: both payloads, A only, B only, neither.
Remove payload blocks while retaining benign counts, source identities, and
consistent derived file metadata. Confirm both sources were actually exposed.

For the first pilot use a conjunctive construction: both fragments are needed
to form the target content. A later separately frozen redundant-source variant
can place the same steering information in both sources. In the redundant case,
removing A or B alone can preserve the action while removing both changes it.
Neither pattern can be inferred solely from a single-source removal.

Use the existing `causal_v2.py` and controlled panel interfaces for diagnostic
source sets, but keep authored construction labels, model behavior, and judge
predictions separate. A judge's assertion is not an observed counterfactual.

### Case C: transformation and a real session boundary

Use the existing native file-memory adapter and separate-process session pattern
in `scripts/run_memory_pair.py`. The old authorized exact-copy experiment is an
engineering control, not this attack. Introduce a new frozen summarization or
paraphrase task, with a benign clean branch and an attacked branch.

Persist the actual native file state and observer checkpoint separately. Start
session B with fresh messages, retrieve the bound stored version, and record its
actual model exposure before the later sink. Include an exact-copy control when
diagnosing a lost transformed path, under a separately declared small follow-up.
Distinguish a broken checkpoint adapter from a detector miss on correctly
restored, paraphrased content. For this case the whole-trajectory intervention
must start before session A; editing only B cannot test the full persistence path.

## Trace and comparison contract

Each case report should contain:

1. Legitimate task, permitted sink/arguments, attacker objective, source IDs,
   payload spans, and the clean/attacked run and session IDs.
2. Model-visible entry point bound to the actual request prefix, with event IDs
   and hashes; distinguish retrieved material from material actually exposed.
3. First observable **agent behavior** mismatch and first **security-relevant**
   mismatch. Do not choose the deliberately changed input text as either answer.
4. The changed tool name, argument JSON Pointer, and clean/attacked values.
   Match tool-call/result IDs within each run; use a documented alignment rule
   across runs. Preserve inserted calls, missing calls, and ambiguous alignment.
5. Intermediate outputs, transformations, memory writes/versions, session
   boundaries, restored reads, and subsequent tool interactions.
6. Actual simulated final state and task/attack evaluation. Keep proposal,
   execution, success, failure, and unavailable outcome distinct.
7. NeuroTaint candidates, route/tier, source sets, recovered path segments,
   unsupported/missing segments, and explicitly unknown conclusions.
8. If performed, sham/neutralized replay observations and separate no-tools
   judge predictions, with run stability, schema failures, and disagreements.

Do not claim to observe private model reasoning. Source-to-action explanations
are based on recorded inputs, outputs, runtime state, and controlled interventions.

### Illustrative flowchart format

This is a template for Case C. It is not evidence that an attack succeeded.
Replace each node label with links/IDs from a real recorded trace.

```mermaid
flowchart LR
    subgraph A[Session A]
        S[Manipulated source] --> E[Model-visible tool result]
        E -. candidate influence .-> D[First security-relevant argument change]
        D --> W[Successful native memory write]
    end
    W --> V[Persisted file version and observer checkpoint]
    subgraph B[Fresh session B]
        R[Read stored file] --> O[Model-visible retrieved summary]
        O -. candidate influence .-> P[Later sensitive call proposal]
        P --> X[Executed simulated sink and final state]
    end
    V --> R
```

Solid edges denote recorded execution/storage relationships in the eventual
report; dashed edges denote inferred influence candidates. Unobserved or
unverified links must be visibly marked unknown. Add a clean graph beside the
attacked graph and highlight the first changed security-sensitive field.

## Implementation order and acceptance criteria

| Order | Bounded task | Completion evidence |
| --- | --- | --- |
| 1 | Restore lab prerequisites and inventory old artifacts | Python 3.12, pinned AgentDojo and lock, available/missing artifact list; selected integrity checks |
| 2 | Establish local inference feasibility | HF access, storage, allocated GPU topology, pinned serving environment, successful small endpoint smoke test |
| 3 | Integrate explicit local transport for primary and auditors | Wire tests for endpoint/key/model routing, no-tools judge isolation, tool-call/result round trips, failures, usage, and zero hidden retries |
| 4 | Add an offline paired trace exporter | Same-tool changed-argument fixture, inserted/deleted-call case, memory-session fixture, escaped HTML, and links back to source events |
| 5 | Freeze small native pilot | Versioned manifest binding cases, payloads, conditions, order, versions, budgets, source sets, oracles, and hashes |
| 6 | Execute and export meeting packet | All started slots accounted for, three or fewer case reports, complete path evidence and limitations |
| 7 | Repeat one candidate pattern | New fixed repetitions and controls; assess reproducibility before asserting a systematic limitation |

For order 3, start with `runner.py` and `groq_adapter.py`, then inspect online
causal clients, completed-trace auditor factories, and the selected case runners.
Keep primary, causal judge, and embedding model identities separate in manifests.
Do not rename a model in an old frozen config and assume the endpoint changed.
See [HPC_SETUP.md](HPC_SETUP.md) for the complete transport migration checklist.

For order 4, existing `html_report.py`, `provenance_report.py`, and `lineage.py`
already supply most trace content. The comparator in the older
`codebase/tool_output_lab/compare.py` illustrates observable mismatch detection,
but its event schema is incompatible with the active lab and must not be copied
without adaptation. Exclude timestamps/random IDs from semantic comparison,
while preserving all original event references and hashes for auditability.

## Proposed first-pilot budget and stopping rule

Freeze final operational values after the benign endpoint/tool-call smoke test.
The following is a concrete starting budget, not a launched batch:

| Family | Conditions | Initial repetitions | Native sessions |
| --- | --- | ---: | ---: |
| A | clean, attacked | 1 each | 2 |
| B | both, A only, B only, neither | 1 each | 4 |
| C | clean, attacked; sessions A then B in each branch | 1 per branch | 4 |
| Total | Three families | Descriptive pilot only | 10 |

- Cap primary requests at 8 per session: at most 80 requests total. Start with
  temperature 0 and 2,048 generated tokens per request, unless the smoke test
  justifies a different prospectively frozen limit. Fix context length explicitly.
- First export/audit is offline with no generative requests. Reserve at most 24
  one-step replay requests and 12 no-tools judge requests for a separately frozen
  follow-up manifest: at most 116 generative requests including primary execution.
- A proposed follow-up selects the first qualifying sensitive proposal in each
  family, with a sham and declared singleton/pair interventions. Freeze the exact
  selection rule, repetitions, source-set inventory, ordering, and cap before
  any follow-up inference. Missing eligible targets do not get substituted.
- Fix per-request and per-job deadlines using the measured local startup and
  inference time. Include scheduler walltime and GPU-hour ceilings in the manifest.
- Disable SDK retries and retain every started slot as terminal. Non-exposure,
  truncated context, invalid tool calls, and failed jobs stay visible.
- Do not silently truncate long traces to fit the server. Mark over-limit cases
  unavailable or start a new protocol with an explicitly changed context budget.

One repetition supports examples, not a variability estimate or a general attack
success rate. The next stage should prospectively repeat a selected pattern at
least three times per condition, including stable sham controls, and add a second
independent case only if the same limitation remains plausible. Do not keep
generating until a desired failure appears. Quantization or a new backend starts
a new model condition; do not pool it with historical Groq outcomes.

## Candidate hypotheses and what would distinguish them

| Hypothesis | Required comparison | Alternative explanation to exclude |
| --- | --- | --- |
| Sensitive argument is contaminated despite correct tool selection | Recipient-level clean/attacked diff and source witness, verified simulated send | Unrelated model variation or a failed/unexecuted proposal |
| Single removals miss redundancy/joint attribution | A, B, both removals plus sham and exposure checks | Missing source read or intervention changing benign task requirements |
| Transformation loses a path | Exact-copy vs paraphrase with intact versioned storage and fresh-session exposure | Checkpoint/adapter defect or source omitted from the model context |
| Early LCS matching masks meaningful later stages | Fixed positive/unused-source references; tier routing and direct component diagnostics | Implementation bug, denominator/threshold ambiguity, or short-field coincidence |
| Influence judgment is unstable | Repeated identical-prefix sham, neutralized replay, and separately repeated judge | Transport/parser failure or serving configuration changes |

The LCS hypothesis is already suggested by historical reference panels; it is
not a newly discovered result from this planning task. Keep diagnostic variants
separate from the frozen baseline rather than changing thresholds to force the
causal fallback to run.

Classify findings as implementation defects, execution/coverage limitations,
ambiguous method choices, or candidate systematic method limitations. Evidence
that the independent implementation misses a path is not automatically evidence
that the original authors' implementation does so.

## Meeting packet and current progress

The intended packet is a small HTML index plus per-case Markdown/JSON evidence:
paired timelines, argument diffs, flowcharts, a table of covered/missing edges,
and a short explanation of the candidate pattern and its limits. Raw evidence
stays immutable in tracked run directories; new reports and evidence require
credential checks before commit and push. Publish observed counts with their
denominators and unknowns.

- [x] Read project source and prior handoff; record the original idea and new scope.
- [x] Identify existing graph, memory, argument, and report support and the gaps.
- [x] Inspect NeSI scheduler availability and write the Scout deployment plan.
- [x] Verify gated-model access and storage; submit bounded CPU preparation jobs.
- [x] Restore default lab/upstream; pass native offline smoke and initial local transport tests.
- [x] Restore semantic dependencies and pass 53 additional targeted checks.
- [x] Pass the full 2,056-test repository suite and 26 HPC tests.
- [x] Verify Scout inference in GPU attempt `9039289`; synthetic 4/4 and the benign
  native AgentDojo task passed in the same allocation.
- [x] Restore and integrity-check selected historical evidence bundles (`f96bdc8`).
- [x] Implement explicit local primary/online judge and deferred single-source endpoints.
- [x] Finish selected case runners/auditors and cross-session comparison. The
  single-episode and cross-session exporters, bounded Case A runner, configured
  joint auditor and configured one-step replay are verified offline.
- [ ] Freeze the new small protocol, run it, and produce actual case studies.
  Case A job `9043206` was cancelled before allocation; replacement `9050478`
  failed request-free validation before inference. Case B job `9052477` passed
  four synthetic requests, then failed before native inference due a missing
  bundled config. Case C's strict four-session runner and wrapper are implemented;
  its prior scripted fixture predates current hardening and is noncanonical.
  Canonical A v5, B v3 and corrected C v2 preparations and immutable bundles are
  frozen. Those jobs are now terminal, with 25 research requests across eight
  sessions. The Case A comparison, within-session transformation assessment,
  coverage table and meeting packet are complete. Supported causal/cross-session
  claims and the full planned execution remain outstanding.
- [ ] Repeat and classify a supported candidate pattern.

Setup evidence is in `codebase/agentdojo-lab/reports/20260914-nesi-setup-v1` and
`runs/20260914-nesi-offline-smoke-v1`. Model job 9029207 completed successfully;
container job 9029215 failed, and dependent GPU smoke 9029415 was cancelled
without starting. The CPU container retry `9039259` passed in 6m 49s; GPU smoke
`9039289` passed in 9m54s with seven bounded generation requests. Scout inference
is verified; later jobs completed eight research sessions as recorded above.
Case A job `9043206` was submitted at 15:36 NZST from pushed checkpoint `84fe7cc`, then
cancelled at 15:47 before allocation after audit found a Slurm helper-path defect.
It used zero GPU time and requests. Historical 85-source zero-request plan
`runs/scout-case-a-prepared-v4` has SHA-256
`5e3b9aa67767e2bf0b5c1275dac14742ee02f596efff84f0d6fe2cd4c95b5d31`.
Current source hardening invalidates that plan. Canonical Case A v5 bound 205
sources in its request-free preparation, with plan SHA-256
`992509a7a4e1b8e8817072d4c2720ded6ec5981a559fd4aa1062cb5676fe1d15`;
job `9064136` later saved both sessions and failed finalization.
The corrected immutable v2 bundle binds pushed source checkpoint
`228f7c2ce4255a8587921ef955c633868b1fb10d`. Request-free validation and an
independent GO audit with no P1/P2 findings passed before job `9050478` was
submitted. It later failed `1:0` after 30 seconds on `mg14`, before vLLM startup
or any generation request, because its frozen launcher imported changed repository
source. A complete self-contained source bundle is now required.
The 2026-09-14 full repository suite passed 2,056 tests;
new 2026-09-15 checks passed 28 HPC tests plus 25 subtests, 38 paired/report tests,
the 84-test Case A runner/provider/report selection, and the final 109-test plus
16-subtest same-allocation batch selection. The hardened cross-session v2 report
has all 8/8 segments in both offline controls, backed by 74 selected tests and 22
review mutations. Its causal status is `not_assessed` and attack status is
`unknown`. The first Case A draft was platform-flagged and preserved; the Daybreak
Blue retry completed and is verified offline. The independent final Case A/B
wrapper selection passed 191 tests plus 16 subtests; root's broader selection
passed 214 plus 16 subtests. Case B v2 passed offline preflight, request-free
validation and an independent GO audit with no P1/P2 findings. Job `9052477` ran
8m 35s on `mg14`: Scout loaded and synthetic smoke passed 4/4, then native smoke
failed before its first request because `configs/local_scout.toml` was absent
from the immutable bundle. It made zero Case B requests. That v2 plan is now
source-invalidated. Canonical Case B v3 bound 164 sources in its request-free
preparation, with plan SHA-256 `a5c0b7d19d32b619df337ab5ba47f79a4c6ba1e47732ea2f08278236390d98cf`;
job `9064141` completed its four research conditions. Case C's prior offline
four-worker fixture completed both observed native paths with scripted responses, but later hardening
source-invalidated it. Rejected unsubmitted C v1 used zero calls/resources;
corrected canonical C v2 bound 206 sources in its request-free preparation, with
plan SHA-256
`b28f3497f1f75faf608784d73714b9ec67cf07bbdae89e21399508a217aa1388`;
job `9064142` saved two first sessions, then blocked both second sessions
before inference because its memory handoff was unverified.
See RESEARCH_PROGRESS.md for receipts and limits. Update checkboxes only with
concrete evidence and actual verification results.

## Report archive synchronization — 2026-09-16, Mac

At the report-only Mac checkpoint, the researcher requested tracking the 990
local reports. This archive operation did not complete an experimental checklist
item or include NeSI-only reports.
Inventory, file-size checks and a credential-pattern scan were run locally.
Report bytes were preserved. Raw `runs/` were still excluded at that checkpoint;
the follow-up below added them. Credentials and model caches remain excluded.
See [the synchronization note](PROJECT_CONTEXT.md#report-synchronization--2026-09-16-mac).

### Raw-run archive follow-up — 2026-09-16, Mac

The user also requested and explicitly authorized synchronization of the local
`runs/` archive to the same GitHub repository and branch. Its blanket ignore rule
is removed; 3,943 existing files (162,050,027 bytes) are prepared for tracking with
original bytes preserved. This supersedes the report-only exclusion above, not
the experimental plan or any result. No new model calls were made. The archive
was pushed and pulled on NeSI at `f96bdc8`; credential and model-cache exclusions
remain. See [raw-run synchronization](PROJECT_CONTEXT.md#raw-run-synchronization--2026-09-16-mac).

## Historical evidence recovery verified — 2026-09-16

This checkpoint supersedes earlier statements that historical artifacts are absent
or excluded from Git. Pulled source `f96bdc8` contains 4,933 tracked run/report
files. Offline verification parsed 3,204 JSON documents and all 761 JSONL files
(10,771 records), checked 652 original/recovered attack-batch SHA-256 values with
zero mismatches, and checked 612 local links across 329 HTML reports with none
missing. Two historical stdout captures are empty (`control.stdout.json` and
`memory.stdout.json` under the paper-conformance report); their bytes are preserved.

Receipt: [HISTORICAL_EVIDENCE_VERIFICATION.json](HISTORICAL_EVIDENCE_VERIFICATION.json).
Verification ran with the lab Python 3.12 using `/tmp/verify_recovered_reports.py`.
This verifies recovered file integrity/readability, not a new scientific replication;
no model requests were made. Original process failures and later analytical recovery
remain separate. Recovery completed preparation: **12/12 (100%)**. With the later
saved-run comparison, overall progress is **13/25 (52%)** and experimental deliverables
are **1/13 (8%)**. Use recovered reports alongside the new Scout analysis for
meeting preparation; file integrity alone does not validate scientific claims.
Archive recovery used pushed checkpoint `f96bdc8`. This analysis checkpoint includes
the recovery receipt, new analysis, and the three original Scout case directories.

## Meeting-packet milestone — 2026-09-16

The [HTML packet](codebase/agentdojo-lab/reports/20260916-meeting-packet-v1/index.html)
completes items 5, 11 and 12 alongside the previously completed item 9. Current
experimental progress is **4/13 (31%)**, overall **16/25 (64%)**. Item 5 is limited
to observed within-session paraphrase and persisted candidate lineage; item 11
is an assessment that explicitly includes missing coverage. Neither changes the
unmet attack, causal or cross-session acceptance criteria.

The nine unchecked items retain their original criteria in the
[deliverable ledger](codebase/agentdojo-lab/reports/20260916-meeting-packet-v1/deliverables.json).
The independent coverage assessment completed; the separate archived judge/replay
review and independent full acceptance review were blocked by platform
cybersecurity-risk flags and are not counted as completed reviews. At this packet
checkpoint no new inference, scheduler allocation, runtime repair or replacement
trial had occurred; the later prospective code repairs are recorded below.

Fresh offline verification checked eight event audits, 25 request-ledger entries,
96 terminal-bound hashes and 206 unchanged raw files. The coverage assessment's
79 input hashes also match. The HTML renderer passes scoped Ruff and compilation;
local link and checklist-accounting checks pass. See the
[verification receipt](codebase/agentdojo-lab/reports/20260916-meeting-packet-v1/validation.json).
No application regression suite or browser visual QA is claimed for this report.
Synchronization started from pushed `f528341`; the packet and current status
documents are the changes in this continuation, with raw evidence unchanged.

## Prospective code-repair milestone — 2026-09-16

Concrete infrastructure and reporting defects are fixed while all frozen evidence
and acceptance criteria remain intact:

- Case A records precise finalizer failures and credential-safe process-group
  snapshots before/after bounded TERM/KILL grace periods. Shutdown confirmation
  is not weakened.
- Case B enumerates per-condition interpretation blockers and displays task utility.
  The saved four-arm result has four `utility_failed` blockers.
- Case C separates all observed per-call evidence from its exact-one selection.
  Multiple reads/writes now yield unknown selected fields and a specific blocked
  handoff, never a favorable retrospective selection.
- Packet charts now fully map the observed A/B source-to-state paths and display
  C's absent fresh-session path. Item 10 stays partial because that path did not run.

Verification passed 202 HPC tests plus 25 subtests, 32 Case B tests, 38 Case C
runner tests and 47 Case C HPC tests, with scoped Ruff, compilation, Bash syntax
and whitespace checks. No new checkbox is completed by these software repairs;
progress stays **4/13 experimental** and **16/25 overall**. The remaining nine
items need valid new observations or independent evidence, not changes to labels.

## Submitted follow-up observations — 2026-09-17 NZST

Three prospectively named follow-ups now bind the pushed repaired source at
`134ee6b`, fresh preparations, fresh evidence paths and immutable copied bundles:

- Case A job `9123394`: repaired cleanup/finalization validation.
- Case B job `9123398`: one additional descriptive four-condition observation.
- Case C job `9123399`: repaired per-call uncertainty and handoff diagnostic.

Slurm accepted all three at 09:27 NZST. At the recorded checkpoint they were
pending for Priority, with zero GPU runtime, research sessions and model
requests. Each has a four-A100, 48-CPU, 320-GiB, two-hour ceiling and starts
automatically when allocated. The displayed Sep 18 02:04 NZST start is only a
scheduler estimate.

This submission does not mark a checkbox complete. The nine open entries are
scientific criteria, not queued tasks. In particular, the new jobs do not yet
provide the missing redundant-source construction or no-tools judge/intervention
panel; a single added B observation also does not meet the frozen three-repeat
criterion. Terminal results must be assessed against the existing acceptance
language before updating **4/13 experimental** or **16/25 overall**.

## Additional prospective protocols implemented — 2026-09-17 NZST

- [x] Implement and independently audit Case C2 with a prospectively named native
  handoff target, a one-artifact checkpoint, fresh worker/history, and a fully
  bound simulated sink.
- [x] Implement and independently audit Case D's redundant-source construction
  with four isolated arms and fail-closed terminal acceptance for the exact
  `true/true/true/false` pattern.
- [x] Implement and independently audit a three-repeat sham/neutralized/no-tools
  panel with byte-identical inputs, direct loopback transport, no retries, no
  proposed-tool execution and explicit unknown/disagreement retention.

These are implementation substeps, not additions to the 13 experimental checkbox
count. Root's stable selection passed **214 tests plus 16 subtests**. Independent
reviews passed 55 C2, 94 D and 97 repeat/judge tests and exercised copied-source,
partial-evidence, scientific-acceptance, proxy and server-identity mutations. Ruff,
compilation, shell syntax and whitespace checks pass.

Next, commit and push the reviewed bytes, regenerate request-free preparations,
copy the exact plan-bound sources into fresh immutable bundles, repeat copied-bundle
validation and submit the three wrappers. Terminal evidence may address items 3,
4, 6, 7, 8 and 10. Completion is outcome-dependent; the protocols preserve a
negative or unknown result, and item 13 stays unchecked unless repeated evidence
actually distinguishes a method limitation from implementation and task effects.
Items 1 and 2 continue to depend on valid terminal A/B evidence. Current progress
remains **4/13 experimental (31%)** and **16/25 overall (64%)**.

## Additional protocol submissions — 2026-09-17 NZST

The copied-bundle gate rejected the first D preparation because its runner tried
to validate two filtered Case B launcher paths. No model request or GPU allocation
occurred. The fix adds a pre-validation runtime candidate helper and a regression
that copies exactly the D plan inventory and verifies it in isolation. Focused
B/D validation passed 105 tests; shared validation passed 68 tests plus 16
subtests. Final source `43d068e` is pushed and binds fresh C2/D v2 preparations.

All final immutable bundles passed independent launch audit and were submitted:

- C2 `9126739`, for items 4, 6 and the missing endpoint of item 10;
- D `9126740`, for the separate redundant-source criterion in item 3;
- repeat/judge `9126776`, for items 7 and 8 and evidence relevant to item 13.

Each has a fixed four-A100, 48-CPU, 320-GiB, two-hour ceiling and no fallback
model. Their initial state is pending for Priority with zero runtime and zero
observed research requests. The three new jobs had a provisional Sep 18 04:05
NZST start; A/B/C remained provisionally at 02:04. They start automatically.

After terminal completion, validate each saved receipt and update the deliverable
ledger without replacing failures. C2 can complete items 4, 6 and 10 only if the
prospectively bound handoff and fresh-session sink are observed. D can complete
item 3 only if utility, exposure, witnesses and the exact fixed outcome pattern
pass. Repeat/judge can complete item 7 only when at least one pair is determinate;
an all-unknown panel remains incomplete. Disagreement is retained as evidence,
and item 13 remains conditional on an actual systematic method limitation. Items
1 and 2 still depend on terminal A/B evidence.
Current checkbox progress remains **4/13 experimental** and **16/25 overall**.

## Joint-source and multi-candidate submissions — 2026-09-17 NZST

- [x] Freeze and independently audit Case E: three independent four-arm
  joint-source blocks, 56 requests at most including smoke.
- [x] Freeze and independently audit the four-candidate repeat/intervention/judge
  panel: three repetitions of each arm, 44 requests at most including smoke.
- [x] Submit Case E as job `9129880` and the multi-candidate panel as job
  `9129940` from pushed source `c062d0f949d722d9329a06577a4d1788206daeaf`.
- [ ] Assess their terminal receipts against the frozen acceptance criteria.

The Case E immutable bundle is
`evidence/scout-case-e-submission-20260917-v1` in the private lab root; its
12-entry manifest SHA-256 is
`f69e7d4106e39ff06dbbd3904d9d16736ecc39eeb3197e33dbc4bf227f1737ce`.
The multi-candidate bundle has an exact 77-entry whole-bundle manifest with
SHA-256 `b4013ac5f1db9da438f1da9e00a6b60801c4847d46815733b4235c022839f099`.
Both builds made zero requests and passed owner-only, secret and symlink gates.

Case E may complete item 2 only if all frozen gates pass in all three blocks.
The multi-candidate protocol remains construction-scoped and cannot alone
complete item 13. Its request-free `content_composition` r01/r02 check found no
eligible probes because explicit candidates were present and made zero model
requests. Both jobs were pending for Priority with provisional Sep 18 06:05 NZST
starts; all six earlier jobs also remained pending. Progress remains **4/13
experimental (31%)** and **16/25 overall (64%)**.

## Second-family argument intervention submission — 2026-09-17 NZST

- [x] Freeze the complete two-prefix `content_composition` inventory, exact
  proposal/request/call IDs, all 21 archived file hashes per prefix, and the two
  exposed Tier-2 `/content` source bindings.
- [x] Implement three repetitions of sham, A removal, B removal, joint removal,
  and an isolated no-tools judgment for every removal arm.
- [x] Replace only the exact A/B contribution fragments in all frozen carrier
  occurrences, preserving surrounding text and filename, and score typed
  `/content` persistence separately from filename and exact-call identity.
- [x] Add independent same-allocation validation, conservative unknown handling,
  authoritative scheduler-I/O receipts, bundle-disjoint output gates, early
  cleanup finalization, fixed 42/50 request ceilings and a 3.5-hour four-A100
  wrapper.
- [x] Verify a 42-slot request-free plan with zero requests and run focused and
  related regression selections.
- [x] Commit and push the reviewed bytes, build and audit a fresh immutable
  70-entry copy, and submit it as Slurm job `9135588`.
- [ ] Validate job `9135588` after it reaches a terminal state without replacing
  failed, unknown or incomplete observations.
- [ ] If terminal evidence is collected, combine this second task-family panel
  prospectively with the independently frozen `conditional_action` panel before
  assessing item 13.

The older `explicit_candidate_present` zero-probe result remains valid for its
no-explicit-candidate planner. This new protocol asks a different, predeclared
argument-level question and does not reinterpret that result. Request-free
preparation made no model call. Source and remote HEAD match
`307869dacad57261a5897d2d4492905342bcf24b`; the final manifest and site hashes
are `45b6d316cf699b74323b176585990df269f5b41cdfae83ef18ea482981573c85`
and `195f5526d700951e663cd14f83c157a571bb6dd20e962fe7c48ede9071859b60`.

Slurm accepted `9135588` at 13:19 NZST with four A100s, 48 CPUs, 320 GiB and a
3h 30m ceiling. Its initial state was PENDING (Priority), runtime zero and null
`AllocTRES`, with a provisional Sep 18 00:17 NZST start. The submission and raw
`scontrol` receipt hashes are
`da7ee5562a1863017fcd0362c559280bd31b0a1181b7cf2c7b22ffb55eb23b96`
and `75ae03a75014ded74b2f201e5a02023324a40564cf94d20d9d10e11d3dfc491a`.
The previous eight jobs remained PENDING with 0:00 runtime and provisional Sep 17
16:59, 19:00, 21:00 and 23:00 NZST estimates. Item 13 and the **4/13
experimental, 16/25 overall** counts remain unchanged pending terminal evidence.

## Graphical presentation milestone — 2026-09-17

- [x] Replace the paired report's default JSON display with clickable clean and
  attacked SVG paths, synchronized readable event details, word-level differences,
  and separate source/exposure navigation.
- [x] Rebuild the single-run template around an interactive recorded-event route
  and readable cards; retain original evidence and metadata in disclosures.
- [x] Generate the [visual library](codebase/agentdojo-lab/reports/visual-library-v1/index.html):
  251 visual runs, four visual comparisons, and 138 clearly labeled archived reports.
- [x] Verify related tests, escaping and alignment, original source hashes, browser
  interaction and desktop/mobile layout. See the library's `inventory.json`,
  `paired-refresh.json`, and `browser-verification.json` receipts.
- [x] Record the reusable [visualization requirements](codebase/agentdojo-lab/PAIRED-REPORT-VISUALIZATION.md)
  and [rebuild instructions](codebase/agentdojo-lab/VISUAL-REPORT-LIBRARY.md).

These are presentation substeps, not extra experimental deliverables. The
six additional completed run folders encountered during the snapshot are included
for browsing; their scientific acceptance was not assessed here. No model or
scheduler request was issued by the reporting work. Next action is to inspect
the graphical views and separately review new terminal results against the frozen
13-item ledger. This presentation checkpoint remains local and uncommitted.

## Active Groq diagnostics — 2026-09-23

- [x] Freeze a separate four-position Case T1 runtime-canary protocol, preserving
  the original source, transformation prompts, model and tools. The named
  [protocol note](codebase/agentdojo-lab/CASE-T1-PLACEMENT-GROQ-V1.md) and
  config bind 96 slots and 108 sessions; selected sinks and memory paths must
  be native-confirmed before entering the principal matrix.
- [x] Run the request-free scripted main control (108/108 sessions; all 32
  placement-by-transformation cells eligible). This validates execution and
  report binding, not model behavior.
- [x] Preserve the first, network-restricted pilot as a partial infrastructure
  attempt (three `APIConnectionError` summaries, one interrupted session), then
  run a separate network-enabled pilot. The latter completed 15/16 sessions
  (47 requests, 33,124 tokens), with 11/12 final tasks eligible; the one
  metadata-after verbatim failure is a Groq HTTP 400 schema rejection and is
  retained in the [pilot packet](codebase/agentdojo-lab/reports/20260923-case-t1-placement-pilot-access-retry-v2/index.html).
- [x] Resume only the five never-started slots after the Groq daily-token
  quota recovered, retaining the earlier HTTP 429 trial byte for byte. The
  final batch has 108/108 started sessions, 107 completed, one failed, no
  remaining pause, 346 captured requests and 274,627 reported tokens. The
  [final packet](codebase/agentdojo-lab/reports/20260923-case-t1-placement-groq-v1/index.html)
  has 94/96 eligible final-stage tasks: fresh metadata-after verbatim is 0/3
  original-UUID retention versus 9/9 in the three content arms; two of nine
  in-content paraphrases retain the marker; 12/12 restored B paths recover
  lineage candidates but 0/12 final sinks retain the original marker. The
  [paused packet](codebase/agentdojo-lab/reports/20260923-case-t1-placement-groq-paused-v2/index.html)
  remains a versioned pre-resume snapshot.
- [x] Run a separate offline Tier-2 short-target scaling diagnostic with the
  unchanged LCS implementation: 6,912/6,912 shuffled negatives and 6,775/6,912
  independent negatives match at the fixed threshold. Its
  [report](codebase/agentdojo-lab/reports/20260923-tier2-short-target-scaling-v1/index.html)
  is synthetic, request-free and not source-attribution accuracy.
- [x] Update the dated project context and protocol note with final executed
  counts and failure limits. Verification and Git status are recorded there;
  decide any next named protocol from the observed failure modes rather than
  changing prior interpretations in place.
- [ ] Synchronize the local `codex/agentdojo-lab` commits after the GitHub
  destination and raw-artifact disclosure are approved and authentication is
  repaired. The first local checkpoint is `4af5f4a`; automatic approval review
  rejected its push as an unverified large payload, and `gh auth status` reports
  an invalid token. No alternate push route was used.

## Case R Groq phase — 2026-09-21

- [x] Choose the Groq backend and freeze Case R (recipient contamination; redundant and
  split constructions) with a pilot, a three-repetition main batch, offline attribution
  diagnostics and a forced replay/judge panel. Spec and protocol note are linked from
  PROJECT_CONTEXT.md.
- [x] Run the pilot (8/8 predictions matched), the main batch (24/24 slots) and the
  follow-up panel (6/6 sinks); render the interactive packet
  [reports/20260921-case-r-groq-v1/index.html](codebase/agentdojo-lab/reports/20260921-case-r-groq-v1/index.html).
- [x] Record the candidate systematic pattern: universal Tier-2 correspondence on short
  sensitive arguments closes the causal gate; the forced counterfactual is unstable and
  confounded by benign-content removal. Evidence covers two constructions in one task
  family and one model.
- [ ] Add a second task family (a different sensitive argument, for example a file share
  target or calendar participant) with the same three-repetition design before claiming
  a systematic method limitation.
- [ ] Stage the deferred cross-session memory chain (Cluster 2) on Groq if budget allows.
- [ ] Push the local commits once the GitHub credential on this machine matches the
  repository owner.

## Case M Groq phase — 2026-09-21

- [x] Implement Case M (two sessions, restored drive and DCPG registry, memory-only
  Session B) with offline transport, handoff blocking, pause/resume and packet tests.
- [x] Run the pilot (2/2 chains matched) and the three-repetition main batch (6/6
  chains matched; 3/3 attacks via memory); render
  `codebase/agentdojo-lab/reports/20260921-case-m-groq-v1/index.html`.
- [x] Record that the DCPG recovers the cross-session path in every chain, identically
  for clean and attacked, and that the paraphrase step is matched by subsequence LCS
  rather than the semantic tier.
- [ ] Add a Case M panel to the summary figure and a forced replay/judge panel for the
  Session B sinks if budget allows before the meeting.

## Case R tier diagnostic — 2026-09-22

- [x] Bootstrap the lab on the Linux workstation (uv-managed Python 3.12, semantic and
  figures extras, hash-verified MiniLM) and freeze the tier-ablation design
  (`docs/superpowers/specs/2026-09-22-case-r-tier-diagnostic-design.md`).
- [x] Recompute Tier 3/4 independently on every recorded Case R pair, cross-check against the
  2026-09-21 packet (134/134 agree), and render
  `codebase/agentdojo-lab/reports/20260922-case-r-tier-diagnostic-v1/index.html` plus the
  static figure. Zero requests.
- [x] Record the answer to the supervisor's ordering question: bypassing Tier 2 does not let
  Tier 3/4 localize the attacker-address source (0/10 attacker-sent sinks; Tier 4 hits only the
  legitimate carrier, 13/13), so the Case R limitation is broader than cascade ordering
  (reading B). Bounded substring isolates the carrier 23/23 but cannot see the instruction
  source; no evaluator represents decision influence.
- [x] Tier-1 transformation stress test (Case T1, spec
  `docs/superpowers/specs/2026-09-22-case-t1-canary-transformations-design.md`): pilot 9/9 and
  main 27/27 sessions on Groq (116 requests, 92,756 tokens). Information reached the sink
  24/24; the runtime canary 0/24; Tier 2 caught every pair. Verbatim copies reproduce the
  content field but not the metadata block carrying the canary; an in-content reference
  survives whole-text transformations (9/9) and is dropped by selective ones (0/15). Packet
  `codebase/agentdojo-lab/reports/20260922-case-t1-groq-v1/index.html`.
- [ ] Second task family for Case R (different sensitive argument) before calling the pattern
  systematic; Case M forced replay/judge panel if budget allows.
