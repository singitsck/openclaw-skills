# Swarm Solver Examples

Complete workflow examples for reference.

## Example 1: GitHub Repository Analysis

### Task
Analyze the Next.js repository and generate a contribution guide.

### swarm-plan.md
```markdown
# Swarm Execution Plan

## Task Overview
**Task Name:** Next.js Contribution Guide
**Objective:** Analyze vercel/next.js and create a comprehensive contribution guide
**Success Criteria:** Guide covers setup, coding standards, PR process, and common issues
**Estimated Duration:** 45 minutes

## Sub-Task Decomposition

| ID | Agent | Role | Task | Dependencies | Timeout | Model |
|----|-------|------|------|--------------|---------|-------|
| 1 | research | Researcher | Analyze repo structure, find CONTRIBUTING.md, identify key files | None | 180s | minimax-m2.7 |
| 2 | analyze | Researcher | Analyze issue patterns, PR templates, code standards | None | 180s | minimax-m2.7 |
| 3 | compile | Developer | Create comprehensive contribution guide | 1, 2 | 300s | k2p5 |

## Output Files
- swarm-results-research.md (repo structure)
- swarm-results-analysis.md (patterns analysis)
- swarm-results-compile.md (final guide)
```

### Execution Commands

```bash
# Step 1: Switch to supervisor
session_status --model kimi-coding/kimi-k2-thinking

# Step 2: Create plan
write swarm-plan.md << 'EOF'
[plan content above]
EOF

# Step 3: Spawn research agents
sessions_spawn \
  --task "Analyze https://github.com/vercel/next.js repository. Find: 1) CONTRIBUTING.md content, 2) Key directories structure, 3) package.json scripts, 4) Test setup. Write findings to swarm-results-research.md" \
  --label worker-research \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180 \
  --cleanup delete

sessions_spawn \
  --task "Analyze Next.js issues and PRs. Find: 1) Common issue types, 2) PR template, 3) Code review patterns, 4) Release process. Write to swarm-results-analysis.md" \
  --label worker-analyze \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180 \
  --cleanup delete

# Step 4: Wait and monitor
sleep 60
subagents list --compact

# Step 5: Spawn compiler
sessions_spawn \
  --task "Create comprehensive CONTRIBUTING.md guide for Next.js. Read swarm-results-research.md and swarm-results-analysis.md. Include: setup instructions, coding standards, PR process, testing, common issues. Write to swarm-results-compile.md" \
  --label worker-compile \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 300 \
  --cleanup delete

# Step 6: Integrate results
read swarm-results-compile.md
write CONTRIBUTING.md << 'EOF'
[Final content from compile agent]
EOF
```

---

## Example 2: Web Application Architecture Design

### Task
Design architecture for an online todo app.

### swarm-plan.md
```markdown
# Swarm Execution Plan

## Task Overview
**Task Name:** Todo App Architecture
**Objective:** Design complete architecture for online todo application
**Success Criteria:** Covers frontend, backend, database, auth, deployment
**Estimated Duration:** 60 minutes

## Sub-Task Decomposition

| ID | Agent | Role | Task | Dependencies | Timeout | Model |
|----|-------|------|------|--------------|---------|-------|
| 1 | requirements | Researcher | Gather requirements, research similar apps | None | 120s | minimax-m2.7 |
| 2 | frontend | Developer | Design frontend architecture | 1 | 300s | k2p5 |
| 3 | backend | Developer | Design backend architecture | 1 | 300s | k2p5 |
| 4 | integration | Developer | Create integration plan | 2, 3 | 240s | k2p5 |

## Execution Order
Parallel: [1] → Parallel: [2, 3] → [4]
```

### Execution Commands

