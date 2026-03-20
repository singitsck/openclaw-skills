---
name: swarm-solver
description: |
  Multi-Agent Swarm Solver with pattern-based workflows.
  
  Use when: User requests handling complex, large-scale tasks requiring multi-agent 
  coordination, multi-step collaboration across domains, or explicitly specifies 
  "complex scenario" or "swarm".
  
  This skill provides pattern-based multi-agent orchestration with support for:
  - Research-First Pattern (for content/report generation)
  - Code-First Pattern (for software development)
  - Design-First Pattern (for creative/visual tasks)
  - Orchestrator-Worker Pattern (for general parallel tasks)
  
  Key Features:
  - Pattern-based workflow selection
  - Automatic model switching (worker ↔ supervisor)
  - Parallel agent spawning and coordination
  - Robust error handling with retry logic
  - Multi-model support (Kimi + MiniMax)

metadata:
  openclaw:
    emoji: "🐝"
    requires:
      bins: ["bash", "python3"]
    tags: ["multi-agent", "swarm", "parallel", "coordination", "pattern"]
    author: "singit"
    version: "3.1.1"
---

# 🐝 Multi-Agent Swarm Solver

## Description

A pattern-based multi-agent coordination system that decomposes complex tasks into parallel sub-tasks following established workflow patterns.

**Key Features:**
- **Pattern-based workflows** - Choose the right pattern for your task type
- **Research-First architecture** - For content that requires external data
- **Automatic model switching** (worker ↔ supervisor)
- **Parallel agent spawning** and coordination
- **Robust error handling** with retry logic
- **Multi-model support** (Kimi + MiniMax)

---

## 🎯 Pattern Selection Guide

### When to use which pattern?

| Pattern | Best For | Workflow | Example Tasks |
|---------|----------|----------|---------------|
| **research-first** | Reports, presentations, analysis | Research → Design → Create → Merge | PPT generation, research reports, market analysis |
| **code-first** | Software development | Explore → Implement → Test → Review | Feature development, bug fixes, refactoring |
| **design-first** | Visual/Creative work | Research → Design System → Visual → Content | UI/UX design, branding, artwork |
| **orchestrator-worker** | General parallel tasks | Split → Parallel Process → Merge | Data processing, batch operations |

### Pattern Decision Tree

```
Task Type?
├── Content/Report/Analysis → research-first
├── Software Development → code-first
├── Visual/Creative → design-first
└── General Parallel Work → orchestrator-worker
```

---

## 🚀 Quick Start

### 1. Analyze Task and Select Pattern

```
Thought: What type of task is this?
- Needs external research/data? → research-first
- Software development? → code-first
- Visual design needed? → design-first
- Just parallel processing? → orchestrator-worker
```

### 2. Switch to Supervisor Model

```bash
session_status --model kimi-coding/kimi-k2-thinking
```

### 3. Execute Pattern

#### Pattern: Research-First (for PPT/Report Generation)

```bash
# Phase 1: Research (Parallel)
sessions_spawn \
  --task "Research [TOPIC]: Use web_search/web_fetch to gather information about [ASPECT 1]. Save to research-1.md" \
  --label researcher-1 \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180

sessions_spawn \
  --task "Research [TOPIC]: Use web_search/web_fetch to gather information about [ASPECT 2]. Save to research-2.md" \
  --label researcher-2 \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180

# Wait for research to complete, then...

# Phase 2: Design
sessions_spawn \
  --task "Read all research-*.md files and create design-plan.json with structure and layouts" \
  --label designer \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 240

# Phase 3: Create Content (Parallel)
sessions_spawn \
  --task "Create chapter-1.pptx based on design-plan.json and research files" \
  --label chapter-1 \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 300

# ... more chapters

# Phase 4: Merge
python3 merge-script.py  # Merge all chapter-*.pptx
```

#### Pattern: Code-First (for Development)

```bash
# Phase 1: Explore
sessions_spawn \
  --task "Explore codebase structure, identify relevant files for [FEATURE]" \
  --label explorer \
  --model "minimax-portal/MiniMax-M2.7-highspeed"

# Phase 2: Implement
sessions_spawn \
  --task "Implement [FEATURE] based on exploration results" \
  --label developer \
  --model "kimi-coding/k2p5"

# Phase 3: Test
sessions_spawn \
  --task "Write and run tests for [FEATURE]" \
  --label tester \
  --model "minimax-portal/MiniMax-M2.7-highspeed"

# Phase 4: Review
sessions_spawn \
  --task "Review implementation and tests, provide feedback" \
  --label reviewer \
  --model "kimi-coding/k2p5"
```

