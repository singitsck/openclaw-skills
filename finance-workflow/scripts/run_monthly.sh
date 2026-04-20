#!/bin/bash
# 香港銀行財務自動化 Workflow - 每月執行腳本
# 設為每月 5 號 8:30 執行

set -e

SCRIPT_DIR="$HOME/.finance/scripts"
FINANCE_DIR="$HOME/.finance"
LOG_FILE="$FINANCE_DIR/logs/finance-$(date +%Y-%m-%d).log"
DISCORD_CHANNEL="${DISCORD_CHANNEL_ID:-1473609423405580298}"

# Create log directory
mkdir -p "$FINANCE_DIR/logs"

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "========================================"
echo "🏦 財務自動化 Workflow 開始"
echo "⏰ $(date)"
echo "========================================"

# Determine last month
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    LAST_MONTH=$(date -v-1m +%Y-%m)
else
    # Linux
    LAST_MONTH=$(date -d "last month" +%Y-%m)
fi

echo "📅 處理月份: $LAST_MONTH"

# Run workflow
cd "$SCRIPT_DIR"
python3 finance_workflow.py --month "$LAST_MONTH" 2>&1

# Check for errors
if [ $? -ne 0 ]; then
    echo "❌ Workflow 執行失敗"
    # Send alert to Discord if available
    if command -v openclaw &> /dev/null; then
        openclaw message send --channel discord --message "⚠️ 財務 Workflow 失敗！請檢查 $LOG_FILE"
    fi
    exit 1
fi

# Send Discord summary if file exists
DISCORD_MSG_FILE="$FINANCE_DIR/discord_summary_$LAST_MONTH.txt"
if [ -f "$DISCORD_MSG_FILE" ]; then
    echo "📤 發送 Discord 通知..."
    MSG=$(cat "$DISCORD_MSG_FILE")
    # Use openclaw to send message
    # Note: This requires openclaw CLI to be available
fi

echo ""
echo "✅ Workflow 完成: $(date)"
echo "========================================"