```bash
# Phase 1: Requirements
sessions_spawn \
  --task "Research online todo apps. Identify: must-have features, tech stack trends, scalability needs, security requirements. Write to swarm-results-requirements.md" \
  --label worker-requirements \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 120

# Wait for completion
sleep 30
while subagents list | grep "worker-requirements" | grep -q "running"; do
  sleep 10
done

# Phase 2: Parallel design
sessions_spawn \
  --task "Design frontend architecture for todo app. Include: framework choice, state management, component structure, styling approach. Read requirements from swarm-results-requirements.md. Write to swarm-results-frontend.md" \
  --label worker-frontend \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 300

sessions_spawn \
  --task "Design backend architecture for todo app. Include: API design, database schema, auth strategy, deployment approach. Read requirements from swarm-results-requirements.md. Write to swarm-results-backend.md" \
  --label worker-backend \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 300

# Wait for both
sleep 60
subagents list --compact

# Phase 3: Integration
sessions_spawn \
  --task "Create complete architecture document. Read frontend and backend results. Create: system diagram, API contract, deployment guide. Write to swarm-results-integration.md" \
  --label worker-integration \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 240

# Final integration
read swarm-results-frontend.md
read swarm-results-backend.md
read swarm-results-integration.md
write ARCHITECTURE.md << 'EOF'
# Todo App Architecture

## Overview
[Summary from integration]

## Frontend
[Content from frontend agent]

## Backend
[Content from backend agent]

## Integration
[Content from integration agent]
EOF
```

---

## Example 3: Technical Documentation with FAQ

### Task
Create asyncio developer FAQ from official docs.

### swarm-plan.md
```markdown
# Swarm Execution Plan

## Task Overview
**Task Name:** AsyncIO FAQ
**Objective:** Create comprehensive FAQ for Python asyncio developers
**Success Criteria:** Covers common questions with code examples
**Estimated Duration:** 40 minutes

## Sub-Task Decomposition

| ID | Agent | Role | Task | Dependencies | Timeout | Model |
|----|-------|------|------|--------------|---------|-------|
| 1 | extract | Researcher | Extract key concepts from asyncio docs | None | 180s | minimax-m2.7 |
| 2 | patterns | Researcher | Identify common patterns and anti-patterns | None | 180s | minimax-m2.7 |
| 3 | compile | Developer | Create FAQ with examples | 1, 2 | 300s | k2p5 |

## Output
- FAQ.md with 20+ Q&A pairs
- Code examples for each answer
```

---

## Example 4: Complex PPT Generation (High Complexity)

### Task
Generate FYP-level presentation about AI evolution.

### swarm-plan.md
```markdown
# Swarm Execution Plan

## Task Overview
**Task Name:** AI Evolution PPT
**Objective:** Create 25-slide FYP presentation on AI evolution (ChatGPT → Agents → MCP → Skills)
**Success Criteria:** Professional design, complete content, consistent style
**Estimated Duration:** 90 minutes

## Sub-Task Decomposition

| ID | Agent | Role | Task | Dependencies | Timeout | Model |
|----|-------|------|------|--------------|---------|-------|
| 1 | cover | Designer | Generate algorithmic art cover | None | 120s | minimax-m2.7 |
| 2 | toc | Developer | Create table of contents slide | None | 120s | k2p5 |
| 3 | ch1 | Researcher | Chapter 1: ChatGPT Era content | None | 300s | minimax-m2.7 |
| 4 | ch2 | Researcher | Chapter 2: GPT-4 Evolution | None | 300s | minimax-m2.7 |
| 5 | ch3 | Researcher | Chapter 3: AI Agents | None | 300s | minimax-m2.7 |
| 6 | ch4 | Researcher | Chapter 4: MCP Protocol | None | 300s | minimax-m2.7 |
| 7 | ch5 | Researcher | Chapter 5: Skills Ecosystem | None | 300s | minimax-m2.7 |
| 8 | merge | Developer | Merge all chapters into final PPT | 1-7 | 600s | k2p5 |

## Execution Order
```
Parallel Phase 1: [1, 2, 3, 4, 5, 6, 7]
↓
Phase 2: [8] Merge
```

## Design System
- Font: Microsoft JhengHei
- Colors: #1E3A5F (primary), #3B82F6 (secondary)
- Layouts: varied per slide type
```

