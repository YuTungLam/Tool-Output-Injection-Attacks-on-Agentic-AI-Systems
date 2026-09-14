# NeSI setup and local inference plan

Last inspected: **2026-09-14 UTC**. This is a deployment plan, not a deployment receipt. No dependencies or weights were downloaded, no GPU job was submitted, and no model endpoint was tested during this assessment.

## What is available here

Read-only checks of this session found:

| Item | Observed state |
| --- | --- |
| Host | `login03.hpc.nesi.org.nz`; use scheduled compute nodes for inference |
| System Python | `3.9.25`; the AgentDojo lab requires Python `3.12.*` |
| Scheduler | Slurm; cluster `hpc`; user association with account `uoa04799`, QOS `debug,normal`, default `normal` |
| GPU partitions | `milan`: 4 nodes × 4 `a100`; `genoa`: 4 nodes × 2 `h100`, 4 nodes × 2 `pro_6000`, and 4 nodes × 4 `l4` |
| Environment modules | `uv/0.10.3-GCC-12.3.0`, Miniforge3, and CUDA versions are listed; no vLLM module was found |
| Containers | System Apptainer `1.4.5-3.el9` is available |
| Upstream dependency | `codebase/agentdojo-lab/vendor/agentdojo` is absent; the lab cannot run until its pinned checkout is restored |

Commands used to inspect scheduler metadata:

```bash
sinfo -o '%P %a %l %D %G'
sacctmgr -n -P show assoc user=dyu848 format=Cluster,Account,Partition,QOS,DefaultQOS
```

These succeeded outside the tool's socket-restricted sandbox after read-only escalation. The association establishes an account relationship, not the project's remaining allocation, an approved job budget, or guaranteed GPU scheduling. Recheck inventory when deploying.

