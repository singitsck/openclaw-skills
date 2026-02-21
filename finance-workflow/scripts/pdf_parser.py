#!/usr/bin/env python3
"""
PDF 月結單解析器 - 支援 HSBC / 中銀 BOC
PDF Statement Parser - Supports HSBC / BOC
"""

import pdfplumber
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class StatementParser:
    """銀行月結單解析器基類"""
    
    def __init__(self, bank_name: str):
        self.bank_name = bank_name.lower()
    
    def parse(self, pdf_path: str) -> List[Dict]:
        """解析 PDF，返回交易列表"""
        raise NotImplementedError
    
    def extract_date(self, date_str: str, year: int = None) -> str:
        """標準化日期格式為 YYYY-MM-DD"""
        if year is None:
            year = datetime.now().year
        
        # 嘗試多種格式
        patterns = [
            (r'(\d{1,2})\s*([A-Za-z]{3})\s*(\d{2,4})?', '%d %b %Y'),  # 15 Jan 2026
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', '%Y/%m/%d'),           # 2026/01/15
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%d/%m/%Y'),           # 15/01/2026
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', '%d-%m-%Y'),           # 15-01-2026
        ]
        
        for pattern, fmt in patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if len(match.groups()) == 3 and match.group(3):
                        parsed = datetime.strptime(match.group(0), fmt)
                        return parsed.strftime('%Y-%m-%d')
                    elif len(match.groups()) == 2:
                        # 只有日/月，使用預設年份
                        day, month = int(match.group(1)), match.group(2)
                        parsed = datetime.strptime(f"{day} {month} {year}", '%d %b %Y')
                        return parsed.strftime('%Y-%m-%d')
                except:
                    continue
        
        return date_str  # 返回原始值如果無法解析
    
    def parse_amount(self, amount_str: str) -> float:
        """解析金額，處理貨幣符號和千分位"""
        if not amount_str:
            return 0.0
        
        # 移除貨幣符號和千分位逗號
        cleaned = re.sub(r'[^\d.-]', '', amount_str.replace(',', ''))
        try:
            return float(cleaned)
        except:
            return 0.0


class HSBCParser(StatementParser):
    """HSBC 月結單解析器"""
    
    def __init__(self):
        super().__init__('hsbc')
    
    def parse(self, pdf_path: str) -> List[Dict]:
        """解析 HSBC PDF 月結單"""
        transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 HSBC PDF 共 {len(pdf.pages)} 頁")
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                
                # HSBC 格式：日期 | 描述 | 提款 | 存款 | 結餘
                # 嘗試提取表格
                tables = page.extract_tables()
                
                for table in tables:
                    for row in table:
                        if not row or len(row) < 3:
                            continue
                        
                        # 檢查是否為交易行
                        txn = self._parse_row(row)
                        if txn:
                            txn['bank'] = 'hsbc'
                            transactions.append(txn)
                
                # 如果表格提取失敗，嘗試正則解析
                if not tables:
                    transactions.extend(self._parse_text(text))
        
        print(f"✅ HSBC: 提取 {len(transactions)} 筆交易")
        return transactions
    
    def _parse_row(self, row: List[str]) -> Optional[Dict]:
        """解析表格行"""
        # 過濾表頭
        if any(keyword in ' '.join(row).upper() for keyword in ['DATE', 'DESCRIPTION', 'WITHDRAWAL', 'DEPOSIT']):
            return None
        
        # 嘗試識別日期列
        date_pattern = r'\d{1,2}\s+[A-Za-z]{3}'
        date_str = None
        description = None
        withdrawal = None
        deposit = None
        
        for cell in row:
            if not cell:
                continue
            
            # 尋找日期
            if re.match(date_pattern, cell.strip()):
                date_str = cell.strip()
            # 尋找金額（提款/存款）
            elif re.search(r'\d{1,3}(,\d{3})*\.\d{2}', cell):
                if withdrawal is None:
                    withdrawal = cell.strip()
                elif deposit is None:
                    deposit = cell.strip()
            # 其他為描述
            elif len(cell.strip()) > 5:
                description = cell.strip()
        
        if not date_str:
            return None
        
        # 計算金額
        amount = 0.0
        if withdrawal and withdrawal != '-':
            amount = -self.parse_amount(withdrawal)
        elif deposit and deposit != '-':
            amount = self.parse_amount(deposit)
        
        if amount == 0.0:
            return None
        
        return {
            'date': self.extract_date(date_str),
            'description': description or 'HSBC Transaction',
            'amount': amount,
            'currency': 'HKD',
            'category': self._categorize(description or ''),
        }
    
    def _parse_text(self, text: str) -> List[Dict]:
        """正則解析文本（備用方案）"""
        transactions = []
        
        # HSBC 常見格式
        lines = text.split('\n')
        for line in lines:
            # 嘗試匹配: 日期 描述 金額
            # 例如: "15 Jan GROCERY STORE 150.00"
            pattern = r'(\d{1,2}\s+[A-Za-z]{3})\s+(.+?)\s+([\d,]+\.\d{2})'
            match = re.search(pattern, line)
            
            if match:
                date_str, desc, amt_str = match.groups()
                amount = self.parse_amount(amt_str)
                
                # 判斷是收入還是支出（根據上下文）
                if 'PAYMENT' in line.upper() or 'DEPOSIT' in line.upper():
                    amount = abs(amount)
                else:
                    amount = -abs(amount)
                
                transactions.append({
                    'date': self.extract_date(date_str),
                    'description': desc.strip(),
                    'amount': amount,
                    'currency': 'HKD',
                    'category': self._categorize(desc),
                    'bank': 'hsbc'
                })
        
        return transactions
    
    def _categorize(self, description: str) -> str:
        """根據描述自動分類"""
        desc = description.upper()
        categories = {
            'groceries': ['PARKNSHOP', 'WELLCOME', 'GROCERY', 'SUPERMARKET'],
            'dining': ['RESTAURANT', 'CAFE', 'FOOD', 'MCDONALD', 'KFC'],
            'transport': ['MTR', 'TAXI', 'UBER', 'DIDI', 'BUS', 'TRANSPORT'],
            'shopping': ['HKTV', 'SHOP', 'STORE', 'RETAIL'],
            'utilities': ['ELECTRICITY', 'WATER', 'GAS', 'UTILITY'],
            'fees': ['FEE', 'CHARGE', 'INTEREST'],
            'transfer': ['TRANSFER', 'FPS', 'REMITTANCE'],
        }
        
        for category, keywords in categories.items():
            if any(kw in desc for kw in keywords):
                return category
        
        return 'uncategorized'