#### Pattern: Orchestrator-Worker (General Parallel)

```bash
# Spawn multiple workers in parallel
sessions_spawn --task "Process batch 1" --label worker-1 &
sessions_spawn --task "Process batch 2" --label worker-2 &
sessions_spawn --task "Process batch 3" --label worker-3 &

# Wait and collect results
```

---

## 📋 Pattern Library

### Pattern: research-first

**Use Case**: Content generation requiring external data (PPTs, reports, analysis)

**Workflow**:
```
Phase 1: Research (Parallel)
  ├── Researcher 1 → research-1.md
  ├── Researcher 2 → research-2.md
  └── Researcher N → research-n.md

Phase 2: Design
  └── Designer → design-plan.json

Phase 3: Create (Parallel)
  ├── Chapter Agent 1 → chapter-1.pptx
  ├── Chapter Agent 2 → chapter-2.pptx
  └── Chapter Agent N → chapter-n.pptx

Phase 4: Merge
  └── Supervisor → final-output.pptx
```

**Key Rules**:
- Research Agents MUST use `web_search` or `web_fetch` for external data
- Designer Agent reads ALL research files before creating design plan
- Chapter Agents read design plan AND corresponding research files
- Each agent writes ONLY to their assigned output file

**Example**:
```bash
# Research Phase
sessions_spawn \
  --task "Research WWI: causes, battles, impact. Use web_fetch. Save to research-wwi.md" \
  --label research-wwi \
  --model "minimax-portal/MiniMax-M2.7-highspeed"

sessions_spawn \
  --task "Research WWII: causes, battles, impact. Use web_fetch. Save to research-wwii.md" \
  --label research-wwii \
  --model "minimax-portal/MiniMax-M2.7-highspeed"

# Design Phase
sessions_spawn \
  --task "Read research-*.md, create design-plan.json with 5 chapters, layouts, color scheme" \
  --label designer \
  --model "kimi-coding/k2p5"

# Create Phase
sessions_spawn \
  --task "Create chapter-1.pptx (WWI) using design-plan.json and research-wwi.md" \
  --label chapter-1 \
  --model "kimi-coding/k2p5"

# ... more chapters

# Merge
python3 merge_ppt.py chapter-*.pptx final.pptx
```

---

### Pattern: code-first

**Use Case**: Software development tasks

**Workflow**:
```
Phase 1: Explore
  └── Explorer → codebase-map.md

Phase 2: Implement
  └── Developer → code changes

Phase 3: Test
  └── Tester → test results

Phase 4: Review
  └── Reviewer → review feedback
```

---

### Pattern: orchestrator-worker

**Use Case**: General parallel processing

**Workflow**:
```
Split Task → Parallel Workers → Merge Results
```

---

## 👥 Agent Roles

| Role | Model | Responsibility | Pattern |
|------|-------|----------------|---------|
| **Supervisor** | k2-thinking | Planning, spawning, integration, recovery | All |
| **Researcher** | MiniMax M2.7 | External data gathering | research-first |
| **Designer** | k2p5 | Structure and layout planning | research-first |
| **Content Creator** | k2p5 | Generate final deliverables | research-first |
| **Explorer** | MiniMax M2.7 | Codebase exploration | code-first |
| **Developer** | k2p5 | Implementation | code-first |
| **Tester** | MiniMax M2.7 | Validation | code-first |
| **Reviewer** | k2p5 | Code review | code-first |

---

## ⚙️ Model Configuration

| Model | Alias | Role | Best For | Timeout |
|-------|-------|------|----------|---------|
| `kimi-coding/k2p5` | - | Worker | General, coding | 300-600s |
| `kimi-coding/kimi-k2-thinking` | - | Supervisor | Planning | - |
| `minimax-portal/MiniMax-M2.7-highspeed` | minimax-m2.7 | Worker | Research, fast tasks | 180s |

---

## 🛠️ Best Practices

### 1. Always Use Research-First for Content

**Don't**: Skip research phase and rely on LLM knowledge  
**Do**: Spawn Research Agents to gather external data first

**Why**: Ensures accuracy, freshness, and verifiability of content

### 2. Design Before Create

**Don't**: Let Chapter Agents decide their own layouts  
**Do**: Have a Designer Agent create unified design plan first

**Why**: Ensures visual consistency across all outputs

### 3. Parallelize Where Possible

**Don't**: Run tasks sequentially when independent  
**Do**: Spawn multiple agents in parallel, then wait

**Why**: Dramatically reduces total execution time

### 4. Handle Failures Gracefully

**Don't**: Let one failed agent stop everything  
**Do**: Implement retry logic and fallback strategies

