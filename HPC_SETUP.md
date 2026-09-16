# NeSI setup and local inference plan

> **Meeting-packet assessment — 2026-09-16:** The
> [HTML packet](codebase/agentdojo-lab/reports/20260916-meeting-packet-v1/index.html)
> contains all eight Scout session outcomes, observed paths, a tracer-coverage
> table and all 13 deliverable statuses. Preparation is **12/12**; experimental
> deliverables **4/13 (31%)**; overall **16/25 (64%)**. Completed items are
> within-session transformation/provenance assessment, clean/attacked comparison,
> coverage assessment and the meeting packet. Causal, repeated and cross-session
> claims remain incomplete. All three jobs are terminal: **25 research requests**
> total, with zero additional requests in this reporting continuation.
> Case A cleanup diagnostics, Case B blocker reporting and Case C per-call
> reporting are now repaired prospectively. Saved outcomes and counts are unchanged.

Last updated: **2026-09-16 UTC**. The CPU lab and pinned MiniLM files have been
restored, and the offline native-tool fixture passes. Hugging Face login and
Scout gated-file access are verified. Local transport is implemented; the pinned
checkpoint is fully downloaded and verified. The first serving-container build
failed; its dependent GPU smoke was cancelled before starting. The separately
named retry passed, followed by a successful four-A100 GPU smoke. Scout inference
and a benign native tool loop are verified. A separate smoke-plus-Case-A wrapper,
canonical plan, private site and immutable bundle were frozen. First Case A job
`9043206` was cancelled before allocation after audit found a Slurm helper-path
defect. Corrected job `9050478` later failed before inference because its frozen
launcher imported a changed repository module. Case B job `9052477` loaded Scout
and passed 4/4 synthetic requests, then failed before native inference because
its bundle omitted `configs/local_scout.toml`. Both made zero research requests.
Self-contained A/B remediation and the new Case C implementation passed the final
exact submitted-source suite: **351 tests plus 16 subtests in 168.01 seconds**.
Scoped Ruff, compilation, Bash syntax and diff checks passed. Independent final
audits returned GO for all three cases after copied-bundle and path-mutation checks.
The copied-wrapper gate rejected unsubmitted Case C v1 because its plan omitted an
explicit `online_causal_audit = false` setting; commit
`74c31d5e5ad5fc5bbb89a5eb4e1520b7787d3336` fixed the binding, and 81
current-source focused Case C tests passed. Canonical Case A v5, Case B v3 and
Case C v2 preparations and immutable bundles are now frozen. Jobs `9064136`,
`9064141` and `9064142` are terminal, with 25 research requests across eight
sessions. See the saved-results analysis above for outcomes and defects.

## Terminal research jobs and saved-evidence review — 2026-09-16

The user requested continued runs with percentages and explanations. The fresh
container retry and its GPU smoke **passed**. The first separately frozen Case A
job was cancelled before allocation; corrected Case A job `9050478` and Case B
job `9052477` are terminal failures with zero research requests. The repaired
source is pushed, frozen and audited. Case A v5, Case B v3 and corrected Case C
v2 ran as separately named jobs and are now terminal. See
[RESEARCH_PROGRESS.md](RESEARCH_PROGRESS.md) for the checklist count and the
interpretation of every attempt.

| Job | Latest observed state | Bounded scope |
| --- | --- | --- |
| `9039259` | COMPLETED on Genoa `g01`, Slurm elapsed 6m 49s, exit `0:0` | CPU container retry: 8 requested CPUs / 16 allocated logical CPUs, 32 GiB, local SSD, 2 hours maximum; no GPUs |
| `9039289` | COMPLETED on Milan `mg15`, Slurm elapsed 9m 54s, exit `0:0` | Four A100 SXM4 80 GB GPUs, 48 requested / 96 allocated logical CPUs, 320 GiB; synthetic 4/4 and benign native 9/9 checks passed with seven requests |
| `9043206` | CANCELLED before allocation, elapsed 00:00:00 | First Case A submission; helper-path defect found by audit; zero GPU time and requests; preserve v1 bundle |
| `9050478` | FAILED `1:0` on `mg14`, elapsed 00:00:30 | Request-free Case A validation rejected source drift before vLLM; zero generation requests and zero research sessions |
| `9052477` | FAILED `1:0` on `mg14`, elapsed 00:08:35 | Scout loaded and synthetic smoke passed 4/4; missing bundled local config stopped native smoke before its first request; zero Case B sessions |
| `9064136` | FAILED `1:0`, 12:24–12:35 NZST on mg15, 11m20s | Both research sessions completed (8 requests); shutdown unconfirmed and final validation incomplete |
| `9064141` | COMPLETED `0:0`, 12:36–12:47 NZST on mg15, 10m56s | Four research conditions completed (11 requests); utility failures limit interpretation |
| `9064142` | FAILED `1:0`, 12:47–12:57 NZST on mg15, 9m53s | First sessions completed (6 requests); later sessions blocked by unverified memory handoff |

