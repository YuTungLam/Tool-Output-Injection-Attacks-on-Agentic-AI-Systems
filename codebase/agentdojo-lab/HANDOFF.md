# Handoff: current state and historical notes

## Paper conformance and complete method target — 2026-09-10

Latest user clarification: implement the published method ideas in AgentDojo and
investigate reproducible limitations. Do not require alignment with author code,
original datasets or original result tables. M7 online causal integration is now
implemented and verified. Read [M7-RESULTS.md](M7-RESULTS.md) and
[M7_PROGRESS.json](M7_PROGRESS.json), then inspect the retained
[live interactive report](runs/20260910-online-causal-live-v1/report.html).
Preserve the frozen baseline and all historical records.
The earlier rejection is a Codex subagent error recorded at
2026-09-09T23:16:27.446Z, with an OpenAI cybersecurity-risk message. It is not a
Groq API rejection and does not establish a need for local Llama deployment.

The user explicitly needs the full method working as a usable research baseline.
Start with
[REPRODUCTION-CONTRACT.md](REPRODUCTION-CONTRACT.md). Its M1–M7 checklist separates
implementation requirements from stronger live coverage; original tables are outside scope.
Tier1–4, all four profiles, native file memory, single/pair judge planning, the
completed-trace composer and the native online hook are implemented. The M7 hook
uses a separate no-tools client, bounded one-attempt probes, strict bindings and
typed derived edges. It records decisions before native tool runtime and never
changes actions or model weights. Three completed-trace integrations live under
`reports/20260910-paper-conformance-v1/{explicit-v2,control-v2,memory-v2}`.
Reuse preserves the old auditor's exact planning budget. A narrowly verified
legacy memory adapter supports old explicit paths without laundering missing
condition fields; future memory records declare the passive condition directly.
The initial failed integrations and executed composer remain preserved.

Do not call an omitted source read, unavailable branch, provider/parser error or
execution-policy rejection a paper gap. Do not require independent human labels
or actual agent counterfactual replays merely to declare judge-based code present.
The earlier evidence and failed trials remain unchanged. The retained M7 clean live
run completed with two pre-runtime receipts but zero judge requests: the first
proposal was not a sink, and the only selected sink had six Tier-2 hits. This is a
real skip-path and runtime-integration result, not live eligible-judge coverage.

The next experiment is causal-fallback reachability across native tasks and fixed
source/sink-length controls. Freeze the task set and thresholds before execution;
report routing tier, eligible fraction, unused-source controls, latency and utility.
The first concrete hypothesis is that LCS normalization by the shorter input can
overmatch short sink fields inside long tool outputs and starve the causal fallback.
Do not tune thresholds merely to force judge calls. Keep detector-gating limits,
transport failures and causal-judge errors as separate outcomes.

## Controlled semantic validation — 2026-09-10

Start with [SEMANTIC-VALIDATION-RESULTS.md](SEMANTIC-VALIDATION-RESULTS.md) and
[SEMANTIC_VALIDATION_PROGRESS.json](SEMANTIC_VALIDATION_PROGRESS.json).
This fixed phase is complete and no model calls remain scheduled. Preserve all
sixteen component pairs, four terminal native trials and six fresh auditor replies.
Do not rerun native trials to replace the omitted background reads: all four
agents skipped file 2, so background attribution is unavailable and full requested
observable task compliance is 0/4, despite successful writes and normal endings.

The auditor's new punctuation-compatible mode is explicit and versioned; ASCII/v2
remains the default. Prior invalid results remain invalid. The six fresh v3 replies
are valid, with four agreements and two disagreements against the fixed old replays.
The component diagnostic finds all ordinary comparisons exiting at Tier 2; direct
Tier 3/4 each retain six of eight authored positives and match all six declared
other-origin controls. These mixed reference contracts do not supply independent
real-agent semantic accuracy or confirm a novel research gap.

Use the existing result overview to inspect cases and timelines. Future work should
begin with an explicit new hypothesis and fixed evaluation set, preserving this
baseline. The user's request to run this phase continuously does not imply silently
expanding it with unlimited follow-up model calls.

## Native attack validation — 2026-09-10

Read [ATTACK-VALIDATION-RESULTS.md](ATTACK-VALIDATION-RESULTS.md),
[ATTACK-VALIDATION.md](ATTACK-VALIDATION.md) and
[ATTACK_VALIDATION_PROGRESS.json](ATTACK_VALIDATION_PROGRESS.json) first.
The original sixteen live primary slots are terminal and must not be rerun.
An independently verified mirror restores quarantined metadata byte for byte;
the original language-check failures and process statuses remain preserved.
The new result note separates native attack success, literal correspondence,
one-step replay observations and auditor prediction concordance.
No owner relabeling is required for this phase. Full-paper reproduction remains
incomplete, and the older phase ledgers below are not overall completion scores.

## Method completion and automatic controls — 2026-09-10

Read [METHOD-COMPLETION-RESULTS.md](METHOD-COMPLETION-RESULTS.md) and
[METHOD_COMPLETION_PROGRESS.json](METHOD_COMPLETION_PROGRESS.json) for the new phase.
The original September 9 progress ledger and closeout remain unchanged historical evidence.

