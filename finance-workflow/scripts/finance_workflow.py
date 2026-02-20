#!/usr/bin/env python3
"""
香港銀行/信用卡財務自動化 Workflow
處理 Yahoo Mail 的月結單與交易通知
"""

import os
import sys
import imaplib
import email
import email.policy
import re
import csv
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import base64
import tempfile

# Configuration
FINANCE_DIR = Path.home() / ".finance"
RAW_DIR = FINANCE_DIR / "raw"
PROCESSED_DIR = FINANCE_DIR / "processed"
REPORTS_DIR = FINANCE_DIR / "reports"
CONFIG_FILE = FINANCE_DIR / "config.json"

# Bank domains to search
BANK_DOMAINS = [
    # 香港主要銀行
    "@hsbc.com.hk",
    "@notification.hsbc.com.hk",
    "@informationservices.hsbc.com.hk",
    "@citi.com",
    "@standardchartered.com.hk",
    "@dbs.com",
    "@boa.com",
    "@hangseng.com",
    "@bankcomm.com.hk",
    "@icbcasia.com",
    "@boc.com.hk",
    "@bochk.com",
    "@za.group",
    "@mox.com",
    # 日本/亞洲銀行
    "@aeon.com.hk",
    # 支付平台
    "@alipay.com",
    "@mail.alipay.com",
    "@wechatpay.com",
    "@wechat.com",
    "@tenpay.com",
    # 商家交易通知
    "@email.apple.com",
    "@steampowered.com",
]

# Search keywords
KEYWORDS = [
    "月結單", "e-Statement", "對帳單", "電子月結單",
    "Statement", "Transaction Summary", "transaction alert",
    "credit card statement", "銀行月結單",
    "Transaction Alert", "交易提示", "Payment Confirmation",
    "Receipt", "收據", "Purchase", "Order Confirmation",
    "直接扣賬", "Direct Debit", "e-Statement Alert",
    # Alipay / WeChat Pay
    "支付寶", "Alipay", "交易成功", "付款成功",
    "微信支付", "WeChat Pay", "轉賬", "交易完成",
    "消費", "支付成功", "扣款成功"
]

# Category rules
CATEGORY_RULES = {
    "飲食": ["餐廳", "food", "cafe", "麥當勞", "mcdonald", "kfc", "pizza", "starbucks",
            "coffee", "restaurant", "食", "飯", "茶餐廳", "大家樂", "大快活", "美心"],
    "交通": ["mtr", "taxi", "的士", "octopus", "fuel", "petrol", "shell", "esso",
            "mobil", "parking", "停車場", "港鐵", "地鐵", "巴士", "uber"],
    "娛樂購物": ["netflix", "spotify", "apple", "amazon", "淘寶", "taobao",
               "disney", "youtube", "steam", "game", "cinema", "戲院", "電影"],
    "超市": ["超市", "supermarket", "parknshop", "wellcome", "marketplace",
            "360", "jasons", "citysuper"],
    "醫療": ["醫院", "clinic", "doctor", "pharmacy", "萬寧", "mannings",
            "屈臣氏", "watsons", "醫生", "牙醫"],
    "水電煤": ["中電", "clp", "港燈", "hke", "煤氣", "towngas", "寬頻",
             "broadband", "phone bill", "電話費"],
}


