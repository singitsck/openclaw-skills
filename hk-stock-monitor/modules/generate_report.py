#!/usr/bin/env python3
"""
生成每日分析報告
"""
import sys
import os
import json
from datetime import datetime
from typing import Dict

def format_number(num):
    """格式化大數字"""
    if num is None:
        return "N/A"
    if num >= 1e12:
        return f"{num/1e12:.2f}T"
    elif num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif num >= 1e6:
        return f"{num/1e6:.2f}M"
    else:
        return f"{num:,.0f}"

def calculate_technical_analysis(quote: Dict) -> str:
    """簡單技術分析"""
    analysis = []
    
    # 從52週高低點分析位置
    week_low = quote.get('week_52_low')
    week_high = quote.get('week_52_high')
    price = quote.get('price')
    
    if week_low and week_high and price:
        position = (price - week_low) / (week_high - week_low) * 100
        if position > 80:
            analysis.append(f"📊 股價接近52週高位（{position:.1f}%位置）")
        elif position < 20:
            analysis.append(f"📊 股價接近52週低位（{position:.1f}%位置）")
        else:
            analysis.append(f"📊 股價處於52週中間位置（{position:.1f}%位置）")
    
    # 成交量分析
    volume = quote.get('volume')
    if volume:
        if volume > 5000000:
            analysis.append("📈 今日成交量較大")
        elif volume < 1000000:
            analysis.append("📉 今日成交量較小")
    
    return "\n".join(analysis) if analysis else "📊 無明顯技術信號"

def generate_daily_report(quotes: Dict[str, Dict], date_str: str = None) -> str:
    """生成每日分析報告"""
    
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 準備報告路徑
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_file = os.path.join(reports_dir, f"{date_str}.md")
    
    # 生成報告內容
    report_lines = []
    report_lines.append(f"# 📊 港股監控日報 - {date_str}")
    report_lines.append("")
    report_lines.append(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # 市場概覽
    report_lines.append("## 📈 市場概覽")
    report_lines.append("")
    
    up_count = sum(1 for q in quotes.values() if q['change_pct'] > 0)
    down_count = sum(1 for q in quotes.values() if q['change_pct'] < 0)
    
    report_lines.append(f"- 📈 上漲: {up_count} 只")
    report_lines.append(f"- 📉 下跌: {down_count} 只")
    report_lines.append(f"- 📊 持平: {len(quotes) - up_count - down_count} 只")
    report_lines.append("")
    
    # 個股詳情
    report_lines.append("## 📋 個股詳情")
    report_lines.append("")
    
    for i, (code, quote) in enumerate(quotes.items(), 1):
        emoji = "🟢" if quote['change_pct'] > 0 else "🔴" if quote['change_pct'] < 0 else "⚪"
        
        report_lines.append(f"### {i}. {emoji} {code} - {quote['name']}")
        report_lines.append("")
        report_lines.append("| 指標 | 數值 |")
        report_lines.append("|------|------|")
        report_lines.append(f"| **收盤價** | ${quote['price']:.2f} |")
        report_lines.append(f"| **漲跌幅** | {quote['change_pct']:+.2f}% |")
        report_lines.append(f"| **漲跌額** | ${quote['change']:+.2f} |")
        report_lines.append(f"| **開盤價** | ${quote['open']:.2f} |")
        report_lines.append(f"| **最高價** | ${quote['high']:.2f} |")
        report_lines.append(f"| **最低價** | ${quote['low']:.2f} |")
        report_lines.append(f"| **成交量** | {format_number(quote['volume'])} |")
        report_lines.append(f"| **市值** | {format_number(quote['market_cap'])} |")
        report_lines.append(f"| **52週區間** | ${quote.get('week_52_low', 'N/A')} - ${quote.get('week_52_high', 'N/A')} |")
        report_lines.append(f"| **P/E 比率** | {quote.get('pe_ratio') if quote.get('pe_ratio') else 'N/A'} |")
        report_lines.append(f"| **P/B 比率** | {quote.get('pb_ratio') if quote.get('pb_ratio') else 'N/A'} |")
        report_lines.append("")
        
        report_lines.append("**技術分析**:")
        report_lines.append("")
        report_lines.append(calculate_technical_analysis(quote))
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
    
    # 風險提醒
    report_lines.append("## ⚠️ 風險提醒")
    report_lines.append("")
    report_lines.append("1. 數據來自Yahoo Finance，約有15分鐘延遲，僅供參考")
    report_lines.append("2. 本報告不構成任何投資建議")
    report_lines.append("3. 投資有風險，入市需謹慎")
    report_lines.append("")
    
    # 寫入文件
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return report_file

def main():
    """主函數 - 從今日數據生成報告"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    today = datetime.now().strftime("%Y-%m-%d")
    data_file = os.path.join(data_dir, f"{today}.json")
    
    if not os.path.exists(data_file):
        print(f"❌ 找不到今日數據: {data_file}")
        print("請先運行 daily_monitor.py 獲取數據")
        return 1
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    report_path = generate_daily_report(data['stocks'], today)
    print(f"✅ 報告已生成: {report_path}")
    
    # 同時輸出到控制台
    with open(report_path, 'r', encoding='utf-8') as f:
        print("\n" + "="*60)
        print(f.read())
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