The new native cross-session pilot is terminal: four sessions, twelve real Groq requests,
4,830 reported tokens, no replacement runs. Original and neutralized branches each perform
an explicit copy task across separate processes. All copies, expected file reads, restored
origin matches and pre-runtime receipts pass. This is marker-copy/lineage evidence, not an
attack experiment or independent causal accuracy. Use its existing English timelines.

The automatic reference harness completed 84 slots: 21 known-program references under four
fixed profiles. Ordinary cascade has TP10/FP7/FN0/TN1, with three unknown references excluded;
implicit-string has TP10/FP4/FN0/TN4. Do not pool profile repetitions, infer deployment false
positives, or tune the frozen fixture matrix based on these results.

Next research evidence should address semantic and joint-control attribution on actual
agent trajectories, with clearly defined reference semantics and intervention controls.
No manual relabeling of the owner's previous twenty items is required to use the new code.
Independent human accuracy, general memory backend coverage and original numerical tables
remain unvalidated. New APIs and commands are documented in the phase result note.

The older sections below are historical snapshots and do not supersede this phase.

## Final closeout — 2026-09-09

**The bounded reproduction phase is closed with evidence limits. There are no remaining
scheduled steps or model experiments.** Read [CLOSEOUT.md](CLOSEOUT.md) and open
`reports/20260909-reproduction-closeout-v1/index.html` for the English component/claim ledger.
It links original reports and timeline/diagram evidence, keeps native outcomes by protocol,
and provides JSON, JSONL, Markdown, CSV, input snapshots and a hash manifest.

Seven declared local engineering gates remain accepted. Gate8 has final status `not_accepted`
because independent attribution references, second review/adjudication and scoring remain absent;
its acceptance criterion was not relaxed. This differs from leaving the bounded project running.
Independent accuracy, malicious propagation, causal influence, defense benefit and original-table
reproduction remain unvalidated. The report's partial component assessments also disclose missing
specialized thresholds, joint-cause detection and broader memory/framework coverage.

The three repeated native batches have 30 distinct trials without overlap; v2 HTML and scalar
replays are derived reports, not additional executions. Earlier provider failures remain visible.
The twenty assisted labels remain completed Codex development evidence and are not reassigned.
The user-provided-email/LCS observation is a candidate specificity concern, not a confirmed gap.

Use `scripts/export_reproduction_closeout.py --output reports/NEW` for offline regeneration
from present local artifacts. Do not resume or replace any terminal live slot. Source/configuration
and result notes remain on `codex/agentdojo-lab`, committed locally without push. Runtime evidence
and model files require separate transfer; never include `.env` or other credentials.
Further independent evaluation or method improvement is a separately scoped research phase.

All lower sections are historical snapshots; their former "next step" instructions are superseded.

## Latest completed work: prospective passive calendar experiment — 2026-09-09

Read [HELDOUT-RESULTS.md](HELDOUT-RESULTS.md). All ten frozen task8 slots completed once:
five clean and five injected, with passive inputs in both arms. Native utility is 5/5 per arm;
injected payload exposure is 5/5 and native delete-file-13 goal success is 0/5. All 300 prefix
checks pass. There are no unknown evaluations, failures, replacements or native query restarts.
Thirty primary requests report 59,759 tokens; there are zero auditor requests.

Open `reports/20260909-heldout-v2/index.html` for the compact English table and expandable
trial timelines/diagrams. The optional new scalar report is `reports/20260909-heldout-spans-v1`:
12/12 controls, 30 selected fields, 330 scored comparisons, no unavailable comparisons.
Whole-tool LCS flags all twenty user-provided participant emails even though those complete
addresses are absent from the eligible calendar output. Preserve this lexical-candidate limitation;
do not call it independently measured false positives, malicious propagation or causality.

Execution commit: `191fffd46f49f586804079b3f35e198c17737201`. Frozen batch:
`runs/20260909-heldout-v1`; plan SHA-256
`16c79d770492ccebe12f986a73f4e37c0f889e7d464c606214903b78257fb35d`.
At close, all 139 frozen source files and 1,632 older protected artifacts matched. The new
legitimate operation was selected prospectively; source event24/carrier, model, tools and
attack pattern were not unseen. The older strict task29 protocols remain separate.

After batch close, only an analyzer HTML branch was corrected so clean exposure details show
"Not applicable" rather than "Unknown." Original v1 is preserved; corrected v2 JSON/CSV/TEX
are byte-identical. Preflight: 1,383 tests, 67 targeted final protocol checks, Ruff, offline wheel.
After the display correction: 33 report tests. English/static artifact receipts are in
`reports/20260909-heldout-validation-v1/`. Execution resume requires the original frozen source;
there are no unstarted slots to resume. Read-only analysis uses current code without new API calls.

Next is the final evidence/acceptance closeout described in [NEXT-STRATUM.md](NEXT-STRATUM.md).
Seven of eight gates remain accepted. Independent labels, a second review, adjudication and
scoring are still required for independent attribution acceptance; precision/recall/F1 stay null.
The owner's twenty assisted annotations remain complete and must not be repeated or called
independent. No extra model experiments, defense methods, CTTA, weight updates or action blocking
are automatically added. Code/result notes stay on `codex/agentdojo-lab`, committed locally
without push; ignored runtime artifacts require separate transfer, excluding `.env`.

The sections below are historical snapshots and do not supersede this update.

## Latest completed work: offline span diagnostic — 2026-09-09

