# Bounded Scout serving smoke test

Prepared 2026-09-14. This tooling has **not deployed Scout**. The shell and
synthetic transport tests run without a scheduler or model. The batch script
requires an already prepared local model, chat template, and Apptainer image.
It never downloads them, submits another job, or runs research attacks.

Status rechecked 2026-09-15: model download/verification job `9029207` completed,
container job `9029215` failed during SIF creation after 50m 31s, and dependent
GPU job `9029415` was cancelled without starting. No live Scout smoke passed.
See [the current setup status](../../../HPC_SETUP.md#status-recheck-on-2026-09-15).

## Resource and software choice

`scout-smoke.sbatch` requests one Milan node, four A100s, 48 CPU cores,
320 GiB host RAM and 45 minutes, with no automatic requeue. The maximum
GPU allocation is 3 GPU-hours. The request is 48 CPUs; on this system Slurm
allocates 96 logical CPUs for it, so inspect actual accounting rather than
treating requested CPU count as billed usage. Host RAM is separate
from GPU VRAM. These are initial smoke limits, not measured Scout requirements.
NeSI documents four A100 80 GB GPUs and 64 cores per Milan GPU node; 320 GiB
leaves room below its reported schedulable host memory and per-core ratio.
[NeSI hardware](https://docs.nesi.org.nz/Batch_Computing/Hardware/),
[GPU resource syntax](https://docs.nesi.org.nz/Batch_Computing/Using_GPUs/).

The serving candidate is **vLLM 0.29.0, CUDA 12.9, linux/amd64** in a local SIF.
The release and image tag are documented by the
[vLLM 0.29.0 release](https://github.com/vllm-project/vllm/releases/tag/v0.29.0).
Registry inspection resolved `vllm/vllm-openai:v0.29.0-cu129` on 2026-09-14:

- Registry index: `sha256:7ef5a35d1ef8ce2cf9d671dd91eec6e367c5849262e0362b4d3d4a26be0d87d2`.
- Linux/amd64 manifest: `sha256:3e10e8189823e0f7ae4620c271bcdaaf64127ec7d0edc351591a508498b7684a`.

The manifest reference is in `site.env.example`; image preparation is a separate
step. Record the resulting **SIF file's own SHA-256** after preparation. The
registry digest and SIF checksum are different artifacts; do not interchange
them. GPU driver compatibility remains unverified until a scheduled job runs.
The runtime precheck requires vLLM 0.29.0 (including its `+cu129` package suffix),
PyTorch CUDA 12.9, and four visible A100 GPUs.

Use the separately named local
[`tool_chat_template_llama4_pythonic_typed_v1.jinja`](tool_chat_template_llama4_pythonic_typed_v1.jinja),
derived from the **v0.29.0** vLLM template as described below. Its SHA-256 is
pinned in `site.env.example`. Llama 4's recommended parser is
`llama4_pythonic`; automatic tool choice is enabled.
[Official tool-calling documentation](https://docs.vllm.ai/en/v0.29.0/features/tool_calling/).
The job fixes BF16, tensor parallel size 4, one active sequence, context 8192,
GPU memory fraction 0.90, eager safetensors loading and eager execution. The
safetensors strategy avoids random memory-mapped reads on the shared filesystem;
its host-memory use still needs measurement. Eager execution
reduces CUDA-graph startup work for this smoke test; it is not a performance
benchmark. [Pinned serve arguments](https://docs.vllm.ai/en/v0.29.0/cli/serve/).

### Prospective template correction: typed_v1

The upstream
[`examples/tool_chat_template_llama4_pythonic.jinja`](https://github.com/vllm-project/vllm/blob/v0.29.0/examples/tool_chat_template_llama4_pythonic.jinja)
is preserved byte-for-byte in the
[`v0.29.0 regression fixture`](../tests/fixtures/tool_chat_template_llama4_pythonic_v0_29_0.jinja)
and in its original downloaded location. Its 7,347 bytes have SHA-256
`3fe950790d033a6ee07a563fb6ad7c34e40f860b8ff99333b0b0aed6204ba258`.
The source belongs to the Apache-2.0-licensed vLLM project; its
[upstream license](third_party/vllm-LICENSE) is retained alongside these files.

That template quotes every historical tool argument after string formatting:
an actual list becomes `labels="['café', 'tea']"`, null becomes `note="None"`,
and an integer becomes `count="7"`. Embedded quotes, backslashes and newlines
are also unescaped. This changes the previous call seen by the model and can
produce malformed Pythonic history. It is a serving-template defect, not an
observed influence-tracking result or a model capability finding.

The local `typed_v1` file adds one recursive, zero-output Jinja macro and changes
only historical argument-value serialization. Strings use Transformers'
`tojson(ensure_ascii=False)` escaping; arrays and objects recurse; null and
booleans use Python literals; finite numbers retain their numeric form.
Nonfinite numbers fail explicitly. System/user/tool text, tool definitions,
role delimiters, call order and generation-prefix behavior retain the upstream
template's bytes. The original request objects are not mutated.

This is a **new, explicitly recorded serving condition**, prepared before the
first Scout GPU smoke. The 8,830-byte corrected file has SHA-256
`524a672eb654846b9ba1ab8a59ad9c3a80e3ad035dd7d01f701c64a71a09385f`.
It must not be substituted into historical runs or described as the unmodified
official template. The job preflight records its actual path and hash.

The offline
[`template tests`](../tests/test_scout_chat_template.py) demonstrate the original
type/escaping regression and verify rendered values through `ast.literal_eval`,
including nested objects, arrays, Unicode/emoji, booleans, null, numeric types,
quotes, backslashes and newlines. No function call or payload is executed.
They also compare unaffected prompt regions and exercise the production
Transformers compiler when installed. vLLM normalizes empty assistant content
and parses serialized tool arguments before template rendering; the fixture
uses that normalized input shape. A live Scout tool round trip remains a
separate GPU smoke requirement.

On 2026-09-14, all 28 template tests passed in the restored lab environment.
The separately downloaded, pinned Scout tokenizer also passed real
`apply_chat_template` rendering and token encode/decode checks for 20 argument
cases (328 prompt tokens), using Transformers 5.16.1. The local
[`tokenizer receipt`](../reports/20260914-nesi-setup-v1/typed-template-check.json)
records tokenizer-file and template hashes. This is offline tokenizer evidence;
it does not establish the serving container's runtime or model behavior.

## Prepare inputs outside the GPU allocation

Copy `site.env.example` to a private file outside Git and fill its placeholders.
Its defaults keep large regenerable data under
`/nesi/nobackup/uoa04799/dyu848/tool-output-lab/{models,cache,containers,tmp}`.
The storage check found a 10,240 GiB scratch quota and a 200 GiB project
quota: the approximately 203 GiB BF16 weight estimate alone exceeds the latter.
Keep code and small durable evidence under `/nesi/project/uoa04799/dyu848/`.
Do not treat scratch as archival storage.

The HF CLI is `/nesi/project/uoa04799/dyu848/tools/hf/bin/hf`. Authenticate during
preparation, keeping its token at private `~/.cache/huggingface/token`.
`HF_HUB_CACHE` and `HF_XET_CACHE` point to scratch; `HF_HOME` is not moved there.
Do not add an HF token to the site file or submission command. The GPU job uses
no HF credentials and creates its own temporary local API key in memory.

Required inputs:

| Variable | Requirement |
| --- | --- |
| `SCOUT_SNAPSHOT` | Absolute, complete materialized local Scout snapshot directory |
| `SCOUT_REVISION` | Exact 40-hex Hugging Face commit used for the download |
| `SCOUT_MODEL_INTEGRITY` | Successful complete download/checksum receipt matching this snapshot |
| `SCOUT_CHAT_TEMPLATE`, `SCOUT_TEMPLATE_SHA256` | Local typed_v1 template and recorded SHA-256 |
| `VLLM_SIF`, `VLLM_SIF_SHA256` | Prepared local SIF and its recorded SHA-256 |
| `SCOUT_RUN_DIR` | Fresh directory for durable evidence; existing directories are rejected |
| `SCOUT_HPC_DIR` | Absolute path to this folder, which must remain available on the compute node |

Public model metadata resolves Scout to revision
`92f3b1597a195b523d8d9e5700e57e4fbb8f20d3`: 50 root safetensors files total
217,283,738,720 bytes (about 202.4 GiB). The checked defaults use that revision
and `models/llama-4-scout-92f3b159`. Authentication and a gated config download
have since passed; this is still distinct from complete weight verification. Its local receipt is
`reports/20260914-nesi-setup-v1/scout-public-metadata.json` in the lab.

Keep the full download receipt in durable project evidence and set
`SCOUT_MODEL_INTEGRITY` to it. Preflight requires its successful terminal status,
matching snapshot/revision, and verified sizes/hashes for every serving file.
Metadata content is rechecked against its pinned checksum; every index-listed
weight shard must exist with the verified size,
and hashes the config, tokenizer files, index, chat template, and SIF. It does
**not** reread hundreds of GB of weight data for full shard hashing inside the
allocation; the recorded revision is a declared download identity, not proof of
origin by itself. Complete integrity verification belongs to model preparation.
An HF cache snapshot with symlinks pointing outside its directory is rejected:
materialize it first so binding `/scout-model` cannot break shard/tokenizer paths.

The CPU download script performs the complete integrity pass outside the GPU
allocation. With a signed-in HF CLI and the prepared site file:

```bash
sbatch --export=HOME,PATH,LANG \
  --output=/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-download-%j.log \
  scout-download.sbatch /nesi/project/uoa04799/dyu848/tools/scout-site.env \
  /nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-download-UNIQUE_ID
```

It requests four CPUs, 16 GiB RAM and four hours maximum, with two download
workers and no GPU. Job `9029207` completed successfully in 27m 05s; all 63
selected files passed verification. Reuse that snapshot and receipt. It writes a pinned inventory before downloading, then a terminal
`model-integrity.json` only after all 63 selected root files pass their LFS
SHA-256 or Git blob checks. A partial/failed receipt cannot pass GPU preflight.
A nonblocking snapshot lock prevents two copies of this preparation script from
writing concurrently. Set the site receipt path to the matching attempt.

Check inputs before spending GPU time, using a new receipt path:

```bash
source /path/to/private/scout-site.env
python3 "$SCOUT_HPC_DIR/preflight.py" --output /path/to/fresh/preflight-check.json
```

For the first combined check, run four synthetic requests followed by one
benign native AgentDojo task in the same allocation. Submit **once** with a
60-minute ceiling and dependencies on the successful preparation jobs:

```bash
sbatch --time=01:00:00 --dependency=afterok:9029207:9029215 \
  --kill-on-invalid-dep=yes \
  --export=HOME,PATH,LANG,SCOUT_SITE_FILE=/nesi/project/uoa04799/dyu848/tools/scout-site.env,SCOUT_NATIVE_SMOKE=1 \
  --output=/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-smoke-%j.log \
  scout-smoke.sbatch
```

The site file is read at job start, after successful preparation. Update job IDs
for a later attempt and use a fresh `SCOUT_RUN_DIR`. The combined ceiling is
four GPU-hours and **eight generative requests**: four synthetic requests at
512 completion tokens each, then at most four native requests at 2,048 tokens
each. The native wrapper rejects further SDK attempts across native retries,
uses no online auditor, and has a 780-second process deadline. It fixes native
workspace `user_task_0`, records actual task utility, validates event links and
successful tool execution, and exports per-run HTML. A failed native task remains
a failed integration/utility check; it is not attack evidence. The wrapper hash,
server command, synthetic receipt, and model/container/template pins are linked
in `native-smoke.json`. The loopback client uses no proxies or redirects.

For a synthetic-only check, omit `SCOUT_NATIVE_SMOKE=1` and retain the default
45-minute batch limit. Neither mode starts research experiments. Native input
prompts must fit the explicit 8,192-token context; there is no silent truncation.


The log parent directory must already exist before `sbatch`; Slurm opens its
output before the script creates directories. The combined command was submitted
as job **9029415** on 2026-09-14; it was cancelled after container preparation
failed. The command above records that historical submission. A new attempt
needs successful preparation dependencies and a fresh evidence directory. The job and smoke client use the stdlib
features available in Python 3.9+, so the host Python suffices; the AgentDojo lab
itself still requires its separate Python 3.12 environment.

## Separate CPU container preparation

`container-prep.sbatch` downloads the pinned public linux/amd64 OCI manifest and
converts it to a SIF on a compute node. It requests 8 CPUs, 32 GiB host memory,
60 minutes and **zero GPUs**. The build itself has a 3,000-second timeout;
SquashFS compression is limited to 8 workers and 8 GiB. Slurm CPU affinity and
memory limits also apply. `apptainer build` is used because the installed 1.4.5
`pull` command does not expose compressor resource flags.
[Apptainer build documentation](https://apptainer.org/docs/user/1.4/build_a_container.html).

After successful conversion, `finalize_container.py` hashes the SIF, publishes it
without overwriting an existing image, and atomically changes only
`VLLM_SIF_SHA256` in the private site file. It preserves failed/partial artifacts
and records the immutable OCI source, SIF bytes/hash, job ID and config-update
status. No source site contents or tokens are written to evidence. GPU runtime
validation remains a separate smoke job. The anonymous public registry download
does not use HF authentication.

After reviewing the populated private site file, a fresh preparation can use:

```bash
SCOUT_SITE_FILE=/path/to/private/scout-site.env \
SCOUT_PREP_EVIDENCE=/path/to/fresh/container-preparation \
  sbatch --output=/path/to/existing/log-directory/container-%j.log \
  codebase/agentdojo-lab/hpc/container-prep.sbatch
```

The first authorized submission on 2026-09-14 is job `9029215`; its live state is
recorded by Slurm, not by this README. Evidence is under
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/container-prep-20260914-v1`,
with scheduler log `evidence/prep-logs/container-9029215.log`. A job ID is not a
completion or deployment claim. Do not submit a replacement without inspecting
the retained outcome and its bounded protocol.

## Bounds, isolation, and receipts

The server binds `127.0.0.1`, receives a new random key through `VLLM_API_KEY`,
and the client reads the matching `LOCAL_LLM_API_KEY`. No token is passed on a
command line or written to the receipt. HTTP proxies and redirects are disabled
for the smoke client. Requests require literal loopback HTTP; no remote fallback
exists. Apptainer uses a new private home and `--cleanenv --no-eval`, retaining
host IPC for tensor-parallel shared memory. HF/Transformers offline flags and
disabled telemetry prevent intentional model downloads; this is not a network
namespace sandbox. [Apptainer environment controls](https://apptainer.org/docs/user/1.4/environment_and_metadata.html),
[vLLM environment settings](https://docs.vllm.ai/en/v0.29.0/configuration/env_vars/).

Readiness polls authenticated `/v1/models` for at most 1,500 seconds and checks
the exact served name. Wrong-model/authentication failures stop immediately.
Each synthetic generation allows 120 seconds and 512 completion tokens, without retries:

1. One automatic function call with Unicode labels, an array, and a null value.
2. Return a synthetic tool result under the original call ID and require its
   receipt identifier in the final text.
3. Two automatic function calls in one response with separate IDs and integer
   arguments; these calls are validated but not executed.
4. An isolated JSON judge request with `response_format={"type":"json_object"}`
   and without tool definitions or tool history, matching the local auditor path.

This is at most **four generative requests and 2,048 generated tokens**. A failed
stage stops dependent execution; unstarted stages are not retried. GET readiness
requests are separate from that generation count. On exit or Slurm's early TERM,
the job terminates the server process group, waits up to ten seconds, and sends
KILL if needed. Slurm remains the final walltime bound. Existing cache/evidence
files are retained; no experiment artifacts are deleted.

`SCOUT_RUN_DIR` receives `preflight.json`, `gpus.csv`, `container-runtime.json`,
`server-command.txt`, `server.log`, `smoke.json`, and `job-exit-code.txt` as far as
execution reaches. The receipt records each attempted synthetic request,
response, status, and timing, excluding authentication headers and redacting
any echoed local key. Forced scheduler termination can leave an incomplete
receipt; that remains a failed/unavailable smoke attempt.

A passing smoke demonstrates this narrow transport/parser behavior. It does not
test native AgentDojo execution, NeuroTaint, attack success, causal accuracy,
long-context reliability, performance, or repeated-run stability. The integrated
lab uses `configs/local_scout.toml` and the same served model/key environment
names; a native clean task is a separate next check inside a separately bounded
allocation. The smoke job shuts its server down when these four requests finish.

## Offline verification

```bash
python3 -m unittest discover -s codebase/agentdojo-lab/hpc -p 'test_*.py' -v
bash -n codebase/agentdojo-lab/hpc/scout-smoke.sbatch
bash -n codebase/agentdojo-lab/hpc/site.env.example
bash -n codebase/agentdojo-lab/hpc/container-prep.sbatch
codebase/agentdojo-lab/.venv/bin/ruff check codebase/agentdojo-lab/hpc
codebase/agentdojo-lab/.venv/bin/python -m pytest codebase/agentdojo-lab/tests/test_scout_chat_template.py -q
```

Run these from the repository root. Tests cover a complete fake round trip,
argument types, duplicate IDs, truncated/wrong-model replies, request budgets,
credential redaction, failed receipts, bounded readiness, missing weight shards,
escaping model symlinks, and frozen image/template drift. They open no network
socket and do not load model weights.
