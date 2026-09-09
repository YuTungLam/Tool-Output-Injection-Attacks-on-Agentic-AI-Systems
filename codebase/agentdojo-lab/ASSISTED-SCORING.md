# Exploratory assisted agreement — 2026-09-09

The saved 20-item review is now joined to the first pilot's recorded predictions.
Project owner: Donglin Yu. Annotation author: Codex. These retrospective,
AI-assisted judgments are not independent human ground truth.

| Measurement | Observed result |
| --- | --- |
| Reviewed fields | 20 |
| Definitive file-ID fields | 10 |
| Ambiguous generated-content fields | 10 |
| Definitive negative eligible source references | 0 |
| Exact agreement on comparable source pairs | 10/10 |
| LCS agreement on comparable source pairs | 10/10 |
| Saved cascade agreement on comparable source pairs | 10/10 |
| Independent precision, recall, F1 | Unavailable |

Only half the fields have definitive judgments. All definitive references are
positive file-ID correspondences. The 10/10 counts therefore do not establish
specificity, general attribution accuracy, or accurate malicious-span tracing.
LCS and the saved cascade predict a correspondence for all ten ambiguous content
fields; exact matching predicts none. This difference needs finer source-span
and generated-claim assessment before it can be called a false positive or a
method gap.

The scorer validates packet and private identity-map digests, all 40 referenced
source artifacts, field/call/source identities, request pointers and evidence
spans before joining predictions. Repeated occurrences of one source count as
one source: any definite match is positive; every occurrence must be completely
negative for a negative prediction; otherwise the prediction is unknown.
Policy-excluded context sources are not negative examples. Ambiguous and
unjudgeable references are excluded from agreement denominators.

No new model calls were made. Label bytes, packet material and referenced traces
were unchanged. Canonical label SHA-256:
`6db72600c05d542c759142f4f22b5042adff13afa4ac31122097c024399ed7fa`.

Open `reports/20260909-assisted-scoring-v1/index.html` for a compact English table
and expandable item details. Machine-readable evidence is in
`reports/20260909-assisted-scoring-v1/assisted-agreement.json`.

Re-analysis requires a new output directory:

```bash
.venv/bin/dojo-lab assisted-score \
  --packet reports/20260909-evaluation-review-v1 \
  --labels annotations/20260909-pilot-assisted-labels.json \
  --output reports/<new-assisted-scoring-directory>
```

The user does not need to repeat these 20 items. Independent evaluation and
broader, prospectively chosen cases remain open under gate 8.
