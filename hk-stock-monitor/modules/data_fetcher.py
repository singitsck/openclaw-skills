"""
港股數據獲取器 - Yahoo Finance
"""
import yfinance as yf
import time
import json
from datetime import datetime
from typing import Dict, Optional, List
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HKStockDataFetcher:
    """港股數據獲取器 - 使用 Yahoo Finance（免費）"""
    
    # 監控的股票列表
    WATCHLIST = ['2513.HK', '0100.HK']
    
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 2  # Yahoo Finance 有請求限制，最少間隔2秒
    
    def _rate_limit(self):
        """請求頻率限制，避免被封"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def get_quote(self, stock_code: str) -> Optional[Dict]:
        """
        獲取單只股票行情
        
        Returns:
            {
                "code": "2513.HK",
                "name": "Knowledge Atlas Tech Joint",
                "price": 550.00,
                "change": -170.50,
                "change_pct": -23.65,
                "volume": 1720291,
                "market_cap": 245210000000,
                "week_52_low": 116.1,
                "week_52_high": 725.0,
                "timestamp": "2026-03-02 16:00:00"
            }
        """
        try:
            self._rate_limit()
            ticker = yf.Ticker(stock_code)
            info = ticker.info
            hist = ticker.history(period="5d")  # 獲取5天數據用於計算漲跌
            
            if hist.empty:
                logger.warning(f"{stock_code}: 無歷史數據")
                return None
            
            latest = hist.iloc[-1]
            prev_close = info.get('previousClose', latest['Close'])
            
            change = latest['Close'] - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
            
            return {
                "code": stock_code,
                "name": info.get('longName', info.get('shortName', stock_code)),
                "price": round(latest['Close'], 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "open": round(latest['Open'], 2),
                "high": round(latest['High'], 2),
                "low": round(latest['Low'], 2),
                "volume": int(latest['Volume']),
                "market_cap": info.get('marketCap'),
                "week_52_low": info.get('fiftyTwoWeekLow'),
                "week_52_high": info.get('fiftyTwoWeekHigh'),
                "pe_ratio": info.get('trailingPE'),
                "pb_ratio": info.get('priceToBook'),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            logger.error(f"獲取 {stock_code} 數據失敗: {e}")
            return None
    
    def get_watchlist_quotes(self) -> Dict[str, Dict]:
        """批量獲取監控列表中的所有股票"""
        results = {}
        logger.info(f"開始獲取 {len(self.WATCHLIST)} 只股票數據...")
        
        for code in self.WATCHLIST:
            quote = self.get_quote(code)
            if quote:
                results[code] = quote
                logger.info(f"✅ {code}: ${quote['price']} ({quote['change_pct']:+.2f}%)")
            else:
                logger.error(f"❌ {code}: 獲取失敗")
        
        return results
    
    def get_historical_data(self, stock_code: str, period: str = "1mo") -> List[Dict]:
        """獲取歷史K線數據"""
        try:
            self._rate_limit()
            ticker = yf.Ticker(stock_code)
            hist = ticker.history(period=period)
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume'])
                })
            return data
            
        except Exception as e:
            logger.error(f"獲取 {stock_code} 歷史數據失敗: {e}")
            return []


if __name__ == "__main__":
    # 測試
    fetcher = HKStockDataFetcher()
    quotes = fetcher.get_watchlist_quotes()
    print(json.dumps(quotes, indent=2, ensure_ascii=False))
