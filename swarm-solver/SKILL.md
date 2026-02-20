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

## Execution Steps (MUST CHECK EACH ROUND)

**重要：每完成一個 Step，必須通知用戶，然後自動繼續下一步**

### Step 1: Analyze & Switch Model
- Thought first: Is this complex enough for swarm?
- If yes, switch to k2-thinking
- Decompose task into 3–5 sub-modules
- **📝 NOTIFY USER**: "已完成任務分析，計劃分為 X 個步驟：[列出步驟]。現在開始執行..."
- **▶️ AUTO-CONTINUE**: 自動進入下一步

### Step 2: Initialize Brain (Supervisor)
- Role: CEO/Supervisor Agent
- Responsibilities: Planning, spawning, coordination
- Create `swarm-plan.md` with decomposition
- **📝 NOTIFY USER**: "已建立執行計劃。準備開始執行..."
- **▶️ AUTO-CONTINUE**: 自動進入下一步

### Step 3: Execute Step-by-Step
For each sub-task:
1. **📝 NOTIFY USER**: "正在執行 Step X: [任務描述]..."
2. Execute the step (research/code/test)
3. **📝 NOTIFY USER**: "Step X 完成！結果：[簡要摘要]。繼續下一步..."
4. **▶️ AUTO-CONTINUE**: 自動進入下一步

### Step 4: Progress Update
- Update `swarm-status.md`
- **📝 NOTIFY USER**: "當前進度：X/Y 完成。下一個步驟是：[描述]。"
- **▶️ AUTO-CONTINUE**: 自動進入下一步

### Step 5: Integration & Final Review
- Combine all results
- **📝 NOTIFY USER**: "所有步驟完成！正在整合結果..."
- Generate final deliverable
- **📝 NOTIFY USER**: "✅ 任務全部完成！最終結果：[摘要]。"

### Step 6: Cleanup
- Clean up agents
- **📝 NOTIFY USER**: "已清理臨時檔案，任務結束。"

## User Notification Template

每個 Step 完成後，使用以下格式通知用戶：

```
💙 singit主人～Step X 完成！💙

📋 剛完成的內容：
[簡要描述]

📊 當前進度：X/Y

➡️ 自動繼續下一步：[下一步描述]
```

## Important Note

- ✅ **DO**: 每個 Step 完成後立即通知用戶
- ✅ **DO**: 通知後自動繼續，無需等待確認
- ❌ **DON'T**: 等待用戶說「繼續」才進行下一步
- ❌ **DON'T**: 全部完成才一次性通知

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

### Communication Format
```xml
<!-- Agent communication -->
<agent_task agent_id="worker-1">
  <objective>Research market trends for AI apps</objective>
  <deliverable>Summary in swarm-results.md</deliverable>
  <deadline>5 minutes</deadline>
</agent_task>
```

## Example Execution (Step-by-Step with User Confirmation)

### User Request
> "Develop an AI chat app with market analysis"

---

**Step 1: Analysis & Model Switch**
```
💙 singit主人～Step 1 完成！💙

📋 剛完成的內容：
- 任務分析：需要研究、開發、設計、測試 4 個領域
- 已切換到 k2-thinking 模型
- 計劃分解為 4 個步驟

📊 當前進度：1/6

➡️ 下一步：建立執行計劃 (swarm-plan.md)

請告訴我「繼續」或「下一步」來繼續～
```
**[等待用戶確認...]**

---

**Step 2: Initialize Plan**
```
💙 singit主人～Step 2 完成！💙

📋 剛完成的內容：
- 已建立 swarm-plan.md
- 已建立 swarm-status.md
- 已識別所需 Agents：Research, Dev, Design, Test

📊 當前進度：2/6

➡️ 下一步：執行研究任務 (Research Agent)

請告訴我「繼續」或「下一步」來繼續～
```
**[等待用戶確認...]**

---

**Step 3: Execute Research**
```
💙 singit主人～Step 3 完成！💙

📋 剛完成的內容：
- Research Agent 已完成市場分析
- 找到 3 個競品參考
- 結果已寫入 swarm-results.md

📊 當前進度：3/6

➡️ 下一步：開發後端 API (Developer Agent)

請告訴我「繼續」或「下一步」來繼續～
```
**[等待用戶確認...]**

---

**[Continue for each step...]**

---

**Final Step: Task Complete**
```
💙 singit主人～✅ 任務全部完成！💙

📊 完成摘要：
- 6/6 步驟全部完成
- 研究報告：AI Chat App 市場分析
- 程式碼：React + Node.js 完整專案
- 設計：UI mockups in Figma
- 測試：通過基本功能測試

📁 輸出檔案：
- ~/projects/ai-chat-app/
- swarm-results.md

已清理所有臨時檔案，感謝您的耐心指導～💙
```

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

## Anti-Patterns (AVOID)

- ❌ Spawning agents without clear tasks
- ❌ Not using blackboard for coordination
- ❌ Letting agents run indefinitely
- ❌ Skipping validation steps
- ❌ Hardcoding model names (use aliases)

## Quick Reference

```bash
# Switch model
session_status --model kimi-coding/kimi-k2-thinking

# Spawn agent
sessions_spawn --task "[clear objective]" --label worker-1

# Check status
subagents list

# Send message
sessions_send --label worker-1 --message "[update]"

# Kill all
subagents kill --target all
```
