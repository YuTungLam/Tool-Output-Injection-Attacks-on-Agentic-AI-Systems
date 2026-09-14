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
| [HPC_SETUP.md](HPC_SETUP.md) | NeSI migration and Llama 4 Scout deployment plan |
| [AGENTS.md](AGENTS.md) | Instructions for future Codex sessions |

**Current phase, 2026-09-14:** prepare local inference on NeSI and a few concrete
propagation case studies. Historical large evaluation plans are deferred. The
local endpoint adapter is tested, and Scout is authenticated, downloaded and
checksum-verified. Container preparation and a dependent GPU smoke are scheduled. Scout inference and the new pilot
have not run. See HPC_SETUP.md for current jobs and checks before resubmitting.

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