Slurm eventually started `9039289` automatically on `mg15`; earlier queue
estimates were provisional and did not predict its actual start. The model loaded
across all four GPUs and both smoke phases passed. The job's server stopped at
completion. Those receipts cannot authorize a later allocation because the
same-allocation gate must observe its own serving process and smoke results.

Do not modify `9039289`, its v2 site file or frozen submission bundle. Its script
ended after smoke and cannot run Case A. Checkpoint `7b5f1eb` added a separately
named wrapper, `codebase/agentdojo-lab/hpc/scout-smoke-case-a.sbatch`. Historical
preparation `runs/scout-case-a-prepared-v4` recorded zero model requests, 85 bound
source files and plan SHA-256
`5e3b9aa67767e2bf0b5c1275dac14742ee02f596efff84f0d6fe2cd4c95b5d31`.
It contains exactly `plan.json` and `preparation.json`; the preparation receipt
has SHA-256
`b315d3ee67a338124a5b9c35825824dd058e89e25a56a077134fbd9456f3dbd4`.
Current source hardening also invalidates v4, while the first three preparations
remain preserved and source-invalidated; v3 omitted the runtime-read MiniLM
revision pin from its inventory. Smoke timing supported the existing two-hour
envelope, so a new private site and immutable helper bundle were frozen and job
`9043206` was submitted. Audit found a relative helper-path defect before
allocation, and the job was cancelled. Job `9050478` was required to repeat
synthetic and benign native smoke in its own allocation but failed before them.
Later v5 job `9064136` passed its own gates before both research sessions;
old receipts did not authorize it.
The final wrapper/Case/report/smoke selection passed 109 tests plus 16 subtests,
Ruff, Bash syntax and Python compilation. These are offline checks only.

The first Case A submission used private site
`/nesi/project/uoa04799/dyu848/tools/scout-case-a-site-20260915-v1.env`, immutable
bundle `evidence/scout-case-a-submission-20260915-v1`, run evidence
`evidence/scout-case-a-20260915-v1`, and scheduler log
`evidence/case-a-logs/scout-case-a-9043206.log`. It binds pushed source checkpoint
`84fe7cc` and passed input preflight. Slurm accepted it at 15:36 NZST. It was
cancelled at 15:47 before allocation after audit found that a relative helper path
would resolve from Slurm's spool directory. Accounting records 00:00:00 elapsed,
zero GPU time and zero requests. Preserve the v1 bundle. A corrected v2 bundle and
replacement were subsequently prepared and submitted as job `9050478`.

The preserved mode-0400 cancellation receipt is
`evidence/scout-case-a-submission-20260915-v1/cancelled.json`, SHA-256
`35bfde30958b8ecb49aafcb31c448e69c0c0e71fe57ce8387f8c535b6d6a9e5a`.
It records `CANCELLED by 200426`, exit `0:0`, 00:00:00 elapsed and no assigned
node.

The corrected wrapper uses an absolute frozen helper directory, verifies its
submission-bound checksum manifest, and confirms that Slurm's spooled wrapper is
byte-identical to the frozen canonical copy. `SCOUT_CASE_A_MODE=1` also makes the
preflight distinguish smoke-only limits from the enclosing 7,200-second,
24-total-request, 16-Case-A-request and zero-online-auditor envelope. The
remediation selection passed 108 tests plus 16 subtests, Ruff, Python compilation,
Bash syntax and diff checks. ShellCheck was unavailable.

