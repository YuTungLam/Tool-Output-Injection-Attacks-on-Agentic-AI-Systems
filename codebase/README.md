# Tool-Output Injection Research Harness

This directory contains a sandboxed experimental harness for studying how attacker-controlled content returned by a legitimately invoked tool can influence an LLM agent's subsequent behaviour.

The current implementation is a controlled, synthetic pilot. It uses synthetic tasks, `CANARY-*` values and an in-process simulated sink that cannot produce real external effects. The implementation status below deliberately separates working infrastructure from planned thesis experiments and empirical findings.

## Implementation Status

Last verified on **2026-08-09** while integrating the paired clean noise-floor protocol from commit `694906e044ee76f2e0b30d9c2322e3710190269d` into `main`.

Legend:

- ✅ Completed and covered by the current offline test suite
- 🟡 Incomplete, including partially implemented and planned work

```text
Current main-branch implementation
│
├── ✅ Completed and Reasonably Well Established
│   │
│   ├── ✅ Synthetic Task Testbed
│   │   ├── ✅ Five synthetic tasks
│   │   ├── ✅ Synthetic confidential CANARY tokens
│   │   ├── ✅ Predefined public answer for each task
│   │   ├── ✅ Predefined tool query for each task
│   │   └── ✅ Simulated sensitive sink for each task
│   │
│   ├── ✅ Matched Payload Construction
│   │   ├── ✅ Clean condition
│   │   ├── ✅ Placebo condition
│   │   ├── ✅ Attack condition
│   │   ├── ✅ Shared task, schema and stable fields
│   │   ├── ✅ Controlled payload length
│   │   └── ✅ Stable payload IDs, hashes and fixture versions
│   │
│   ├── ✅ Parameterised Tool-output Fixtures
│   │   ├── ✅ legacy_override
│   │   ├── ✅ exact_function_call
│   │   ├── ✅ task_aligned_audit
│   │   └── ✅ structured_next_action
│   │
│   │   Note: these are currently payload/carrier formulations,
│   │   not four independent attack families.
│   │
│   ├── ✅ Safe Experimental Execution
│   │   ├── ✅ In-process MockDocumentTool
│   │   ├── ✅ Memory-only SimulatedSink
│   │   ├── ✅ Synthetic data only
│   │   ├── ✅ No real external side effects
│   │   └── ✅ Any external effect is treated as a fatal error
│   │
│   ├── ✅ Custom Two-stage Agent Harness
│   │   ├── ✅ Stage 1: shared tool-selection prelude
│   │   ├── ✅ Invocation of the synthetic source tool
│   │   ├── ✅ Exposure of condition-specific tool results
│   │   └── ✅ Stage 2: model response and optional sink action
│   │
│   ├── ✅ Real-model Provider Adapters
│   │   ├── ✅ Gemini adapter
│   │   │   └── ✅ Current default: gemini-3.6-flash
│   │   └── ✅ Groq adapter
│   │       └── ✅ Current default: llama-3.3-70b-versatile
│   │
│   ├── ✅ Reproducible Experiment Planning
│   │   ├── ✅ Matched-set identifiers
│   │   ├── ✅ Repetition scheduling
│   │   ├── ✅ Predeclared seeds
│   │   ├── ✅ Randomised execution order
│   │   ├── ✅ Configuration hashing
│   │   └── ✅ Git commit and dirty-state recording
│   │
│   ├── ✅ Observable Trace Logging
│   │   ├── ✅ Run start and user input
│   │   ├── ✅ Tool selection
│   │   ├── ✅ Normalised tool arguments
│   │   ├── ✅ Raw tool result
│   │   ├── ✅ Defence-boundary decision
│   │   ├── ✅ Tool result exposed to the model
│   │   ├── ✅ Agent decision
│   │   ├── ✅ Sink attempt
│   │   ├── ✅ Sink result
│   │   ├── ✅ Simulated sink effect
│   │   ├── ✅ Task evaluation
│   │   ├── ✅ Run error
│   │   └── ✅ Run termination
│   │
│   ├── ✅ Separation of Sink Outcomes
│   │   ├── ✅ Agent selected/requested a sink action
│   │   ├── ✅ Sink action was attempted
│   │   ├── ✅ Simulator accepted/rejected the arguments
│   │   ├── ✅ Action classified as authorised/unauthorised
│   │   ├── ✅ Prohibited simulated effect recorded
│   │   └── ✅ External side effect recorded separately
│   │
│   ├── ✅ Evidence and Qualification Controls
│   │   ├── ✅ Smoke-test role
│   │   ├── ✅ Capability-control role
│   │   ├── ✅ Vulnerable-calibration role
│   │   ├── ✅ Neutral-calibration role
│   │   ├── ✅ Held-out eligibility checks
│   │   ├── ✅ Incomplete matched-set detection
│   │   └── ✅ Calibration results cannot be reported as formal ASR
│   │
│   ├── ✅ Comparison Infrastructure
│   │   ├── ✅ Clean-versus-placebo comparison
│   │   ├── ✅ Clean-versus-attack comparison
│   │   ├── ✅ First observable structural mismatch
│   │   └── ✅ Control-object divergence position
│   │
│   ├── ✅ Paired Clean Test-retest Noise Floor
│   │   ├── ✅ Dedicated clean-noise-floor analysis mode
│   │   ├── ✅ Matched clean-A/clean-B planning under one shared prelude
│   │   ├── ✅ Complete empirical-pair eligibility checks
│   │   ├── ✅ Control-object discordance comparison
│   │   ├── ✅ First-divergence-stage and missingness metrics
│   │   └── ✅ Explicitly diagnostic rather than attack/defence evidence
│   │
│   └── ✅ Offline Test Coverage
│       ├── ✅ 138 unit tests passing on the integrated main tree
│       ├── ✅ Condition and fixture tests
│       ├── ✅ Experiment-planning tests
│       ├── ✅ Gemini and Groq adapter tests
│       ├── ✅ Trace-validation tests
│       ├── ✅ Qualification-gate tests
│       ├── ✅ Sink and policy tests
│       └── ✅ Clean-noise planning, qualification and comparator tests
│
├── 🟡 Partially Implemented
│   │
│   ├── 🟡 Adversarial Tool Testbed
│   │   ├── ✅ One generic in-process document tool exists
│   │   └── 🟡 It has not been extended into four formal interfaces
│   │
│   ├── 🟡 Attack-taxonomy Content
│   │   ├── ✅ Plain-text instruction payloads exist
│   │   ├── ✅ Role-escalation wording exists
│   │   ├── ✅ A JSON-shaped next-action payload exists
│   │   └── 🟡 These are not yet independent taxonomy fields
│   │
│   ├── 🟡 First Observable Divergence
│   │   ├── ✅ Finds the first difference in retained observable traces
│   │   └── 🟡 Does not observe hidden reasoning or independently prove causality
│   │
│   ├── 🟡 ASR Measurement
│   │   ├── ✅ Basic sink-attempt and simulated-effect rates exist
│   │   └── 🟡 Not yet separated into five objective-specific ASRs
│   │
│   ├── 🟡 D1-related Separation and Provenance Plumbing
│   │   ├── ✅ Prompt, schema and provenance plumbing exists
│   │   ├── ✅ Raw and exposed tool results are recorded separately
│   │   └── 🟡 No real D1 transformation or blocking algorithm
│   │
│   ├── 🟡 D3-related Sandbox Safety
│   │   ├── ✅ A safe simulated sink exists
│   │   └── 🟡 No classifier, output quarantine or memory quarantine
│   │
│   ├── 🟡 D4-related Capability and Authorisation Measurement
│   │   ├── ✅ Strict sink schema exists
│   │   ├── ✅ Authorised/unauthorised outcomes are measured
│   │   └── 🟡 No real pre-execution allow/block gate
│   │
│   ├── 🟡 Performance Measurement
│   │   ├── ✅ Latency is recorded
│   │   ├── ✅ Input, output and total token usage are recorded
│   │   └── 🟡 Defence-specific overhead is not yet calculated
│   │
│   ├── 🟡 Provider-backed Empirical Evidence
│   │   ├── ✅ Gemini and Groq adapters and response contracts exist
│   │   ├── 🟡 No qualified Gemini held-out ASR is established here
│   │   ├── 🟡 No frozen Groq-specific held-out protocol or ASR is established
│   │   └── 🟡 No provider-backed defence-effectiveness result is established
│
└── 🟡 Not Yet Implemented
    │
    ├── 🟡 Four Formal Adversarial Tool Interfaces
    │   ├── 🟡 Mock web search
    │   ├── 🟡 File-system reader
    │   ├── 🟡 API endpoint
    │   └── 🟡 MCP server
    │
    ├── 🟡 First-class AttackSpec Taxonomy
    │   ├── 🟡 attack_family
    │   ├── 🟡 carrier
    │   ├── 🟡 interface/client
    │   ├── 🟡 payload_technique
    │   ├── 🟡 placement
    │   ├── 🟡 propagation
    │   ├── 🟡 objective
    │   └── 🟡 optimisation_regime
    │
    ├── 🟡 Multi-hop cross-tool contamination
    ├── 🟡 MCP server-response injection
    ├── 🟡 LangChain/LangGraph stateful pipeline
    ├── 🟡 Short-horizon tasks of 3–5 steps
    ├── 🟡 Long-horizon tasks of 20+ steps
    ├── 🟡 Agent memory read/write/persistence
    ├── 🟡 Propagation-depth and taint-edge measurement
    │
    ├── 🟡 Formal Three-model Evaluation Matrix
    │   ├── 🟡 GPT 5.5 adapter and protocol
    │   ├── 🟡 Claude Sonnet 5 adapter and protocol
    │   └── 🟡 Llama 4 Scout adapter and protocol
    │
    ├── 🟡 Five Objective-specific ASRs
    │   ├── 🟡 Data-exfiltration ASR
    │   ├── 🟡 Unsafe-action ASR
    │   ├── 🟡 Goal-deviation ASR
    │   ├── 🟡 Cross-tool-contamination ASR
    │   └── 🟡 Memory-corruption ASR
    │
    ├── 🟡 GCG-style Optimisation Attack
    │
    ├── 🟡 MCP Cross-client Study
    │   ├── 🟡 Custom reproducible MCP client
    │   ├── 🟡 Claude Desktop
    │   └── 🟡 Cursor
    │
    ├── 🟡 Ablation Studies
    │   ├── 🟡 Payload position
    │   ├── 🟡 Obfuscation technique
    │   ├── 🟡 Tool/interface type
    │   ├── 🟡 Memory configuration
    │   └── 🟡 Horizon length
    │
    ├── 🟡 Complete Defence Algorithms
    │   ├── 🟡 D1 structured separation
    │   ├── 🟡 D2 trust scoring
    │   ├── 🟡 D3 classification and quarantine
    │   ├── 🟡 D4 least-privilege authorisation
    │   └── 🟡 Combined D1–D4 profile
    │
    ├── 🟡 Matched Defence Experiment Factor
    │   └── 🟡 payload_condition × defence_profile
    │
    ├── 🟡 Adaptive and Defence-aware Attacks
    │
    └── 🟡 Security–Utility Analysis
        ├── 🟡 Residual ASR
        ├── 🟡 ASR reduction
        ├── 🟡 Benign task-completion delta
        ├── 🟡 False-blocking rate
        ├── 🟡 Defence latency/token overhead
        ├── 🟡 Pareto-frontier calculation
        └── 🟡 Predeclared efficiency calculation
```

