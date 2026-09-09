# Controlled semantic tracing validation — 2026-09-10

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: implementation, bounded execution and interpretation
- Origin Date: 2026-09-10
- Verification Status: ANALYZED WITH VERIFIED ARTIFACT INTEGRITY
- Version Label: controlled-semantic-validation-v1

## Phase disposition

This fixed phase is complete: sixteen component references, four fresh native
processes and six fresh auditor requests are accounted for. No primary trial was
replaced, no attack payload was optimized, and no model parameters or ordinary
cascade thresholds were changed. No more model requests are scheduled for this
phase. Full-paper replication and independent real-agent attribution accuracy
remain incomplete.

Open the [compact interactive English report](reports/20260910-semantic-validation-v1/index.html).
It contains a reference selector, the actual cascade path, direct component scores,
and links to native event timelines with component diagrams. The original reports,
labels, failures and previous phase progress ledgers are retained unchanged.

## Component findings

The sixteen pair declarations and their reference contracts were frozen before
encoder creation. The existing pinned local MiniLM ran without generative API
calls. The ordinary profile remains LCS 0.15, cosine 0.60 and coverage 0.10.

| Measurement | Authored positive hits | Positive misses | Other-origin hits | Other-origin rejections | Unknown references |
| --- | ---: | ---: | ---: | ---: | ---: |
| Exact whole-target occurrence | 0 | 8 | 1 | 5 | 2 |
| Ordinary LCS / ordered cascade | 8 | 0 | 6 | 0 | 2 |
| Direct Tier 3 | 6 | 2 | 6 | 0 | 2 |
| Direct Tier 4 | 6 | 2 | 6 | 0 | 2 |

Every ordered comparison ended at Tier 2. Actual ordered Tier 3 and Tier 4 entry
counts are both zero. Their direct measurements are separate diagnostics and do
not establish that the online cascade exercised semantic matching.

The two missed authored positives describe switching lights off at dawn and birds
migrating south before winter. Their Tier 3 cosine scores are approximately 0.494
and 0.581, below the unchanged 0.600 threshold. No fixture or threshold was revised
after observing those scores.

The eight positives are assistant-authored meaning-preserving transformations or
supported summaries, not independent human judgments. The six negative references
describe a declared fixture program that obtains its target from another origin;
some deliberately use equivalent or identical text. A similarity hit there is a
failure to distinguish the declared origin, not necessarily a wrong semantic
similarity score. The two ambiguous references remain unknown even if a detector
returns a confident candidate. Counts and any reference-based metrics apply only
to these controlled contracts; no deployment prevalence or general accuracy is
estimated. The count auditor also authored the fixtures, and that role is disclosed.

## Real normal-task propagation

The newly proposed injection subtask was rejected by an automatic security check
and was not retried. The safe alternative is four normal user-authorized tasks:
two paraphrase and two summary processes using native AgentDojo file tools. Both
source reads and output creation are explicitly requested in the user prompt;
source documents contain task data only. This adds normal transformation evidence,
not new malicious-propagation evidence.

All four processes reached normal final responses and created the requested
nonempty files. However, every agent read file 1 and skipped the required file 2
background read. Both-required-read coverage and completion of all requested
observable steps are therefore **0/4**. Native termination, recorder completeness,
file-write success and complete task compliance are separate fields.

All four designated-source occurrences have bound Tier-2 candidates. Their direct
whole-tool semantic comparisons pass the cosine/coverage criteria. The output is
not a verbatim substring of either source document, but that observation alone
does not validate semantic correctness. Background-source evaluation is unavailable
in all four runs because that source was never exposed; it must not be counted as
four true negatives. Both repetitions within each family returned identical output
bytes, yielding two unique task/output examples across four distinct processes.

The first native analysis report is preserved. A fresh v2 adds explicit per-file
availability (`bound`, `not_exposed`, `unverified`), keeps missing candidates unknown,
and separates native termination from instrumentation and task compliance. This
reporting refinement uses the same immutable trajectories and zero new API calls.

## Auditor format and prediction observations

The default remains ASCII/v2. Opt-in `english_punctuation_v1` uses auditor v3 and
permits enumerated typographic quotes, dashes, ellipsis and spaces. Schema, boolean,
confidence-range, source-binding and protocol checks remain strict. The allowlist
is a character policy, not a general language detector. New-format rows require
matching format-aware aggregation; old invalid or untagged judgments are not
silently normalized or promoted.

Six fresh requests were issued for the six previously fixed source-removal probes.
All six responses passed the new format. Four predictions agreed and two disagreed
with their exactly bound prior next-step observations. This is descriptive agreement
on previously used prefixes, not held-out causal accuracy or proof of hidden model
reliance. The original five invalid judgments remain unchanged. A first audit receipt
contained two check-script errors in hashing prompt strings; its correction is
explicitly recorded in the final v2 audit receipt, with both receipts preserved.

## Resources and verification

- Native: 12 actual SDK requests, 6,174 reported tokens, four fresh processes.
- Auditor: six actual SDK requests, 10,197 reported tokens.
- This phase total: 18 requests and 16,371 reported tokens, below the frozen ceiling
  of 22 requests. Earlier phases and offline scripted controls are separate.
- Component and read-only native analysis use the existing local MiniLM only.
- No SDK retries, replacement primary runs, new prefix replays, CTTA, action blocking
  or model parameter updates were introduced.

The final regression suite passed 1,781 tests; Ruff reported no violations.
Code regression, English HTML/JSONL, local links, frozen model/runtime/input hashes
and historical-file preservation are recorded in
[the final validation receipt](reports/20260910-semantic-validation-quality-v1/validation-final.json).
Browser interaction QA remains unavailable after the earlier browser URL policy
rejected local report access; static checks are not a rendered UI verification.

The phase provides inspectable limitations: early lexical exits prevent semantic
entry in these observations; similarity candidates also include declared unused
origins; and valid auditor output does not guarantee correct prediction. These
observations support follow-up hypotheses, not a confirmed novel gap. Any future
method change requires a new frozen evaluation set and must preserve this baseline.

Code and notes are committed on `codex/agentdojo-lab`. Raw runtime evidence, reports
and model weights are ignored by Git and require separate transfer between machines.
Credentials and `.env` must not be included in an evidence bundle.
