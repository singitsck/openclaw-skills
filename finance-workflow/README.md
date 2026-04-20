# 💰 香港銀行財務自動化 Workflow (Hybrid Mode)

混合模式：Email 交易通知 + PDF 月結單合併，生成完整財務報表

## 目錄結構

```
~/.finance/
├── config.json                    # 設定檔案
├── scripts/
│   ├── reconciler.py             # ⭐ 對帳腳本（Email + PDF 合併）
│   ├── pdf_parser.py             # PDF 月結單解析器
│   ├── finance_workflow.py       # 原有 Email workflow
│   ├── sync-to-github.sh         # 自動同步到 GitHub
│   └── ...
├── transactions/                 # Email 抓取的交易記錄
│   └── YYYY-MM-email.json
├── statements/                   # 手動下載的 PDF 月結單
│   └── YYYY-MM/
│       ├── hsbc.pdf
│       └── boc.pdf
├── reconciled/                   # 合併後的完整記錄
│   ├── YYYY-MM-complete.csv
│   └── YYYY-MM-complete.json
└── HYBRID_MODE_GUIDE.md         # 詳細使用指南
```

## 🚀 快速開始

### 1. 每月工作流程

```bash
# Step 1: 日常（自動）
# Email Parser 持續抓取交易通知

# Step 2: 月底（手動 5 分鐘）
# 從各銀行網站下載 PDF 月結單，放到:
# ~/.finance/statements/2026-01/

# Step 3: 執行對帳
python3 ~/.finance/scripts/reconciler.py reconcile 2026-01

# Step 4: 查看報告
python3 ~/.finance/scripts/reconciler.py report 2026-01
```

### 2. 同步到 GitHub

```bash
# 自動同步（手動執行）
~/.finance/scripts/sync-to-github.sh

# 或使用 alias
alias sync-finance='~/.finance/scripts/sync-to-github.sh'
```

## 📊 功能特性

| 功能 | 說明 |
|------|------|
| **智能去重** | 自動識別 Email 和 PDF 中的重複交易 |
| **模糊匹配** | 基於日期+金額+描述相似度合併 |
| **多銀行支援** | HSBC、BOC、ZA Bank、Mox、AEON |
| **自動分類** | 餐飲、交通、購物、轉賬等類別 |
| **iCloud 同步** | 報表自動同步到 iCloud Drive |

## 📈 輸出檔案

執行對帳後生成：

| 檔案 | 位置 | 用途 |
|------|------|------|
| `YYYY-MM-complete.csv` | `~/.finance/reconciled/` | Excel 可開啟 |
| `YYYY-MM-complete.json` | `~/.finance/reconciled/` | 程式讀取 |
| `YYYY-MM-report.txt` | `~/.finance/reconciled/` | 文字報告 |
| `Reports/YYYY-MM/` | `iCloud Drive/Documents/Finance/` | 全設備同步 |

## 🔧 技術細節

### 去重邏輯

```python
# 匹配鍵：日期 + 金額
key = ("2026-01-15", -150.00)

# 描述相似度 >= 30% 視為同一筆
# 合併後標記為 source: "email+pdf"
```

### 支援的銀行

| 銀行 | Email | PDF | 狀態 |
|------|-------|-----|------|
| HSBC | ✅ | ✅ | 可用 |
| BOC | ✅ | ✅ | 可用 |
| ZA Bank | ✅ | ⏳ | 待開發 |
| Mox | ✅ | ⏳ | 待開發 |
| AEON | ✅ | ⏳ | 待開發 |

## 📚 相關文檔

- [HYBRID_MODE_GUIDE.md](./HYBRID_MODE_GUIDE.md) - 詳細使用指南
- [RESEARCH_REPORT.md](./RESEARCH_REPORT.md) - 國際最佳實踐研究

## 📝 更新日誌

### 2026-02-22
- ✨ 新增混合模式對帳系統
- ✨ 新增 PDF 自動解析器（HSBC/BOC）
- ✨ 新增智能去重功能
- ✨ 新增 iCloud 自動同步
- ✨ 新增 GitHub 自動同步腳本

---

**注意**: `.finance/` 目錄包含敏感數據（交易記錄），不應推送到 GitHub。
僅推送通用腳本和文檔到 `openclaw-skills` 倉庫。
