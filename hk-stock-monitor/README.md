# 📊 港股監控助手

監控 2513.HK 和 0100.HK，每日收盤後生成分析報告。

## 📁 目錄結構

```
~/.openclaw/skills/hk-stock-monitor/
├── SKILL.md                 # Skill 定義
├── README.md                # 本文件
├── run_monitor.sh           # 運行腳本
├── modules/
│   ├── data_fetcher.py      # 數據獲取模組
│   ├── daily_monitor.py     # 每日監控主程式
│   └── generate_report.py   # 報告生成器
├── data/                    # 原始數據存儲 (JSON)
├── reports/                 # 分析報告 (Markdown)
└── logs/                    # 運行日誌
```

## 🚀 快速開始

### 1. 手動運行（立即測試）

```bash
cd ~/.openclaw/skills/hk-stock-monitor
./run_monitor.sh
```

或直接使用 Python：
```bash
cd ~/.openclaw/skills/hk-stock-monitor
.venv/bin/python3 modules/daily_monitor.py
```

### 2. 查看報告

```bash
cat ~/.openclaw/skills/hk-stock-monitor/reports/2026-03-02.md
```

### 3. 設置定時任務（自動運行）

編輯 crontab：
```bash
crontab -e
```

添加以下行（週一至週五 17:05 運行）：
```bash
5 17 * * 1-5 cd ~/.openclaw/skills/hk-stock-monitor && ./run_monitor.sh >> logs/cron.log 2>&1
```

## 📊 監控股票

| 代碼 | 公司名稱 |
|------|----------|
| 2513.HK | Knowledge Atlas Tech Joint (知識圖譜科技) |
| 0100.HK | MiniMax Group Inc |

## 📝 報告內容

每日報告包含：
- ✅ 收盤價格和漲跌幅
- ✅ 開高低收數據
- ✅ 成交量和市值
- ✅ 52週高低點位置分析
- ✅ 簡單技術分析

## ⚠️ 重要提醒

1. **數據延遲**：Yahoo Finance 數據約有 15 分鐘延遲
2. **僅供參考**：本工具不構成任何投資建議
3. **投資風險**：股市有風險，投資需謹慎

## 🔧 故障排除

### 如果無法獲取數據

1. 檢查網絡連接
2. 檢查 yfinance 是否安裝：
   ```bash
   cd ~/.openclaw/skills/hk-stock-monitor
   .venv/bin/pip install yfinance pandas
   ```

### 修改監控股票

編輯 `modules/data_fetcher.py`，修改 `WATCHLIST`：
```python
WATCHLIST = ['2513.HK', '0100.HK', '0700.HK']  # 添加或修改
```

## 📜 數據源

- **Yahoo Finance** (免費，15分鐘延遲)

---

*最後更新: 2026-03-02*
