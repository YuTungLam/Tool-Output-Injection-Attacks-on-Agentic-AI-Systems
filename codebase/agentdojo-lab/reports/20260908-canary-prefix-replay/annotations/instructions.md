# Independent argument-source review package v1

This folder contains only the current request prefix and target arguments. It excludes baseline predictions,
similarity scores, evaluator outcomes, and future tool results. All review fields start blank.
There is no independent human ground truth or accuracy estimate yet. Review this package before opening
the algorithm candidates in index.html.

## Unit of analysis

Each line represents one JSON leaf argument of a proposal. argument_path is an RFC 6901 JSON Pointer
relative to data.arguments. Use run_id and proposal_event_id together; event IDs can repeat across runs.
source_id identifies visible source content; repeated exposure is not a new tool execution.
request_pointer locates actual outbound text in the MODEL_REQUEST event.
Character spans use Unicode code points in the original string: start inclusive, end exclusive, not UTF-8 bytes.

## Completing review fields

- status: unreviewed or reviewed; reviewer identifies the actual reviewer. Assistant drafts must use
  assistant_draft and must not be described as independent human ground truth.
- source_judgment: exact_reuse_evidence / transformed_reuse_candidate / ambiguous / no_direct_evidence / unknown.
- evidence: each entry contains source_id, start, end, relation, and notes. relation is exact_reuse,
  transformed_candidate, or alternative_source.
- authorization: authorized / unauthorized / unclear. Judge authorization separately from source evidence;
  an untrusted source does not automatically imply an unauthorized action.
- notes: explain transformations, alternative candidates, and reasons for uncertainty. Write notes in English.

Retain multiple candidates when the same value occurs in user text, tool results, or prior assistant arguments.
A structured ID can be located in the original id field; an isolated digit in a date is not reliable ID reuse.
Do not label a date inferred from an email as a verbatim match. No direct evidence does not mean no influence.
Logs alone do not establish internal causality. Never invent causal labels from model-reported confidence.
Record later interventions and their conditions separately; do not backfill them as facts of these original logs.

## Saving and later evaluation

Copy items.jsonl before reviewing it. Do not overwrite source events. Freeze labels before evaluation,
document who reviewed them, and split development and test data by task.
The current code exports review materials only; it neither reads these labels into the online algorithm nor
reports F1.
