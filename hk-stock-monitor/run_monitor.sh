#!/bin/bash
# 港股監控運行腳本

cd "$(dirname "$0")"

# 使用 venv 中的 Python
VENV_PYTHON="./.venv/bin/python3"

# 運行監控腳本
$VENV_PYTHON modules/daily_monitor.py "$@"
