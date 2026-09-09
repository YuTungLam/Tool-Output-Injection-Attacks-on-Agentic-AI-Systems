# Completed assisted review — 2026-09-09

Project owner: **Donglin Yu**. Annotation author: **Codex**, AI-assisted, retrospective and exploratory.
All **20/20** public review items have a verdict, an explanation and located source evidence.
The independent human packet stays unchanged. This work used no new model API calls.

Open `reports/20260909-assisted-review-v2/review.html`. The page shows one item at a time,
with detailed reasoning and sources collapsed. It exports the completed annotations and saves
optional personal notes separately. Browser storage is best-effort; download notes for a portable copy.
Notes do not change the frozen assistant judgments or attest to human authorship.

Version 2 corrects the project owner's name to Donglin Yu. The main view uses neutral annotation
wording; actual authorship is available under Annotation provenance and retained in exported data.
The 20 judgments and their evidence are unchanged. Version 1 remains an archived artifact. Browser
notes are scoped to both the packet and owner, so the corrected report cannot overwrite notes saved
under the earlier name. The earlier report remains available to read or export those notes.

| Target | Items | Assisted verdict | Evidence |
| --- | ---: | --- | --- |
| `/file_id` | 10 | Single source | Source 4 associates the requested filename with ID `3` in the same record. |
| `/content` | 10 | Ambiguous | Source 4 plausibly supports some objectives; new activities and logistics have no visible specific support. |

There are 40 Unicode source spans. Two Codex agents read all public items and the primary agent
checked their conclusions against the evidence. This is an AI cross-check, not a second human review.
The annotating agents did not receive private mappings or detector scores. The parent conversation
already discussed pilot results and provisional labels, so the process is not an independent blinded evaluation.

## How to interpret the decisions

The ID example has a precise relation: `team-building-activities.docx` is returned with `id_: '3'`,
and the agent proposes appending to `file_id: '3'`. The relevant evidence is that contextual pair,
not an incidental digit in a date, Activity 3 or file 23.

The activity example mixes several questions inside one `/content` argument. The original plan
contains problem solving, communication and team bonds; these partly correspond to the proposed
objectives. Continuing Activities 1–4 with Activities 5–6 and retaining the headings also has structural
support. But the sources do not specify an escape room, a volunteering project, their venues or dates.
Similar goals and formatting cannot establish where the new activity ideas came from. We therefore
retain whole-field ambiguity and identify the unsupported parts explicitly. This is a disclosed
rubric choice, not a unique ground-truth answer: if the unit were only the new activities and logistics,
their visible-support verdict would be `no_visible_source`.

This exposes a concrete evaluation design issue: split factual values, activity propositions and
structural reuse before scoring long arguments. Freeze that finer rubric on a separate development
set, then assess held-out cases. Do not tune a rubric to make this tracer's existing results look better.
This single case does not establish a general flaw in NeuroTaint.

Source correspondence, malicious content propagation and causal influence are separate claims.
Source 4 combines legitimate document content with other material; a supported file-ID match does
not demonstrate propagation of a malicious instruction elsewhere in the same tool result.

## Recreate and validate

The exporter reads only the public packet and assistant answer list. It checks the packet digest,
every item/source identity, verdict cardinality, explanation and Unicode evidence spans. It does not
read the private review key or compute detector accuracy. The original human validator is unchanged
and rejects this assisted envelope as a human submission.

```bash
.venv/bin/dojo-lab assisted-review \
  --packet reports/20260909-evaluation-review-v1 \
  --answers reports/20260909-assisted-review-v2-work/answers.json \
  --owner "Donglin Yu" \
  --output reports/20260909-assisted-review-v2
```

Use a new output directory for another export. `assisted-labels.json` contains the complete declaration,
rubric and judgments; `assisted-labels.jsonl` repeats AI authorship on every row. `validation.json`
reports structural completeness, with independent accuracy left null. The HTML embeds its public evidence.
The canonical `labels_sha256` hashes sorted compact JSON, not the pretty-printed file bytes.

The completed label envelope is also retained in `annotations/20260909-pilot-assisted-labels.json`.
Runtime reports remain ignored by Git and need separate transfer to another machine. Export a new
answer list from that envelope's `answers` field if the temporary working answer file is absent.

The original experiment belongs to its frozen implementation at commit `a4a0da1`. This report code is
a later revision; do not update the old plan hashes or rerun its closed slots to match the new code.
The accepted reproduction count remains **7/8**. Independent attribution accuracy, malicious
propagation validation and causal validation remain pending. The earlier independent-review protocol
is still required for that gate, but it does not prevent continued engineering or exploratory analysis.

## Verification

All **1,056 tests passed in 26.71 seconds**. Ruff and offline wheel checks passed. The new report's
classic JavaScript parses in Node, and pure helpers cover notes round trips, rejected incompatible
imports, annotation provenance and Unicode slicing. No browser visual QA is claimed. All 212 files
in the original frozen batch and review packet retain their hashes. The generated HTML and JSONL
pass the English-language character audit. These are engineering checks, not annotation accuracy tests.
