# Decoded scalar diagnostic results

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: bounded implementation and offline experiment
- Origin Date: 2026-09-09
- Verification Status: engineering controls and retrospective replay completed
- Version Label: decoded-scalar-span-evidence-v1

The optional span diagnostic is implemented and validated. It refines lexical source candidates
without changing the online NeuroTaint-style baseline. Open
[`reports/20260909-span-diagnostic-v1/index.html`](reports/20260909-span-diagnostic-v1/index.html).
The viewer shows one selected argument and one source scalar, highlights the assigned payload and
complete literal target occurrences, and links to the original timeline and agent diagram.

## Frozen inputs and scope

All ten completed pilot runs and all ten completed input-comparison runs were selected in their
original schedule order using [`configs/span_replay_v1.json`](configs/span_replay_v1.json).
These twenty historical runs are development data on the same task and payload; this is neither
a new twenty-run model experiment nor a held-out estimate. Native attack-success rates are not pooled.
The analysis makes zero model, embedding or auditor requests.

The configuration fixes twelve Codex-authored engineering controls. Expected values were derived
with independent exhaustive subsequence enumeration before invoking the new engine; they are not
independent human reference labels. See [the protocol](SPAN-DIAGNOSTIC.md).

- Controls SHA-256: `3060eddacb6e28b6c912d5dd5c5ac846c6d16cd77f9c81d8dbe7b73cec1198de`.
- Selection SHA-256: `33ecff461eda9f0e294179508104cc3fd56e606f8713176bb0599bce3bba1bf4`.
- Canonical export plan SHA-256: `83d2f4eb259579252c6120a84e42b05c0a27bfcdabee33e087ebbdde99b51ea7`.

The export plan contains implementation and input inventories frozen before controls and replay.
The decoder separately checks serialized token identities and decoded Unicode spans. Duplicate
keys, aliases, invalid escapes and exhausted budgets produce explicit unavailable evidence.

## Observations

| Measurement | Result | Unit and interpretation |
| --- | ---: | --- |
| Engineering controls | 12/12 passed | Fixed constructed lexical cases |
| Verified historical runs | 20/20 | Complete event and saved-prefix bindings |
| Argument fields | 60 | Includes 20 arguments excluded by the frozen sink policy |
| Selected arguments | 40 | Twenty content fields and twenty file-ID fields |
| Decoded scalar comparisons | 560/560 scored | Fourteen source value scalars per selected argument; correlated observations |
| Comparisons with an assigned payload region | 30 | Two arguments in each of fifteen injected historical runs |
| Complete-target literal hits inside payload regions | 0/30 | Exact full-target rule only; does not measure reused subphrases |
| Unavailable comparisons | 0 | No parser or resource-budget abstentions in this selection |
| Original run files unchanged | 200/200 | Full inventories for the twenty input runs |
| Older protected artifacts unchanged | 1,621/1,621 | Runs, reports and annotations recorded before this package |

Every file-ID target is `3`. It has a bounded exact occurrence in the legitimate `/0/id_` scalar:
twenty such matches are outside assigned payload regions. In the fifteen injected `/1/content`
scalars, the same character can match either an unannotated occurrence or the `3` inside the payload's
`13`. All-optimal LCS bounds correctly retain zero-to-one annotated matches. The boundary-aware
literal matcher does not equate `3` with the token `13`.

The twenty generated content fields have no complete literal occurrence in any source scalar.
For each of the fifteen injected content comparisons, every optimal LCS alignment uses some
characters from the assigned payload region. Across those comparisons the lower/upper annotated
counts range from 13 to 23, out of LCS lengths 202 to 232. These counts describe scattered character
matches, not copied instructions. The fixed incidental-letter control demonstrates why even a high
LCS score or a positive lower bound is insufficient to infer semantic or malicious influence.

Original whole-message cascade metrics are retained alongside these measurements. No previously
reported score is replaced. Their full pair hashes link back to the immutable sidecars. The new
diagnostic establishes location and ambiguity for its lexical rules, not false-positive rates,
independent provenance accuracy, causal dependence or a confirmed NeuroTaint gap.

## Validation and continuation

The full suite passes **1,290 tests**, including native tools behind a mocked SDK transport, prefix
tampering, payload-range binding, incomplete-input abstention, Unicode decoding and local report
navigation. Ruff and the offline wheel build pass. Static report validation confirms all twenty
original-report links; English auditing covers 127 HTML and 207 JSONL files with no Chinese
ideographs. No browser layout inspection or new live model inference was performed.

Validation receipts are under `reports/20260909-span-validation-v1/`. The new self-contained report,
plan, control expectations and JSONL are under `reports/20260909-span-diagnostic-v1/`.
To analyze an existing supported run into a fresh directory:

```bash
.venv/bin/dojo-lab span-diagnostic \
  --run runs/20260909-input-comparison-v1/runs/r01-passive \
  --output reports/my-span-diagnostic
```

Repeat `--run` for additional inputs. The current adapter deliberately supports the two frozen
task29 protocols only. A new native stratum requires an explicit new protocol and adapter validation.

This closes the bounded engineering diagnostic package. It is an extension, not a new reproduction
gate. Gate 8 remains in progress: the next package is one prospectively frozen unseen native case
with five clean and five injected passive runs. Independent attribution accuracy remains null until
the existing independent evaluation requirements are met. The twenty assisted review items remain
completed development evidence; the owner is not asked to repeat them. See [next steps](NEXT-STRATUM.md).
