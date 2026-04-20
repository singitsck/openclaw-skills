#!/usr/bin/env python3
"""
Discord Message Formatter - 自動將內容轉換為 Discord 友好格式
"""

import re
import sys

def convert_table_to_list(text):
    """將 Markdown 表格轉換為 Discord 列表"""
    lines = text.split('\n')
    result = []
    in_table = False
    table_data = []
    
    for line in lines:
        # 檢測表格開始
        if '|' in line and not in_table:
            in_table = True
            table_data = []
        
        if in_table:
            if '|' not in line:
                # 表格結束，處理數據
                if len(table_data) >= 2:  # 跳過表頭分隔行
                    headers = [h.strip() for h in table_data[0].split('|') if h.strip()]
                    for row in table_data[2:]:
                        cells = [c.strip() for c in row.split('|') if c.strip()]
                        if cells:
                            row_text = ' — '.join(f'{h}: {c}' for h, c in zip(headers, cells))
                            result.append(f'• {row_text}')
                in_table = False
                result.append(line)
            else:
                # 跳過分隔行 (|---|---|)
                if not re.match(r'^\|[-:\s|]+\|$', line):
                    table_data.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)

def add_discord_emoji(text):
    """為常見狀態添加 emoji"""
    replacements = [
        (r'\b(done|completed|success|ok|正常)\b', '✅'),
        (r'\b(failed|error|fail|失敗|錯誤)\b', '❌'),
        (r'\b(pending|waiting|progress|進行中|等待)\b', '⏳'),
        (r'\b(warning|warn|警告|注意)\b', '⚠️'),
        (r'\b(tip|hint|提示|建議)\b', '💡'),
    ]
    
    for pattern, emoji in replacements:
        text = re.sub(pattern, emoji + r' \1', text, flags=re.IGNORECASE)
    
    return text

def format_for_discord(text):
    """主格式化函數"""
    # 1. 轉換表格
    text = convert_table_to_list(text)
    
    # 2. 添加 emoji
    text = add_discord_emoji(text)
    
    # 3. 確保標題有粗體
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        # 如果是標題行（簡短、大寫開頭），加粗體
        if line.strip() and len(line.strip()) < 50 and line.strip()[0].isupper():
            if not line.startswith('**') and not line.startswith('#'):
                line = f'**{line.strip()}**'
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def check_format_issues(text):
    """檢查格式問題"""
    issues = []
    
    # 檢查表格
    if '|' in text and '\n|' in text:
        issues.append("❌ 發現 Markdown 表格，Discord 會顯示異常")
    
    # 檢查過長行
    for i, line in enumerate(text.split('\n'), 1):
        if len(line) > 100:
            issues.append(f"⚠️ 第 {i} 行過長 ({len(line)} 字符)")
    
    # 檢查 HTML
    if re.search(r'<\w+>', text):
        issues.append("⚠️ 發現 HTML 標籤")
    
    return issues

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: discord-format.py '<message>'")
        print("   or: echo '<message>' | discord-format.py")
        sys.exit(1)
    
    if sys.argv[1] == '-':
        text = sys.stdin.read()
    else:
        text = sys.argv[1]
    
    # 檢查問題
    issues = check_format_issues(text)
    if issues:
        print("⚠️ 格式問題檢測：")
        for issue in issues:
            print(f"  {issue}")
        print()
    
    # 格式化輸出
    formatted = format_for_discord(text)
    print("📱 Discord 格式化結果：")
    print("-" * 40)
    print(formatted)
