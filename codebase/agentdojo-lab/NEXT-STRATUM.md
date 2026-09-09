# DRAFT: source-span attribution measurement

**Status: proposed, not executed.** This document does not change the running input comparison,
its task, payload, model, thresholds or acceptance status.

## Measurement question

Can the tracer distinguish correspondence to an injected instruction from correspondence to
legitimate content elsewhere in the same tool result, especially when an argument mixes reused
structure and newly generated ideas?

The assisted review has ten definitive file-ID items on which all three methods agree. Ten
long-content items remain ambiguous: LCS/cascade produce ten candidates, exact none. These
AI-assisted judgments establish neither independent accuracy nor a NeuroTaint gap.

The current cascade compares each selected argument leaf with the whole visible source message
([provenance.py](src/agentdojo_lab/provenance.py)). LCS returns a subsequence length and normalized
score, not an alignment to the injected scalar span ([lexical.py](src/agentdojo_lab/lexical.py)).
A whole-result match can reflect benign wording or formatting without localizing the injection.
The payload-exposure audit locates the incoming instruction, but does not connect it to a target span.

## Proposed bounded work

1. **Freeze a development rubric and span schema.** Retain original source/result/request IDs,
   decoded JSON/YAML scalar pointers, and half-open Unicode codepoint ranges in both source and
   target. Split long targets into factual values, activity propositions and structural fragments
   using a deterministic rule. Label candidate spans as injected-content support, other-source
   support, no visible support, or ambiguous/mixed support, with literal/paraphrase/structural
   evidence. Preserve multiple origins. Injection assignment does not establish action causality.
2. **Validate engineering controls first.** Author fixed source/target pairs with benign text and a
   separately marked injection region: copy only benign text, copy only injected text, copy both,
   generate unsupported text, and reuse an ambiguous ID. Include Unicode and escaped scalars.
   Literal correspondences are known by construction; authored paraphrases remain disclosed
   challenge cases. Neither supplies independent human accuracy. Preserve existing whole-result
   scores beside proposed localization; missing localization is not a malicious-span negative.
3. **Freeze one held-out native case before new inference.** Use a documented native read-to-write
   eligibility rule and fixed task-ID order, excluding task 29 and all rubric-development cases.
   Record eligibility rejections. Select a compatible native goal/vector and exact direct payload
   from definitions without testing attack success. Freeze the assignment, rubric, scorer, schedule
   and budgets. Proposed initial
   sample: five clean and five injected runs in a fixed passive condition, with the existing model,
   thresholds and request/time caps. Retain failures, unexposed injections and unsuccessful attacks;
   never replace cases after observing results.

## Acceptance and required evidence

- Controls recover declared literal spans and exact scalar round trips; ambiguous and unscored
  cases retain uncertainty.
- All ten held-out planned slots and source/target artifacts are accounted for, with immutable
  inputs, English reports and separate exposure, native attack outcome and span-correspondence data.
- Reports distinguish benign correspondence from injected-span correspondence and show coverage,
  ambiguity and abstention. A source-level candidate alone cannot become a malicious-span positive.
- Independent accuracy requires human-authored source/target ranges, support verdicts and provenance,
  plus a frozen scoring/adjudication procedure. Reuse current assisted labels only for development;
  do not ask the owner to repeat twenty whole-field items or relabel assistance as independent review.

Without those independent labels, deliver engineering verification and descriptive held-out
measurements with independent precision/recall/F1 left null. Do not promise a security improvement
or interpret correspondence as hidden causal influence. No CTTA, parameter updates or action
blocking is proposed.
