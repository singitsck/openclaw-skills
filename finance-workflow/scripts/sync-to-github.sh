#!/bin/bash
# 自動同步腳本 - 將本地財務工具同步到 GitHub
# Auto-sync script - Sync local finance tools to GitHub

set -e

# 路徑設定
LOCAL_DIR="$HOME/.finance"
REPO_DIR="$HOME/github-repos/openclaw-skills"
REPO_WORKFLOW_DIR="$REPO_DIR/finance-workflow"

echo "🔄 開始同步財務工具到 GitHub..."
echo "=================================="

# 檢查目錄是否存在
if [ ! -d "$LOCAL_DIR" ]; then
    echo "❌ 錯誤: 本地目錄不存在 $LOCAL_DIR"
    exit 1
fi

if [ ! -d "$REPO_DIR" ]; then
    echo "❌ 錯誤: GitHub 倉庫不存在 $REPO_DIR"
    exit 1
fi

# 檔案列表（要同步的檔案）
declare -a FILES_TO_SYNC=(
    "scripts/reconciler.py"
    "scripts/pdf_parser.py"
    "scripts/pdf_helper.sh"
    "HYBRID_MODE_GUIDE.md"
)

# 複製檔案
echo "📁 複製檔案..."
for file in "${FILES_TO_SYNC[@]}"; do
    if [ -f "$LOCAL_DIR/$file" ]; then
        target_dir="$REPO_WORKFLOW_DIR/$(dirname $file)"
        mkdir -p "$target_dir"
        cp "$LOCAL_DIR/$file" "$target_dir/"
        echo "  ✅ $file"
    else
        echo "  ⚠️  跳過（不存在）: $file"
    fi
done

# 進入倉庫目錄
cd "$REPO_DIR"

# 檢查是否有變更
if git diff --quiet && git diff --staged --quiet; then
    echo ""
    echo "✅ 沒有變更，無需同步"
    exit 0
fi

# 顯示變更
echo ""
echo "📊 變更摘要:"
git status --short

# 添加所有變更
echo ""
echo "📝 提交變更..."
git add -A

# 生成提交信息（包含時間戳）
COMMIT_MSG="Update finance workflow - $(date '+%Y-%m-%d %H:%M')

Changes:
$(git diff --cached --name-only | sed 's/^/- /')

Auto-sync from ~/.finance/"

git commit -m "$COMMIT_MSG"

# 推送到 GitHub
echo ""
echo "☁️  推送到 GitHub..."
if git push origin main; then
    echo ""
    echo "✅ 同步完成！"
    echo "   https://github.com/singitsck/openclaw-skills"
else
    echo "❌ 推送失敗"
    exit 1
fi

echo "=================================="
