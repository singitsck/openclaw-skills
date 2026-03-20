# 🐝 Swarm Solver - Quick Reference

## Essential Commands

### Model Switching
```bash
# Switch to supervisor
session_status --model kimi-coding/kimi-k2-thinking

# Verify switch
session_status | grep "model"

# Switch back to worker
session_status --model kimi-coding/k2p5
```

### Spawning Agents
```bash
# Basic spawn
sessions_spawn --task "[description]" --label worker-1

# With model and timeout
sessions_spawn \
  --task "[description]" \
  --label worker-1 \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 300 \
  --cleanup delete
```

### Monitoring
```bash
# List all agents
subagents list

# Compact view
subagents list --compact

# Check specific agent
sessions_history --sessionKey agent:main:subagent:[label]
```

### Error Recovery
```bash
# Kill failed agent
subagents kill --target worker-1

# Respawn with retry
sessions_spawn \
  --task "[SIMPLIFIED] [original task]" \
  --label worker-1-retry \
  --model "kimi-coding/k2p5"
```

## Agent Templates

### Research Agent
```bash
sessions_spawn \
  --task "Research [topic]. Find [specific info]. Write findings to swarm-results-research.md" \
  --label worker-research \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180
```

### Developer Agent
```bash
sessions_spawn \
  --task "Implement [feature]. Write code to [file]. Update swarm-results-dev.md" \
  --label worker-dev \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 600
```

### Tester Agent
```bash
sessions_spawn \
  --task "Test [feature]. Run [tests]. Report results to swarm-results-test.md" \
  --label worker-test \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 120
```

## Model Selection Guide

| Task Type | Recommended Model | Why |
|-----------|------------------|-----|
| Research | MiniMax M2.7 | Fast, cost-effective |
| Coding | k2p5 | Better code quality |
| Planning | k2-thinking | Deep reasoning |
| Testing | MiniMax M2.7 | Quick validation |

## Timeout Guidelines

| Task | Timeout | Token Budget |
|------|---------|--------------|
| web_search | 180s | ~2K |
| code_gen | 600s | ~10K |
| testing | 120s | ~1K |
| analysis | 300s | ~5K |

## File Naming Convention

```
swarm-plan.md                 # Execution plan
swarm-status.md               # Status tracking
swarm-results-[agent].md      # Individual results
swarm-results-integrated.md   # Combined results
```

## Health Check Schedule

```
T+0min:   Spawn agents
T+30s:    First health check
T+60s:    Second check
T+90s:    Third check
...
Until all complete or timeout
```

## Common Patterns

### Pattern 1: Research → Dev → Test
```
1. Spawn researcher (MiniMax, 180s)
2. Wait for completion
3. Spawn developer (k2p5, 600s)
4. Wait for completion
5. Spawn tester (MiniMax, 120s)
```

### Pattern 2: Parallel Research
```
1. Spawn 3 researchers simultaneously (different aspects)
2. Monitor all
3. Integrate when all complete
```

### Pattern 3: Retry on Failure
```
1. Spawn agent
2. Monitor
3. If failed → kill → respawn with simplified task
4. If failed again → log to blockers
```

## One-Liners

```bash
# Quick spawn with defaults
sessions_spawn --task "[task]" --label w1

# Spawn with cost optimization
sessions_spawn --task "[task]" --label w1 --model "minimax-portal/MiniMax-M2.7-highspeed"

# Kill all agents
subagents list | grep "subagent:" | awk '{print $2}' | xargs -I {} subagents kill --target {}

# Check all agent status
for label in worker-1 worker-2 worker-3; do
  echo "=== $label ==="
  subagents list | grep $label || echo "Not found"
done
```

## Emergency Procedures

### All Agents Stuck
```bash
# Kill all
subagents list | grep "subagent:" | awk '{print $2}' | xargs subagents kill --target

# Restart with simplified tasks
# ... respawn each with reduced scope
```

### High Token Usage
```bash
# Switch to cheaper model
session_status --model "minimax-portal/MiniMax-M2.7-highspeed"

# Reduce task scope
# Update swarm-plan.md with smaller sub-tasks
```

---

**Tip:** Save this as a bookmark for quick access during swarm execution!
