---
name: swarm-solver
description: |
  Multi-Agent Swarm Solver with automatic model switching and error recovery.
  
  Use when: User requests handling complex, large-scale tasks requiring multi-agent 
  coordination, multi-step collaboration across domains, or explicitly specifies 
  "complex scenario" or "swarm".
  
  This skill automatically switches between k2p5 (worker) and k2-thinking (supervisor) 
  models, spawns parallel agents, and handles failures with retry logic.
  
  Make sure to use this skill for:
  - Multi-agent task decomposition
  - Parallel research and development
  - Complex problem solving requiring multiple perspectives
  - Any task that benefits from distributed cognition

metadata:
  openclaw:
    emoji: "🐝"
    requires:
      bins: ["bash", "python3"]
    tags: ["multi-agent", "swarm", "parallel", "coordination"]
    author: "singit"
    version: "2.0.0"
---

# 🐝 Multi-Agent Swarm Solver

## Description

A production-ready multi-agent coordination system that decomposes complex tasks into parallel sub-tasks, assigns specialized agents, and integrates results into cohesive deliverables.

**Key Features:**
- Automatic model switching (worker ↔ supervisor)
- Parallel agent spawning and coordination
- Robust error handling with retry logic
- Dynamic timeout configuration
- Multi-model support (Kimi + MiniMax)

## Quick Start

### 1. Analyze Task Complexity
```
Thought: Does this task need multi-agent coordination?
- Multi-domain expertise needed? → YES
- Can be parallelized? → YES
- User said "complex" or "swarm"? → YES
→ Use Swarm Solver
```

### 2. Switch to Supervisor Model
```bash
session_status --model kimi-coding/kimi-k2-thinking
```

### 3. Create Swarm Plan
```bash
# Create swarm-plan.md with task decomposition
cat > swarm-plan.md << 'EOF'
# Swarm Execution Plan

## Task: [Task Name]

### Sub-Tasks
| ID | Agent | Task | Timeout | Model |
|----|-------|------|---------|-------|
| 1 | research | [Task] | 180s | minimax-m2.7 |
| 2 | dev | [Task] | 600s | k2p5 |
| 3 | test | [Task] | 120s | minimax-m2.7 |

### Status Tracking
| Agent | Status | Result File |
|-------|--------|-------------|
| research | pending | swarm-results-research.md |
| dev | pending | swarm-results-dev.md |
| test | pending | swarm-results-test.md |
EOF
```

### 4. Spawn Agents
```bash
# Spawn in parallel
sessions_spawn \
  --task "[Sub-task description]" \
  --label worker-research \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180 \
  --cleanup delete
```

### 5. Monitor & Recover
```bash
# Check every 30 seconds
subagents list --compact

# If failed, retry with simplified task
subagents kill --target worker-research
sessions_spawn \
  --task "[SIMPLIFIED] Retry with reduced scope" \
  --label worker-research-retry \
  --model "kimi-coding/k2p5"
```

### 6. Integrate Results
```bash
# Read individual results
read swarm-results-research.md
read swarm-results-dev.md

# Combine into final deliverable
write swarm-results-integrated.md
```

## Agent Roles

| Role | Model | Responsibility | Tools |
|------|-------|----------------|-------|
| **Supervisor** | k2-thinking | Planning, spawning, integration, recovery | All coordination tools |
| **Researcher** | MiniMax M2.7 | Information gathering, analysis | web_search, web_fetch |
| **Developer** | k2p5 | Code generation, implementation | write, edit, exec |
| **Tester** | MiniMax M2.7 | Validation, verification | exec, test frameworks |

## Model Configuration

### Available Models

| Model | Alias | Role | Best For |
|-------|-------|------|----------|
| `kimi-coding/k2p5` | - | Worker | General tasks, coding |
| `kimi-coding/kimi-k2-thinking` | - | Supervisor | Complex planning |
| `minimax-portal/MiniMax-M2.7-highspeed` | minimax-m2.7 | Worker | Fast, cost-effective |

### Switch Protocol

```bash
# 1. Check current model
session_status | grep "model"

# 2. Switch to thinking model
session_status --model kimi-coding/kimi-k2-thinking

# 3. Verify switch
session_status | grep -q "kimi-k2-thinking" && echo "✓ Switched"

# 4. Switch back (optional)
session_status --model kimi-coding/k2p5
```

## Error Handling

### Failure Detection
Check every 30 seconds:
```bash
subagents list --compact
```

### Recovery Strategy

| Failure Type | Action | Max Retries |
|-------------|--------|-------------|
| Timeout | Respawn with 1.5x timeout | 2 |
| Error | Respawn with simplified task | 2 |
| No progress | Send status check message | 1 |

### Decision Tree
```
Worker Failed?
├── Yes → Retry count < 2?
│   ├── Yes → Respawn with simplified task
│   └── No → Mark as failed, log to Blockers
│       └── Can continue without this worker?
│           ├── Yes → Continue with remaining
│           └── No → Abort and report to user
└── No → Continue normal execution
```

## Dynamic Timeouts

| Task Type | Timeout | Reason |
|-----------|---------|--------|
| web_search | 180s | Usually fast |
| code_generation | 600s | Needs time for complex logic |
| testing | 120s | Should be quick |
| analysis | 300s | Medium complexity |
| design | 240s | Creative work |

## File Structure

```
swarm-plan.md              # Supervisor only
swarm-status.md            # Supervisor only
swarm-results-research.md  # Research Agent only
swarm-results-dev.md       # Developer Agent only
swarm-results-design.md    # Designer Agent only
swarm-results-test.md      # Tester Agent only
swarm-results-integrated.md # Supervisor only (after collection)
```

**Write Rules:**
- Each agent ONLY writes to their assigned result file
- Use `--append` flag instead of overwrite
- Supervisor is the ONLY entity that can write integrated file

## Examples

### Example 1: Research + Development
```bash
# Task: Develop AI chat app with market analysis

# Step 1: Switch to supervisor
session_status --model kimi-coding/kimi-k2-thinking

# Step 2: Spawn parallel agents
sessions_spawn \
  --task "Research AI chat market trends, competitors, and user needs" \
  --label worker-research \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180

sessions_spawn \
  --task "Design backend API architecture for chat app" \
  --label worker-backend \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 600

# Step 3: Monitor
subagents list --compact

# Step 4: Integrate results
read swarm-results-research.md
read swarm-results-dev.md
write swarm-results-integrated.md
```

See [references/examples.md](references/examples.md) for more detailed examples.

## References

- [Model Configuration](references/model-config.md) - Detailed model settings and aliases
- [Agent Templates](references/templates.md) - File templates for swarm execution
- [Advanced Examples](references/examples.md) - Complete workflow examples
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick command reference

## Troubleshooting

### Issue: Model switch not working
**Solution:** Verify with `session_status | grep model`

### Issue: Worker agent stuck
**Solution:** Check with `subagents list`, kill and retry if needed

### Issue: Results not combining correctly
**Solution:** Ensure each worker writes to their assigned file only

### Issue: High token usage
**Solution:** Use MiniMax M2.7 for research tasks, k2p5 for coding

## Version History

- v2.0.0 (2026-03-20) - Added error handling, dynamic timeouts, MiniMax support
- v1.0.0 (2026-03-15) - Initial release

---

**Note:** This skill is designed for production use. Always monitor agent health and have retry strategies in place.