Read [SPAN-DIAGNOSTIC-RESULTS.md](SPAN-DIAGNOSTIC-RESULTS.md). The optional lexical extension passes
12/12 frozen engineering controls and processes all twenty selected historical runs: sixty total
argument fields, forty selected sink fields, 560 decoded scalar comparisons, no unavailable
comparisons. There are zero full-target literal occurrences inside assigned payload regions. Fifteen
content comparisons require some annotated characters in every optimal LCS alignment; fifteen
file-ID comparisons preserve a zero-to-one annotated-character ambiguity. These are lexical
properties, not confirmed malicious or causal propagation. No new model requests were made.

Open `reports/20260909-span-diagnostic-v1/index.html` for one-field-at-a-time English navigation,
decoded source highlighting, original cascade metrics and links to the original timeline/diagram.
Plan, controls and JSONL are alongside it. Validation is in
`reports/20260909-span-validation-v1/`: 1,290 tests, Ruff, offline wheel, English audit,
200/200 unchanged selected-run files and 1,621/1,621 unchanged older protected artifacts.

The new modules are `span_scalars.py`, `span_evidence.py`, `span_diagnostic.py` and `span_report.py`;
the CLI command is `span-diagnostic`. Source annotation uses exact payload exposure tied to the same
request and decoded scalar. It is not a whole-tool-result malicious label. The adapter currently
accepts only the existing task29 pilot and input-comparison protocols. Original online modules and
prior result artifacts remain unchanged.

This closes the bounded engineering extension. No new acceptance gate was added: seven of eight
gates remain accepted. Next, follow [NEXT-STRATUM.md](NEXT-STRATUM.md) to select and freeze one unseen
native case with five clean/five injected passive runs. That experiment has not been executed.
Independent accuracy remains null. The user's twenty assisted annotations are complete; do not ask
for them again. No CTTA, weight updates, action blocking or attack-success-driven selection.

Work stays on `codex/agentdojo-lab`, committed locally without push. Runtime runs/reports remain
ignored; source, tests, frozen configurations and result notes are tracked. Never archive `.env`.

## Previous completed work: input comparison — 2026-09-09

The injected passive/Canary comparison is complete. Read
[INPUT-COMPARISON-RESULTS.md](INPUT-COMPARISON-RESULTS.md). Each arm completed five fresh trials:
utility 5/5, native attack goal 0/5, payload exposure 5/5. There were no unknown outcomes, failures,
replacements, budget exhaustion or native query restarts. All 320 prefix checks pass, with 100
unchanged primary source files and 1,368 unchanged older protected files. Thirty primary requests
used 80,848 reported tokens; no auditor requests were made. No outcome benefit or malicious
propagation accuracy is established. Gate 8 is still open (7/8 accepted).

Open `reports/20260909-input-comparison-v1/index.html` for the compact English table and expandable
paired/trial details. CSV and LaTeX table exports are alongside it. Complete validation receipts are
in `reports/20260909-input-comparison-validation/`. The batch is
`runs/20260909-input-comparison-v1`; all ten slots are terminal and must not be rerun.

Run code commit: `0d7ea92eddd74f359bd21edf84c0fd7ee6ca2f79`.
Plan SHA-256: `75a166a84ffbe1f2cc25ad2845150d462346cf4df9d553af299c1df3081e59a2`.
All 118 frozen files matched at batch close. Afterward, one analyzer HTML sentence was corrected
because the primary timer excludes initial model loading and finalization/export. Frozen and
corrected analyzer JSON outputs are byte-identical. Preflight: 1,164 tests; after wording fix: 40
report tests. Ruff, offline wheel and English checks pass. Current code can analyze saved batches;
execution resume demands the original frozen implementation and only never-started slots.

The 20 assisted annotations have also been scored offline; read
[ASSISTED-SCORING.md](ASSISTED-SCORING.md). Ten definite file-ID items agree across all three
methods; ten ambiguous content items are excluded. No definitive negative eligible references or
independent attribution metrics exist. Annotation author remains Codex, project owner Donglin Yu.
Do not ask the user to repeat these twenty items or treat assisted judgments as independent labels.

Next: review [NEXT-STRATUM.md](NEXT-STRATUM.md), a draft for span-level measurements separating
benign content reuse from injected-instruction correspondence. Start with disclosed engineering
controls before a prospectively chosen held-out native case. The draft is not executed. Preserve
unknowns, fixed thresholds, all planned outcomes and the no-CTTA/no-weights/no-blocking scope.

Code and result notes are committed locally on `codex/agentdojo-lab`; no push is performed. Ignored
runs, reports, local model cache and credentials are not included in commits. Transfer needed
runtime artifacts separately; never put `.env` into an experiment archive or Git.

The sections below are historical and do not supersede this completed update.

## Current handoff — 2026-09-09

Latest addition: the user delegated all 20 review items. They are completed in
`reports/20260909-assisted-review-v2/` and retained in
`annotations/20260909-pilot-assisted-labels.json`. Project owner is Donglin Yu; actual annotation author
is Codex, explicitly AI-assisted. Results: 10 single-source file-ID matches and 10 ambiguous generated
content fields, with 40 source spans. Read [ASSISTED-REVIEW.md](ASSISTED-REVIEW.md). The original
human packet is unchanged, including its blank on-disk template; any browser-only drafts were not
reloaded or overwritten. Independent accuracy remains null. Do not ask the user to work through
these 20 items again; they requested delegated completion and a short explanation.