The corrected source checkpoint
`228f7c2ce4255a8587921ef955c633868b1fb10d` is pushed. The v2 submission bundle is
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-case-a-submission-20260915-v2`,
and its private site file is
`/nesi/project/uoa04799/dyu848/tools/scout-case-a-site-20260915-v2.env`. The site,
helper manifest and offline preflight SHA-256 values are
`985c5f97ca5ce6141b5d6c04a8abaef797251f900eccce51676f0bfce1ca905d`,
`5cc8195c816e43c1c2ec22237cbadc9cacd4503f5beca75ae5e4a243014a6451`
and `6a8b2f5e3ba7da0f61c7dd9b0723135cdf7b12d15b97fe37492852c004f54aab`.
Request-free validation passed, and the independent launch audit returned GO
with no P1/P2 findings after 81 focused tests plus 16 subtests.

Job `9050478` was submitted at the scheduler's Sep 15 17:08 display. Slurm later
ran it on `mg14`; it failed `1:0` after 30 seconds during request-free validation.
The frozen launcher imported the mutable repository's Case A module, whose bytes
no longer matched the prepared plan. vLLM never started, so synthetic, native and
Case A request counts were all zero. The bundle's `submitted.json` has SHA-256
`770b8e9fc66590f968d1e0f6bbc7e731b70ff7db66c1c197366955b25a4744c9`.
The terminal scheduler log SHA-256 is
`7124e18c9729caa29124cd422819b407f800c58588f8262b05f66fc851a22af6`.

### Submitted Case B launch implementation

The reviewed `nesi-scout-smoke-case-b-v1` wrapper requests four A100s for no more
than two hours. Its maximum is 24 generation attempts: four synthetic, four
benign-native and 16 Case B. It requires one current `squeue` record and at least
3,900 seconds remaining before Case B, applies a 3,600-second process-group
watchdog, binds server PID/phase/cleanup evidence and runs a full request-free
source verification at terminal close. The prepared v2 plan inventory contains
163 source files, including all 113 AgentDojo runtime/package-metadata files from
pinned commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60`, and its launch manifest
has exactly nine entries. The upstream runtime-tree SHA-256 is
`4c58924aeb917f1daf29a4fcb11d79e716af8baf7266b73c592b39aa93a4edd7`.

The independent final Case A/B wrapper selection passed 191 tests plus 16
subtests; root's broader selection passed 214 tests plus 16 subtests. Ruff, Bash
syntax, Python compilation and diff checks passed. Preserved Case B v1 has 41
sources, zero model calls and plan SHA-256
`4b8bc845437ce557fe6bbe589dd90d6ccc5b083d92955ef0fb1324f4df52c036`.
It is source-invalidated and fails request-free verification as designed.
Historical v2 path `runs/scout-case-b-prepared-v2` contains exactly `plan.json`
and `preparation.json`, whose SHA-256 values are
`69b0b0c2a77bff5057789719ae76a4a05c757a1acc511e3f66f14bd13dff60ff`
and `ba663d561892b614f7320be36a8fc9c4bf363c946c15837ac52e905fa1b45906`.
The preparation itself records zero model calls. Current source/config hardening
invalidates v2. Later Case B v3 ran as terminal job `9064141`; its exact
receipt is recorded below.