**Why**: Increases system robustness

---

## 🐛 Error Handling

### Recovery Strategy

| Failure Type | Action | Max Retries |
|-------------|--------|-------------|
| Timeout | Respawn with 1.5x timeout | 2 |
| Error | Respawn with simplified task | 2 |
| No progress | Send status check message | 1 |

### Supervisor Recovery Flow

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

---

## 📁 File Structure (Research-First Pattern)

```
swarm-plan.md                    # Supervisor: execution plan
research-{topic}.md              # Research Agents: findings (read-only for others)
design-plan.json                 # Designer: structure and layouts (read-only for others)
chapter-{n}.pptx                 # Chapter Agents: outputs
final-output.pptx                # Supervisor: merged result
EXECUTION_SUMMARY.md             # Supervisor: execution report
```

**Write Rules**:
- Research Agents → ONLY write to research-*.md
- Designer → ONLY write to design-plan.json
- Chapter Agents → ONLY write to chapter-*.pptx
- Supervisor → ONLY entity that reads all files and writes final output

---

## 📊 Real-World Examples

### Example 1: PPT Generation (Research-First)
```bash
# Task: Generate "World Wars to Modern Era" PPT (17 slides)

# Phase 1: 4 Research Agents (Parallel)
sessions_spawn --task "Research WWI" --label r1 --model minimax-m2.7 &
sessions_spawn --task "Research WWII" --label r2 --model minimax-m2.7 &
sessions_spawn --task "Research Cold War" --label r3 --model minimax-m2.7 &
sessions_spawn --task "Research Modern Era" --label r4 --model minimax-m2.7 &

# Phase 2: Designer
sessions_spawn --task "Create design plan from research files" --label designer --model k2p5

# Phase 3: 5 Chapter Agents (Parallel)
sessions_spawn --task "Create chapter 1" --label c1 --model k2p5 &
sessions_spawn --task "Create chapter 2" --label c2 --model k2p5 &
# ...

# Phase 4: Merge
python3 merge_ppt.py
```

### Example 2: Feature Development (Code-First)
```bash
# Task: Implement user authentication

sessions_spawn --task "Explore auth patterns in codebase" --label explorer
sessions_spawn --task "Implement auth feature" --label developer --model k2p5
sessions_spawn --task "Write auth tests" --label tester
sessions_spawn --task "Review auth implementation" --label reviewer --model k2p5
```

---

## 📚 References

- [Pattern Library](patterns/) - Pre-defined workflow patterns
- [Model Configuration](references/model-config.md) - Model settings
- [Agent Templates](references/templates.md) - Reusable templates
- [Advanced Examples](references/examples.md) - Complete examples

---

## 🔄 Version History

- **v3.0.0** (2026-03-20) - Pattern-based architecture, Research-First workflow
- **v2.0.0** (2026-03-15) - Error handling, dynamic timeouts
- **v1.0.0** (2026-03-10) - Initial release

---

**Note**: This skill follows the Anthropic Research-First pattern for content generation tasks. Always spawn Research Agents before Content Creators to ensure accuracy.


---

## 📚 Subagent Library (New in v3.1)

### 快速使用預定義角色

OpenClaw 現在提供可复用的 Subagent 角色庫，位於 `~/.openclaw/subagents/`。

### 可用角色

| 類別 | 角色ID | 名稱 | 用途 |
|------|--------|------|------|
| Research | web-researcher | 網頁研究員 | 搜索和收集外部資料 |
| Content | ppt-designer | PPT設計師 | 生成專業簡報 |
| Code | code-explorer | 代碼探索者 | 分析代碼庫結構 |

### 使用方式

#### 方式 1: 命令行直接引用

```bash
# 使用預定義角色創建 subagent
sessions_spawn \
  --task "subagent:web-researcher | 研究 WWII 起因和影響，保存到 research-wwii.md" \
  --label researcher-1
```

#### 方式 2: 在 Pattern 中引用

```yaml
# patterns/research-first.yaml
phases:
  - id: research
    name: Research Phase
    parallel: true
    agent_count: 4
    subagents:          # 引用預定義角色
      - web-researcher
    task_template: |
      研究 [TOPIC] 的 [ASPECT]
      保存到 research-[aspect].md
```

#### 方式 3: 手動加載角色配置

```bash
# 讀取角色配置
cat ~/.openclaw/subagents/research/web-researcher/SUBAGENT.md

# 根據配置創建 subagent
sessions_spawn \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --timeout 180 \
  --task "[任務描述，遵循 SUBAGENT.md 中的模板]" \
  --label [角色名稱]
```

