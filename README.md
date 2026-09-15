# Tool Output Injection Attacks on Agentic AI Systems

This project studies how manipulated tool outputs affect an AI agent's decisions
and sensitive tool arguments, and whether provenance tracking captures the full
path to the resulting action.

The active implementation is [AgentDojo Lab](codebase/agentdojo-lab/README.md),
which combines native AgentDojo execution, an independent NeuroTaint-style
implementation, and interactive experiment reports.

## Start here

| Document | Purpose |
| --- | --- |
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | Original idea, supervisor guidance, repository map, and current state |
| [RESEARCH_PLAN.md](RESEARCH_PLAN.md) | Small case-study pilot, evidence requirements, and implementation order |
| [RESEARCH_PROGRESS.md](RESEARCH_PROGRESS.md) | Percentage, progress bars, and explanations of each setup/experiment run |
| [HPC_SETUP.md](HPC_SETUP.md) | NeSI migration and Llama 4 Scout deployment plan |
| [AGENTS.md](AGENTS.md) | Instructions for future Codex sessions |

**Current phase, 2026-09-15:** prepare local inference on NeSI and a few concrete
propagation case studies. Historical large evaluation plans are deferred. The
local endpoint adapter is tested, and Scout is authenticated, downloaded and
checksum-verified. The container retry and four-A100 GPU smoke `9039289` passed;
synthetic 4/4 and all nine benign-native checks passed with seven requests. The
single- and cross-session exporters, configured joint/replay transport and
bounded Case A runner are verified. The current Case A plan binds 85 source files
and made zero requests. Its first submitted wrapper job, `9043206`, was cancelled
before allocation after an audit found a Slurm helper-path defect. Corrected job
`9050478` is pending for Priority with zero runtime, no allocation and no model
requests; Slurm will start it automatically. The strict Case B runner and
same-allocation wrapper are reviewed and test-clean; its 163-source v2 plan is
prepared with zero calls. Its immutable bundle passed offline validation, and job `9052477` is
pending for Priority with no allocation or calls; it also starts automatically.
No new research experiment has completed.
The supervisor checklist is **10/25 (40%)** overall, **10/12 (83%)** for
preparation, and **0/13** for new experimental deliverables.
See [progress and per-run results](RESEARCH_PROGRESS.md), [the supervisor checklist](RESEARCH_PLAN.md#supervisor-checklist--checked-2026-09-15)
and HPC_SETUP.md for the remaining work and retained job outcomes.

## Continuing on another device

Use the `codex/agentdojo-lab` branch and pull its latest changes before opening
Codex in the repository. For an existing clean checkout:

```bash
git fetch origin
git switch codex/agentdojo-lab
git pull --ff-only
```

If the branch is not local yet, use
`git switch --track origin/codex/agentdojo-lab` after fetching. Preserve or commit
local work before changing branches. Git authentication must be configured on
each device; the NeSI SSH setup is not copied by Git.

The root AGENTS.md directs new sessions to the project brief and plan. This uses
[Codex's repository instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
These files must be present in the branch checked out on the new device.

Git carries source, configurations, and Markdown notes. It does **not** carry the
ignored experiment runs, generated HTML reports, model weights, environments, or
credentials. See [the artifact handoff](PROJECT_CONTEXT.md#moving-between-devices)
before trying to reopen historical reports.