### Execution Commands

```bash
# Phase 1: Parallel content generation
echo "Spawning 7 parallel agents..."

sessions_spawn \
  --task "Generate algorithmic art cover for AI Evolution presentation. Use flow fields + particles style. Dark blue theme (#1E3A5F). Save as cover.html" \
  --label worker-cover \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 120

sessions_spawn \
  --task "Create table of contents slide for AI Evolution PPT. 5 chapters. Professional design. Save as toc.pptx" \
  --label worker-toc \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 120

sessions_spawn \
  --task "Create Chapter 1: ChatGPT Era. 5 slides covering: launch, impact, capabilities, limitations. Professional PPT. Save as ch1.pptx" \
  --label worker-ch1 \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 300

# ... similar for ch2, ch3, ch4, ch5

# Monitor progress
echo "Monitoring agents..."
sleep 60
subagents list --compact

# Check every 30s until all complete
while subagents list | grep -q "running"; do
  echo "Still running..."
  subagents list --compact | grep "worker-"
  sleep 30
done

# Phase 2: Merge
echo "All chapters complete. Merging..."

sessions_spawn \
  --task "Merge all PPT chapters into final presentation. Read: toc.pptx, ch1-5.pptx. Add cover.html as background. Create AI_Evolution_Final.pptx. Apply consistent design system." \
  --label worker-merge \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 600

# Verify result
read AI_Evolution_Final.pptx
echo "✓ Presentation generated successfully"
```

---

## Example 5: Error Recovery Scenario

### Scenario
Research agent failed after 2 retries.

### Recovery Process

```bash
# Step 1: Detect failure
subagents list --compact
# Output shows: worker-research | error

# Step 2: Check logs
sessions_history --sessionKey agent:main:subagent:worker-research

# Step 3: Decide on recovery
# Option A: Simplify task and retry
sessions_spawn \
  --task "[SIMPLIFIED] Research only the key concepts of [topic]. Focus on top 3 findings only. Write to swarm-results-research.md" \
  --label worker-research-retry \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 240

# Option B: Continue without this agent
# Update swarm-plan.md to mark research as optional
# Continue with remaining agents

# Step 4: Update status
cat >> swarm-status.md << 'EOF'
## Blockers
| Issue | Agent | Action |
|-------|-------|--------|
| Research failed after 2 retries | worker-research | Continuing with simplified task |
EOF
```

---

## Example 6: Cost Optimization

### Strategy: Use cheapest model for research

```bash
# Original approach (expensive)
sessions_spawn \
  --task "Research AI trends" \
  --label worker-research \
  --model "kimi-coding/k2p5"  # 2x cost

# Optimized approach (cheap)
sessions_spawn \
  --task "Research AI trends" \
  --label worker-research \
  --model "minimax-portal/MiniMax-M2.7-highspeed"  # 1.2x cost

# Savings: ~40% on research tasks
```

---

## Tips from Real Usage

1. **Always verify agent completion** before spawning dependents
2. **Use MiniMax for research** to save costs
3. **Set shorter timeouts for simple tasks** (web_search: 180s)
4. **Monitor token usage** with `session_status`
5. **Have a backup plan** for failed agents
6. **Write results incrementally** to avoid losing progress
7. **Use descriptive labels** for easier monitoring

---

## Common Patterns

### Pattern: Map-Reduce
```
Map: Spawn N agents to process data chunks
↓
Reduce: Spawn 1 agent to combine results
```

### Pattern: Pipeline
```
Stage 1 → Stage 2 → Stage 3 → Stage 4
(Sequential, each depends on previous)
```

### Pattern: Fan-Out-Fan-In
```
    ┌→ Agent 1
    ├→ Agent 2
Start → Agent 3 → Integration
    ├→ Agent 4
    └→ Agent 5
```