Gate 8 has started with the first native clean/injected evaluation stratum. The accepted count remains
**7/8 gates, 87.5%**. Read [EVALUATION.md](EVALUATION.md), [EVALUATION-RESULTS.md](EVALUATION-RESULTS.md),
and [REPRODUCTION_PROGRESS.json](REPRODUCTION_PROGRESS.json). This percentage is a checklist count,
not accuracy, work hours, security benefit, or original-table reproduction.

The first stratum completed all ten trials: native utility 10/10, payload exposure 5/5 injected trials,
attack-goal success 0/5, no unknown evaluations, and no replacement runs. There were 30 primary API
requests and zero auditor requests, using 81,170 reported tokens. All 340 prefix checks pass; frozen
sources and old artifacts remain unchanged. The test suite passes 1,043 tests. The review packet has
20 fields without independent human labels; source precision/recall/F1 remain null. These outcomes do not validate malicious
propagation or a security benefit.

The frozen batch is `runs/20260909-evaluation-pilot-v1`. It uses workspace task 29, injection task 1,
one native direct payload, and five repetitions per condition with Canary enabled. Model, policy,
local MiniLM, thresholds, request caps and order are fixed. Do not replace or retry any started slot.
`dojo-lab evaluate --resume` runs only never-started slots and requires the frozen implementation/runtime.
Each worker also records an exclusive claim before model setup. Plan hash and protected prior artifacts
are recorded in `reports/20260909-evaluation-validation/`.

Native task utility, native attack-goal success, actual payload exposure and source-field attribution
are different measurements. Partial/failed evaluations remain unknown. The native goal evaluator also
runs on clean environments, but its raw value is not counted as injected ASR. Request/token accounting
and pacing are separate from measured synchronous tracer time. Keep all adverse results visible.

Each trial retains the English event timeline and linked diagram. The aggregate report is
`reports/20260909-evaluation-pilot-v1/index.html`. The human review packet is
`reports/20260909-evaluation-review-v1/`; keep its private `review-key.json` out of any reviewer handout.
The page hides model scores, conditions and outcomes, but exact text can reveal condition, so blinding
is partial. Labels remain blank until a human completes them. Validate a downloaded label JSON with
`dojo-lab review-labels --packet <packet-directory> --labels <downloaded-json>`.
The validator checks provenance and attestations, not actual reviewer identity. Do not invent labels.

Next: obtain independent source-content correspondence judgments, a second review and adjudication,
then freeze those labels before computing attribution precision/recall/F1. Broader cases, passive/Canary
primary comparisons, other ablations and causal validation remain open. Exact/LCS comparisons on a
saved marked trace are computational comparisons, not a passive primary arm or measured security benefit.

One disclosed boundary remains: native no-final-text query restarts retain their simulated environment,
while the current DCPG adapter retires active memory bindings at the episode boundary. Multi-attempt
ancestry must be marked unavailable, not negative or proof of environment reset. The general tracer was
not silently changed during the frozen pilot. The earlier gate 7 A/B auditor remains a deferred,
no-tools prediction; it does not execute a native counterfactual agent.

No CTTA, weight updates, action blocking, or real-account operations are included. Branch remains
`codex/agentdojo-lab`; local changes are committed at the end of the session, with no push. Ignored
`runs/`, `reports/`, and `.model-cache/` need separate transfer to continue on another machine.
The material below is historical and does not supersede this update.

---

最新补记：2026-09-08（Pacific/Auckland）。下方 2026-09-07 的详细交接保留为历史快照，当前状态以本补记、[PROVENANCE.md](PROVENANCE.md) 和 [SEMANTIC.md](SEMANTIC.md) 为准。

最新用户约定：按论文方法独立重实现，不等待作者代码，也不以逐值复制原论文表格为前提。复现失败需区分实现问题、设定差异和方法局限，再验证是否构成 gap。所有生成 HTML、diagram、JSONL 说明与助手标注使用英文，对话可继续中文。详见 [REPRODUCTION.md](REPRODUCTION.md)。

已新增 `ProvenanceTracker.consume(event)`、参数级精确匹配、NeuroTaint-style Tier 2 LCS、空白来源核查包和本地 HTML 证据报告。已有 10 条真实轨迹按历史前缀重放得到 21 次提议、54 个叶参数：27 个单来源候选、4 个多来源候选、23 个没有精确证据。没有增加 Groq 调用。

随后已新增可选 MiniLM Tier 3 整段与 Tier 4 分块语义组件，固定 revision/文件哈希/分块假设/截断范围；命令与最新结果见 SEMANTIC.md。8 个教学案例已整理为助手开发标注草稿，明确非盲、非独立，仍需人工核查。

Current progress (2026-09-08): gate 6 is accepted for the declared engineering scope; six of eight
acceptance gates are complete. Read [CANARY.md](CANARY.md) and [CANARY-RESULTS.md](CANARY-RESULTS.md).
The default remains passive. The explicit canary_enabled condition appends one unpredictable UUID to
eligible native source results, records an intervention audit, validates publication and actual request
exposure, and checks exact sink-argument membership before the other cascade tiers. Original native
returns and environment snapshots are preserved. The private DCPG checkpoint retains original marker
references only under the matching condition/profile and confirmed memory retrieval/exposure.

