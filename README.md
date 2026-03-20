# 🐝 Multi-Agent Swarm Solver

A production-ready multi-agent coordination system for OpenClaw.

## What is Swarm Solver?

Swarm Solver enables complex task decomposition and parallel execution using multiple AI agents. It automatically:
- Switches between models (worker ↔ supervisor)
- Spawns parallel agents for sub-tasks
- Handles failures with retry logic
- Integrates results into cohesive deliverables

## When to Use

Use this skill when:
- ✅ Task requires multiple domain expertise
- ✅ Work can be parallelized
- ✅ User explicitly mentions "complex scenario" or "swarm"
- ✅ Multi-step collaboration needed

Don't use when:
- ❌ Simple, single-step task
- ❌ Quick answer needed
- ❌ No opportunity for parallelization

## Quick Start

```bash
# 1. Activate skill (auto-triggered by complex task)

# 2. Switch to supervisor model
session_status --model kimi-coding/kimi-k2-thinking

# 3. Create execution plan
write swarm-plan.md

# 4. Spawn parallel agents
sessions_spawn --task "[sub-task]" --label worker-1 --model "minimax-portal/MiniMax-M2.7-highspeed"
sessions_spawn --task "[sub-task]" --label worker-2 --model "kimi-coding/k2p5"

# 5. Monitor progress
subagents list --compact

# 6. Integrate results
write swarm-results-integrated.md
```

## File Structure

```
swarm-solver-anthropic/
├── SKILL.md              # Main skill file
├── QUICK_REFERENCE.md    # Command cheat sheet
├── README.md            # This file
├── references/
│   ├── model-config.md  # Model selection guide
│   ├── templates.md     # File templates
│   └── examples.md      # Complete examples
├── scripts/
│   └── example.py       # Python implementation example
└── evals/
    └── evals.json       # Test cases
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Model Switching** | Auto-switch between k2p5 (worker) and k2-thinking (supervisor) |
| **Error Recovery** | Detect failures, retry with simplified tasks |
| **Dynamic Timeouts** | Configure timeouts by task type |
| **Multi-Model Support** | Kimi + MiniMax models |
| **Cost Optimization** | Use cheaper models for research tasks |

## Documentation

- **[SKILL.md](SKILL.md)** - Complete usage guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet
- **[references/model-config.md](references/model-config.md)** - Model selection
- **[references/templates.md](references/templates.md)** - File templates
- **[references/examples.md](references/examples.md)** - Workflow examples

## Example Workflows

### GitHub Analysis
```bash
# Analyze repo and generate contribution guide
sessions_spawn --task "Research Next.js repo" --label research --model minimax-m2.7
sessions_spawn --task "Create contribution guide" --label compile --model k2p5
```

### PPT Generation
```bash
# Generate 25-slide presentation in parallel
sessions_spawn --task "Generate chapter 1" --label ch1 --model minimax-m2.7
sessions_spawn --task "Generate chapter 2" --label ch2 --model minimax-m2.7
# ... spawn chapters 3-5
sessions_spawn --task "Merge all chapters" --label merge --model k2p5
```

## Model Selection

| Task Type | Recommended Model | Why |
|-----------|------------------|-----|
| Research | MiniMax M2.7 | Fast, cost-effective |
| Coding | k2p5 | Better quality |
| Planning | k2-thinking | Deep reasoning |
| Testing | MiniMax M2.7 | Quick validation |

## Cost Comparison

MiniMax M2.7 is ~50% cheaper than k2p5 for research tasks.

## Troubleshooting

### Model switch not working
```bash
session_status | grep model  # Verify current model
```

### Agent stuck
```bash
subagents list               # Check status
subagents kill --target [id] # Kill if needed
```

### High token usage
- Use MiniMax M2.7 for research
- Reduce task scope
- Set token budgets per agent

## Version

v2.0.0 - Added error handling, dynamic timeouts, MiniMax support

## License

MIT