## Important Taxonomy Boundary

The proposed five attack families do not all describe the same conceptual dimension:

- plain text and JSON/XML describe a carrier or encoding;
- role escalation describes a payload technique;
- multi-hop describes a propagation pattern;
- MCP describes an interface or transport.

The intended first-class representation is therefore multidimensional:

```text
Attack instance
= semantic tool
× transport/client
× carrier format
× payload technique
× placement
× propagation pattern
× attack objective
× optimisation regime
× payload version
```

The five named attacks may remain canonical benchmark families, but they should not be treated as mutually exclusive values of one flat field.

## Experimental-factor Boundary

`Defended` is not a fourth payload condition. The intended design uses two orthogonal factors:

```text
payload_condition ∈ {clean, placebo, attack}
×
defence_profile ∈ {D0, D1, D2, D3, D4, combined}
```

This makes the following matched comparisons possible:

- attack effect: `clean-D0` versus `attack-D0`;
- residual harm: `attack-D0` versus `attack-Dx`;
- benign utility and false blocking: `clean-D0` versus `clean-Dx`;
- placebo cells as an additional negative control.

## Evidence and Claim Boundaries

The current repository provides a tested experimental harness, not a completed empirical thesis evaluation.

- Passing offline tests validates implementation behaviour and trace invariants; it does not establish model susceptibility or defence effectiveness.
- Capability control validates provider, parser, argument and simulated-sink plumbing; it is not attack evidence.
- Calibration determines whether an attack configuration is eligible for later evaluation; it is not held-out ASR.
- First observable divergence is an observable structural mismatch, not hidden reasoning divergence or causal attribution.
- A sink decision, sink attempt, simulator acceptance, policy violation, prohibited simulated effect and external effect are distinct outcomes.
- `pass_through_boundary` is a no-defence baseline seam, not an implemented defence.
- `ScriptedSafePolicy` is an instrumentation control, not a matched D1–D4 defence.
- Generated traces and summaries must be written outside the repository.

