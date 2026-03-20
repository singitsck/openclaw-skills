

---

## 🎯 Agency-Agents Integration (Layer 4)

### 概述

OpenClaw 已整合 [agency-agents](https://github.com/msitarzewski/agency-agents) 的 **156個專業角色**，可直接在 swarm-solver 中使用。

**安裝位置**: `~/.openclaw/agency-agents/`  
**角色數量**: 156個專業 Agents  
**涵蓋領域**: Engineering, Design, Marketing, Sales, Game Dev, Specialized 等

---

### 快速查找角色

```bash
# 查看所有已安裝的角色
ls ~/.openclaw/agency-agents/ | sort

# 按類別查看
ls ~/.openclaw/agency-agents/ | grep -E "(developer|engineer|architect)"  # Engineering
ls ~/.openclaw/agency-agents/ | grep -E "(designer|researcher)"           # Design
ls ~/.openclaw/agency-agents/ | grep -E "(strategist|specialist)"         # Marketing
```

---

### 使用 Agency-Agents 角色

#### 方式 1: 直接使用 (推薦)

```bash
# Step 1: 查看角色定義
cat ~/.openclaw/agency-agents/frontend-developer/AGENTS.md

# Step 2: 提取關鍵內容創建 subagent
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "
[Identity]
You are Frontend Developer, an expert in React/Vue/Angular...

[Core Mission]
Build modern web applications...

[Task]
Create a login form component with email validation and error handling.
Save to ~/.openclaw/workspace-rem/login-component.tsx
" \
  --label frontend-task
```

#### 方式 2: 讀取角色文件作為上下文

```bash
# 先讀取角色定義文件
read ~/.openclaw/agency-agents/security-engineer/AGENTS.md

# 然後創建引用該角色的 subagent
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "作為 Security Engineer，請審查這段代碼的安全性..." \
  --label security-review
```

#### 方式 3: 在 Pattern 中混合使用

```yaml
# 示例：code-first Pattern 結合 agency-agents
phases:
  - id: implement
    name: Implementation Phase
    parallel: false
    steps:
      # 使用我們自己的基礎角色
      - role: code-explorer
        task: "探索代碼庫結構"
      
      # 使用 agency-agents 的專業角色
      - role: frontend-developer
        task: "實現 React 組件"
        source: agency-agents
      
      - role: security-engineer
        task: "安全審查"
        source: agency-agents
```

---

### 熱門角色速查

| 任務類型 | 推薦角色 | 查看定義 |
|---------|---------|---------|
| 前端開發 | frontend-developer | `cat ~/.openclaw/agency-agents/frontend-developer/AGENTS.md` |
| 後端架構 | backend-architect | `cat ~/.openclaw/agency-agents/backend-architect/AGENTS.md` |
| UI設計 | ui-designer | `cat ~/.openclaw/agency-agents/ui-designer/AGENTS.md` |
| 安全審計 | security-engineer | `cat ~/.openclaw/agency-agents/security-engineer/AGENTS.md` |
| AI功能 | ai-engineer | `cat ~/.openclaw/agency-agents/ai-engineer/AGENTS.md` |
| DevOps | devops-automator | `cat ~/.openclaw/agency-agents/devops-automator/AGENTS.md` |
| 內容創作 | content-creator | `cat ~/.openclaw/agency-agents/content-creator/AGENTS.md` |
| SEO優化 | seo-specialist | `cat ~/.openclaw/agency-agents/seo-specialist/AGENTS.md` |
| 代碼審查 | code-reviewer | `cat ~/.openclaw/agency-agents/code-reviewer/AGENTS.md` |
| 測試 | api-tester | `cat ~/.openclaw/agency-agents/api-tester/AGENTS.md` |

---

### 角色文件結構

每個 agency-agents 角色包含：

```
~/.openclaw/agency-agents/[role-name]/
├── SOUL.md          # 身份、性格、溝通風格
├── AGENTS.md        # 核心任務、技術交付物、工作流程
└── IDENTITY.md      # 額外身份信息
```

**使用時主要參考 AGENTS.md**：
- Core Mission (核心使命)
- Technical Deliverables (技術交付物)
- Workflow Process (工作流程)

---

### 與 Subagent Library 的協作

```
Agency-Agents (Layer 4)     Subagent Library (Layer 3.5)
        ↓                           ↓
   專業領域expertise          基礎協作能力
   (如：Security Engineer)     (如：web-researcher)
        ↘                       ↙
              Pattern (Layer 3)
                   ↓
           組成完整 Swarm
```

**最佳實踐**：
- 基礎協調任務 → 使用 Subagent Library 角色
- 專業領域任務 → 使用 Agency-Agents 角色
- 複雜項目 → Pattern 組合兩者

---

### 完整示例：網站開發項目

```bash
# Phase 1: 設計 (使用 Agency-Agents)
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取~/.openclaw/agency-agents/ui-designer/AGENTS.md] 設計一個登錄頁面" \
  --label ui-design

# Phase 2: 前端實現 (使用 Agency-Agents)
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取~/.openclaw/agency-agents/frontend-developer/AGENTS.md] 實現登錄頁面React組件" \
  --label frontend-dev

# Phase 3: 後端實現 (使用 Agency-Agents)
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取~/.openclaw/agency-agents/backend-architect/AGENTS.md] 設計登錄API" \
  --label backend-dev

# Phase 4: 安全審查 (使用 Agency-Agents)
sessions_spawn \
  --model "kimi-coding/k2p5" \
  --task "[讀取~/.openclaw/agency-agents/security-engineer/AGENTS.md] 審查登錄功能安全性" \
  --label security-review
```

---

### 注意事項

1. **模型選擇**: Agency-Agents 角色通常使用 `kimi-coding/k2p5` 以獲得最佳效果
2. **上下文長度**: 讀取 AGENTS.md 後，確保總任務描述不超過 context window
3. **任務具體**: 給予清晰的具體任務，而非模糊的請求
4. **文件輸出**: 明確指定輸出文件路徑，便於後續步驟使用

---

### 相關連結

- **Agency-Agents 源碼**: https://github.com/msitarzewski/agency-agents
- **角色定義位置**: `~/.openclaw/agency-agents/`
- **我們的 Subagent**: `~/.openclaw/subagents/`

---

## 🔄 Version History

- **v3.1.1** (2026-03-20) - Added Agency-Agents integration documentation
- **v3.1.0** (2026-03-20) - Added Subagent Library support
- **v3.0.0** (2026-03-20) - Pattern-based architecture, Research-First workflow
- **v2.0.0** (2026-03-15) - Error handling, dynamic timeouts
- **v1.0.0** (2026-03-10) - Initial release

---

**Note**: This skill now fully supports the 6-layer OpenClaw Multi-Agent Architecture (excluding Layer 5 Application which is not required).