def load_config() -> Dict:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config: Dict):
    """Save configuration to file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def connect_imap(email_addr: str, app_password: str) -> imaplib.IMAP4_SSL:
    """Connect to Yahoo Mail via IMAP"""
    print(f"🔗 Connecting to Yahoo Mail IMAP...")
    mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com", 993)
    mail.login(email_addr, app_password)
    print(f"✅ IMAP login successful")
    return mail


def search_bank_emails(mail: imaplib.IMAP4_SSL, since_date: str, before_date: str) -> List[str]:
    """
    Search for bank/credit card emails
    since_date and before_date format: DD-MMM-YYYY
    """
    mail.select("inbox")

    # Build search criteria
    # Yahoo IMAP supports OR and FROM searches
    from_criteria = []
    for domain in BANK_DOMAINS:
        domain_clean = domain.lstrip("@")
        from_criteria.append(f'FROM "{domain_clean}"')

    # Search for emails from bank domains within date range
    # Using SENTSINCE and SENTBEFORE for date filtering
    search_query = f'(SENTSINCE {since_date} SENTBEFORE {before_date})'

    print(f"🔍 Searching: {search_query}")
    status, messages = mail.search(None, search_query)

    if status != "OK":
        print(f"⚠️ Search failed: {status}")
        return []

    email_ids = messages[0].decode().split()
    print(f"📧 Found {len(email_ids)} emails from bank domains")
    return email_ids


def filter_by_keywords(mail: imaplib.IMAP4_SSL, email_ids: List[str]) -> List[Tuple[str, Dict]]:
    """Filter emails by subject/body keywords"""
    matching = []

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1], policy=email.policy.default)
        subject = msg["Subject"] or ""

        # Check if subject contains any keyword
        subject_lower = subject.lower()
        for keyword in KEYWORDS:
            if keyword.lower() in subject_lower:
                matching.append((eid, {
                    "subject": subject,
                    "from": msg["From"],
                    "date": msg["Date"],
                    "keyword_matched": keyword
                }))
                break

    print(f"🎯 {len(matching)} emails match keywords")
    return matching


def extract_email_content(msg) -> str:
    """Extract text content from email (HTML or plain text)"""
    content = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
                
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        content += payload.decode(charset, errors="ignore") + "\n"
                except:
                    pass
            elif content_type == "text/html":
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        html = payload.decode(charset, errors="ignore")
                        # Simple HTML to text conversion
                        text = re.sub(r'<[^>]+>', ' ', html)
                        text = re.sub(r'\s+', ' ', text)
                        content += text + "\n"
                except:
                    pass
    else:
        # Single part email
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                content = payload.decode(charset, errors="ignore")
                if msg.get_content_type() == "text/html":
                    content = re.sub(r'<[^>]+>', ' ', content)
                    content = re.sub(r'\s+', ' ', content)
        except:
            pass
    
    return content


def download_attachments(mail: imaplib.IMAP4_SSL, email_ids: List[str], download_dir: Path) -> List[Path]:
    """Download PDF attachments from emails"""
    downloaded = []

    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(msg_data[0][1], policy=email.policy.default)
        subject = msg["Subject"] or "No Subject"
        date_str = msg["Date"] or ""

        # Clean subject for filename
        clean_subject = re.sub(r'[^\w\s-]', '', subject)[:50].strip()

        has_pdf_attachment = False
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if content_type == "application/pdf" or "attachment" in content_disposition:
                    has_pdf_attachment = True
                    filename = part.get_filename()
                    if not filename:
                        # Generate filename from subject
                        filename = f"{clean_subject}_{eid}.pdf"

                    # Ensure .pdf extension
                    if not filename.lower().endswith(".pdf"):
                        filename += ".pdf"

                    filepath = download_dir / filename

                    # Handle duplicates
                    counter = 1
                    original_filepath = filepath
                    while filepath.exists():
                        stem = original_filepath.stem
                        filepath = download_dir / f"{stem}_{counter}.pdf"
                        counter += 1

                    payload = part.get_payload(decode=True)
                    if payload:
                        with open(filepath, "wb") as f:
                            f.write(payload)
                        downloaded.append(filepath)
                        print(f"  ⬇️ Downloaded PDF: {filepath.name}")

        # If no PDF attachment, save the email content as text for parsing
        if not has_pdf_attachment:
            content = extract_email_content(msg)
            if content.strip():
                txt_filename = f"{clean_subject}_{eid}.txt"
                txt_path = download_dir / txt_filename
                counter = 1
                while txt_path.exists():
                    txt_path = download_dir / f"{clean_subject}_{eid}_{counter}.txt"
                    counter += 1
                
                # Save content with metadata header
                email_date = msg["Date"] or ""
                from_addr = msg["From"] or ""
                email_metadata = f"EMAIL_METADATA\nDate: {email_date}\nFrom: {from_addr}\nSubject: {subject}\n===CONTENT===\n"
                
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(email_metadata + content)
                downloaded.append(txt_path)
                print(f"  💾 Saved email content: {txt_path.name}")

    return downloaded


def parse_content_to_text(file_path: Path) -> Tuple[str, str]:
    """Extract text from PDF or read text file, return content and email date"""
    email_date = ""
    
    if file_path.suffix.lower() == '.txt':
        # Read text file directly
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract email date from metadata if present
        if content.startswith("EMAIL_METADATA"):
            date_match = re.search(r'Date:\s*(.+?)\n', content)
            if date_match:
                email_date = date_match.group(1).strip()
            # Remove metadata header for parsing
            content = re.sub(r'^EMAIL_METADATA[\s\S]*?===CONTENT===\n', '', content)
        
        return content, email_date
    
    # Parse PDF
    try:
        # Try pdfplumber first (better for tables)
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text, ""
    except ImportError:
        # Fallback to pdftotext (poppler)
        result = subprocess.run(
            ["pdftotext", "-layout", str(file_path), "-"],
            capture_output=True,
            text=True
        )
        return result.stdout, ""


def extract_transactions_from_text(text: str, source_file: str, email_date: str = "") -> List[Dict]:
    """
    Extract transactions from text content
    Supports various HK bank formats including BOC, ZA Bank, etc.
    """
    transactions = []
    
    # Parse email date if available
    parsed_date = "2026-01-15"  # Default
    if email_date:
        try:
            # Try to parse various date formats
            # Example: "Fri, 10 Jan 2026 08:30:00 +0000"
            date_match = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', email_date)
            if date_match:
                day, month_str, year = date_match.groups()
                months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                         'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
                month = months.get(month_str, '01')
                parsed_date = f"{year}-{month}-{day.zfill(2)}"
        except:
            pass
    
    # === BOC (中銀信用卡) Format ===
    # Pattern: 商戶名稱：XXXX 交易金額：HKD/USD XX.XX
    boc_patterns = [
        # Chinese format
        r'商戶名稱[：:]\s*([^\n]+?)\s*交易金額[：:]\s*(HKD|USD)\s*([\d.]+)',
        # English format
        r'Merchant Name[：:]\s*([^\n]+?)\s*Transaction Amount[：:]\s*(HKD|USD)\s*([\d.]+)',
    ]
    
    for pattern in boc_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            merchant = match.group(1).strip()
            currency = match.group(2).upper()
            amount_str = match.group(3)
            
            try:
                amount = float(amount_str)
                # Create transaction key to avoid duplicates
                tx_key = f"{merchant}_{amount}_{currency}"
                if any(tx.get('_key') == tx_key for tx in transactions):
                    continue
                    
                tx = {
                    "日期": parsed_date,
                    "描述": merchant[:80],
                    "金額": amount,
                    "幣別": currency,
                    "類型": "支出",
                    "卡號後四碼": "",
                    "來源檔案": source_file,
                    "_key": tx_key  # Temporary key for deduplication
                }
                transactions.append(tx)
            except (ValueError, IndexError):
                continue
    
    # Remove temporary keys
    for tx in transactions:
        tx.pop('_key', None)
    
    # === BOC Transaction Notification Format ===
    # Alternative format with more details
    boc_alt_pattern = r'您的中銀信用卡賬戶已完成直接扣帳交易.*?詳情如下[：:]\s*商戶名稱[：:]\s*([^\n]+?)\s*交易金額[：:]\s*(HKD|USD)([\d.]+)'
    match = re.search(boc_alt_pattern, text, re.DOTALL | re.IGNORECASE)
    if match and not transactions:  # Only if no transactions found yet
        merchant = match.group(1).strip()
        currency = match.group(2).upper()
        amount_str = match.group(3)
        try:
            amount = float(amount_str)
            transactions.append({
                "日期": parsed_date,
                "描述": merchant[:80],
                "金額": amount,
                "幣別": currency,
                "類型": "支出",
                "卡號後四碼": "",
                "來源檔案": source_file
            })
        except ValueError:
            pass
    
    # === HSBC Hong Kong Format ===
    # HSBC transaction alerts
    if 'hsbc' in source_file.lower():
        # Look for HKD/USD amounts
        hsbc_amount_pattern = r'(HKD|USD)\s*([\d,]+\.\d{2})'
        matches = re.finditer(hsbc_amount_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                currency = match.group(1).upper()
                amount_str = match.group(2).replace(',', '')
                amount = float(amount_str)
                
                # Try to find merchant
                merchant = "Transaction"
                # Look for merchant in nearby text
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                nearby = text[start:end]
                
                # Common patterns for merchant
                merchant_patterns = [
                    r'(?:at|to|merchant|payee)[\s:]+([^\n,]{2,40})',
                    r'(?:from|via)[\s:]+([^\n,]{2,40})',
                ]
                for mp in merchant_patterns:
                    mm = re.search(mp, nearby, re.IGNORECASE)
                    if mm:
                        merchant = mm.group(1).strip()
                        break
                
                tx = {
                    "日期": parsed_date,
                    "描述": f"HSBC: {merchant[:70]}",
                    "金額": amount,
                    "幣別": currency,
                    "類型": "支出",
                    "卡號後四碼": "",
                    "來源檔案": source_file
                }
                if not any(t.get('描述') == tx['描述'] and t.get('金額') == tx['金額'] for t in transactions):
                    transactions.append(tx)
            except (ValueError, IndexError):
                continue
    
    # === Alipay (支付寶) Format ===
    # Alipay transaction notifications
    if 'alipay' in source_file.lower() or 'alipay.com' in text.lower() or '支付寶' in text:
        alipay_patterns = [
            # Chinese format: 交易金額：HKD 100.00
            r'(?:交易|付款|支付)(?:金額|金额)[：:]\s*(?:HKD|USD|CNY|RMB)?\s*([\d,]+\.\d{2})',
            # Alternative: HKD 100.00 元
            r'(?:HKD|USD|CNY|RMB)\s*([\d,]+\.\d{2})\s*(?:元)?',
        ]
        
        for pattern in alipay_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    # Detect currency
                    currency = "HKD"  # Default for HK
                    if "USD" in text[:match.start()]:
                        currency = "USD"
                    elif "CNY" in text[:match.start()] or "RMB" in text[:match.start()]:
                        currency = "CNY"
                    
                    # Extract merchant/product
                    merchant = "Alipay Payment"
                    # Look for merchant patterns
                    merchant_patterns = [
                        r'(?:商家|商戶|商戶名稱|收款方)[：:]\s*([^\n,]{2,40})',
                        r'(?:商品描述|商品|描述)[：:]\s*([^\n,]{2,40})',
                        r'(?:付款給|支付給|轉賬給)\s*([^\n,]{2,40})',
                    ]
                    for mp in merchant_patterns:
                        mm = re.search(mp, text)
                        if mm:
                            merchant = mm.group(1).strip()
                            break
                    
                    tx = {
                        "日期": parsed_date,
                        "描述": f"Alipay: {merchant[:70]}",
                        "金額": amount,
                        "幣別": currency,
                        "類型": "支出",
                        "卡號後四碼": "",
                        "來源檔案": source_file
                    }
                    if not any(t.get('描述') == tx['描述'] and t.get('金額') == tx['金額'] for t in transactions):
                        transactions.append(tx)
                except (ValueError, IndexError):
                    continue
    
    # === WeChat Pay (微信支付) Format ===
    # WeChat Pay transaction notifications
    if 'wechat' in source_file.lower() or 'wechatpay' in text.lower() or '微信支付' in text:
        wechat_patterns = [
            # Chinese format: 支付金額：HKD 50.00
            r'(?:支付|付款|轉賬|消費)(?:金額|金额)[：:]\s*(?:HKD|USD|CNY|RMB)?\s*([\d,]+\.\d{2})',
            # Alternative: 金額 HKD 50.00
            r'(?:金額|金额)[：:]\s*(?:HKD|USD|CNY|RMB)?\s*([\d,]+\.\d{2})',
            # Simple: HKD 50.00
            r'(?:HKD|USD|CNY|RMB)\s*([\d,]+\.\d{2})',
        ]
        
        for pattern in wechat_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    # Detect currency
                    currency = "HKD"
                    if "USD" in text[max(0, match.start()-20):match.start()]:
                        currency = "USD"
                    elif "CNY" in text[max(0, match.start()-20):match.start()] or "RMB" in text[max(0, match.start()-20):match.start()]:
                        currency = "CNY"
                    
                    # Extract merchant
                    merchant = "WeChat Pay"
                    # Look for merchant/store patterns
                    merchant_patterns = [
                        r'(?:商家|商戶|商戶名稱|收款方|商舗)[：:]\s*([^\n,]{2,40})',
                        r'(?:商品|描述|備註)[：:]\s*([^\n,]{2,40})',
                        r'(?:付款給|支付給|轉賬給|掃碼支付)\s*([^\n,]{2,40})',
                    ]
                    for mp in merchant_patterns:
                        mm = re.search(mp, text)
                        if mm:
                            merchant = mm.group(1).strip()
                            break
                    
                    # Check if it's a transfer (轉賬) vs payment
                    tx_type = "支出"
                    if any(kw in text for kw in ['轉賬', '轉賬', '紅包', '收到']):
                        if '收到' in text or '轉入' in text:
                            tx_type = "收入"
                    
                    tx = {
                        "日期": parsed_date,
                        "描述": f"WeChat Pay: {merchant[:70]}",
                        "金額": amount,
                        "幣別": currency,
                        "類型": tx_type,
                        "卡號後四碼": "",
                        "來源檔案": source_file
                    }
                    if not any(t.get('描述') == tx['描述'] and t.get('金額') == tx['金額'] for t in transactions):
                        transactions.append(tx)
                except (ValueError, IndexError):
                    continue
    
    # === Apple Receipt Format ===
    # Apple receipts and billing emails (skip if already extracted by BOC)
    is_boc_email = 'boc' in source_file.lower() or '中銀' in source_file.lower() or '商戶名稱' in text
    if ('apple' in source_file.lower() or 'apple.com' in text.lower() or 'apple.com/bill' in text.lower()) and not is_boc_email:
        # Look for amount patterns
        apple_amount_pattern = r'(HKD|USD|US\$)\s*([\d,]+\.\d{2})'
        match = re.search(apple_amount_pattern, text, re.IGNORECASE)
        if match:
            try:
                currency = match.group(1).upper().replace('US$', 'USD')
                amount_str = match.group(2).replace(',', '')
                amount = float(amount_str)
                
                # Determine product
                product = "Purchase"
                # Check for subscription keywords
                if any(kw in text.lower() for kw in ['subscription', '訂閱', 'icloud', 'apple music', 'apple tv', 'apple one']):
                    product = "Subscription"
                
                # Try to find specific product name
                product_match = re.search(r'(?:for|product|item|app|game)[\s:]+([^\n,]{2,50}?)(?:\n|$|,)', text, re.IGNORECASE)
                if product_match:
                    product = product_match.group(1).strip()[:50]
                
                tx = {
                    "日期": parsed_date,
                    "描述": f"Apple: {product[:70]}",
                    "金額": amount,
                    "幣別": currency if currency != 'US$' else 'USD',
                    "類型": "支出",
                    "卡號後四碼": "",
                    "來源檔案": source_file
                }
                if not any(t.get('描述') == tx['描述'] and t.get('金額') == tx['金額'] for t in transactions):
                    transactions.append(tx)
            except (ValueError, IndexError):
                pass  # Skip on error, no loop to continue
    
    # === Steam Purchase Format ===
    # Steam emails have "Purchase Confirmation" and game names
    if "steampowered.com" in text.lower() or "steam" in source_file.lower():
        steam_patterns = [
            r'(?:Total|總計)[：:]\s*(?:HKD|USD|US\$)?\s*([\d.]+)',
            r'(?:HKD|USD|US\$)\s*([\d.]+)\s+(?:Total|總計)',
        ]
        
        for pattern in steam_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    # Extract game/app name
                    game_match = re.search(r'(?:遊戲|Game|Item)[：:]\s*([^\n]{2,50})', text, re.IGNORECASE)
                    game = game_match.group(1).strip() if game_match else "Steam Purchase"
                    
                    tx = {
                        "日期": parsed_date,
                        "描述": f"Steam: {game[:70]}",
                        "金額": amount,
                        "幣別": "HKD",
                        "類型": "支出",
                        "卡號後四碼": "",
                        "來源檔案": source_file
                    }
                    if not any(t['描述'] == tx['描述'] and t['金額'] == tx['金額'] for t in transactions):
                        transactions.append(tx)
                    break  # Only take first match for Steam
                except (ValueError, IndexError):
                    continue
    
    # === AEON Credit Card Format ===
    # AEON transaction notifications
    aeon_patterns = [
        r'(?:商戶|Merchant)[：:]\s*([^\n]{2,40})[^\n]*(?:金額|Amount)[：:]\s*(?:HKD)?\s*([\d,]+\.\d{2})',
        r'(?:AEON|aeon)[^\n]*(?:HKD)\s*([\d,]+\.\d{2})[^\n]*(?:at|@)\s*([^\n]{2,40})',
    ]
    
    for pattern in aeon_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                # Pattern may have groups in different order
                group1 = match.group(1).strip()
                group2 = match.group(2).replace(',', '')
                
                # Determine which is amount and which is merchant
                try:
                    amount = float(group2)
                    merchant = group1
                except ValueError:
                    amount = float(group1.replace(',', ''))
                    merchant = group2
                
                tx = {
                    "日期": parsed_date,
                    "描述": f"AEON: {merchant[:70]}",
                    "金額": amount,
                    "幣別": "HKD",
                    "類型": "支出",
                    "卡號後四碼": "",
                    "來源檔案": source_file
                }
                if not any(t['描述'] == tx['描述'] and t['金額'] == tx['金額'] for t in transactions):
                    transactions.append(tx)
            except (ValueError, IndexError):
                continue
    
    # === ZA Bank / Statement Table Format ===
    # Look for table-like transaction data
    za_patterns = [
        r'(\d{4}-\d{2}-\d{2})\s+([\u4e00-\u9fa5\w\s./@-]+?)\s+(-?[\d,]+\.\d{2})',
        r'(\d{2}/\d{2}/\d{4})\s+([\u4e00-\u9fa5\w\s./@-]+?)\s+(-?[\d,]+\.\d{2})',
    ]
    
    for pattern in za_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            try:
                date_str = match.group(1)
                desc = match.group(2).strip()
                amount_str = match.group(3).replace(',', '')
                
                # Determine if credit or debit
                is_debit = '-' in amount_str or any(x in desc.lower() for x in ['支出', 'debit', '付款'])
                amount = float(amount_str.replace('-', ''))
                
                # Standardize date format
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts[2]) == 4:  # DD/MM/YYYY
                        date_str = f"{parts[2]}-{parts[1]}-{parts[0]}"
                
                transactions.append({
                    "日期": date_str,
                    "描述": desc[:80],
                    "金額": amount,
                    "幣別": "HKD",
                    "類型": "支出" if is_debit else "收入",
                    "卡號後四碼": "",
                    "來源檔案": source_file
                })
            except (ValueError, IndexError):
                continue
    
    return transactions


def categorize_transaction(description: str) -> str:
    """Categorize transaction based on description"""
    desc_lower = description.lower()

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword.lower() in desc_lower:
                return category

    return "待確認"


def detect_subscriptions(transactions: List[Dict]) -> List[Dict]:
    """Detect potential subscriptions (same amount + description pattern)"""
    # Group by amount and similar description
    amount_groups = {}
    for tx in transactions:
        key = (round(tx["金額"], 2), tx["描述"][:15].lower())
        if key not in amount_groups:
            amount_groups[key] = []
        amount_groups[key].append(tx)

    subscriptions = []
    for key, txs in amount_groups.items():
        if len(txs) >= 2:  # Same amount appears multiple times
            subscriptions.append({
                "描述": txs[0]["描述"][:30],
                "金額": key[0],
                "出現次數": len(txs),
                "類型": "潛在訂閱"
            })

    return subscriptions


def generate_csv(transactions: List[Dict], output_path: Path):
    """Generate CSV file from transactions"""
    if not transactions:
        print(f"⚠️ No transactions to write")
        return

    # Add category
    for tx in transactions:
        tx["類別"] = categorize_transaction(tx["描述"])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
        writer.writeheader()
        writer.writerows(transactions)

    print(f"💾 CSV saved: {output_path}")


def generate_statistics(transactions: List[Dict]) -> Dict:
    """Generate financial statistics"""
    if not transactions:
        return {}

    income = [tx for tx in transactions if tx["類型"] == "收入"]
    expense = [tx for tx in transactions if tx["類型"] == "支出"]

    total_income = sum(tx["金額"] for tx in income)
    total_expense = sum(tx["金額"] for tx in expense)

    # Category breakdown
    categories = {}
    for tx in expense:
        cat = tx.get("類別", "待確認")
        categories[cat] = categories.get(cat, 0) + tx["金額"]

    # Top 5 expenses
    top_expenses = sorted(expense, key=lambda x: x["金額"], reverse=True)[:5]

    # Subscriptions
    subscriptions = detect_subscriptions(transactions)

    return {
        "總收入": total_income,
        "總支出": total_expense,
        "淨額": total_income - total_expense,
        "交易筆數": len(transactions),
        "收入筆數": len(income),
        "支出筆數": len(expense),
        "類別分布": categories,
        "最大支出Top5": [
            {"描述": tx["描述"][:40], "金額": tx["金額"], "日期": tx["日期"]}
            for tx in top_expenses
        ],
        "潛在訂閱": subscriptions
    }


def generate_html_report(transactions: List[Dict], stats: Dict, month: str, output_path: Path):
    """Generate HTML report with simple charts"""

    # Category colors
    colors = {
        "飲食": "#FF6B6B",
        "交通": "#4ECDC4",
        "娛樂購物": "#45B7D1",
        "超市": "#96CEB4",
        "醫療": "#FFEAA7",
        "水電煤": "#DDA0DD",
        "待確認": "#B2BEC3"
    }

    # Build category chart data
    cat_data = stats.get("類別分布", {})
    cat_labels = json.dumps(list(cat_data.keys()))
    cat_values = json.dumps(list(cat_data.values()))
    cat_colors = json.dumps([colors.get(k, "#B2BEC3") for k in cat_data.keys()])

    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>財務報表 {month}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}
        .summary-item {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        .summary-item.Expense {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .summary-item.Income {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .summary-item.Net {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }}
        .summary-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        .summary-value {{
            font-size: 1.8em;
            font-weight: bold;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .amount-expense {{ color: #e74c3c; }}
        .amount-income {{ color: #27ae60; }}
        .alert {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px 16px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .alert-warning {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        .category-tag {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 {month} 財務報表</h1>

        <div class="card">
            <h2>📊 收支摘要</h2>
            <div class="summary-grid">
                <div class="summary-item Income">
                    <div class="summary-label">總收入</div>
                    <div class="summary-value">${stats.get('總收入', 0):,.2f}</div>
                </div>
                <div class="summary-item Expense">
                    <div class="summary-label">總支出</div>
                    <div class="summary-value">${stats.get('總支出', 0):,.2f}</div>
                </div>
                <div class="summary-item Net">
                    <div class="summary-label">淨額</div>
                    <div class="summary-value">${stats.get('淨額', 0):,.2f}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">交易筆數</div>
                    <div class="summary-value">{stats.get('交易筆數', 0)}</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📈 支出類別分布</h2>
            <div class="chart-container">
                <canvas id="categoryChart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>🔥 最大支出 Top 5</h2>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>描述</th>
                        <th>金額</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f"<tr><td>{tx['日期']}</td><td>{tx['描述']}</td><td class='amount-expense'>${tx['金額']:,.2f}</td></tr>" for tx in stats.get('最大支出Top5', []))}
                </tbody>
            </table>
        </div>
"""

    # Add subscriptions alert if any
    subs = stats.get("潛在訂閱", [])
    if subs:
        html += """
        <div class="card">
            <h2>⚠️ 潛在重複訂閱</h2>
"""
        for sub in subs:
            html += f"""
            <div class="alert alert-warning">
                <strong>{sub['描述']}</strong> - ${sub['金額']:,.2f} (出現 {sub['出現次數']} 次)
            </div>
"""
        html += "</div>"

    html += f"""
        <div class="card">
            <h2>📝 交易明細</h2>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>描述</th>
                        <th>類別</th>
                        <th>類型</th>
                        <th>金額</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f"<tr><td>{tx['日期']}</td><td>{tx['描述']}</td><td><span class='category-tag' style='background:{colors.get(tx.get('類別','待確認'),'#B2BEC3')}20;color:{colors.get(tx.get('類別','待確認'),'#B2BEC3')}'>{tx.get('類別','待確認')}</span></td><td>{tx['類型']}</td><td class='{'amount-income' if tx['類型']=='收入' else 'amount-expense'}'>${tx['金額']:,.2f}</td></tr>" for tx in transactions[:50])}
                </tbody>
            </table>
            {'<p style="text-align:center;color:#999;margin-top:16px;">... 還有 ' + str(len(transactions)-50) + ' 筆交易</p>' if len(transactions) > 50 else ''}
        </div>
    </div>

    <script>
        const ctx = document.getElementById('categoryChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: {cat_labels},
                datasets: [{{
                    data: {cat_values},
                    backgroundColor: {cat_colors},
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            font: {{ size: 12 }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"📊 HTML report saved: {output_path}")


def send_discord_summary(stats: Dict, month: str, csv_preview: str):
    """Generate Discord summary message"""
    emoji = "💙"

    message = f"""{emoji} **{month} 財務月報** {emoji}

