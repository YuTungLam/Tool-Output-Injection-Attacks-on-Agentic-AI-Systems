# NeSI setup and local inference plan

Last updated: **2026-09-15 UTC**. The CPU lab and pinned MiniLM files have been
restored, and the offline native-tool fixture passes. Hugging Face login and
Scout gated-file access are verified. Local transport is implemented; the pinned
checkpoint is fully downloaded and verified. The first serving-container build
failed; its dependent GPU smoke was cancelled before starting. The separately
named retry has now passed, and a new GPU smoke is queued. No Scout inference
has completed yet. A separate smoke-plus-Case-A wrapper and canonical Case A plan
are verified offline but remain unsubmitted until that queued smoke passes and
its timing is reviewed.

## Recovery in progress — 2026-09-15

The user requested continued runs with percentages and explanations. The fresh
container retry **passed**, and its GPU smoke is now waiting for scheduling
priority with its build dependency fulfilled. See [RESEARCH_PROGRESS.md](RESEARCH_PROGRESS.md) for the checklist
count and the interpretation of every attempt.

| Job | Latest observed state | Bounded scope |
| --- | --- | --- |
| `9039259` | COMPLETED on Genoa `g01`, Slurm elapsed 6m 49s, exit `0:0` | CPU container retry: 8 requested CPUs / 16 allocated logical CPUs, 32 GiB, local SSD, 2 hours maximum; no GPUs |
| `9039289` | PENDING, Priority; `afterok:9039259` fulfilled | Four A100s, 48 requested CPUs, 320 GiB, 1 hour, at most eight synthetic/benign native generation requests |

Do not modify `9039289`, its v2 site file or frozen submission bundle. Its script
ends after smoke and cannot run Case A in the same allocation. Checkpoint
`7b5f1eb` adds a separately named future wrapper,
`codebase/agentdojo-lab/hpc/scout-smoke-case-a.sbatch`. The canonical ignored
preparation is `runs/scout-case-a-prepared-v1`, with zero model requests and plan
SHA-256 `e4311002046d7ce12c9a1729f169159cb4995609e63e4124ce1ecfdad5b40d76`.
If `9039289` passes, use its measured timing to review the two-hour envelope,
then create a new site file, frozen helper bundle, smoke directory and scheduler
log before submitting the wrapper. That new job must repeat synthetic and benign
native smoke in its own allocation before Case A; old receipts cannot authorize it.
The final wrapper/Case/report/smoke selection passed 109 tests plus 16 subtests,
Ruff, Bash syntax and Python compilation. These are offline checks only.

The new protocol is `nesi-scout-container-prep-ssd-gzip1-v2`: same immutable OCI
image, node-local SSD temporary files, gzip compression level 1, and a 6,600-second
build deadline. It reuses the OCI cache and verified model, preserving the old
incomplete rootfs and failed records. It records stage timestamps in
`stages.jsonl`; a running build has no measurable percentage denominator.