The immutable submission bundle is
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-case-b-submission-20260915-v1`,
using private site
`/nesi/project/uoa04799/dyu848/tools/scout-case-b-site-20260915-v1.env`.
All 163 plan-bound sources are physical mode-0400 files: 50 bind pushed parent
checkpoint `228f7c2ce4255a8587921ef955c633868b1fb10d`, and 113 bind pinned
AgentDojo checkpoint `089ed468cf3ed0322acc66b0211f26d9d90dbf60`. The combined
physical source-tree SHA-256 is
`8ecf7918e814b30989d5a4b94514895093998c897ad3fe2f4adcdaf64e147884`.
The site, nine-entry root manifest, offline preflight, request-free validation
and submission-plan SHA-256 values are
`38c6ab9d6441cc55672efcccd434b4442e0dc12e5c0f4357aee26b6a567e5980`,
`951a00e2cf1d00b255ee390feeebc43a35321cc7162363651bd6d9509b092eac`,
`6c3b6b501733595985df9872fcca2eeca590e773176ca8333a5a866f3df1ea60`,
`4e7748b77e204c5fcebfa95512b3a8b7df114e7607ce1942ca4965921440a424`
and `938cb660d45586a3c5330ae105cbc139228dc567412f8ea715d065d619b9566e`.
Import isolation, native/Case B preflight, request-free runner verification and
fixed limits passed. Independent audit returned GO with no P1/P2 findings.

Job `9052477` was submitted at scheduler display Sep 15 17:30. Slurm ran it on
`mg14` for 8m 35s; it exited `1:0`. The server loaded and all four synthetic
smoke requests passed. Native smoke then failed with `FileNotFoundError` before
its first request because the frozen bundle lacked `configs/local_scout.toml`.
Thus the job made four synthetic, zero native and zero Case B requests. The
`submitted.json` SHA-256 is
`88b00e37fa87aa45755de4749aeaa6ae0a2ee81d62c84c9c36bd2c1bb3812408`.

### Frozen replacement set — 2026-09-16

Case A/B bundles bind pushed source
`ebc619813a9c22bdb2eb3bed675213edfc83bc89`; their inventories exclude the later
C-only plan-field fix and were revalidated after it. Corrected Case C v2 binds
`74c31d5e5ad5fc5bbb89a5eb4e1520b7787d3336`. At freeze time each canonical
preparation contained only `plan.json` and `preparation.json`, recorded zero model
requests and passed request-free verification. Later execution outputs and request
counts are separate from those original preparation receipts:

| Case | Preparation | Sources | Plan SHA-256 | Preparation SHA-256 |
| --- | --- | ---: | --- | --- |
| A v5 | `runs/scout-case-a-prepared-v5` | 205 | `992509a7a4e1b8e8817072d4c2720ded6ec5981a559fd4aa1062cb5676fe1d15` | `c11364861e2d8ef53bb202da66fdaf272d2bbfde2a2a635d84a9e7ebd22e24f3` |
| B v3 | `runs/scout-case-b-prepared-v3` | 164 | `a5c0b7d19d32b619df337ab5ba47f79a4c6ba1e47732ea2f08278236390d98cf` | `88cbdc554b900a2e0af7500b2c293eb96c183bca4cf8cb1df2a2c045e23b1da1` |
| C v2 | `runs/scout-case-c-prepared-v2` | 206 | `b28f3497f1f75faf608784d73714b9ec67cf07bbdae89e21399508a217aa1388` | `5c1a526f2318dca97151a2ec709e757c5ded212b7251c77b64c1b9d2d66c8d85` |

The immutable copied bundles also passed exact request-free validation. Their
submission-bound receipts are:

- Case A:
  `/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-case-a-submission-20260916-v3`;
  site `/nesi/project/uoa04799/dyu848/tools/scout-case-a-site-20260916-v3.env`
  SHA-256 `a2b5c35df88f7ba4e0769bd72b997a6b612c3a47d76d53f47b12948df928cd43`,
  manifest `3be4adeb3d3d91233dc2cbdce6186f3ff2f48ee753b56800dd8dd0bf5d6ac9f8`,
  submission plan `f5351c7113d0c8b3a12236d32e831892511858eb579bf7791e0de37bbd968425`,
  and `submitted.json` `a9638609f9a3ee8109a87f5c3a6ef7b49e17d5ae3cd1b8edeaa7c8b2940a3824`.
- Case B:
  `/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-case-b-submission-20260916-v2`;
  site `/nesi/project/uoa04799/dyu848/tools/scout-case-b-site-20260916-v2.env`
  SHA-256 `0cd2c539ba8b864a46b37b37044cf1a82e8e5b4ab33295e61a1041214a838070`,
  manifest `92a0ff21eafbbf88386c5a394246b53ceebd4d89b8ae00ec272d9d49bcb39f61`,
  submission plan `cf2981956485e6149600e3e3e351c651a757de35486cb4505f38c6642253d221`,
  and `submitted.json` `baf63bf83997b010d4564983907504a6945ac11c9d0a82a9d7402dc09095a288`.
- Case C:
  `/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-case-c-submission-20260916-v2`;
  site `/nesi/project/uoa04799/dyu848/tools/scout-case-c-site-20260916-v2.env`
  SHA-256 `df3852cd896b291301987ee8cde3acfe629157ca2f06fd8168054643bc030548`,
  manifest `aa3b4cb28c403a0d8599f13b2787f47e15b19231f55c09b2a710373a313e2f18`,
  submission plan `c2bd53e9fc4cc183b2889de789a558c07ea32b4184920aa2e5cfb27173fee970`,
  and `submitted.json` `75675a5028dc0ff6cded10bec411af6aa29275c0f429c4922a2cb19546fc8316`.

The first Case C preparation, `runs/scout-case-c-prepared-v1` (plan SHA-256
`356fcba4fb25d0f113ac0e130de6c7514947b7771d202a5e5a558ff1084e04cf`),
and bundle `scout-case-c-submission-20260916-v1` remain preserved. The copied
wrapper gate rejected them before submission because the plan lacked the explicit
disabled online-auditor field. That attempt used zero model calls, scheduler jobs
and GPU time. Its `rejected.json` SHA-256 is
`a855f99b0435770ead2442964164a43812f33fd24aac19cf7a9f01b4d82d092c`.
The corrected C v2 preparation and bundle passed the same gate.

Jobs `9064136` (A), `9064141` (B) and `9064142` (C) are terminal. Actual
execution occurred 12:24–12:57 NZST on September 16, superseding the queue
projections. A saved two sessions/eight requests but failed finalization with
shutdown unconfirmed; B completed four conditions/eleven requests; C saved two
first sessions/six requests and blocked second sessions before inference. No
repair or further model request was performed during the saved-evidence review.

### Successful GPU smoke — job 9039289

Slurm ran the smoke on Milan node `mg15` with four A100 SXM4 80 GB GPUs, 96
allocated logical CPUs and 320 GiB host RAM. It completed in 9m 54s with exit
`0:0`. vLLM `0.29.0+cu129` with CUDA 12.9 loaded all 50 shards; the slowest
worker took 375.30 seconds and reported 52.72 GiB loaded. All four synthetic
checks passed. The benign native task used three requests, recorded 24 events and
passed all nine integration checks. Total usage was seven of eight allowed
generation requests. This is serving/tool integration evidence, not an attack or
attribution result.

Evidence is in
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/scout-smoke-20260915-v2`.
The terminal SHA-256 values are:

- `preflight.json`: `cf6ac029df212ce19a9ab171b0e841e26b13423fa9d86a29588d2ff3c79465ea`
- `container-runtime.json`: `f239a98ceb184be2ff63eaafe68f5e40f46965b38b17b9cb49749d9237bd3f34`
- `smoke.json`: `d7c2b167ab7c1ebd014b16c6fb0cb195323535db2620a5ae921376dd2a287a48`
- `native-smoke.json`: `283361a3e17c8e98f0d71a28fc624be6910243f92e7b01cad5d7c7ac2c8d3192`
- `job-exit-code.txt`: `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- scheduler log: `31cf94502677f83157cfb228ec7ba7cb0dd33623d2aa0975b0ba844c2311fcca`

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
- `scout-smoke-20260915-v2/`: terminal GPU smoke receipts and native HTML/run.

The new SIF destination is
`/nesi/nobackup/uoa04799/dyu848/tool-output-lab/containers/vllm-openai-v0.29.0-cu129-ssd-gzip1-v2.sif`.
The published image is **11,042,500,608 bytes**, SHA-256
`2e34131f9ef3257b67e628e735fa76dee506449152f3882bf50204c92e38b6c2`.
`completed.json` confirms inspection/publication and the private site checksum
update. Build time was 391.20 seconds; hashing/publication took another 10.15
seconds. That CPU receipt predates GPU validation; job `9039289` subsequently
verified the image. Neither job contains a research attack experiment. Treat
queue estimates as provisional and recheck actual state before reporting results.

## Status recheck on 2026-09-15

Read-only `sacct` and retained receipt/log inspection establish:

| Job | Outcome | Evidence/implication |
| --- | --- | --- |
| `9029207` model download | COMPLETED, 27m 05s, exit `0:0` | All 63 pinned files verified; reusable model snapshot is present |
| `9029215` container preparation | FAILED, 50m 31s, Slurm exit `9:0` | Build log ends at SIF creation; wrapper exit is `137`; no `completed.json` or successful SIF-finalization receipt |
| `9029415` GPU smoke | CANCELLED, zero runtime, no start time | Its successful-preparation dependency was not met; no synthetic/native Scout smoke directory or receipt |
| `9039259` container recovery | COMPLETED, 6m 49s, exit `0:0` | Published and checksum-verified the v2 SIF using Genoa local SSD and gzip level 1 |
| `9039289` GPU smoke | COMPLETED, 9m 54s, exit `0:0` | Four A100s on `mg15`; all four synthetic checks and all nine benign-native checks passed with seven requests |
| `9043206` Case A | CANCELLED before allocation, elapsed 00:00:00 | Accepted at 15:36 and cancelled at 15:47 NZST after helper-path audit; zero GPU time and requests |
| `9050478` Case A | FAILED `1:0`, 30 seconds on `mg14` | Frozen runner imported changed repository source; request-free validation stopped before vLLM and made zero requests |
| `9052477` Case B | FAILED `1:0`, 8m 35s on `mg14` | Scout loaded and synthetic smoke passed 4/4; missing bundled `configs/local_scout.toml` stopped native smoke at zero native and Case B requests |

The 50-minute build timeout and 30-second kill grace match the observed failure
timing, but the logs only report that the process was killed; timeout is an
inference, not a conclusively recorded cause. Inspect the retained build/partial
artifacts before choosing a new bounded preparation attempt. No retry was
submitted during the earlier checklist review. Corrected job `9050478` was
submitted later and failed before inference as recorded above. The passing software checks
below are the 2026-09-14 verification results.

Evidence directory:
`/nesi/project/uoa04799/dyu848/tool-output-lab/evidence/container-prep-20260914-v1/`
(`build.log`, `job-exit-code.txt`, `plan.json`), plus scheduler log
`evidence/prep-logs/container-9029215.log`. Preserve these failed-attempt records.
That review identified container recovery and a newly named smoke as the next
steps. Both later attempts passed; the cancelled first attempt remains terminal.
For research deliverables, see [the supervisor checklist](RESEARCH_PLAN.md#supervisor-checklist--checked-2026-09-16).

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
receipts are in `codebase/agentdojo-lab/reports/20260914-nesi-setup-v1/` (runtime
evidence, eligible for tracking). The public inventory predates authentication; retain it
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
run path. The completed-trace joint composer and replay entry points now have
separately named, explicitly configured OpenAI-compatible modes while preserving
their legacy defaults. Starter configs are not frozen research protocols. Live
Scout capability is established only by the terminal smoke receipts below.

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

6. **Run the frozen paired experiments.** Case A v5, Case B v3 and Case C v2 now bind the tasks, model identities, request budgets, context limits, template, settings and order. The initial jobs are now terminal; each passed same-allocation smoke before its research requests. Keep historical Groq results separate. Link each report to immutable source traces; document the first divergence, argument changes, memory/tool propagation, final consequence, and each NeuroTaint prediction. Temperature zero does not eliminate the need to measure run-to-run variability.

## Remaining evidence and diagnostics

- Case A's two completed sessions have been compared. The finalizer and wrapper
  are repaired prospectively: future runs record the exact failed check and four
  bounded process-group snapshots. Job `9064136` remains shutdown-unconfirmed.
- Case B's four conditions are saved. The both-only target outcome and all-four
  utility failures need qualified interpretation; repetition and causal-method
  coverage remain outstanding.
- Case C read/exposed its sources and made two memory writes per first session.
  Reporting now preserves every read/exposure/write while exact-one aggregates
  become unknown with cardinality reasons. The handoff remains blocked and both
  second sessions made zero requests. A complete cross-session path is absent.
- Historical raw run/report bundles are recovered and integrity-checked at
  `f96bdc8`; the verification receipt does not certify every old scientific claim.

The meeting packet and prospective diagnostics are complete. These code repairs
do not change frozen inputs, saved outcomes or experimental counts. No new model,
scheduler or native experimental action occurred.

The starter primary and judge both use local Scout, with independent endpoint
configuration. A different judge requires a new explicit model condition. The
project's remaining allocation balance has not been independently verified.

## Repaired-source GPU follow-up submitted — 2026-09-17 NZST

Fresh request-free preparations were created from pushed commit `134ee6b` and
verified before submission: Case A `runs/scout-case-a-prepared-v6`, Case B
`runs/scout-case-b-prepared-v4`, and Case C
`runs/scout-case-c-prepared-v3`. Each preparation contains only its immutable
`plan.json` and `preparation.json` and records zero model requests.

Three new, separately named jobs were accepted by Slurm at 09:27 NZST:

| Job | Scope | Initial state | Requested resources |
| --- | --- | --- | --- |
| `9123394` | Case A repaired cleanup/finalization validation | PENDING (Priority) | 4 A100s, 48 CPUs, 320 GiB, 2 hours maximum |
| `9123398` | Case B prospective descriptive repeat | PENDING (Priority) | 4 A100s, 48 CPUs, 320 GiB, 2 hours maximum |
| `9123399` | Case C repaired uncertainty/handoff diagnostic | PENDING (Priority) | 4 A100s, 48 CPUs, 320 GiB, 2 hours maximum |

All source, runtime-manifest, model-file, container, site-file and copied-wrapper
gates passed without inference or scheduler allocation. The new bundles are
`evidence/scout-case-a-submission-20260917-v4`,
`evidence/scout-case-b-submission-20260917-v3`, and
`evidence/scout-case-c-submission-20260917-v3` under the private durable lab
root. Their `submitted.json` receipts preserve job IDs, input hashes and initial
Slurm records. The scheduler showed a provisional Sep 18 02:04 NZST start for
all three; that estimate is not an allocation guarantee and can change.

These are three runnable follow-ups, not nine jobs. The nine open checklist
entries are scientific acceptance criteria. These runs may add evidence for A,
B, C and repetition, but they do not implement the absent redundant-source
variant or judge/intervention panel and cannot by themselves complete all nine.
No new model request or GPU second was observed at this submission checkpoint,
so progress remains **4/13 experimental (31%)** and **16/25 overall (64%)**.

## Additional bounded protocols ready for freezing — 2026-09-17 NZST

Three separately named follow-ups now have reviewed local launch paths:

- **Case C2** prospectively fixes native handoff target ID `2`, passes only that
  checkpoint into a fresh session-B worker, and requires an executed simulated
  email sink. It never retrospectively selects among writes.
- **Case D** fixes four redundant-source arms with the prospective target pattern
  `both=true`, `a_only=true`, `b_only=true`, `neither=false`. Its terminal gate
  independently requires utility, both source exposures, native target binding,
  positive-arm carrier witnesses and an eligible unblocked joint interpretation.
- **Repeat/judge v1** schedules three byte-identical sham replays, three identical
  neutralized replays and three isolated no-tools judgments. It makes at most nine
  requests, executes no returned tool call and retains disagreements and unknowns.

Independent launch reviews returned GO for all three. The stable combined selection
passed **214 tests plus 16 subtests**; scoped Ruff, Python compilation, shell syntax
and `git diff --check` also passed. Separate independent selections passed 55 C2,
94 D and 97 repeat/judge tests. Invalid terminal receipts, incomplete handoffs,
pattern mismatches, proxy-influenced transport and altered server identities were
rejected in direct mutation checks.

This checkpoint contains implementation only. The final preparations must be
regenerated after these exact source bytes are committed and pushed; immutable
bundles, site files, Slurm receipts and live evidence do not exist yet for C2, D
or repeat/judge. No model request or GPU allocation was used. Checklist progress
therefore remains **4/13 experimental (31%)** and **16/25 overall (64%)**.

## Additional protocols submitted — 2026-09-17 NZST

The first source commit exposed one isolated-bundle defect before submission: D
validated two Case B-only launchers before filtering them from its inventory.
The retained C2/D v1 preparations made zero requests and are stale. Commit
`43d068e2c682661f6e78873cf44b653f96a57e5c` adds a non-validating reusable
inventory helper, an exact copied-bundle regression, and is pushed to
`origin/codex/agentdojo-lab`. Fresh canonical preparations are
`runs/scout-case-c2-prepared-v2` and `runs/scout-case-d-prepared-v2`.

Final copied-bundle audit returned GO for all three protocols:

| Job | Protocol | Manifest | Initial state |
| --- | --- | --- | --- |
| `9126739` | C2 fixed-target cross-session memory | 13 launch entries, `538db1f9c9d2...` | PENDING (Priority) |
| `9126740` | D redundant-source matrix | 12 launch entries, `be6fc03ba871...` | PENDING (Priority) |
| `9126776` | three-repeat replay/judge panel | exact 51-file bundle, `9dea973489f3...` | PENDING (Priority) |

Slurm accepted all three at 10:53 NZST with four A100s, 48 CPUs, 320 GiB and
a two-hour ceiling each. Owner-only `submitted.json` and raw initial `scontrol`
receipts are outside their immutable bundles under corresponding `*-receipts`
directories. All three showed zero runtime and a provisional Sep 18 04:05 NZST
start at the receipt checkpoint. The older A/B/C jobs remain pending with a
provisional 02:04 start. These estimates may change.

The new jobs start automatically when Slurm allocates them. Queue progress is
**0/6 allocated**; new-protocol submission is **3/3** and terminal evidence is
**0/3**. No terminal scientific outcome exists yet, so checklist progress remains
**4/13 experimental (31%)** and **16/25 overall (64%)**.
