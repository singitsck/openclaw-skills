---
name: hk-stock-monitor
version: 1.0.0
description: 港股監控助手 - 監控2513.HK和0100.HK，每日收盤生成分析報告
trigger: "港股監控|HK stock monitor|2513|0100"
tools: [shell, filesystem, http, chat]
---

# 港股監控助手

## ⚠️ 重要聲明
此Skill僅用於**監控和分析**，不會自動執行任何交易。
數據來自Yahoo Finance（免費，約15分鐘延遲），僅供參考。

## 功能
1. **每日監控**：追蹤2513.HK和0100.HK的價格變動
2. **收盤分析**：每日收盤後生成分析報告
3. **歷史記錄**：保存每日數據到本地

## 監控股票
| 代碼 | 公司名稱 |
|------|----------|
| 2513.HK | Knowledge Atlas Tech Joint |
| 0100.HK | MiniMax Group Inc |

## 使用方法

### 手動獲取數據
```bash
cd ~/.openclaw/skills/hk-stock-monitor
python3 modules/daily_monitor.py
```

### 生成分析報告
```bash
cd ~/.openclaw/skills/hk-stock-monitor
python3 modules/generate_report.py
```

## 設置定時任務（Cron）

每日收盤後（17:00）自動運行：
```bash
# 編輯 crontab
crontab -e

# 添加以下行（香港時間17:05運行）
5 17 * * 1-5 cd ~/.openclaw/skills/hk-stock-monitor && python3 modules/daily_monitor.py >> logs/monitor.log 2>&1
```

## 數據存儲
- 原始數據：`data/YYYY-MM-DD.json`
- 分析報告：`reports/YYYY-MM-DD.md`

## 數據源
- Yahoo Finance（免費，15分鐘延遲）