Private site file: `/nesi/project/uoa04799/dyu848/tools/scout-site-20260915-v2.env`.
The original site file remains unchanged. New evidence directories under
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/` are:

- `scout-recovery-submission-20260915-v2/`: submission plan and frozen helper copies.
- `container-prep-20260915-v2/`: CPU plan, build log, stages and terminal receipts.
- `scout-smoke-20260915-v2/`: GPU receipts, created only when that phase starts.

The new SIF destination is
`/nesi/nobackup/uoa04799/dyu848/tool-output-lab/containers/vllm-openai-v0.29.0-cu129-ssd-gzip1-v2.sif`.
The published image is **11,042,500,608 bytes**, SHA-256
`2e34131f9ef3257b67e628e735fa76dee506449152f3882bf50204c92e38b6c2`.
`completed.json` confirms inspection/publication and the private site checksum
update. Build time was 391.20 seconds; hashing/publication took another 10.15
seconds. The receipt explicitly says GPU validation has not run. The queued
GPU job includes no research experiment. Scheduler test-only probes predicted a much
later start, but backfilling started the CPU job immediately. Treat queue estimates
as provisional and recheck actual state before reporting results or submitting work.

## Status recheck on 2026-09-15

Read-only `sacct` and retained receipt/log inspection establish:

| Job | Outcome | Evidence/implication |
| --- | --- | --- |
| `9029207` model download | COMPLETED, 27m 05s, exit `0:0` | All 63 pinned files verified; reusable model snapshot is present |
| `9029215` container preparation | FAILED, 50m 31s, Slurm exit `9:0` | Build log ends at SIF creation; wrapper exit is `137`; no `completed.json` or successful SIF-finalization receipt |
| `9029415` GPU smoke | CANCELLED, zero runtime, no start time | Its successful-preparation dependency was not met; no synthetic/native Scout smoke directory or receipt |

The 50-minute build timeout and 30-second kill grace match the observed failure
timing, but the logs only report that the process was killed; timeout is an
inference, not a conclusively recorded cause. Inspect the retained build/partial
artifacts before choosing a new bounded preparation attempt. No retry was
submitted during this checklist/status review, and no new test run is claimed.
The passing software checks below are the 2026-09-14 verification results.

Evidence directory:
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/container-prep-20260914-v1/`
(`build.log`, `job-exit-code.txt`, `plan.json`), plus scheduler log
`evidence/prep-logs/container-9029215.log`. Preserve these failed-attempt records.
That review identified container recovery and a newly named smoke as the next
steps. The recovery outcome and new queued job are recorded above; the cancelled
first attempt remains terminal.
For research deliverables, see [the supervisor checklist](RESEARCH_PLAN.md#supervisor-checklist--checked-2026-09-15).

## Selected storage and sign-in

The researcher delegated storage choices. `nn_storage_quota -p uoa04799` reports
a 200 GiB project allocation and a 10,240 GiB scratch allocation, each with about
1 GiB used at inspection. Scout's pinned 50 safetensors shards total
217,283,738,720 bytes (about 202.4 GiB), exceeding project storage even before
environments and results. The chosen layout is:

| Material | Location |
| --- | --- |
| Code and retained experiment evidence | Existing repository in `/nesi/project/uoa04799/dyu848/repos/` |
| Scout weights | `/nesi/nobackup/uoa04799/dyu848/tool-output-lab/models/` |
| Download, serving, and temporary caches | `/nesi/nobackup/uoa04799/dyu848/tool-output-lab/cache/` and `tmp/` |
| Rebuildable serving containers | `/nesi/nobackup/uoa04799/dyu848/tool-output-lab/containers/` |
| Hugging Face CLI | `/nesi/project/uoa04799/dyu848/tools/hf/bin/hf` |
| Hugging Face credential | Private default `~/.cache/huggingface/`; never in Git or the shared model directory |

The scratch root was created with mode 700. No Scout copy was available in
`/opt/nesi/models/huggingface` at inspection. Scratch is not archival storage:
NeSI's policy permits automatic deletion after 90 days without access. Keep
retained results in project storage and preserve model/container revision and
checksum manifests so cached inputs can be restored.
[NeSI storage guidance](https://docs.nesi.org.nz/Getting_Started/FAQs/Where_should_I_store_my_data/),
[scratch cleanup policy](https://docs.nesi.org.nz/Announcements/Autodeletion_of_Scratch_Filesystem/).

The CLI uses `huggingface_hub==1.30.0`, matching the lab lockfile. Sign-in is
complete on this server. On a new device, run this in your own terminal:

```bash
/nesi/project/uoa04799/dyu848/tools/hf/bin/hf auth login
```

Choose browser sign-in if prompted. No token needs to be pasted into chat.
`hf auth whoami` checks the saved account. On 2026-09-14 both this check and an
authenticated download of Scout's pinned `config.json` succeeded. Its receipt
is `reports/20260914-nesi-setup-v1/scout-authenticated-access.json` in the lab.
[Hugging Face CLI authentication](https://huggingface.co/docs/huggingface_hub/guides/cli#hf-auth-login).

The inspected immutable model revision is
`92f3b1597a195b523d8d9e5700e57e4fbb8f20d3`. Public metadata and MiniLM file-hash
receipts are in `codebase/agentdojo-lab/reports/20260914-nesi-setup-v1/` (ignored
runtime evidence). The public inventory predates authentication; retain it
alongside the later access check and complete download receipts.

## What is available here

Read-only checks of this session found:

| Item | Observed state |
| --- | --- |
| Host | `login03.hpc.nesi.org.nz`; use scheduled compute nodes for inference |
| System Python | `3.9.25`; restored lab `.venv` uses `3.12.14` |
| Scheduler | Slurm; cluster `hpc`; user association with account `uoa04799`, QOS `debug,normal`, default `normal` |
| GPU partitions | `milan`: 4 nodes × 4 `a100`; `genoa`: 4 nodes × 2 `h100`, 4 nodes × 2 `pro_6000`, and 4 nodes × 4 `l4` |
| Environment modules | `uv/0.10.3-GCC-12.3.0`, Miniforge3, and CUDA versions are listed; no vLLM module was found |
| Containers | System Apptainer `1.4.5-3.el9` is available |
| Upstream dependency | Restored at pinned commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60`; `doctor` verifies a clean matching checkout |

Commands used to inspect scheduler metadata:

```bash
sinfo -o '%P %a %l %D %G'
sacctmgr -n -P show assoc user=dyu848 format=Cluster,Account,Partition,QOS,DefaultQOS
```

These succeeded outside the tool's socket-restricted sandbox after read-only escalation. The association establishes an account relationship, not the project's remaining allocation, an approved job budget, or guaranteed GPU scheduling. Recheck inventory when deploying.

NeSI currently documents A100 80 GB (four per Milan node), H100 NVL 94 GB (two), RTX PRO 6000 96 GB (two), and L4 24 GB (four). It recommends keeping GPU jobs within one node because GPUDirect RDMA is not enabled. [NeSI hardware, checked 2026-09-14](https://docs.nesi.org.nz/Batch_Computing/Hardware/)

## Scout feasibility

The requested model is [`meta-llama/Llama-4-Scout-17B-16E-Instruct`](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct). Meta specifies **17 billion activated parameters but 109 billion total parameters**. The full expert weights still need storage. Account approval and authenticated gated-file access are verified. [Meta model card, checked 2026-09-14](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct)

Approximate **weights-only estimates**, calculated from 109 billion parameters:

| Representation | Raw estimate | Interpretation |
| --- | --- | --- |
| BF16 / FP16 | 218 GB, about 203 GiB | First unquantized candidate: one four-A100 node, with 320 GB nominal aggregate VRAM |
| 8-bit | 109 GB, about 102 GiB | Requires a separately validated quantization implementation/checkpoint |
| 4-bit | 54.5 GB, about 51 GiB | Requires a separately validated quantization implementation/checkpoint |

These exclude quantization metadata, buffers, activations, KV cache, and runtime overhead. Aggregate VRAM alone does not guarantee a working tensor-parallel configuration. Two H100s have 188 GB nominal VRAM, below the BF16 weights-only estimate. Four A100s are a candidate to validate, not a proven deployment. Do not assume that Scout's advertised maximum context fits this hardware; begin with a bounded text-only context and one sequence, then measure.

Preserve an unquantized baseline if resources permit. Quantization and changing from Groq's `openai/gpt-oss-120b` to Scout both change the experimental condition. Record and analyze them separately.

## Implemented local transport

The active [lab](codebase/agentdojo-lab/README.md) now supports an explicit
`openai_compatible` provider through the OpenAI SDK. The primary agent and online
causal judge have independent endpoint/model/key-variable settings; no local
error falls back to Groq. Credentials remain environment values, SDK retries
remain disabled, and Scout requests omit Groq-specific `reasoning_effort`.
Default Groq configuration serialization remains compatible with frozen runs.

- [local_scout.toml](codebase/agentdojo-lab/configs/local_scout.toml) is the primary
  starter config, with its online observer disabled until a new protocol enables it.
- [local_scout_judge.toml](codebase/agentdojo-lab/configs/local_scout_judge.toml)
  explicitly selects a local completed-trace single-source judge through
  `dojo-lab counterfactual --live --judge-config ...`.
- `dojo-lab doctor --config configs/local_scout.toml` checks local configuration,
  key availability, and upstream pins. It does not contact or prove a live server.
- Offline wire/native-adapter tests cover routing, independent primary/judge
  choices, typed arguments, tool-result IDs, isolated no-tools JSON judgments,
  credential redaction, and default Groq compatibility. The final full suite passed
  **2,056 tests**, including the strict local/Groq online-causal verifier, real
  MiniLM path and report generation; **26 HPC tests** also pass. Ruff and shell
  syntax checks passed. Logs are in `reports/20260914-nesi-setup-v1` in the lab.

Migration is deliberately scoped. Historical batch/memory/panel scripts and
aggregate `dojo-lab report` remain Groq-specific. Per-run HTML works with the local
run path. The old completed-trace joint composer and replay entry points reject
local manifests that would otherwise choose Groq implicitly; they need explicit
local migration before those case-study diagnostics. Starter configs are not
frozen research protocols. No live Scout capability follows from mock tests.

## Pinned preparation and smoke tooling

See [hpc/README.md](codebase/agentdojo-lab/hpc/README.md) for executable steps.
The original private site file is `/nesi/project/uoa04799/dyu848/tools/scout-site.env`.
The successful retry uses the separate `scout-site-20260915-v2.env` recorded above.
It contains paths and pins, not credentials. The candidate is vLLM 0.29.0 with
CUDA 12.9, pinned to a linux/amd64 OCI manifest. The original official chat template is preserved. The separately named
`typed_v1` correction preserves historical argument types and escaping; it passed
28 offline tests and actual Scout tokenizer encode/decode checks. Its SHA-256 is
`524a672eb654846b9ba1ab8a59ad9c3a80e3ad035dd7d01f701c64a71a09385f`. SIF construction and its own checksum are
separate from the OCI digest.

CPU-only download job **9029207** completed successfully in **27m 05s**, using
`hpc/scout-download.sbatch` (4 requested CPUs, 16 GiB RAM, four hours maximum).
All **63 root files** passed their pinned integrity checks,
including 50 safetensors shards, from revision
`92f3b1597a195b523d8d9e5700e57e4fbb8f20d3`; duplicate original-format weights are
excluded. Verification used the Hub's pinned LFS SHA-256 or Git blob ID for
every selected file. A separate preflight recheck also passed for the complete
serving inventory and current metadata content. Its durable evidence directory is
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-download-20260914-v1`.
The completed `model-integrity.json` is the required GPU-preflight input.
The materialized snapshot is
`/nesi/nobackup/uoa04799/dyu848/tool-output-lab/models/llama-4-scout-92f3b159`.

CPU container job **9029215** attempted the immutable OCI-to-SIF build
(8 requested CPUs, 32 GiB RAM, one hour maximum, no GPUs) and failed during
SIF creation. Successful conversion would record the SIF checksum and update
the private site file; that completion receipt is absent.
The preparation jobs received 8 and 16 logical CPUs respectively;
requested CPU count and scheduler billing are not identical on these nodes.

GPU smoke job **9029415** was cancelled because its `afterok` preparation
dependencies were not both successful. It never started. The prepared
combined check requests one Milan node, four A100s, 48 CPUs, 320 GiB host RAM and **60 minutes
maximum** (four GPU-hours at the ceiling). It must depend on successful model
and container preparation. It verifies the full model-integrity receipt,
metadata/template/SIF hashes, container versions and allocated GPUs, then serves
on authenticated loopback. Four synthetic requests cover typed tool calls,
result-ID round trips, parallel calls, and a no-tools JSON judge.

After these pass, a separate native receipt covers one benign AgentDojo
`user_task_0` with at most four additional SDK attempts, 2,048 completion tokens
per request and no online auditor. The combined cap is eight generative requests;
the job shuts down its server afterwards. Native utility, successful tool
execution, event validation and per-run HTML are checked. Exact Scout tokenization
measured 4,591 initial prompt tokens and 4,753 after the expected native read;
with a 2,048-token completion reserve, the latter fits the 8,192 context with
1,391 tokens remaining. Extra actual reads may still exhaust the context and
must remain visible failures. None of these checks is an attack experiment.

## Staged runbook

1. **Restore the CPU-side lab.** Read [bootstrap.py](codebase/agentdojo-lab/scripts/bootstrap.py), then use it to restore AgentDojo commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` and the locked Python 3.12 environment. The script has completed on NeSI and installed its own pinned `uv`. Keep the inference server in a separate environment/container so its Torch/CUDA requirements do not rewrite the lab lockfile. Run `dojo-lab doctor`, the offline fixture, and the appropriate offline tests. The provider-aware `doctor` and the offline native fixture have passed.

   Bootstrap's default sync omits the optional semantic stack. After bootstrap,
   install both semantic and plotting extras from `codebase/agentdojo-lab/` using
   its own environment (plotting is required by the complete report test suite):

   ```bash
   UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.python \
     .bootstrap/bin/python -m uv sync --locked --python 3.12 --extra semantic --extra figures
   ```

   Restore or download `sentence-transformers/all-MiniLM-L6-v2` at revision
   `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` into
   `.model-cache/all-MiniLM-L6-v2-1110a243`, using the exact file inventory in
   [SEMANTIC.md](codebase/agentdojo-lab/SEMANTIC.md#安装下载与运行).
   Verify its files against
   [model_pins/minilm-v1.json](codebase/agentdojo-lab/src/agentdojo_lab/model_pins/minilm-v1.json)
   through `semantic.local_minilm_identity` before using the cascade. This is a
   separate embedding model from Scout; neither its weights nor its dependencies
   arrive through Git. Preserve the lockfile and distinguish model integrity
   checks from historical live-accuracy claims.

2. **Resolve access, storage, and resource limits.** Storage and authenticated HF access are confirmed; the bounded job limits are recorded above. Scheduler acceptance and actual remaining allocation are distinct; record job accounting when it runs. Do not put weights in Git. Authenticate locally; do not send tokens in chat. Record an exact model revision, actual file size, and checksums before scheduling inference.

3. **Pin a serving environment.** Select a vLLM release/container compatible with the allocated GPU driver. Record the release or image digest, CUDA/PyTorch versions, model/tokenizer revision, and tool chat-template hash. Check installed `vllm serve --help` against the pinned release. Current vLLM documentation recommends `llama4_pythonic` and its matching Llama 4 chat template; automatic tool choice needs enabling. [vLLM tool calling, checked 2026-09-14](https://docs.vllm.ai/en/latest/features/tool_calling/)

4. **Prepare a bounded Slurm smoke job.** A candidate BF16 request is `--account=uoa04799 --partition=milan --nodes=1 --gpus-per-node=a100:4`; the prepared batch file fixes its CPU, host RAM and walltime limits above. GPU memory is separate from Slurm host RAM. The typed GPU request follows [NeSI's GPU instructions, checked 2026-09-14](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/). Capture `nvidia-smi` inside the allocation and server startup logs. Serve and run the test client in the same job on loopback; stop the server when the client exits.

   The following is an **unexecuted starting command inside that allocation**, after `SCOUT_SNAPSHOT` points to the downloaded, pinned local model and `SCOUT_CHAT_TEMPLATE` points to the matching pinned vLLM template:

   ```bash
   vllm serve "$SCOUT_SNAPSHOT" \
     --served-model-name llama-4-scout-local \
     --host 127.0.0.1 --port 8000 \
     --tensor-parallel-size 4 --dtype bfloat16 \
     --max-model-len 8192 --max-num-seqs 1 \
     --limit-mm-per-prompt '{"image":0}' \
     --enable-auto-tool-choice --tool-call-parser llama4_pythonic \
     --chat-template "$SCOUT_CHAT_TEMPLATE" \
     --generation-config vllm
   ```

   This command does not supply resource allocation, environment activation, authentication, readiness checks, or teardown by itself. Check every flag against the pinned release. The 8,192-token limit is a starting experiment setting; increase it only after measuring the combined prompt and completion requirements.

5. **Verify actual function calling.** After health/model-list checks, test one synthetic tool request, a tool result followed by a final answer, multiple calls, Unicode content, and array/null arguments. Include the no-tools JSON judge path. A successful text chat response is insufficient. Then run one clean AgentDojo task through the completed local adapter and inspect its native result, saved request, events, and HTML trace. Treat format errors and context exhaustion separately from attack effects.

6. **Run a few new paired experiments.** Freeze fresh clean/attacked cases, explicit primary and judge model identities, request budgets, context limits, template, seed/settings, and repetitions. Keep historical Groq results separate. Link each report to immutable source traces; document the first divergence, argument changes, memory/tool propagation, final consequence, and each NeuroTaint prediction. Temperature zero does not eliminate the need to measure run-to-run variability.

## Inputs and evidence still missing

- A successful GPU capability result for the now-published SIF; its checksum and CPU completion receipt are present.
- Actual GPU driver compatibility and measured Scout memory/startup/tool behavior.
- Successful synthetic and native Scout smoke receipts, followed by a new small frozen research protocol.
- Selected old raw run/report bundles from the personal computer; none restored.

The starter primary and judge both use local Scout, with independent endpoint
configuration. A different judge requires a new explicit model condition. The
project's remaining allocation balance has not been independently verified.
