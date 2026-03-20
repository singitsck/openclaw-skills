# Model Configuration Reference

## Available Models

### Kimi Models

| Model ID | Alias | Context | Speed | Best For |
|----------|-------|---------|-------|----------|
| `kimi-coding/k2p5` | k2p5 | 256K | Fast | General coding, simple tasks |
| `moonshot/kimi-k2.5` | kimi-k2.5 | 250K | Fast | Coding, text tasks |
| `kimi-coding/kimi-k2-thinking` | k2-thinking | 256K | Slow | Complex planning, reasoning |

### MiniMax Models

| Model ID | Alias | Context | Speed | Cost | Best For |
|----------|-------|---------|-------|------|----------|
| `minimax-portal/MiniMax-M2.7-highspeed` | minimax-m2.7 | 195K | Very Fast | Low | Research, quick tasks |
| `minimax-portal/MiniMax-M2.7` | - | 195K | Fast | Low | Balanced |
| `minimax-portal/MiniMax-M2.7-Lightning` | - | 195K | Fastest | Lowest | Ultra-fast responses |

## Model Selection Matrix

### By Task Type

| Task | Primary | Fallback | Reason |
|------|---------|----------|--------|
| **Research** | MiniMax M2.7 | k2p5 | Fast, cheap for info gathering |
| **Code Generation** | k2p5 | MiniMax M2.7 | Better code quality |
| **Code Review** | k2p5 | MiniMax M2.7 | Attention to detail |
| **System Design** | k2-thinking | k2p5 | Deep reasoning needed |
| **Testing** | MiniMax M2.7 | k2p5 | Quick validation |
| **Documentation** | MiniMax M2.7 | k2p5 | Fast writing |
| **Complex Planning** | k2-thinking | - | Required for supervisor |

### By Cost Sensitivity

| Budget Level | Worker Model | Supervisor Model |
|--------------|--------------|------------------|
| **Low budget** | MiniMax M2.7-Lightning | MiniMax M2.7 |
| **Balanced** | MiniMax M2.7-highspeed | k2-thinking |
| **Quality first** | k2p5 | k2-thinking |

### By Speed Requirement

| Speed Need | Model | Expected Latency |
|------------|-------|------------------|
| **Real-time** | MiniMax M2.7-Lightning | ~1-2s |
| **Fast** | MiniMax M2.7-highspeed | ~2-4s |
| **Normal** | k2p5 | ~3-6s |
| **Deep thinking** | k2-thinking | ~5-15s |

## Switch Commands

### Basic Switch
```bash
session_status --model kimi-coding/kimi-k2-thinking
```

### Switch with Verification
```bash
# Switch and verify
session_status --model kimi-coding/kimi-k2-thinking
session_status | grep -q "kimi-k2-thinking" && echo "✓ Success" || echo "✗ Failed"
```

### Conditional Switch
```bash
# Check current model first
current_model=$(session_status | grep "model" | awk '{print $2}')

if [[ "$current_model" != *"k2-thinking"* ]]; then
    echo "Switching to k2-thinking..."
    session_status --model kimi-coding/kimi-k2-thinking
fi
```

### Retry on Failure
```bash
# Try 3 times with 5s delay
for i in 1 2 3; do
    session_status --model kimi-coding/kimi-k2-thinking && break
    echo "Attempt $i failed, retrying..."
    sleep 5
done
```

## Cost Comparison

### Relative Cost (per 1K tokens)

| Model | Input Cost | Output Cost | Total (avg) |
|-------|-----------|-------------|-------------|
| MiniMax M2.7-Lightning | 1x | 1x | **1x** (baseline) |
| MiniMax M2.7-highspeed | 1.2x | 1.2x | **1.2x** |
| MiniMax M2.7 | 1.5x | 1.5x | **1.5x** |
| k2p5 | 2x | 2x | **2x** |
| k2-thinking | 4x | 4x | **4x** |

### Cost Optimization Strategies

1. **Use MiniMax for research** (saves ~50% on info gathering)
2. **Use k2p5 for coding** (better quality justifies cost)
3. **Reserve k2-thinking for planning only** (most expensive)
4. **Batch similar tasks** (reduce model switch overhead)

## Context Window Usage

### Recommended Allocation

| Role | Model | Context Used For | Max Tokens |
|------|-------|------------------|------------|
| Supervisor | k2-thinking | Plan + all results | ~100K |
| Researcher | MiniMax M2.7 | Search results | ~50K |
| Developer | k2p5 | Code + requirements | ~80K |
| Tester | MiniMax M2.7 | Test cases + results | ~30K |

### Monitoring Context Usage
```bash
# Check current session status (includes token usage)
session_status

# Look for:
# - Input tokens used
# - Output tokens used
# - Context window remaining
```

## Fallback Strategy

### When Primary Model Unavailable

```bash
# Primary: k2-thinking for supervisor
# Fallback chain:
1. session_status --model kimi-coding/kimi-k2-thinking
2. If fails → session_status --model kimi-coding/k2p5
3. If fails → session_status --model minimax-portal/MiniMax-M2.7-highspeed
```

### Graceful Degradation

```bash
switch_to_supervisor() {
    # Try thinking model first
    if session_status --model kimi-coding/kimi-k2-thinking 2>/dev/null; then
        echo "✓ Using k2-thinking"
        return 0
    fi
    
    # Fallback to k2p5
    if session_status --model kimi-coding/k2p5 2>/dev/null; then
        echo "⚠ Fallback to k2p5"
        return 0
    fi
    
    echo "✗ No suitable supervisor model available"
    return 1
}
```

## Best Practices

1. **Always verify model switch** - Don't assume it worked
2. **Use cheapest model that can do the job** - MiniMax for research, k2p5 for code
3. **Reserve k2-thinking for supervisor only** - Worker agents don't need deep reasoning
4. **Monitor token usage** - Switch models if context window filling up
5. **Have fallback ready** - Know which model to use if primary fails

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  MODEL CHEAT SHEET                                  │
├─────────────────────────────────────────────────────┤
│  Supervisor  → k2-thinking                          │
│  Research    → MiniMax M2.7 (cheap + fast)         │
│  Code        → k2p5 (quality)                       │
│  Test        → MiniMax M2.7 (quick)                │
│  Emergency   → Any available                        │
├─────────────────────────────────────────────────────┤
│  COST: MiniMax < k2p5 << k2-thinking               │
│  SPEED: MiniMax-fast > k2p5 > k2-thinking          │
│  QUALITY: k2-thinking > k2p5 > MiniMax             │
└─────────────────────────────────────────────────────┘
```
