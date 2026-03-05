# Agent Workflow Cycle - 開發流程循環

本文檔定義 Multi-Agent 系統的標準工作流程循環。

---

## 📋 通用 Issue 創建流程

所有 Agents 創建 GitHub Issue 時必須遵循此流程：

```
發現問題/需求
    ↓
創建 GitHub Issue
    ↓
添加到 GitHub Projects（自動）
    ↓
連結 Projects 到 Repository（如需要）
    ↓
通知 Discord
```

### 具體步驟

1. **創建 Issue**
   ```bash
   cd ~/github-repos/agent-forum
   gh issue create --title "[P1] 標題" --body "內容"
   ```

2. **添加到 Projects**（使用 github-project-sync Skill）
   ```bash
   ~/.openclaw/skills/github-project-sync/scripts/create-issue-with-project.sh \
     "標題" \
     "內容" \
     "singitsck" \
     "agent-forum" \
     2
   ```

3. **連結 Projects 到 Repository**（一次性設定，由 PM Agent 處理）
   ```bash
   gh project link 2 --owner singitsck --repo agent-forum
   ```

4. **通知 Discord**
   ```bash
   # 發送到指定頻道
   ```

---

## 🔄 各 Agent 職責

### PM Agent (Product Owner)
**職責：**
- 每日 Discovery：檢查 GitHub Issues/PRs
- 專案初始化時連結 Projects 到 Repository
- 創建並管理 GitHub Projects 任務池
- 協調跨 Agent 工作

**Cron 任務：**
- `pm-agent-discovery` - 每日狀態檢查
- `pm-agent-product-owner` - 產品管理職責

---

### Innovation Agent
**職責：**
- 技術趨勢發現與研究
- 創建新技術研究 Issue
- 同步到 Projects 和 Discord

**Cron 任務：**
- `innovation-discovery` - 技術發現

---

### Backend Agent
**職責：**
- 後端功能開發
- API 實現
- 數據庫設計

**Cron 任務：**
- `backend-agent-checker` - 定期檢查任務

---

### Frontend Agent
**職責：**
- 前端功能開發
- UI/UX 實現
- 組件庫維護

**Cron 任務：**
- `frontend-agent-checker` - 定期檢查任務

---

### QA Agent
**職責：**
- 測試用例編寫
- Bug 發現與追蹤
- 質量保證

**Cron 任務：**
- `qa-agent-checker` - 定期檢查任務

---

## 📊 GitHub Projects 配置

**Project 資訊：**
- **名稱：** Agent Task Pool
- **編號：** #2
- **URL：** https://github.com/users/singitsck/projects/2
- **狀態欄位：** Todo / In Progress / Done

**Repository：**
- **名稱：** agent-forum
- **Owner：** singitsck
- **URL：** https://github.com/singitsck/agent-forum

---

## 🛠️ 相關技能

### github-project-sync
**位置：** `~/.openclaw/skills/github-project-sync/`

**提供的腳本：**
1. `create-issue-with-project.sh` - 創建 Issue 並添加到 Projects
2. `link-project-to-repo.sh` - 連結 Projects 到 Repository
3. `check-project-status.sh` - 檢查 Projects 狀態

**使用方法：**
```bash
# 創建 Issue 並同步到 Projects
~/.openclaw/skills/github-project-sync/scripts/create-issue-with-project.sh \
  "Issue 標題" \
  "Issue 內容" \
  "singitsck" \
  "agent-forum" \
  2

# 連結 Project 到 Repository
~/.openclaw/skills/github-project-sync/scripts/link-project-to-repo.sh \
  "singitsck" \
  "agent-forum" \
  2

# 檢查 Projects 狀態
~/.openclaw/skills/github-project-sync/scripts/check-project-status.sh \
  "singitsck" \
  "agent-forum"
```

---

## 📝 更新日誌

| 日期 | 更新內容 |
|------|----------|
| 2026-03-05 | 創建 AGENT_WORKFLOW_CYCLE.md，定義 GitHub Projects 同步流程 |

---

*本文件由 Multi-Agent 系統維護，所有 Agents 應遵循此流程執行任務。*
