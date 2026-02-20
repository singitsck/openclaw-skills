#!/bin/bash
# 測試財務 Workflow（處理 2026-01 並顯示預覽）

set -e

SCRIPT_DIR="$HOME/.finance/scripts"
FINANCE_DIR="$HOME/.finance"

echo "🧪 測試模式: 處理 2026-01 數據"
echo ""

cd "$SCRIPT_DIR"

# Run in test mode (will process and show preview)
python3 finance_workflow.py --month "2026-01" --test 2&1

echo ""
echo "========================================"
echo "✅ 測試完成!"
echo ""
echo "請檢查上述輸出:"
echo "1. CSV 前10行預覽是否正確"
echo "2. 統計數字是否合理"
echo "3. 有沒有解析失敗的 PDF"
echo ""
echo "確認無誤後，執行以下命令建立 cron:"
echo "   openclaw gateway cron create --name finance-monthly --schedule '30 8 5 * *' --command '$HOME/.finance/scripts/run_monthly.sh'"
