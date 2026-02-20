# Multi-Agent Swarm Solver - Quick Start

## Usage Example

### Scenario: Complex Task

**User**: "Develop an AI chat app with market research"

**AI (with this skill)**:

1. **Analyze & Switch**
   ```
   Thought: Complex task requiring multiple domains. 
   Switching to kimi-k2-thinking for complex swarm handling.
   ```

2. **Decompose**
   ```
   Breaking down into:
   - Research market trends
   - Design system architecture
   - Implement backend
   - Build frontend
   - Test & validate
   ```

3. **Spawn Agents**
   ```bash
   sessions_spawn --task "Research AI chat market trends" \
                  --label research-agent \
                  --timeoutSeconds 300
                  
   sessions_spawn --task "Design system architecture" \
                  --label architect-agent \
                  --timeoutSeconds 300
   ```

4. **Coordinate**
   ```bash
   subagents list
   sessions_send --label research-agent --message "Status update?"
   ```

5. **Integrate & Deliver**
   - Combine all results
   - Output final deliverable

## Model Aliases

| Alias | Full Model | Use Case |
|-------|-----------|----------|
| k2p5 | kimi-coding/k2p5 | Simple tasks, Workers |
| k2-thinking | kimi-coding/kimi-k2-thinking | Complex tasks, Supervisor |

## File Structure

```
swarm-solver/
├── SKILL.md          # This documentation
├── example.py        # Demo implementation
└── README.md         # Quick start guide
```

## Best Practices

1. **Always use blackboard files** for coordination
2. **Set timeouts** for all spawned agents
3. **Validate results** before integration
4. **Clean up** agents after completion
5. **Switch models** appropriately for task complexity