class BOCParser(StatementParser):
    """中銀 BOC 月結單解析器"""
    
    def __init__(self):
        super().__init__('boc')
    
    def parse(self, pdf_path: str) -> List[Dict]:
        """解析中銀 PDF 月結單"""
        transactions = []
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 BOC PDF 共 {len(pdf.pages)} 頁")
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue
                
                # 提取表格
                tables = page.extract_tables()
                
                for table in tables:
                    for row in table:
                        if not row or len(row) < 3:
                            continue
                        
                        txn = self._parse_row(row)
                        if txn:
                            txn['bank'] = 'boc'
                            transactions.append(txn)
                
                # 備用：正則解析
                if not tables:
                    transactions.extend(self._parse_text(text))
        
        print(f"✅ BOC: 提取 {len(transactions)} 筆交易")
        return transactions
    
    def _parse_row(self, row: List[str]) -> Optional[Dict]:
        """解析中銀表格行"""
        # 中銀格式：日期 | 項目 | 存入/支出 | 結餘
        
        # 過濾表頭
        if any(keyword in ' '.join(row) for keyword in ['日期', '項目', '存入', '支出', '結餘']):
            return None
        
        date_str = None
        description = None
        amount_str = None
        is_expense = True
        
        for i, cell in enumerate(row):
            if not cell:
                continue
            
            cell = cell.strip()
            
            # 日期格式: 2026/01/15 或 15/01/2026
            if re.match(r'\d{4}/\d{2}/\d{2}', cell):
                date_str = cell
            elif re.match(r'\d{2}/\d{2}/\d{4}', cell):
                date_str = cell
            
            # 金額
            elif re.search(r'[\d,]+\.\d{2}', cell):
                amount_str = cell
                # 判斷是存入還是支出（根據列位置或符號）
                if '存入' in str(row) or (i > 0 and '存入' in str(row[i-1:i+1])):
                    is_expense = False
            
            # 描述（最長的文字）
            elif len(cell) > 5 and not re.match(r'\d', cell):
                description = cell
        
        if not date_str or not amount_str:
            return None
        
        amount = self.parse_amount(amount_str)
        if is_expense:
            amount = -abs(amount)
        
        return {
            'date': self.extract_date(date_str),
            'description': description or 'BOC Transaction',
            'amount': amount,
            'currency': 'HKD',
            'category': self._categorize(description or ''),
        }
    
    def _parse_text(self, text: str) -> List[Dict]:
        """正則解析文本（備用方案）"""
        transactions = []
        
        # 中銀常見格式
        lines = text.split('\n')
        for line in lines:
            # 嘗試匹配: 日期 描述 存入/支出
            pattern = r'(\d{4}/\d{2}/\d{2})\s+(.+?)\s+([\d,]+\.\d{2})'
            match = re.search(pattern, line)
            
            if match:
                date_str, desc, amt_str = match.groups()
                amount = self.parse_amount(amt_str)
                
                # 判斷收支
                if any(kw in line for kw in ['存入', '入賬', '轉入']):
                    amount = abs(amount)
                else:
                    amount = -abs(amount)
                
                transactions.append({
                    'date': self.extract_date(date_str),
                    'description': desc.strip(),
                    'amount': amount,
                    'currency': 'HKD',
                    'category': self._categorize(desc),
                    'bank': 'boc'
                })
        
        return transactions
    
    def _categorize(self, description: str) -> str:
        """根據描述自動分類"""
        desc = description.upper()
        
        # 中英混合關鍵詞
        categories = {
            'groceries': ['百佳', '惠康', 'PARKNSHOP', 'WELLCOME', '超市'],
            'dining': ['餐廳', '美食', 'MCDONALD', 'KFC', 'RESTAURANT'],
            'transport': ['港鐵', 'MTR', '的士', 'TAXI', 'UBER'],
            'shopping': ['網購', 'SHOP', 'HKTV'],
            'utilities': ['電費', '水費', '煤氣'],
            'fees': ['手續費', '費用', '利息', 'FEE'],
            'salary': ['糧', '薪金', 'SALARY', 'PAYROLL'],
            'transfer': ['轉賬', '過數', 'FPS'],
        }
        
        for category, keywords in categories.items():
            if any(kw in desc for kw in keywords):
                return category
        
        return 'uncategorized'


