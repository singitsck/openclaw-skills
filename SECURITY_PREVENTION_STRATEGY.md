# 🛡️ GitHub 敏感資料洩漏防護策略

## 事件回顧

**時間**: 2026-02-20  
**問題**: 不小心將個人財務交易資料（銀行郵件、CSV 報表）Push 到 GitHub  
**影響**: 個人交易記錄、商家名稱、金額等敏感資訊洩漏

---

## 5 層防護機制

### Layer 1: .gitignore（基礎防護）

**作用**: 告訴 Git 哪些檔案不應該追蹤

**關鍵配置**:
```gitignore
# 🔴 絕對不能 Push
raw/           # 郵件內容
*.csv          # 交易報表
config.json    # 含密碼的配置
*.log          # 日誌檔案

# 🟡 謹慎處理
.env           # 環境變數
*.key          # 憑證檔案
```

**狀態**: ✅ 已配置

---

### Layer 2: Pre-commit Hook（自動檢查）

**作用**: 提交前自動檢查敏感資料

**安裝**:
```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**檢查內容**:
- ❌ 港幣/美元金額格式
- ❌ 信用卡相關關鍵字
- ❌ 商家名稱
- ❌ CSV/Log/Raw 檔案類型

**狀態**: ✅ 已創建腳本

---

### Layer 3: Security Checklist（人工檢查）

**作用**: Push 前人工確認

**檢查清單**:
```bash
# 1. 查看即將 Push 的檔案
git status

# 2. 檢查是否有敏感內容
git diff --cached | grep -E "(HKD|USD|信用卡)"

# 3. 確認沒有個人資料
ls -la  # 確認沒有 raw/、*.csv、config.json
```

**狀態**: ✅ 已創建 SECURITY_CHECKLIST.md

---

### Layer 4: git-secrets（進階防護）

**作用**: AWS 推薦的專業密碼防護工具

**安裝**:
```bash
# macOS
brew install git-secrets

# 初始化
git secrets --install
git secrets --add 'HKD\s+\d+'  # 添加財務資料檢查
git secrets --add '信用卡.*\d{4}'
```

**效果**: Commit 時自動阻擋含密碼/金額的提交

**狀態**: 🔄 建議安裝

---

### Layer 5: Agent 行為準則（最後防線）

**作用**: 我的內部安全規範

**準則**:
1. ✅ 逐個檔案確認內容
2. ✅ 使用模板（.template）而非真實配置
3. ✅ Push 前向用戶確認
4. ❌ 絕不使用 `git add .`
5. ❌ 絕不自動 Push 未確認檔案

**狀態**: ✅ 已建立 AGENT_SECURITY_GUIDELINES.md

---

## 📊 防護效果對比

| 防護層 | 自動/人工 | 效果 | 狀態 |
|--------|----------|------|------|
| .gitignore | 自動 | ⭐⭐⭐ | ✅ 已配置 |
| Pre-commit Hook | 自動 | ⭐⭐⭐⭐⭐ | ✅ 已創建 |
| Security Checklist | 人工 | ⭐⭐⭐⭐ | ✅ 已創建 |
| git-secrets | 自動 | ⭐⭐⭐⭐⭐ | 🔄 建議安裝 |
| Agent 準則 | 人工 | ⭐⭐⭐⭐⭐ | ✅ 已建立 |

---

## 🚀 立即執行

### 1. 安裝 Pre-commit Hook
```bash
cd ~/github-repos/openclaw-skills
cp hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### 2. 安裝 git-secrets（可選但推薦）
```bash
brew install git-secrets
git secrets --install
git secrets --add 'HKD\s+\d+'
git secrets --add '信用卡'
```

### 3. 測試防護機制
```bash
# 創建一個測試檔案
echo "HKD 100.00" > test_sensitive.txt
git add test_sensitive.txt
git commit -m "Test"

# 應該看到錯誤：❌ ERROR: Detected sensitive pattern
```

---

## 📚 參考資源

- [GitHub Docs - Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [GitHub Docs - Ignoring files](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files)
- [AWS git-secrets](https://github.com/awslabs/git-secrets)
- [Git .gitignore docs](https://git-scm.com/docs/gitignore)

---

*建立時間*: 2026-02-21  
*建立者*: 雷姆 (OpenClaw Agent)  
*目的*: 防止敏感資料洩漏到 GitHub
