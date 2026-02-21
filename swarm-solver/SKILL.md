# Multi-Agent Swarm Solver with Model Switch

## Description

This skill enables handling complex, large-scale tasks using a multi-agent swarm architecture with automatic model switching.

- **Default model**: `kimi-coding/k2p5` for general tasks
- **Complex scenarios**: Automatically switch to `kimi-coding/kimi-k2-thinking` as Supervisor/Brain

Use cases: Software development, market analysis, multi-step collaboration, company simulation, etc.

## Trigger Conditions

**Activate when:**
- User requests handling "complex problems" or "large tasks"
- Multi-step collaboration required
- Task spans multiple domains (research + development + testing)
- User explicitly specifies "complex scenario"

**Don't activate when:**
- Simple, single-turn solvable tasks
- Straightforward Q&A
- Simple file operations

## Model Switching Rules (MUST FOLLOW)

### Default Model
- `kimi-coding/k2p5` – For simple tasks or Worker Agents

### Switch Conditions
Switch to `kimi-coding/kimi-k2-thinking` as Supervisor when:
- Multi-agent swarm needed
- Multi-layer recursion (depth > 1)
- Sustained collaboration required
- User specifies "complex scenario"

### Switch Protocol
1. In your first Thought, output: `Switching to kimi-k2-thinking for complex swarm handling`
2. Assume system has switched (or call session_status to switch)
3. Continue as Supervisor Agent

### Fallback
If k2-thinking unavailable or slow:
```
Fallback to default model (k2p5) due to availability
```

## Execution Steps

### Step 1: Analyze & Switch Model
- Thought first: Is this complex enough for swarm?
- If yes, switch to k2-thinking
- Decompose task into 3–5 sub-modules

### Step 2: Initialize Brain (Supervisor)
- Role: CEO/Supervisor Agent
- Responsibilities: Planning, spawning, coordination
- Create `swarm-plan.md` with decomposition

### Step 3: Execute Step-by-Step
For each sub-task:
1. Execute the step (research/code/test)
2. Update `swarm-status.md`
3. Continue to next step automatically

### Step 4: Integration & Final Review
- Combine all results
- Generate final deliverable

### Step 5: Cleanup
- Clean up agents
- Present final results to user

## Agent Role Templates

### Supervisor (Brain)
- **Model**: kimi-k2-thinking
- **Role**: CEO, planner, coordinator
- **Tasks**: Decompose, assign, review, integrate

### Research Agent
- **Model**: k2p5
- **Tools**: web_search, web_fetch
- **Tasks**: Search, collect data, summarize findings

### Developer Agent
- **Model**: k2p5
- **Tools**: exec, write, edit
- **Tasks**: Code generation, file operations, implementation

### Progress Manager
- **Model**: k2p5
- **Tasks**: Track all agent states, remind Supervisor

### Tester Agent (Optional)
- **Model**: k2p5
- **Tasks**: Test outputs, debug, validate results

## Tool Usage Guide

### Required Tools
1. `sessions_spawn` – Create worker agents
2. `sessions_send` – Send messages to agents
3. `subagents` – List, steer, kill agents
4. `write` / `edit` – Update blackboard files
5. `web_search` – Research tasks

### sessions_spawn Parameters (Complete Example)

```bash
sessions_spawn \
  --task "Research AI market trends and write summary" \
  --label research-worker \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 600 \
  --cleanup delete
```

**Parameter Explanation:**
- `--task`: Clear objective for the agent
- `--label`: Unique identifier for the agent
- `--model`: Override model for this agent (use cheap model for workers)
- `--runTimeoutSeconds`: Maximum execution time (default: 300)
- `--cleanup delete`: Auto-delete session when done (saves resources)

### Nested Spawning Check

**⚠️ Important**: OpenClaw default does NOT allow sub-agents to call `sessions_spawn`.

**Check before spawning:**
```
Thought: Check if nested spawning is allowed in config. 
If subagents.allowSpawn is false, Supervisor must spawn all agents directly.
```

**Config requirement for nested spawning:**
```json
{
  "subagents": {
    "allowSpawn": true,
    "maxDepth": 2
  }
}
```

**Workaround (if nested not allowed):**
- All spawning must be done by Supervisor Agent
- Workers should use `sessions_send` to request new agents from Supervisor