NeSI currently documents A100 80 GB (four per Milan node), H100 NVL 94 GB (two), RTX PRO 6000 96 GB (two), and L4 24 GB (four). It recommends keeping GPU jobs within one node because GPUDirect RDMA is not enabled. [NeSI hardware, checked 2026-09-14](https://docs.nesi.org.nz/Batch_Computing/Hardware/)

## Scout feasibility

The requested model is [`meta-llama/Llama-4-Scout-17B-16E-Instruct`](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct). Meta specifies **17 billion activated parameters but 109 billion total parameters**. The full expert weights still need storage. Access is gated; this session has not verified account approval. [Meta model card, checked 2026-09-14](https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct)

Approximate **weights-only estimates**, calculated from 109 billion parameters:

| Representation | Raw estimate | Interpretation |
| --- | --- | --- |
| BF16 / FP16 | 218 GB, about 203 GiB | First unquantized candidate: one four-A100 node, with 320 GB nominal aggregate VRAM |
| 8-bit | 109 GB, about 102 GiB | Requires a separately validated quantization implementation/checkpoint |
| 4-bit | 54.5 GB, about 51 GiB | Requires a separately validated quantization implementation/checkpoint |

These exclude quantization metadata, buffers, activations, KV cache, and runtime overhead. Aggregate VRAM alone does not guarantee a working tensor-parallel configuration. Two H100s have 188 GB nominal VRAM, below the BF16 weights-only estimate. Four A100s are a candidate to validate, not a proven deployment. Do not assume that Scout's advertised maximum context fits this hardware; begin with a bounded text-only context and one sequence, then measure.

Preserve an unquantized baseline if resources permit. Quantization and changing from Groq's `openai/gpt-oss-120b` to Scout both change the experimental condition. Record and analyze them separately.

## Repository integration still required

The active package is [codebase/agentdojo-lab](codebase/agentdojo-lab/README.md). It already uses the OpenAI Python SDK, but it does **not** currently expose a supported local-provider configuration:

| Code | Gap to address |
| --- | --- |
| [runner.py](codebase/agentdojo-lab/src/agentdojo_lab/runner.py) | `RunConfig.provider` accepts only `groq`; authentication uses `GROQ_API_KEY`; primary and online causal clients hard-code the Groq endpoint |
| [groq_adapter.py](codebase/agentdojo-lab/src/agentdojo_lab/groq_adapter.py) | Native tool serialization and observation hooks are reusable; provider naming and wire compatibility require explicit tests |
| [counterfactual_audit.py](codebase/agentdojo-lab/src/agentdojo_lab/counterfactual_audit.py), [causal_v2_audit.py](codebase/agentdojo-lab/src/agentdojo_lab/causal_v2_audit.py), [cli.py](codebase/agentdojo-lab/src/agentdojo_lab/cli.py) | Separate auditor entry points also default to Groq; changing the primary client alone leaves these remote defaults intact |
| Evaluation and batch configs | Several freeze Groq model IDs and protocol settings; create new local experiment identities instead of modifying or resuming historical batches |

Minimal implementation should add an explicit OpenAI-compatible provider with a required endpoint, environment-variable name for its key, served model name, and equivalent settings for every enabled auditor. Reuse the observation hooks, retain disabled SDK retries and existing request budgets, omit unsupported `reasoning_effort` for Scout, and record actual provider/model/endpoint metadata. Endpoint errors must fail visibly without falling back to Groq. Keep secrets out of config snapshots and logs.

Before live inference, extend [the mock transport tests](codebase/agentdojo-lab/tests/test_groq_adapter.py) and runner tests to cover local routing, primary/judge endpoint selection, untouched tool-output content, call IDs, argument types, no-tools judge requests, error handling, and credential redaction. Existing Groq tests should continue to pass. These tests establish transport behavior; they do not establish Scout's tool-use quality.

## Staged runbook

1. **Restore the CPU-side lab.** Read [bootstrap.py](codebase/agentdojo-lab/scripts/bootstrap.py), then use it to restore AgentDojo commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` and the locked Python 3.12 environment. The script downloads packages and installs its own pinned `uv`; it was not run in this assessment. Keep the inference server in a separate environment/container so its Torch/CUDA requirements do not rewrite the lab lockfile. Run `dojo-lab doctor`, the offline fixture, and the appropriate offline tests. The current `doctor` reports Groq readiness and needs updating for local endpoints.

   Bootstrap's default sync omits the optional semantic stack. After bootstrap,
   install that extra from `codebase/agentdojo-lab/` using its own environment:

   ```bash
   UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.python \
     .bootstrap/bin/python -m uv sync --locked --python 3.12 --extra semantic
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

2. **Resolve access, storage, and resource limits.** Confirm the project's GPU allocation and the agreed first-job limit, HF model access, and a project model/cache directory with enough quota for the checkpoint, container/environment, and temporary download files. Do not put weights in Git. Authenticate locally; do not send tokens in chat. Record an exact model revision, actual file size, and checksums before scheduling inference.

3. **Pin a serving environment.** Select a vLLM release/container compatible with the allocated GPU driver. Record the release or image digest, CUDA/PyTorch versions, model/tokenizer revision, and tool chat-template hash. Check installed `vllm serve --help` against the pinned release. Current vLLM documentation recommends `llama4_pythonic` and its matching Llama 4 chat template; automatic tool choice needs enabling. [vLLM tool calling, checked 2026-09-14](https://docs.vllm.ai/en/latest/features/tool_calling/)

4. **Prepare a bounded Slurm smoke job.** A candidate BF16 request is `--account=uoa04799 --partition=milan --nodes=1 --gpus-per-node=a100:4`; CPU count, RAM, walltime and QOS still need setting from the resource budget. GPU memory is separate from Slurm host RAM. The typed GPU request follows [NeSI's GPU instructions, checked 2026-09-14](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/). Capture `nvidia-smi` inside the allocation and server startup logs. Serve and run the test client in the same job on loopback; stop the server when the client exits.

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

- HF access approval for the requested checkpoint; no secret needs to be shared.
- Model/cache storage location and quota; any existing approved checkpoint or serving container.
- Remaining project allocation and the first job's CPU/RAM/GPU/walltime budget.
- Actual GPU driver compatibility, a pinned vLLM release, and measured Scout memory/startup behavior.
- Whether the initial causal judge uses Scout as well or a separately specified model; record the resulting evaluation limitations.
- Restored runtime/test results and a live local tool-call receipt. Until those exist, local inference remains planned.