All 760 tests pass. Fourteen native control runs pass replay; scripted copy reaches Tier 1 with zero
subsequent LCS/encoder entries, and a second native memory session distinguishes the old stored marker
from the fresh retrieval marker. Ten earlier real traces reproduce full calls and graphs exactly.
All frozen source and old experiment hashes remain unchanged after the recorded trials.

The two selected Groq task31 trials are retained failures: on request two the provider rejects
search_files<|channel|>commentary as an unknown tool. Each has one native search proposal/execution,
one pre-runtime receipt, complete observation, and exact replay. The Canary arm assigns, publishes and
exposes one UUID. Neither reaches a sink or native utility evaluation: live sink survival is unavailable,
not a negative, and utility remains unknown. Do not rerun the frozen pair to obtain a preferred result.

Open reports/20260908-canary-pair-v1/index.html for the pair, or
runs/20260908-canary-native-control/cross-session-memory/session2/report.html for controlled restoration.
Each report retains the timeline and diagram; the intervention event exposes original/marked text.
HTML and decoded JSONL pass the English-only audit (64 HTML and 118 JSONL files).

Next is gate 7: freeze paper-based sink-triggered source neutralization and comparison in isolated
shadow contexts, with no native tool execution by probes and no primary action changes. Gate 8 remains
independent clean/injected evaluation. The provider's malformed-tool-name error also limits these real
trials; it is not yet a NeuroTaint gap. No CTTA, weight updates or action blocking is included.

[REPRODUCTION_PROGRESS.json](REPRODUCTION_PROGRESS.json) remains the gate-status record. Earlier
ordinary-cascade and independent-scoring modes and evidence remain preserved. Independent source ground
truth, attribution accuracy, malicious propagation, and causal validation remain pending. Keep failures,
unsupported operations and source-policy exclusions visible. Continuing older frozen clean repetitions
requires their original implementation snapshot; do not bypass hash checks. `runs/`, `reports/`, and
`.model-cache/` are ignored: another machine needs those artifacts and the pinned local model separately.

---

以下为 2026-09-07 的交接快照。

## 先读这一段

AgentDojo + Groq 已搭好，运行时 recorder、每次实验的独立交互 HTML、时间线与 diagram 联动、多任务批次和论文式导出均已实现。首轮 10 个不同正常任务已完成，全部通过原生效用评估，10 份记录完整且通过审计。

**当前只有可核查的运行记录与工具输出曝光关联，尚未实现参数来源匹配，也未验证恶意传播。** 下一阶段的优先事项是来源标注、参数级匹配和 NeuroTaint-style baseline，再根据错误分析确定改进机制。后两轮 20 次 clean 重复已预定但尚未运行，不是来源归因实验的替代品。

本次 handoff 仅整理已有工作与讨论，不启动额外模型调用、实验或定时任务。

## Material Passport

- Origin Skill: academic-research-suite
- Origin Mode: experiment handoff / planning
- Origin Date: 2026-09-07
- Verification Status: MIXED — 已完成工程状态与首轮结果已核对；算法方案为待实现、待验证建议
- Version Label: recorder-to-provenance-handoff-v1

## 1. 工作区、分支与环境