### Communication Format
```xml
<!-- Agent communication -->
<agent_task agent_id="worker-1">
  <objective>Research market trends for AI apps</objective>
  <deliverable>Summary in swarm-results.md</deliverable>
  <deadline>5 minutes</deadline>
</agent_task>
```

### Model Alias Configuration

**Required Setup**: Add Moonshot/Kimi provider to OpenClaw config:

```json
{
  "providers": {
    "moonshot": {
      "baseUrl": "https://api.moonshot.cn/v1",
      "apiKey": "your-api-key"
    }
  },
  "models": {
    "kimi-coding/k2p5": {
      "provider": "moonshot",
      "model": "kimi-k2-0711"
    },
    "kimi-coding/kimi-k2-thinking": {
      "provider": "moonshot",
      "model": "kimi-k2-thinking-0711"
    }
  }
}
```

**⚠️ Cost Note**: `kimi-k2-thinking` is significantly more expensive than `k2p5`. Use thinking model only for Supervisor/Brain roles.

### Progress Tracking

```bash
# View agent status with compact stats
subagents list --compact

# Example output:
# research-worker | running | 2m30s | 1.2k tokens
# dev-worker      | idle    | -     | -
```

Update `swarm-status.md` after each spawn/kill.

## Example Execution

### User Request
> "Develop an AI chat app with market analysis"

### Execution Flow

**Step 1: Analysis & Model Switch**
- Switch to k2-thinking
- Decompose: Research → Dev → Design → Test
- Create `swarm-plan.md`

**Step 2: Spawn Research Agent**
```bash
sessions_spawn \
  --task "Research AI chat app market, find 3 competitors, analyze features" \
  --label research-worker \
  --model "kimi-coding/k2p5" \
  --cleanup delete
```

**Step 3: Spawn Developer Agent**
```bash
sessions_spawn \
  --task "Build React frontend and Node.js backend for AI chat app" \
  --label dev-worker \
  --model "kimi-coding/k2p5" \
  --cleanup delete
```

**Step 4: Integration**
- Collect results from all agents
- Generate final deliverable
- Present to user

## Blackboard File Templates

### swarm-plan.md
```markdown
# Swarm Execution Plan

## Task
[Original user request]

## Decomposition
1. [Sub-task 1] → Agent: research-worker
2. [Sub-task 2] → Agent: dev-worker
3. [Sub-task 3] → Agent: design-worker

## Success Criteria
- [ ] All sub-tasks complete
- [ ] Results validated
- [ ] Final deliverable ready

## Timeline
- Start: [timestamp]
- Expected End: [timestamp]
```

### swarm-status.md
```markdown
# Swarm Status Tracker

| Agent | Status | Last Update | Notes |
|-------|--------|-------------|-------|
| research-worker | running | 10:30 | Gathering data |
| dev-worker | pending | - | Waiting for research |
| design-worker | idle | - | Not started |

## Blockers
- None

## Next Actions
- Check research progress in 2 min
```

### swarm-results.md
```markdown
# Accumulated Results

## Research Findings
[Populated by Research Agent]

## Development Output
[Populated by Developer Agent]

## Design Assets
[Populated by Designer Agent]

## Final Integration
[Populated by Supervisor]
```

## Safety Rules

1. **Maximum 6 concurrent agents** – Don't overwhelm the system
2. **Recursive depth ≤ 3** – Avoid infinite spawning
3. **5-minute timeout per agent** – Early stop if stuck
4. **Validate before integration** – Don't blindly combine results
5. **Clean up on completion** – Use `cleanup=delete` or kill agents
6. **Check nested spawning config** – Workers may fail to spawn

## Anti-Patterns (AVOID)

- ❌ Spawning agents without clear tasks
- ❌ Not using blackboard for coordination
- ❌ Letting agents run indefinitely
- ❌ Skipping validation steps
- ❌ Hardcoding model names (use aliases)
- ❌ Assuming nested spawning works (check config first)

## Quick Reference

```bash
# Switch model
session_status --model kimi-coding/kimi-k2-thinking

# Spawn agent with full options
sessions_spawn \
  --task "[clear objective]" \
  --label worker-1 \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 600 \
  --cleanup delete

# Check status with compact view
subagents list --compact

# Send message
sessions_send --label worker-1 --message "[update]"

# Kill all
subagents kill --target all
```
