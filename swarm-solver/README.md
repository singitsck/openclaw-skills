# 🐝 Multi-Agent Swarm Solver - Quick Start

> 基於 AB 測試驗證的生產級多智能體協作系統

---

## 🚀 標準使用流程

### 第一步：判斷是否需要 Swarm
```
問自己：
- 任務是否需要多個領域的專業知識？
- 工作可以並行處理嗎？
- 用戶明確說了「複雜」或「swarm」嗎？

是 → 使用 Swarm Solver
否 → 直接用單一 Agent
```

### 第二步：切換到 Supervisor Model
```bash
session_status --model kimi-coding/kimi-k2-thinking
```

### 第三步：創建執行計劃
```bash
write swarm-plan.md << 'EOF'
# Swarm Execution Plan

## 任務：[任務名稱]

### 子任務
| ID | Agent | 任務 | 超時 | 模型 |
|----|-------|------|------|------|
| 1 | research | [研究任務] | 180s | minimax-m2.7 |
| 2 | dev | [開發任務] | 300s | k2p5 |

### 執行順序
[1] → [2] 或 並行
EOF
```

### 第四步：並行 Spawn Agents
```bash
# 同時啟動多個 Agents
sessions_spawn \
  --task "[任務描述]" \
  --label worker-1 \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180 \
  --cleanup delete

sessions_spawn \
  --task "[任務描述]" \
  --label worker-2 \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 300 \
  --cleanup delete
```

### 第五步：監控進度
```bash
# 每 30 秒檢查一次
subagents list --compact
```

### 第六步：整合結果
```bash
# 讀取所有結果
read swarm-results-worker-1.md
read swarm-results-worker-2.md

# 合併到最終文檔
write final-output.md << 'EOF'
# 最終結果

## Worker 1 結果
[內容]

## Worker 2 結果
[內容]
EOF
```

### 第七步：清理
```bash
# 可選：清理臨時文件
rm swarm-plan.md swarm-results-*.md
```

---

## 🎯 模型選擇指南

| 模型 | 角色 | 使用場景 | 成本 |
|------|------|----------|------|
| **kimi-coding/k2p5** | Worker | 一般任務、程式開發 | 中等 |
| **kimi-coding/kimi-k2-thinking** | Supervisor | 複雜規劃、深度推理 | 較高 |
| **minimax-portal/MiniMax-M2.7-highspeed** | Worker | 快速回應、成本敏感 | 最低 ⭐ |

### 💡 模型選擇建議

| 任務類型 | 推薦模型 | 原因 |
|---------|---------|------|
| 研究/搜尋 | MiniMax M2.7 | 快速、便宜 |
| 程式生成 | k2p5 | 品質較好 |
| 系統設計 | k2-thinking | 深度推理 |
| 測試驗證 | MiniMax M2.7 | 快速完成 |

---

## 📊 AB 測試驗證結果

| 指標 | Version A (舊格式) | Version B (Anthropic) |
|------|-------------------|----------------------|
| **成功率** | ✅ 100% | ⚠️ 50% |
| **穩定性** | ✅ 極高 | ❌ 頻繁超時 |
| **時間效率** | ✅ 快 2-3 分鐘 | ❌ 較慢 |
| **Integration** | ✅ 成功 | ❌ 常失敗 |
| **Token 效率** | 中等 | ✅ 節省 72% |

> **結論：** 生產環境使用 **Version A（舊格式）** 更穩定可靠

---

## 🛠️ 完整示例

### 場景：開發 AI Chat App

**用戶：** "開發一個有市場分析的 AI 聊天應用"

**執行流程：**

```bash
# 1. 切換 Supervisor
session_status --model kimi-coding/kimi-k2-thinking

# 2. Spawn Research Agent（用便宜的 MiniMax）
sessions_spawn \
  --task "研究 AI chat app 市場，找出 3 個競品並分析功能" \
  --label research-worker \
  --model "minimax-portal/MiniMax-M2.7-highspeed" \
  --runTimeoutSeconds 180 \
  --cleanup delete

# 3. Spawn Developer Agent（用 k2p5 寫程式）
sessions_spawn \
  --task "構建 React 前端和 Node.js 後端" \
  --label dev-worker \
  --model "kimi-coding/k2p5" \
  --runTimeoutSeconds 600 \
  --cleanup delete

# 4. 監控進度
subagents list --compact

# 5. 整合結果
# ... 讀取各 agent 輸出並合併
```

---

## 📁 文件結構

```
swarm-solver/
├── SKILL.md          # 📖 完整技能文檔（主要使用）
├── README.md         # 🚀 本快速入門
└── example.py        # 💻 示例實現
```

---

## ⚡ 關鍵原則

1. **模型選擇**：研究用 MiniMax，開發用 k2p5
2. **超時設置**：搜尋 180s，程式生成 600s
3. **錯誤處理**：失敗則重試，最多 2 次
4. **文件命名**：swarm-results-[agent].md
5. **成本優化**：Worker 任務優先用 MiniMax

---

## 🔗 相關鏈接

- **完整文檔**：[SKILL.md](./SKILL.md)
- **AB 測試報告**：https://github.com/singitsck/openclaw-skills/tree/ab-test-results-backup
- **Anthropic 格式版本**：[swarm-solver-anthropic/](../swarm-solver-anthropic/)

---

**記住：簡單任務直接用單一 Agent，複雜任務才用 Swarm Solver！** 💙
