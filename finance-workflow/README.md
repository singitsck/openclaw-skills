# 💰 香港銀行財務自動化 Workflow

## 目錄結構

```
~/.finance/
├── config.json              # Yahoo Mail 設定 (需要手動填寫)
├── scripts/
│   ├── finance_workflow.py  # 主要 workflow 腳本
│   ├── run_monthly.sh       # 每月執行腳本
│   ├── test_workflow.sh     # 測試腳本
│   └── requirements.txt     # Python 依賴
├── raw/                     # 原始 CSV
│   └── YYYY-MM.csv
├── processed/               # 分類後 CSV
│   └── YYYY-MM_classified.csv
├── reports/                 # HTML 報表
│   └── YYYY-MM.html
└── logs/                    # 執行日誌
```

## 設定步驟

### 1️⃣ Yahoo App Password 設定

**⚠️ 重要：Yahoo 已停用普通密碼的 IMAP 存取，必須使用 App Password**

1. 前往 https://login.yahoo.com/account/security
2. 登入 Yahoo 帳號
3. 找到「**Generate app password**」(產生應用程式密碼)
4. 選擇應用類型「**Other**」，輸入名稱「Finance Workflow」
5. 複製生成的 16 位密碼（格式：xxxx xxxx xxxx xxxx）
6. **立即貼到 config.json**

### 2️⃣ 確認 IMAP 已啟用

1. 在 https://login.yahoo.com/account/security
2. 確認「**Allow apps that use less secure sign in**」或 IMAP 存取已啟用

### 3️⃣ 設定 config.json

```bash
cp ~/.finance/config.json.template ~/.finance/config.json
# 編輯 config.json，填入 email 和 app_password
```

config.json 格式：
```json
{
  "email": "your-email@yahoo.com",
  "app_password": "abcd efgh ijkl mnop"
}
```

### 4️⃣ 測試 Workflow

```bash
~/.finance/scripts/test_workflow.sh
```

這會：
- 搜尋 2026-01 的銀行郵件
- 下載 PDF 附件
- 解析交易
- 顯示 CSV 前10行 + 統計草稿

### 5️⃣ 確認測試結果

檢查：
- [ ] CSV 欄位正確（日期、描述、金額、幣別、類型、卡號後四碼）
- [ ] 金額正確無誤
- [ ] 類別分類合理
- [ ] 沒有遺漏重要交易
- [ ] 沒有解析失敗的 PDF

**如有問題**，手動檢查原始 PDF 並調整 `finance_workflow.py` 中的 `extract_transactions_from_text()` 函數。

### 6️⃣ 建立 Cron Job

測試通過後，建立每月自動執行：

```bash
# 每月 5 號 8:30 執行
openclaw gateway cron create \
  --name finance-monthly \
  --schedule "30 8 5 * *" \
  --command "$HOME/.finance/scripts/run_monthly.sh"
```

或使用 crontab：
```bash
# 編輯 crontab
crontab -e

# 加入這行
30 8 5 * * /Users/$USER/.finance/scripts/run_monthly.sh
```

## 手動執行

```bash
# 處理上個月
python3 ~/.finance/scripts/finance_workflow.py

# 處理指定月份
python3 ~/.finance/scripts/finance_workflow.py --month 2026-01

# 僅下載附件
python3 ~/.finance/scripts/finance_workflow.py --month 2026-01 --download-only
```

## 輸出檔案

- **原始 CSV**: `~/.finance/raw/YYYY-MM.csv`
- **分類 CSV**: `~/.finance/processed/YYYY-MM_classified.csv`
- **HTML 報表**: `~/.finance/reports/YYYY-MM.html`
- **Discord 摘要**: `~/.finance/discord_summary_YYYY-MM.txt`

## 故障排除

### PDF 解析失敗
- 檢查 `~/.finance/raw/YYYY-MM/` 下的原始 PDF
- 不同銀行格式不同，可能需要調整正則表達式

### IMAP 連線失敗
- 確認 App Password 正確
- 確認 Yahoo 帳號沒有啟用兩步驟驗證阻擋

### 郵件搜尋不到
- 檢查郵件是否在 Inbox
- 確認郵件標題包含關鍵字（月結單、Statement 等）

## 自訂設定

編輯 `finance_workflow.py` 可調整：
- `BANK_DOMAINS`: 銀行域名列表
- `KEYWORDS`: 搜尋關鍵字
- `CATEGORY_RULES`: 交易分類規則