## Repository Layout

```text
codebase/
├── configs/
│   └── tasks.json             Frozen synthetic task definitions
├── tool_output_lab/
│   ├── cli.py                 Command-line interface
│   ├── conditions.py          Clean/placebo/attack fixture construction
│   ├── domain.py              Validated domain types
│   ├── experiment.py          Matched experiment controller
│   ├── gemini.py              Gemini provider adapter
│   ├── groq.py                Groq provider adapter
│   ├── llm.py                 Provider-neutral two-stage agent harness
│   ├── policy.py              Scripted instrumentation controls
│   ├── qualification.py       Evidence roles and qualification gates
│   ├── tools.py               Mock source tool and simulated sink
│   └── tracing.py             Versioned JSONL trace schema and validation
├── tests/                     Offline unit and integration tests
└── pyproject.toml             Package and optional-provider dependencies
```

## Offline Verification

From the repository root in Windows PowerShell:

```powershell
Set-Location .\codebase
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

Expected result for the verified `main` snapshot above:

```text
Ran 138 tests
OK
```

## Scripted Demonstration

The scripted policies exercise the harness without calling a model API. Trace and summary artifacts must be written outside the repository:

```powershell
$artifactDirectory = Join-Path $env:TEMP "tool-output-injection-lab"
New-Item -ItemType Directory -Force -Path $artifactDirectory | Out-Null

.\.venv\Scripts\python.exe -m tool_output_lab run `
  --policy vulnerable `
  --trace "$artifactDirectory\scripted-vulnerable.jsonl" `
  --summary "$artifactDirectory\scripted-vulnerable.summary.json"
```

Provider-backed modes require the corresponding optional dependency and locally configured environment variable. Only synthetic tasks are permitted, and moving model aliases are rejected so that the exact model identifier can be recorded.

## Claim-safe Summary

> The current implementation provides a tested, matched two-stage qualification harness with synthetic tasks, parameterised clean/placebo/attack tool outputs, two real-provider adapters, observable trace provenance, repeated-run planning, qualification gates, a simulated sensitive sink and paired clean test-retest noise-floor analysis. It does not yet implement the proposed multi-interface attack taxonomy, multi-hop or memory propagation, three named model backends, short/long-horizon evaluation, GCG optimisation, MCP cross-client study, genuine D1–D4 defences, their combined profile, or the final security–utility analysis.
