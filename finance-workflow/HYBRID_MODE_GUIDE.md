# 💰 財務混合模式 - 使用指南

## 📁 目錄結構

```
~/.finance/
├── transactions/          # Email 抓取的交易記錄
│   └── 2026-01-email.json
├── statements/            # 手動下載的 PDF 月結單
│   └── 2026-01/
│       ├── hsbc.pdf
│       ├── boc.pdf
│       └── zabank.pdf
├── reconciled/            # 合併後的完整記錄
│   ├── 2026-01-complete.json
│   ├── 2026-01-complete.csv
│   └── 2026-01-report.txt
└── scripts/
    └── reconciler.py      # 對帳腳本
```

---

## 🔄 每月工作流程

### 第 1 步：日常（自動）

Email Parser 持續運行，自動抓取交易通知：

```bash
# 檢查已抓取的交易
ls -la ~/.finance/transactions/
```

### 第 2 步：月底（手動 5 分鐘）

下載各銀行 PDF 月結單：

| 銀行 | 下載方式 |
|------|----------|
| **HSBC** | 網銀 → 戶口 → 電子結單 |
| **中銀 BOC** | 網銀 → 電子結單服務 |
| **ZA Bank** | App → 戶口 → 月結單 |
| **Mox** | App → 戶口 → 月結單 |
| **AEON** | 網銀 → 電子結單 |

**保存位置**:
```bash
~/.finance/statements/2026-01/
├── hsbc.pdf
├── boc.pdf
├── zabank.pdf
├── mox.pdf
└── aeon.pdf
```

### 第 3 步：PDF 解析（需實現）

目前需要手動將 PDF 轉換為 JSON，格式如下：

```json
[
  {
    "date": "2026-01-15",
    "bank": "hsbc",
    "amount": -150.00,
    "currency": "HKD",
    "description": "SUPERMARKET PURCHASE",
    "category": "groceries"
  }
]
```

### 第 4 步：自動對帳

```bash
# 執行對帳
python3 ~/.finance/scripts/reconciler.py reconcile 2026-01

# 生成月度報告
python3 ~/.finance/scripts/reconciler.py report 2026-01
```

---

## 📊 輸出檔案說明

### 1. `2026-01-complete.json`
合併後的完整交易記錄（JSON 格式）

### 2. `2026-01-complete.csv`
Excel 可開啟的表格格式

欄位：
- `date` - 交易日期
- `bank` - 銀行
- `amount` - 金額（負數為支出）
- `currency` - 貨幣
- `description` - 描述
- `category` - 分類
- `source` - 來源（email / pdf_hsbc 等）
- `id` - 交易唯一 ID

### 3. `2026-01-report.txt`
月度財務報告摘要

---

## 🛠️ 下一步優化

### 優先級 1: PDF 自動解析
使用以下工具實現 PDF 提取：

```python
# 方案 A: pdfplumber
import pdfplumber

with pdfplumber.open("statement.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        # 解析表格數據

# 方案 B: LLM Vision (推薦)
# 使用 Claude/GPT-4V 直接讀取 PDF 圖像
```

### 優先級 2: 自動下載（進階）
部分銀行支援：
- **ZA Bank API** - 可申請 developer account
- **Plaid / Yodlee** - 第三方聚合服務（收費）

### 優先級 3: 報表自動化
- 自動發送月度報告到 Email
- 連接到 Notion / Google Sheets
- 異常支出預警

---

## 💡 常見問題

### Q: Email 和 PDF 記錄有重複怎麼辦？
**A**: 腳本會自動去重，基於 `date + amount + description + bank` 生成唯一 ID

### Q: 如果某筆交易只在 PDF 中出現？
**A**: 會被標記為 `pdf_only`，並補齊到完整記錄中

### Q: 支援哪些銀行？
**A**: 目前架構支援任何銀行，只需：
1. 提供對應的 PDF 解析邏輯
2. 或在 `reconcile()` 中指定銀行列表

---

## 📝 使用範例

```bash
# 初始化
python3 ~/.finance/scripts/reconciler.py setup

# 月底對帳（假設已下載 PDF 並解析為 JSON）
python3 ~/.finance/scripts/reconciler.py reconcile 2026-01

# 查看報告
cat ~/.finance/reconciled/2026-01-report.txt

# 用 Excel 開啟
open ~/.finance/reconciled/2026-01-complete.csv
```

---

*創建時間: 2026-02-22*  
*版本: v1.0*
