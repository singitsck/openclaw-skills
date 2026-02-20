# 🛡️ 安全檢查清單 - Push 到 GitHub 前必讀

## Push 前必須檢查（3 秒鐘）

```bash
# 1. 檢查即將 push 的檔案
git status

# 2. 檢查是否有敏感資料
git diff --cached --name-only | xargs grep -l "HKD\|USD\|信用卡\|交易" 2>/dev/null

# 3. 確認沒有個人資料
git diff --cached | grep -E "(HKD|USD|CNY)\s+[0-9]" && echo "⚠️  WARNING: Found currency amounts!"
```

## ❌ 絕對不能 Push 的內容

- [ ] 郵件內容檔案（含銀行通知）
- [ ] CSV 交易報表
- [ ] config.json（含密碼）
- [ ] 日誌檔案（*.log）
- [ ] 任何含「交易金額」的檔案

## ✅ 可以 Push 的內容

- [ ] Python 腳本 (*.py)
- [ ] Shell 腳本 (*.sh)
- [ ] 說明文件 (*.md)
- [ ] 模板檔案（config.json.template）
- [ ] 範例程式（不含真實資料）

## 🔍 快速檢查命令

```bash
# 檢查即將提交的檔案列表
git diff --cached --stat

# 檢查特定檔案內容（確認沒有敏感資料）
git diff --cached filename.txt

# 如果發現敏感資料，從暫存區移除
git reset HEAD filename.txt
```

## 🚨 發現敏感資料已 Push 怎麼辦？

### 立即採取行動：

1. **撤銷憑證**（如果含 API Key/密碼）
2. **清理 Git History**：
   ```bash
   # 使用 filter-branch 清理
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch PATH_TO_FILE' \
     --prune-empty --tag-name-filter cat -- --all
   
   # 強制 push 清理後的 history
   git push origin --force --all
   ```

3. **通知團隊**（如果是協作專案）

## 📞 緊急聯絡

如果發現敏感資料洩漏，立即：
1. 撤銷相關憑證/密碼
2. 清理 Git History
3. 通知相關人員
