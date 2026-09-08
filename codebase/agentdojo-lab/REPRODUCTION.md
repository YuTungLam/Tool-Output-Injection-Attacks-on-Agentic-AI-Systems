# Paper-based NeuroTaint reproduction

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: implementation and experiment planning
- Origin Date: 2026-09-08
- Verification Status: user-approved scope; method validation is ongoing
- Version Label: paper-based-reproduction-v1

## Objective

Independently implement NeuroTaint from the published method and test whether it works in the AgentDojo
setting. Access to author code is not a prerequisite. Matching the original tables numerically is not the
acceptance condition. The paper remains the method reference; original code or artifacts may provide
additional checks if they become available.

Implement specified components faithfully. Where the paper is incomplete, freeze and disclose the local
choice before interpreting results. Keep separate names and configurations for the paper-based baseline
and proposed modifications. Do not tune thresholds using evaluation labels or describe an engineering
assumption as an author-specified choice.

## Implementation sequence

1. Completed: recorded request prefixes, exact baseline, Tier 2 LCS, local MiniLM Tier 3, and a disclosed
   Tier 4 chunk/coverage implementation. The original independent mode remains available.
2. Completed for the tested integration scope: opt-in live attribution writes a separate JSONL sidecar and
   flush receipts before tool runtime entry. Deterministic native controls preserve requests/actions/history/
   environment. One fresh Groq task has 3/3 pre-runtime analyses, 7 fields and 36 semantic comparisons,
   with exact live/replay agreement. See [ONLINE-RESULTS.md](ONLINE-RESULTS.md).
3. Completed for the ordinary passive condition: frozen workspace source/sink policy and ordered active
   Tier 2–4 routing. Ten saved runs and a fresh Groq task pass replay checks, with actual encoder-boundary
   controls. Tier 1 is explicitly disabled. See [CASCADE-RESULTS.md](CASCADE-RESULTS.md).
4. Add DCPG lineage and memory restoration, a separate canary condition, and sink-driven counterfactual
   analysis. Canary and shadow
   interventions must be distinguished from passive primary runs.
5. Evaluate clean and injected cases with independent source judgments, repeated trials, component ablations,
   false attribution/unknown/ambiguity analysis, timing, and resource costs.

No CTTA, model-weight updates, automatic action blocking, or real-account operations are part of this scope.

## Acceptance progress

[REPRODUCTION_PROGRESS.json](REPRODUCTION_PROGRESS.json) fixes eight equal acceptance gates. Four are
accepted as of 2026-09-08: local components, deterministic live integration, fresh real-agent timing
validation, and source/sink policy with the ordinary passive cascade. The next gate is DCPG lineage and
memory restoration. This count is not a work estimate,
accuracy measurement, or claim that the original paper's tables have been reproduced. Completing an
independent evaluation can include negative results; benchmark efficacy remains a separate measurement.

## How a reproduction failure becomes a research question

A failure is evidence to investigate, not automatically a research gap. Preserve the exact inputs,
configuration, source/argument identities, outputs, and repeat results. Then distinguish:

- Implementation errors, including serialization, tokenization, time boundaries, and missing instrumentation.
- Underspecified choices and sensitivity to reasonable alternate chunking, thresholds, and neutralization.
- Setting differences, including model, tool format, task distribution, and source availability.
- Method limitations that persist after the above checks, such as topical overlap, competing sources,
  short identifiers, transformed facts, or decision changes without copied content.

Develop a gap claim only when controlled examples and evaluation support the limitation. Keep unsuccessful
runs and negative findings. Neither similarity nor a judge confidence score constitutes causal ground truth.

## Language convention

Generated HTML interfaces, diagrams, report explanations, JSONL annotations, and assistant-authored notes
are in English. Conversation with the user may remain Chinese. Future descriptive task metadata is English.

Existing observed event/native records already contain no Chinese text. The language migration changes
presentation text and assistant annotation notes, preserving event contents, source IDs, offsets, scores,
measurements, and frozen experiment hashes. Legacy Chinese task descriptions receive an explicitly labelled
English rendering in derived pilot pages; the frozen source configuration is unchanged.

Audit all generated HTML and decoded JSONL keys/string values with:

```bash
.venv/bin/python scripts/audit_report_language.py
```

The audit detects Chinese text after JSON decoding and in HTML entities/Unicode escapes; encoding text
with escapes is not a translation. Raw evidence must not be silently translated or rewritten. If future
experiments intentionally introduce non-English source data, retain the observation and distinguish an
English presentation from original evidence explicitly.