def detect_bank(pdf_path: str) -> str:
    """根據 PDF 內容自動識別銀行"""
    with pdfplumber.open(pdf_path) as pdf:
        # 讀取前幾頁文字
        text = ""
        for i, page in enumerate(pdf.pages[:3]):
            page_text = page.extract_text()
            if page_text:
                text += page_text.upper()
        
        # 識別關鍵詞
        if 'HSBC' in text or 'HONG KONG & SHANGHAI' in text or '滙豐' in text:
            return 'hsbc'
        elif 'BANK OF CHINA' in text or '中銀' in text or '中國銀行' in text:
            return 'boc'
        elif 'ZA BANK' in text or 'ZA 銀行' in text:
            return 'zabank'
        elif 'MOX' in text:
            return 'mox'
        elif 'AEON' in text:
            return 'aeon'
    
    return 'unknown'


def parse_statement(pdf_path: str, bank: str = None) -> List[Dict]:
    """
    主入口：解析月結單 PDF
    
    Args:
        pdf_path: PDF 檔案路徑
        bank: 銀行代碼（如 'hsbc', 'boc'），如果不指定會自動識別
    
    Returns:
        交易列表
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 檔案不存在: {pdf_path}")
    
    # 自動識別銀行
    if not bank:
        bank = detect_bank(str(pdf_path))
        print(f"🔍 自動識別銀行: {bank.upper()}")
    
    # 選擇解析器
    parsers = {
        'hsbc': HSBCParser(),
        'boc': BOCParser(),
    }
    
    parser = parsers.get(bank.lower())
    if not parser:
        raise ValueError(f"不支援的銀行: {bank}")
    
    return parser.parse(str(pdf_path))


def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方式:")
        print(f"  python {sys.argv[0]} <pdf_path> [bank]")
        print(f"  python {sys.argv[0]} statement.pdf hsbc")
        print(f"  python {sys.argv[0]} statement.pdf boc")
        return
    
    pdf_path = sys.argv[1]
    bank = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        transactions = parse_statement(pdf_path, bank)
        
        # 輸出 JSON
        output = {
            'pdf_path': pdf_path,
            'bank': bank or detect_bank(pdf_path),
            'transaction_count': len(transactions),
            'transactions': transactions
        }
        
        print("\n" + "="*60)
        print(json.dumps(output, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
