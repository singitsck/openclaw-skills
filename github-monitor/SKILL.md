---
name: github-monitor
description: 監控 GitHub 項目更新，支持 OpenClaw 官方項目追蹤
trigger: "監控github|github更新|項目追蹤"
tools: [shell, filesystem, http]
---

# GitHub 項目監控

監控 GitHub 項目的最新 commits、releases 和 issues。

## 支持的項目

- ✅ OpenClaw 官方項目 (openclaw/openclaw)
- ✅ 可配置其他項目

## 使用方法

### 手動查看更新
```bash
~/.openclaw/skills/github-monitor/scripts/monitor-openclaw.sh
```

### 添加到 OpenClaw Cron（推薦）
```bash
# 每天上午 9 點檢查更新
openclaw cron add \
  --name "openclaw-updates" \
  --cron "0 9 * * *" \
  --message "請運行 ~/.openclaw/skills/github-monitor/scripts/monitor-openclaw.sh 檢查 OpenClaw 項目更新並報告結果"
```

## 監控內容

- 📌 最近 5 個 commits
- 📦 最新 release
- 📊 項目統計（stars, forks, issues）

## 數據源

- GitHub REST API（免費，無需認證）
