#!/usr/bin/env python3
"""
每日監控腳本 - 獲取數據並保存
建議設置為 Cron 定時運行（週一至週五 17:05）
"""
import sys
import os
import json
from datetime import datetime

# 添加模組路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import HKStockDataFetcher

def main():
    """主函數"""
    print(f"\n{'='*60}")
    print(f"港股每日監控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 初始化數據獲取器
    fetcher = HKStockDataFetcher()
    
    # 獲取所有監控股票數據
    quotes = fetcher.get_watchlist_quotes()
    
    if not quotes:
        print("❌ 未能獲取任何股票數據")
        return 1
    
    # 準備保存路徑
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    data_file = os.path.join(data_dir, f"{today}.json")
    
    # 保存數據
    data_to_save = {
        "date": today,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stocks": quotes,
        "count": len(quotes)
    }
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 數據已保存: {data_file}")
    
    # 生成簡要摘要
    print(f"\n{'-'*60}")
    print("今日摘要")
    print(f"{'-'*60}")
    
    for code, quote in quotes.items():
        emoji = "🟢" if quote['change_pct'] > 0 else "🔴" if quote['change_pct'] < 0 else "⚪"
        print(f"{emoji} {code} ({quote['name']})")
        print(f"   收盤價: ${quote['price']}")
        print(f"   漲跌: {quote['change_pct']:+.2f}% (${quote['change']:+.2f})")
        print(f"   成交量: {quote['volume']:,}")
        print()
    
    # 同時生成報告
    print("正在生成詳細報告...")
    try:
        from generate_report import generate_daily_report
        report_path = generate_daily_report(quotes, today)
        print(f"✅ 報告已生成: {report_path}")
    except Exception as e:
        print(f"⚠️ 報告生成失敗: {e}")
    
    print(f"\n{'='*60}")
    print("監控完成")
    print(f"{'='*60}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
