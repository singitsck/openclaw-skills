# 🤖 Agent 安全行為準則

## ⚠️ CRITICAL: Push 到 GitHub 前必須檢查

### 1. 自動檢查機制

每次執行 `git add` 和 `git commit` 前，雷姆必須：

```python
# 自動檢查函數
def check_sensitive_files(files_to_add):
    """Check if any sensitive files are being added"""
    sensitive_patterns = [
        r'\.csv$',           # CSV files with transaction data
        r'raw/.*',           # Raw email content
        r'config\.json$',    # Config with passwords
        r'.*\.log$',         # Log files
        r'processed/',       # Processed transaction data
        r'reports/.*\.html$', # HTML reports with data
    ]
    
    risky_files = []
    for file in files_to_add:
        for pattern in sensitive_patterns:
            if re.search(pattern, file):
                risky_files.append(file)
    
    return risky_files

# 在 git add 前調用
risky = check_sensitive_files(files)
if risky:
    print("⚠️  WARNING: Detected potentially sensitive files:")
    for f in risky:
        print(f"   - {f}")
    print("\n❌  These files should NOT be pushed to GitHub!")
    print("💡  Add them to .gitignore instead.")
```

### 2. Push 前確認清單

**必須向用戶確認**：

```
💙 主人～準備 Push 到 GitHub，請確認以下內容：

📋 即將 Push 的檔案：
   - finance_workflow.py (程式碼) ✅
   - README.md (文件) ✅
   - config.json.template (模板) ✅

🔒 敏感資料檢查：
   - ❌ 無 CSV 交易報表
   - ❌ 無郵件內容檔案
   - ❌ 無 config.json (含密碼)

請確認無誤後，我再執行 git push～
```

### 3. 禁止的行為

❌ **絕對禁止**：
- 未經檢查直接 `git add .`
- 未確認內容直接 `git commit -m "xxx"`
- 含敏感資料的檔案加入版本控制
- 使用 `git push --force` 除非緊急清理洩漏

✅ **必須做到**：
- 逐個檔案確認內容
- 使用 `git status` 查看變更
- 敏感資料只留在本地 `~/.finance/`
- 模板檔案使用 `.template` 後綴

### 4. 安全資料夾結構

```
~/.finance/           ← 本地資料，絕不 Push
├── raw/              ← 郵件內容
├── processed/        ← CSV 報表
├── reports/          ← HTML 報表
└── config.json       ← 含密碼

~/github-repos/openclaw-skills/  ← 只放程式碼
├── finance-workflow/
│   ├── scripts/      ← Python 腳本 ✅
│   ├── README.md     ← 文件 ✅
│   └── config.json.template  ← 模板 ✅
└── .gitignore        ← 保護敏感資料 ✅
```

## 🚨 緊急處理流程

如果不小心 Push 了敏感資料：

1. **立即停止** - 不要讓更多人 clone
2. **撤銷憑證** - 如果是 API Key/密碼，立即撤銷
3. **清理 History** - 使用 filter-branch
4. **Force Push** - 覆蓋遠端 history
5. **通知用戶** - 報告事件和處理結果

## 📚 參考資源

- [GitHub Docs - Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [AWS git-secrets](https://github.com/awslabs/git-secrets)
- [Git .gitignore documentation](https://git-scm.com/docs/gitignore)
