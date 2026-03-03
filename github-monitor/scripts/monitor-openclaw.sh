#!/bin/bash
# OpenClaw 官方項目監控腳本

REPO="openclaw/openclaw"
DATA_DIR="$(dirname "$(dirname "$(realpath "$0")")")/data"
LOG_FILE="$(dirname "$(dirname "$(realpath "$0")")")/logs/monitor.log"

# 確保目錄存在
mkdir -p "$DATA_DIR"

# 獲取最新 commit
echo "=== OpenClaw 項目更新監控 - $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 使用 GitHub API 獲取最近5個 commits
curl -s "https://api.github.com/repos/$REPO/commits?per_page=5" | \
python3 -c "
import sys, json
try:
    commits = json.load(sys.stdin)
    print('📌 最近 Commits:')
    print()
    for i, c in enumerate(commits[:5], 1):
        sha = c['sha'][:7]
        msg = c['commit']['message'].split('\n')[0][:60]
        author = c['commit']['author']['name']
        date = c['commit']['author']['date'][:10]
        print(f'{i}. {sha} - {msg}')
        print(f'   作者: {author} | 日期: {date}')
        print()
except Exception as e:
    print(f'獲取失敗: {e}')
" | tee -a "$LOG_FILE"

# 獲取最新 release
echo "📦 最新 Release:" | tee -a "$LOG_FILE"
curl -s "https://api.github.com/repos/$REPO/releases/latest" | \
python3 -c "
import sys, json
try:
    release = json.load(sys.stdin)
    if 'tag_name' in release:
        tag = release['tag_name']
        name = release.get('name', 'N/A')
        date = release.get('published_at', '')[:10]
        print(f'   {tag} - {name}')
        print(f'   發布日期: {date}')
    else:
        print('   暫無 release 信息')
except Exception as e:
    print(f'   獲取失敗: {e}')
" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "🔗 項目地址: https://github.com/$REPO" | tee -a "$LOG_FILE"
echo "📝 完整日誌: $LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