📊 **收支摘要**
• 總收入: ${stats.get('總收入', 0):,.2f}
• 總支出: ${stats.get('總支出', 0):,.2f}
• 淨額: ${stats.get('淨額', 0):,.2f}
• 交易筆數: {stats.get('交易筆數', 0)}

🔥 **最大支出 Top 3**
"""
    for i, tx in enumerate(stats.get('最大支出Top5', [])[:3], 1):
        message += f"{i}. {tx['描述'][:25]} - ${tx['金額']:,.2f}\n"

    # Category breakdown
    cats = stats.get("類別分布", {})
    if cats:
        message += "\n📈 **支出類別**\n"
        for cat, amount in sorted(cats.items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = (amount / stats.get('總支出', 1)) * 100 if stats.get('總支出', 0) > 0 else 0
            message += f"• {cat}: ${amount:,.2f} ({pct:.1f}%)\n"

    # Subscriptions warning
    subs = stats.get("潛在訂閱", [])
    if subs:
        message += f"\n⚠️ **訂閱警示**: 檢測到 {len(subs)} 項潛在重複訂閱\n"

    message += f"\n📁 詳細報表: `~/.finance/reports/{month}.html`"

    return message


def main():
    import argparse
    parser = argparse.ArgumentParser(description="香港銀行財務自動化 Workflow")
    parser.add_argument("--month", help="處理月份 (YYYY-MM格式，默認上個月)")
    parser.add_argument("--test", action="store_true", help="測試模式：只處理前10行並輸出預覽")
    parser.add_argument("--download-only", action="store_true", help="僅下載附件，不解析")
    args = parser.parse_args()

    # Determine target month
    if args.month:
        target_month = args.month
    else:
        last_month = datetime.now().replace(day=1) - timedelta(days=1)
        target_month = last_month.strftime("%Y-%m")

    print(f"🗓️ 處理月份: {target_month}")

    # Load config
    config = load_config()
    if not config.get("email") or not config.get("app_password"):
        print("❌ 請先設定 Yahoo Mail 帳號和 App Password")
        print("   編輯: ~/.finance/config.json")
        print(json.dumps({"email": "your@yahoo.com", "app_password": "xxxx xxxx xxxx xxxx"}, indent=2))
        sys.exit(1)

    # Calculate date range for email search
    year, month = map(int, target_month.split("-"))
    month_start = datetime(year, month, 1)
    if month == 12:
        next_month_start = datetime(year + 1, 1, 1)
    else:
        next_month_start = datetime(year, month + 1, 1)

    since_date = month_start.strftime("%d-%b-%Y")
    before_date = next_month_start.strftime("%d-%b-%Y")

    print(f"📅 搜尋日期範圍: {since_date} 至 {before_date}")

    # Create directories
    month_dir = RAW_DIR / target_month
    month_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Connect to IMAP
        mail = connect_imap(config["email"], config["app_password"])

        # Search emails
        email_ids = search_bank_emails(mail, since_date, before_date)

        # Filter by keywords
        matching = filter_by_keywords(mail, email_ids)

        if not matching:
            print("⚠️ 沒有找到符合的郵件")
            mail.logout()
            return

        # Download attachments
        matching_ids = [eid for eid, _ in matching]
        downloaded = download_attachments(mail, matching_ids, month_dir)

        print(f"\n📦 已下載 {len(downloaded)} 個附件")

        if args.download_only:
            mail.logout()
            return

        # Parse content and extract transactions
        all_transactions = []
        failed_files = []

        for file_path in downloaded:
            print(f"\n📄 Parsing: {file_path.name}")
            try:
                text, email_date = parse_content_to_text(file_path)
                transactions = extract_transactions_from_text(text, file_path.name, email_date)

                if transactions:
                    print(f"   ✅ 提取 {len(transactions)} 筆交易")
                    all_transactions.extend(transactions)
                else:
                    print(f"   ⚠️ 未能識別交易格式")
                    failed_files.append(file_path)

            except Exception as e:
                print(f"   ❌ 解析失敗: {e}")
                failed_files.append(file_path)

        mail.logout()

        if not all_transactions:
            print("\n❌ 未能從任何郵件提取交易")
            if failed_files:
                print(f"   {len(failed_files)} 個檔案需要手動處理")
            return

        # Sort by date
        all_transactions.sort(key=lambda x: x.get("日期", ""))

        # Add categories
        for tx in all_transactions:
            tx["類別"] = categorize_transaction(tx["描述"])

        # Generate CSVs
        raw_csv = RAW_DIR / f"{target_month}.csv"
        classified_csv = PROCESSED_DIR / f"{target_month}_classified.csv"
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        # Raw CSV
        with open(raw_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_transactions[0].keys())
            writer.writeheader()
            writer.writerows(all_transactions)
        print(f"\n💾 原始 CSV: {raw_csv}")

        # Classified CSV (same format but with category)
        with open(classified_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_transactions[0].keys())
            writer.writeheader()
            writer.writerows(all_transactions)
        print(f"💾 分類 CSV: {classified_csv}")

        # Generate statistics
        stats = generate_statistics(all_transactions)

        # Generate HTML report
        report_path = REPORTS_DIR / f"{target_month}.html"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        generate_html_report(all_transactions, stats, target_month, report_path)

        # Generate Discord summary
        preview_data = all_transactions[:10]
        preview_csv = "\n".join([f"{tx['日期']}, {tx['描述'][:20]:20}, ${tx['金額']:.2f}, {tx.get('類別','')}" for tx in preview_data])
        discord_msg = send_discord_summary(stats, target_month, preview_csv)

        # Save Discord message for later sending
        discord_file = FINANCE_DIR / f"discord_summary_{target_month}.txt"
        with open(discord_file, "w") as f:
            f.write(discord_msg)

        print("\n" + "=" * 50)
        print("✅ 處理完成!")
        print("=" * 50)
        print(f"\n📊 CSV 預覽 (前10行):")
        print(preview_csv)
        print(f"\n📊 統計摘要:")
        print(f"   總收入: ${stats.get('總收入', 0):,.2f}")
        print(f"   總支出: ${stats.get('總支出', 0):,.2f}")
        print(f"   淨額: ${stats.get('淨額', 0):,.2f}")
        print(f"\n📁 輸出檔案:")
        print(f"   CSV: {raw_csv}")
        print(f"   HTML: {report_path}")
        print(f"   Discord: {discord_file}")

        if failed_files:
            print(f"\n⚠️ 解析失敗的檔案 ({len(failed_files)}):")
            for f in failed_files:
                print(f"   - {f.name}")

        if args.test:
            print("\n🧪 測試模式完成 - 請檢查上述結果")
            print("   確認無誤後，執行: openclaw gateway cron create ...")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
