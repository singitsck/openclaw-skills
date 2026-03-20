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

### Available Models

| Model | Role | Use Case | Alias |
|-------|------|----------|-------|
| `kimi-coding/k2p5` | Worker | Simple tasks, fast responses | `Kimi K2.5` |
| `kimi-coding/kimi-k2-thinking` | Supervisor | Complex planning, deep reasoning | - |
| `minimax-portal/MiniMax-M2.7-highspeed` | Worker | Fast, cost-effective | `minimax-m2.7-highspeed` |

## 3-Tier Model Selection System (Recommended)

For optimal cost-performance balance, use the 3-Tier system:

| Tier | Model | Cost | Speed | Use When |
|------|-------|------|-------|----------|
| **Tier-1** | `minimax-portal/MiniMax-M2.7-highspeed` | 1× | ⚡ Fastest | Research, testing, simple tasks |
| **Tier-2** | `kimi-coding/k2p5` | 2× | 🟡 Balanced | Code generation, general tasks |
| **Tier-3** | `kimi-coding/kimi-k2-thinking` | 4× | 🐢 Deliberate | Supervisor, complex planning |

### Quick Selection Guide

| Task Type | Recommended Tier | Model |
|-----------|-----------------|-------|
| Web search, data extraction | Tier-1 | MiniMax M2.7 |
| Simple validation, testing | Tier-1 | MiniMax M2.7 |
| Code generation, refactoring | Tier-2 | k2p5 |
| System design (medium) | Tier-2 | k2p5 |
| Complex architecture | Tier-3 | k2-thinking |
| Multi-agent coordination | Tier-3 | k2-thinking |

### Cost Optimization Rules

1. **Never start with the most expensive model** – Begin with Tier-1
2. **Use Tier-1 for 70% of Worker tasks** – Research, testing, validation
3. **Reserve Tier-3 for Supervisor only** – Unless task explicitly requires deep reasoning
4. **Auto-downgrade on budget exceed** – If预估 tokens > 50k, use Tier-1
5. **Batch tasks by tier** – Group similar complexity tasks together

**Expected savings: 40-60% cost reduction while maintaining quality.**

### Default Model
- `kimi-coding/k2p5` – For simple tasks or Worker Agents
- Alternative: `minimax-portal/MiniMax-M2.7-highspeed` – For cost-sensitive scenarios

### Switch Conditions
Switch to `kimi-coding/kimi-k2-thinking` as Supervisor when:
- Multi-agent swarm needed
- Multi-layer recursion (depth > 1)
- Sustained collaboration required
- User specifies "complex scenario"

### Switch Protocol (CORRECT WAY)

**Step 1: Check current model**
```bash
session_status | grep "model"
```

**Step 2: Switch to thinking model**
```bash
session_status --model kimi-coding/kimi-k2-thinking
```

**Step 3: Verify switch**
```bash
session_status | grep -q "kimi-k2-thinking" && echo "✓ Model switched" || echo "✗ Switch failed"
```

**Step 4: Confirm in thought**
```
Thought: Successfully switched to kimi-k2-thinking. Now acting as Supervisor Agent.
```

### Switch Back (Optional)
After complex planning is done, switch back to save costs:
```bash
session_status --model kimi-coding/k2p5
```

### Fallback
If k2-thinking unavailable or slow:
```bash
# Try 2 times with 5s delay
for i in 1 2; do
  session_status --model kimi-coding/kimi-k2-thinking && break
  sleep 5
done

# If still failing, fallback
echo "Fallback to default model (k2p5) due to availability"
session_status --model kimi-coding/k2p5
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

## Error Handling & Recovery

### Worker Agent Failure Handling

**When a worker agent fails or gets stuck:**

1. **Detect Failure** (Every 30 seconds)
```bash
subagents list --compact
```

2. **Identify Failed Agents**
   - Status = `error`
   - Status = `idle` for >5 minutes without progress
   - High token usage but no output

3. **Recovery Strategy**

| Failure Type | Action | Max Retries |
|-------------|--------|-------------|
| Timeout | Kill & respawn with longer timeout | 2 |
| Error | Kill & respawn with simplified task | 2 |
| No progress | Send message via `sessions_send` to check status | 1 |

4. **Kill and Retry**
```bash
# Kill failed agent
subagents kill --target worker-1

# Respawn with retry count tracking
sessions_spawn \
  --task "[SIMPLIFIED TASK] Original task failed. Retry with reduced scope." \
  --label worker-1-retry \
  --model "kimi-coding/k2p5" \
  --cleanup delete
```

5. **Update Status**
```markdown
# In swarm-status.md
| Agent | Status | Retries | Notes |
|-------|--------|---------|-------|
| worker-1 | failed → retry-1 | 1/2 | Simplified task |
```

6. **If All Retries Fail**
   - Log error to `swarm-status.md` Blockers
   - Continue with partial results
   - Notify Supervisor to adjust plan

### Supervisor Decision Tree
```
Worker Failed?
├── Yes → Retry count < 2?
│   ├── Yes → Respawn with simplified task
│   └── No → Mark as failed, log to Blockers
│       └── Can continue without this worker?
│           ├── Yes → Continue with remaining workers
│           └── No → Abort and report to user
└── No → Continue normal execution
```

## Blackboard File Structure (Concurrency-Safe)

### File Organization
To avoid concurrent write conflicts, use **one file per agent**:

```
swarm-plan.md              # Supervisor only (read/write)
swarm-status.md            # Supervisor only (read/write)
swarm-results-research.md  # Research Agent only (write)
swarm-results-dev.md       # Developer Agent only (write)
swarm-results-design.md    # Designer Agent only (write)
swarm-results-test.md      # Tester Agent only (write)
swarm-results-integrated.md # Supervisor only (write after collection)
swarm-reflection.md        # Reflection Agent (optional)
```

### Write Rules
1. **Each agent ONLY writes to their assigned result file**
2. **Use `--append` flag instead of overwrite**
3. **Supervisor is the ONLY entity that can write to integrated file**
4. **Status file is updated only by Supervisor**

### Supervisor Integration Process
```bash
# 1. Read all individual result files
read swarm-results-research.md
read swarm-results-dev.md
read swarm-results-design.md

# 2. Integrate and write to combined file
write swarm-results-integrated.md << 'EOF'
# Combined Results

## Research
[Content from research file]

## Development
[Content from dev file]

## Design
[Content from design file]
EOF
```

## Dynamic Timeout Configuration

### Task-Type Based Timeouts
Instead of fixed 5 minutes, use dynamic timeouts:

| Task Type | Timeout | Reason |
|-----------|---------|--------|
| `web_search` | 180s | Usually fast |
| `code_generation` | 600s | Needs time for complex logic |
| `testing` | 120s | Should be quick |
| `analysis` | 300s | Medium complexity |
| `design` | 240s | Creative work |

### Usage
```bash
sessions_spawn \
  --task "Generate React component" \
  --label dev-worker \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 600  # 10 min for code gen
  --cleanup delete
```

### Pre-Timeout Warning
For long-running tasks, warn 60 seconds before timeout:
```bash
# Spawn with warning
sessions_spawn \
  --task "[Task with progress updates] Report progress every 2 minutes" \
  --label long-task \
  --runTimeoutSeconds 600

# In worker: Send progress updates
sessions_send --label supervisor --message "Progress: 50% complete"
```

### Extend Timeout Dynamically
If a task needs more time:
1. Worker sends "Need more time" message
2. Supervisor kills current agent
3. Respawn with extended timeout
4. Worker resumes from saved progress

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
