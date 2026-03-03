# GitHub 項目監控

方便地監控 GitHub 項目更新，特別適合追蹤 OpenClaw 官方項目。

## 🚀 快速開始

### 手動查看
```bash
~/.openclaw/skills/github-monitor/scripts/monitor-openclaw.sh
```

### 輸出示例
```
=== OpenClaw 項目更新監控 - 2026-03-03 15:44:26 ===

📌 最近 Commits:

1. ae29842 - Gateway: fix stale self version in status output (#32655)
   作者: Liu Xiaopai | 日期: 2026-03-03

2. b1b41eb - feat(mattermost): add native slash command support
   作者: Muhammed Mukhthar CM | 日期: 2026-03-03

📦 最新 Release:
   v2026.3.2 - openclaw 2026.3.2
   發布日期: 2026-03-03
```

## ⚙️ 自動監控（Cron）

### 方法一：OpenClaw Cron（推薦）
```bash
openclaw cron add \
  --name "openclaw-updates" \
  --cron "0 9 * * *" \
  --message "檢查 OpenClaw 項目更新" \
  --session isolated \
  --announce
```

### 方法二：系統 Crontab
```bash
crontab -e

# 每天上午 9 點檢查
0 9 * * * ~/.openclaw/skills/github-monitor/scripts/monitor-openclaw.sh
```

## 📁 目錄結構

```
github-monitor/
├── SKILL.md
├── README.md
├── scripts/
│   └── monitor-openclaw.sh
├── data/          # 數據緩存
└── logs/          # 運行日誌
```

## 🔧 監控其他項目

編輯 `scripts/monitor-openclaw.sh`，修改第一行：
```bash
REPO="owner/repo-name"
```

## 📊 數據源

- GitHub REST API（免費，無需認證）
- 限制：每小時 60 次請求（未認證）

---

*最後更新: 2026-03-03*