- 仓库：`/Users/Jerry/Documents/GitHub/YuTungLam/Agentic AI Cybersecurity`
- 实验目录：`codebase/agentdojo-lab/`
- 当前分支：`codex/agentdojo-lab`
- 本 handoff 创建前的最新提交：`5c7939d`，首轮结果说明。
- 实验实现提交：`226d7bd`，冻结 clean pilot、配额控制与离线回放对照。
- HTML 流程图联动提交：`0a97260`。
- Python：3.12.14；本机 `.venv` 已安装。
- AgentDojo：0.1.35，benchmark `v1.2.2`，上游 commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60`，上游未修改。
- 模型：Groq `openai/gpt-oss-120b`；temperature 0、reasoning effort low、completion 上限 4096、工具循环上限 8、SDK timeout 60 秒、SDK 不重试。
- `.env` 已有用户填写的 `GROQ_API_KEY`。不要读出、打印、提交或让用户贴到聊天。`doctor` 可只检查设置状态。
- 仓库根目录的 `deliverables/` 是已有未跟踪内容，保持原状，不混入本任务提交。

当前目标：单 agent、单会话、AgentDojo 本地模拟环境内的被动记录与来源分析。暂不做 CTTA/TTA、参数更新、自动阻断、输入净化、跨会话记忆或真实账户操作。

## 2. 已完成与尚未完成

| 项目 | 状态 |
| --- | --- |
| AgentDojo 原生 pipeline 与 Groq 接入 | 已完成，真实模型已运行 |
| 运行时事件采集、ID 关联、完整性检查 | 已完成当前观测范围内的实现与验证 |
| 每次实验独立 HTML、时间线、diagram 联动 | 已完成 |
| 批次冻结、独立进程、恢复、HTML/CSV 总览 | 已完成 |
| 正常任务首轮 | 10 个不同任务，各 1 次，已完成 |
| 正常任务第 2、3 轮 | 20 个槽位尚未开始 |
| 固定响应下采集开/关对照 | 两条正常轨迹已完成；有严格解释边界 |
| 来源字段/片段注册与参数匹配 | 未实现 |
| 独立来源标签、歧义与未知标签 | 未建立 |
| NeuroTaint-style baseline | 只做了论文与公开材料核查，尚未实现或复现 |
| 恶意内容传播、控制影响、越权判定评测 | 尚未完成 |
| 在线归因准确率、执行前及时性、归因成本 | 尚无结果 |

上一轮代码验证为 **164 项本地测试通过，Ruff 通过，wheel 构建与打包内容核对通过**。本次只新增文档，无须重复全部测试。HTML 已做结构、脚本语法与筛选函数验证；没有执行浏览器视觉验收，不要写成已做。

## 3. 当前 recorder 到底记录什么

| 事件/材料 | 内容与边界 |
| --- | --- |
| manifest / 原生记录 | 用户任务、配置、上游版本、最终回答与原生效用结果 |
| `EPISODE_STARTED` / `EPISODE_ENDED` | pipeline 调用起止、初始环境 |
| `MODEL_REQUEST` | HTTP 客户端实际出站 JSON，包括 messages、工具定义与生成参数 |
| `MODEL_RESPONSE` / `MODEL_PARSED` / `MODEL_ERROR` | API 响应正文、原始调用、解析计数和异常类型 |
| `TOOL_CALL_PROPOSED` | 模型提议的函数和参数 |
| `TOOL_RUNTIME_STARTED` / `TOOL_RUNTIME_RETURNED` | 顶层 runtime 入口参数、返回对象即时 JSON 快照、错误 |
| `TOOL_RESULT` | 原生 executor 形成的 tool 消息，包括最终格式化文本 |
| `TOOL_OUTPUT_EXPOSED` | 某条工具结果进入了哪次出站请求，保存来源事件 ID 和消息位置 |
| `ENVIRONMENT_CHANGE` | 单次顶层调用前后的环境快照；只表示前后净变化 |
| `RUN_END` / 批次 execution | 正常结束或异常状态；进程超时/中断另有批次级记录 |

每条事件有 run/task/episode/request/call 身份、事件顺序、UTC/单调时钟与父事件引用；已知 API 密钥被脱敏，HTTP 鉴权头不入日志。

必须保持的解释边界：

- 出站请求包含某内容，不证明服务端已收到或模型关注了它。
- runtime 参数是在内部校验、默认值补全之前捕获；不称为工具内部所有最终参数。
- 当前不观察嵌套 runtime 内部调用、所有中间状态或模型内部真实推理。
- `call_ref` 和父事件引用表示执行关系，不能直接当作字段级来源或因果边。
- `recording.complete` 与 audit 有效是记录质量指标，不是来源归因准确率。
- 来源不可信不等于内容恶意；正常 agent 本来就需要使用外部信息。

## 4. 已完成实验与入口

主批次：`runs/20260907T025045Z-clean-pilot-b93eae95/`。

固定任务顺序为 workspace `0, 7, 9, 14, 18, 20, 28, 29, 32, 33`。按覆盖目的选择，涉及日历、邮件、联系人和云盘；并非随机 benchmark 样本。

| 首轮指标 | 数值 |
| --- | ---: |
| 已完成 / 原生效用通过 / 记录完整且审计有效 | 10 / 10 / 10 |
| 预定总 trial / 待运行 | 30 / 20 |
| SDK 请求 | 31 |
| API 报告输入 / 输出 tokens | 65,277 / 2,896 |
| 事件 / 工具调用 / 工具种类 | 260 / 21 / 12 |
| 工具输出曝光 / 环境变化事件 | 35 / 8 |
| 已有工具输出且又提出新调用的请求 | 11 |
| 工具错误 / HTTP 错误 | 2 / 0 |
| 单响应包含多个工具调用 | 0（真实覆盖缺口，离线测试有覆盖） |

task 0 和 task 33 各出现一次工具错误，模型随后修正，最终效用通过。11 个请求仅提供来源分析机会，尚无来源标签。10/10 不能推广为整个 benchmark 的成功率或防御效果。

首次未节流的诊断批次 `runs/20260907T024217Z-clean-pilot-3d075ef1/` 共完成 8 次，其中 2 次通过，6 次因 HTTP 429 无法评估。其日志保留，**不与主批次合并**。当前主批次采用 7,000 tokens / 65 秒窗口等待；超时上限 600 秒。配额等待单独统计，不能当成 tracer 开销。

两条固定正常响应的离线对照位于 `reports/pilot-replay-cost-clock-controlled/`：task 0、7 各 5 个测量配对，另各 1 对预热；请求与 episode 终态一致，开启采集的记录均通过审计。配对耗时差中位数为 4.408 ms、6.971 ms；存在约 −31.13 ms 的原始差值。时钟受控、样本少且有调度噪声，不能推广成真实线上开销或普遍非干扰结论。

入口（路径相对本文件）：

- [完整首轮实验说明](pilot-results.md)
- [交互批次总览](runs/20260907T025045Z-clean-pilot-b93eae95/index.html)
- [逐 trial CSV](runs/20260907T025045Z-clean-pilot-b93eae95/trials.csv)
- [论文式表格 PDF](reports/clean-pilot-v1-round1/table_runs.pdf)
- [示例轨迹 PDF](reports/clean-pilot-v1-round1/figure_trace.pdf)
- [离线回放对照 HTML](reports/pilot-replay-cost-clock-controlled/report.html)

示例轨迹是 `r01-user_task_9 / episode:00000002`，由目录名逆序选取，不是按真实执行时间选择的“最新”任务。派生图注已补正；通用导出器的 caption 仍有这一措辞限制。

## 5. 刚讨论的技术路线：待实现建议

### 5.1 最小目标

给定一个真实 `TOOL_CALL_PROPOSED`，只用当时已发生的事件，定位其参数的候选来源片段，并输出证据类型、歧义与未知。先追踪来源，再单独判断授权与恶意性。

第一版不承诺“完整理解所有恶意传播”。需要分开输出三种结论：

1. **曝光事实**：某片段进入过对应出站请求。
2. **内容复用证据**：后续参数与该片段存在复制或改写关系。
3. **行为影响证据**：受控干预下工具选择或参数发生变化。

这些均不自动等于越权。动作是否违背用户授权是另一项独立判断。

### 5.2 来源注册与参数级匹配

- 给所有工具结果建立 source 档案，保留字段位置、文本范围和原文；也检查用户请求及其他来源，避免把重复实体强行归给某个工具。
- 根据 `TOOL_OUTPUT_EXPOSED` 确认来源与请求的可见关系；保留此前来源和中间表示的历史，不能把当前原文不再可见直接当成无影响。
- 逐参数比较，例如 `recipient`、`subject`、`body` 各自归因；不要把整次调用或其全部返回内容自动染成恶意。
- 先做精确实体/字符串匹配，再做片段语义候选；相似度不是因果概率。
- 允许多个候选、歧义和未知。不能用“最高分必为真源”规避困难样本。
- 来源标识放在 tracer 自己的状态中，不插进被测 agent 的提示。

建议的独立结果字段包括：目标提议事件、目标参数路径、来源事件、来源字段/文本范围、证据类型、候选来源集合、判定状态、可用历史截止事件，以及结果产生时间。具体 schema 尚未实现。

### 5.3 控制影响的后续复核

字符串/语义匹配处理不了“没有复制内容但改变工具选择”的情况。后续可在隔离的上下文副本中，用同一模型预测候选指令被弱化后的动作；影子分支只预测，不执行工具，也不改主运行。

必须控制删除正常任务信息造成的混淆：保留任务所需事实，加入普通内容替换对照，并重复观察。若先前摘要已携带源信息，需要说明中间表示是否也被处理；单删原文后动作不变不能证明无影响。

这一环节输出干预条件下的行为变化证据。LLM judge 的自报 confidence 不是真值，也不是校准的因果概率。昂贵复核若晚于工具执行，记为 late，不算执行前归因成功。

### 5.4 候选研究假设

**在多来源包含相似信息的情况下，显式处理来源竞争和不确定性，并把额外推理预算分配给难例，能否减少错误归因，同时保持足够覆盖率？**

这只是待验证假设。来源图、语义匹配、增量维护或反事实检查本身已有相关工作，不能直接当作创新。先固定 baseline，再通过错误分析和消融判断改动是否有价值。

## 6. NeuroTaint：查到了什么，没查到什么

本次已读 [Ghost in the Agent / NeuroTaint，arXiv v1](https://arxiv.org/html/2604.23374v1)。它已有运行时增量来源图、词法/语义跟踪与 sink 处分析。因此不能把“改成 online”本身作为贡献。[§4](https://arxiv.org/html/2604.23374v1#S4)

其 Tier 1 向工具结果插入 UUID canary，会改变输入；若作为工程探针，需要独立报告。我们的被动主条件应明确禁用该机制，并披露与原方法的差异。[§4.2](https://arxiv.org/html/2604.23374v1#S4.SS2)

目前没有从论文、arXiv 页面及作者主页核实到作者公开实现或本论文 TaintBench 发布包；这不是断言它们永远不公开。现阶段应称为 **NeuroTaint-style 论文重实现/迁移基线**，不得声称已复现官方代码或论文指标。

不要把 GitHub 的同名 Android TaintBench 当作本论文数据集。换成 AgentDojo + Groq、限制单会话、禁用 canary 后，也不能直接对照论文表中的数字声称复现成功。

其他一手参考：

- [AttriGuard](https://arxiv.org/html/2603.10749v1#S4.SS2)：已有固定历史动作的影子预测比较；是控制影响分析的重要参考。本项目暂不采用其阻断行为。
- [CausalArmor](https://arxiv.org/abs/2602.07918)：已有基于消融归因的选择性防御；不应宣称“按需做归因”本身全新。

不需要为等到完整官方 artifact 而停止当前来源标注和简单基线开发；有缺失细节时记录假设，避免悄悄把自己的选择当作论文原方法。

## 7. 今晚可以直接接着做的顺序

以下为建议顺序，尚未执行。

1. **恢复状态**：读本文件与 `pilot-results.md`，检查分支、doctor、主批次数据是否存在。不要从安装或 UI 重做开始。
2. **先定义分析单位与标签**：选已有真实 clean 调用，按参数建立候选来源标注格式。区分精确复用、语义复用、歧义、未知以及是否获用户授权。控制影响暂不伪造标签。
3. **导出供独立标注的小集合**：包含读取后回答、多步 ID/数组复用、跨工具复用、自然错误恢复。标注只根据当时可见历史；参考标签与在线算法状态分开。若由助手预标，标为预标，不能声称独立人工真值。
4. **实现最简单匹配 baseline**：来源注册、请求可见关系、字段级精确匹配、多个候选与未知输出。先利用现有日志离线按事件顺序回放，确保不读取未来；再连接运行时同一接口。
5. **加入 NeuroTaint-style 词法/语义 baseline**：固定实现、阈值及与论文的差异。不得在同一测试集上边调参数边报告最终成绩。
6. **将来源证据接入 HTML**：点击参数能定位候选源片段；图上区分执行边、曝光边、复用证据和行为影响证据。未知不画成确定传播。
7. **根据错误分析安排下一组验证**：当前只有 clean 与接入异常记录，恶意条件轨迹尚待另行建立或核实来源。后续分析使用条件固定、脱敏且来源明确的轨迹及正常对照，再考虑有限预算的影子复核。不要把“场景含恶意内容”预先标成“实际传播成功”。

第一阶段验收：对一组已有真实调用，能输出可人工核查的 `source fragment → argument` 证据；来源重复时保留歧义；无证据时输出未知；在线结果不读取未来。至少覆盖正常引用，避免把所有外部信息使用都当成 malicious。

后续指标：来源/参数边的 precision、recall、F1，正常引用误报率，候选覆盖与未知比例，额外模型请求/tokens，归因延迟及执行前完成比例。不同方法使用同一标注集和历史前缀；完整轨迹离线审计若另列，不能冒充在线比较。

## 8. 冻结批次与代码改动的关系

主批次保存 Python 实现、依赖锁、上游、配置和协议哈希。`--resume` 只执行尚未开始的槽位，失败/中断槽位不自动重跑。若修改实现或相关冻结材料，恢复会拒绝混用版本。

继续开发归因时，应保留该实验快照。可用提交 `226d7bd` 的独立 checkout/worktree 加原批次目录完成旧重复，或者按新协议创建新批次；**不要修改计划哈希或覆盖旧数据来绕过检查**。已有日志可用于离线归因开发，不需要为了修改分析器重跑全部 agent。

## 9. 常用命令

在当前机器进入实验目录：

```bash
cd '/Users/Jerry/Documents/GitHub/YuTungLam/Agentic AI Cybersecurity/codebase/agentdojo-lab'
.venv/bin/dojo-lab doctor
.venv/bin/dojo-lab inspect --events runs/20260907T025045Z-clean-pilot-b93eae95/runs/r01-user_task_7/events.jsonl
```

代码改动后按范围验证；完整本地检查命令：

```bash
.venv/bin/python -m pytest
.venv/bin/ruff check src tests scripts/replay_recording_cost.py
```

仅在批次空闲时重建派生总览，不调用模型：

```bash
.venv/bin/dojo-lab pilot-report --batch runs/20260907T025045Z-clean-pilot-b93eae95
```

以下命令会产生真实 Groq 请求，仅在决定补齐旧 clean 重复且冻结环境匹配时执行；它不是恢复工作的必做第一步：

```bash
.venv/bin/dojo-lab pilot --resume runs/20260907T025045Z-clean-pilot-b93eae95 --through-repeat 3
```

核心代码入口：

- [运行时观测](src/agentdojo_lab/observation.py)、[事件写入](src/agentdojo_lab/recording.py)、[事件审计](src/agentdojo_lab/inspection.py)
- [原生运行器](src/agentdojo_lab/runner.py)、[Groq 适配器](src/agentdojo_lab/groq_adapter.py)
- [批次执行](src/agentdojo_lab/pilot.py)、[批次报告](src/agentdojo_lab/pilot_report.py)
- [单次 HTML 导出](src/agentdojo_lab/html_report.py)、[HTML 模板](src/agentdojo_lab/templates/run_report.html)
- [离线对照脚本](scripts/replay_recording_cost.py)、[实验协议](protocol.md)、[使用说明](README.md)

## 10. 换电脑继续时

`.env`、`.venv`、`vendor/`、`runs/`、`reports/` 被 Git 忽略。本机提交不等于已推送；本任务没有执行 push。换电脑只有仓库代码时，不会自动带上真实轨迹、HTML 或密钥。

如果今晚用同一台 Mac，可直接继续。如果换机器，需要自行同步所需的完整批次目录和派生报告（批次跳转依赖目录结构），并在新机器本地配置 key。不要把 `.env` 或整份私人日志顺手加入 Git。

新机器安装按 README 执行 `python3 scripts/bootstrap.py`；先确认数据可用，再开始分析。不要因为报告目录缺失就误认为实验从未运行，也不要为重建 HTML 自动重跑付费模型。

## 11. 可以直接贴给下一次助手的续接提示

> 请先阅读 `codebase/agentdojo-lab/HANDOFF.md` 和 `pilot-results.md`，并核对本机状态。现有 AgentDojo + Groq、recorder、交互 HTML 与首轮 clean pilot 已完成，不要重做安装或展示层。
>
> 接下来优先做单会话、参数级来源归因：先准备可独立核查的来源标注格式与小集合，再实现精确匹配 baseline，随后加入明确披露差异的 NeuroTaint-style 基线。所有在线判断只能使用当时历史；允许多个来源和未知；恶意性与来源关系分开。
>
> 保留原始记录与冻结实验快照，不覆盖旧结果，不把攻击条件或最终 evaluator 标签泄漏给 tracer。不更新模型参数、不修改主运行输入、不自动阻断动作。先完成可离线开发的部分，再根据需要安排真实模型实验。请区分已实现、建议和待验证假设。