### 創建新角色

```bash
# 1. 複製模板
mkdir -p ~/.openclaw/subagents/[category]/[role-name]
cp ~/.openclaw/subagents/_template/SUBAGENT.md \
   ~/.openclaw/subagents/[category]/[role-name]/

# 2. 編輯角色定義
vim ~/.openclaw/subagents/[category]/[role-name]/SUBAGENT.md

# 3. 更新索引
vim ~/.openclaw/subagents/README.md
```

### 角色定義結構

每個角色包含 `SUBAGENT.md`，定義：
- **Identity**: 角色身份和專長
- **Mission**: 核心使命和工作原則
- **Capabilities**: 模型配置和可用工具
- **Workflow**: 標準工作流程
- **Prompt Templates**: 提示模板

---

## 🔄 Version History

- **v3.1.0** (2026-03-20) - Added Subagent Library support
- **v3.0.0** (2026-03-20) - Pattern-based architecture, Research-First workflow
- **v2.0.0** (2026-03-15) - Error handling, dynamic timeouts
- **v1.0.0** (2026-03-10) - Initial release


---

## 🎯 Agency-Agents Integration (Layer 4)

### 概述

OpenClaw 已整合 agency-agents 的 **156個專業角色**，可直接在 swarm-solver 中使用。

**安裝位置**: ~/.openclaw/agency-agents/
**角色數量**: 156個專業 Agents
**涵蓋領域**: Engineering, Design, Marketing, Sales, Game Dev, Specialized 等

### 快速查找角色

```bash
# 查看所有已安裝的角色
ls ~/.openclaw/agency-agents/ | sort

# 熱門角色速查
ls ~/.openclaw/agency-agents/ | grep -E "(frontend|backend|security|ui-)"
```

### 使用 Agency-Agents 角色

#### 方式 1: 直接使用 (推薦)

```bash
# Step 1: 查看角色定義
cat ~/.openclaw/agency-agents/frontend-developer/AGENTS.md

# Step 2: 提取關鍵內容創建 subagent
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取AGENTS.md內容作為系統提示] + 具體任務描述" \
  --label frontend-task
```

#### 方式 2: 在 Pattern 中混合使用

```yaml
# 示例：code-first Pattern 結合 agency-agents
phases:
  - id: implement
    steps:
      - role: code-explorer           # 我們自己的基礎角色
        task: "探索代碼庫結構"
      - role: frontend-developer      # agency-agents 專業角色
        task: "實現 React 組件"
      - role: security-engineer       # agency-agents 專業角色
        task: "安全審查"
```

### 熱門角色速查

| 任務類型 | 推薦角色 | 查看定義 |
|---------|---------|---------|
| 前端開發 | frontend-developer | cat ~/.openclaw/agency-agents/frontend-developer/AGENTS.md |
| 後端架構 | backend-architect | cat ~/.openclaw/agency-agents/backend-architect/AGENTS.md |
| UI設計 | ui-designer | cat ~/.openclaw/agency-agents/ui-designer/AGENTS.md |
| 安全審計 | security-engineer | cat ~/.openclaw/agency-agents/security-engineer/AGENTS.md |
| AI功能 | ai-engineer | cat ~/.openclaw/agency-agents/ai-engineer/AGENTS.md |
| 內容創作 | content-creator | cat ~/.openclaw/agency-agents/content-creator/AGENTS.md |
| 代碼審查 | code-reviewer | cat ~/.openclaw/agency-agents/code-reviewer/AGENTS.md |

### 完整示例

```bash
# 前端開發項目示例
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取~/.openclaw/agency-agents/ui-designer/AGENTS.md] 設計登錄頁面" \
  --label ui-design

sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取~/.openclaw/agency-agents/frontend-developer/AGENTS.md] 實現React組件" \
  --label frontend-dev

sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取~/.openclaw/agency-agents/security-engineer/AGENTS.md] 審查安全性" \
  --label security-review
```

### 相關連結

- Agency-Agents 源碼: https://github.com/msitarzewski/agency-agents
- 角色定義位置: ~/.openclaw/agency-agents/

---

## 🔄 Version History

- **v3.1.1** (2026-03-20) - Added Agency-Agents integration documentation
- **v3.1.0** (2026-03-20) - Added Subagent Library support
- **v3.0.0** (2026-03-20) - Pattern-based architecture, Research-First workflow
- **v2.0.0** (2026-03-15) - Error handling, dynamic timeouts
- **v1.0.0** (2026-03-10) - Initial release

---

**Note**: This skill now supports the 5-layer OpenClaw Multi-Agent Architecture (Layer 5 Application not required).
