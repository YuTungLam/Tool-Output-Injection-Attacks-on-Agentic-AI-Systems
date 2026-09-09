# NeuroTaint reproduction: bounded closeout

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: offline validation and evidence synthesis
- Origin Date: 2026-09-09
- Verification Status: ANALYZED; saved evidence and output integrity checked, no new model experiment
- Version Label: reproduction-closeout-v1

## Final disposition

**This bounded AgentDojo adaptation is closed with evidence limits.** Seven local engineering
gates are accepted. Independent attribution evaluation is not accepted. This records the final
state of the agreed phase; it does not schedule more experiments or assert complete equivalence
to the authors' implementation or original numerical tables.

Open [the English closeout](reports/20260909-reproduction-closeout-v1/index.html). It starts
with the conclusion and eight component assessments. Expand a component for its implementation
scope, limitations and original evidence. Experiment groups retain separate denominators and
link the existing interactive timelines/diagrams. JSON, JSONL, Markdown and CSV exports are
alongside the report, with input snapshots and a hash manifest.

The method reference is [Ghost in the Agent: Redefining Information Flow Tracking for LLM Agents,
arXiv v1](https://arxiv.org/html/2604.23374v1). This closeout distinguishes the original offline
auditing design from the project's pre-runtime online observer and deferred auditor adaptation.
The per-component ledger links the relevant primary-source sections and local evidence separately.

## What is established

- Actual outbound requests, tool proposals/results, argument fields, visible sources, policy
  decisions, cascade stages, DCPG state and timing receipts can be inspected in retained runs.
- Fixed-response controls validate observation isolation; real-agent prefixes reproduce saved
  attribution/lineage outputs within the disclosed implementations. These checks establish
  engineering consistency, not that a candidate source caused a generated argument.
- Three distinct repeated experiments completed all ten planned slots each. Task29 pilot
  compares clean/injected with Canary in both arms; task29 input comparison is all injected;
  task8 calendar compares clean/injected with passive inputs. Each arm has utility 5/5 and
  each injected arm has goal success 0/5. No cross-protocol ASR is pooled.
- Their operational inventory is 30 distinct trials, 90 primary requests and 221,777 reported
  primary tokens. These totals exclude earlier integration/control and separate auditor runs.
  The three batch validations contain 340, 320 and 300 passing prefix checks respectively.
- The optional scalar diagnostics and the twenty assisted review items are completed local
  development evidence. They do not become additional model trials or independent labels.

## What remains partial or unvalidated

The local source policy, leaf-argument comparison, chunking/coverage choices, file-backed memory
adapter and counterfactual neutralization are disclosed adaptations. The implementation does
not include the paper's specialized implicit-string/safe-control profiles, joint/conjunctive
cause detection or general memory/backend coverage. Counterfactual outputs are auditor
predictions; no actual counterfactual agent reruns or independent causal accuracy are established.

Independent attribution precision/recall/F1 remain null. Source-field reference reviews,
second review/adjudication and independent scoring were not completed. Real-model cross-session
efficacy, unseen-tool/attack robustness, malicious propagation accuracy and a defense benefit
remain unvalidated. Native task checks have narrower contracts than these claims. The earlier
lineage and Canary provider failures remain retained and are not replaced by later successes.

The 7/8 count measures the accepted local checklist. The report's verified-in-scope / partial /
unvalidated assessments describe the strength and breadth of each claim. An accepted bounded
engineering gate can still be a partial adaptation of a broader paper component.

## Candidate follow-up, not a concluded gap

In the calendar batch, twenty participant-email fields were supplied directly by the user and
were absent as complete literals from eligible tool output. Nevertheless, whole-output LCS
produced scores of 0.8696–0.9688 and selected that tool as a candidate. The exact observations
are in [the lexical receipt](reports/20260909-heldout-validation-v1/lexical-observations.json).
This motivates investigating candidate specificity. It does not establish an independent
false-positive rate, the model's hidden reliance or a confirmed flaw in the original method.

## Handoff and reproducibility

The closeout exporter reads existing evidence and rejects inconsistent hashes, overlapping
batch identities, missing references and malformed accounting. It writes only to a fresh
output directory. To regenerate from the same local evidence without API calls:

```bash
.venv/bin/python scripts/export_reproduction_closeout.py --output reports/my-closeout
```

Keep older run and report artifacts unchanged. Existing live batches are terminal and must not
be retried or replaced. Runtime HTML/JSONL and model caches remain local and ignored by Git;
source, configuration and result notes are committed on `codex/agentdojo-lab`. Transfer needed
runtime artifacts separately, excluding credentials. The user's twenty assisted items remain
complete and are not assigned for another review during this closeout.

Closeout verification: 34 integrity tests and Ruff pass; 675 referenced source files match the
export manifest, and all 1,916 protected older files remain unchanged. Static QA checks 65 local
links, eight output hashes and folded report details. The English audit covers 153 HTML and
244 decoded JSONL files with no Chinese ideographs. Browser interaction and visual layout were
not tested in this closeout. See [the validation receipt](reports/20260909-closeout-validation-v1/quality.json).

Any later independent evaluation or method improvement is a separate research phase. No CTTA,
weight updates, action blocking or additional model experiment is part of this completed phase.
