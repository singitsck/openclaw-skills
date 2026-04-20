#!/usr/bin/env python3
"""
香港銀行/信用卡財務自動化 Workflow - 改進版 v2.0
使用 mail-parser 庫，添加資料驗證和交易ID去重
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
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Try to import mail-parser, fallback to standard library
try:
    import mailparser
    HAS_MAILPARSER = True
except ImportError:
    HAS_MAILPARSER = False
    print("⚠️  mail-parser not installed, using fallback parser")

# Configuration
FINANCE_DIR = Path.home() / ".finance"
RAW_DIR = FINANCE_DIR / "raw"
PROCESSED_DIR = FINANCE_DIR / "processed"
REPORTS_DIR = FINANCE_DIR / "reports"
CONFIG_FILE = FINANCE_DIR / "config.json"
PROCESSED_IDS_FILE = FINANCE_DIR / "processed_transaction_ids.json"

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


def load_processed_ids() -> set:
    """Load set of already processed transaction IDs"""
    if PROCESSED_IDS_FILE.exists():
        with open(PROCESSED_IDS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_processed_ids(ids: set):
    """Save processed transaction IDs"""
    with open(PROCESSED_IDS_FILE, "w") as f:
        json.dump(list(ids), f, indent=2)


def generate_transaction_id(tx: Dict) -> str:
    """Generate unique ID for transaction based on content"""
    unique_string = f"{tx.get('日期', '')}_{tx.get('描述', '')}_{tx.get('金額', 0)}_{tx.get('幣別', 'HKD')}"
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()


def validate_transaction(tx: Dict) -> Tuple[bool, List[str]]:
    """
    Validate extracted transaction data
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check required fields exist
    required_fields = ['日期', '描述', '金額', '幣別', '類型']
    for field in required_fields:
        if field not in tx:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Check amount is valid
    try:
        amount = float(tx['金額'])
        if amount <= 0:
            errors.append(f"Amount must be positive: {amount}")
        if amount > 1000000:  # Suspiciously large
            errors.append(f"Amount seems too large: {amount}")
    except (ValueError, TypeError):
        errors.append(f"Invalid amount format: {tx.get('金額')}")
    
    # Check date format
    try:
        datetime.strptime(tx['日期'], '%Y-%m-%d')
    except (ValueError, TypeError):
        errors.append(f"Invalid date format: {tx.get('日期')}")
    
    # Check merchant/description exists
    if not tx.get('描述') or len(tx['描述'].strip()) == 0:
        errors.append("Missing merchant/description")
    
    # Check currency is valid
    valid_currencies = ['HKD', 'USD', 'CNY', 'EUR', 'GBP', 'JPY']
    if tx.get('幣別') not in valid_currencies:
        errors.append(f"Unknown currency: {tx.get('幣別')}")
    
    return len(errors) == 0, errors


def connect_imap(email_addr: str, app_password: str) -> imaplib.IMAP4_SSL:
    """Connect to Yahoo Mail via IMAP"""
    print(f"🔗 Connecting to Yahoo Mail IMAP...")
    mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com", 993)
    mail.login(email_addr, app_password)
    print(f"✅ IMAP login successful")
    return mail


def parse_email_with_mailparser(file_path: Path) -> Optional[Dict]:
    """Parse email using mail-parser library"""
    if not HAS_MAILPARSER:
        return None
    
    try:
        mail = mailparser.parse_from_file(str(file_path))
        
        # Extract date from email
        email_date = ""
        if mail.date:
            try:
                # Parse various date formats
                date_match = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})', str(mail.date))
                if date_match:
                    day, month_str, year = date_match.groups()
                    months = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                             'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
                    month = months.get(month_str, '01')
                    email_date = f"{year}-{month}-{day.zfill(2)}"
            except:
                pass
        
        return {
            'from': mail.from_[0] if mail.from_ else '',
            'subject': mail.subject,
            'date': email_date,
            'body': mail.text_plain[0] if mail.text_plain else (mail.text_html[0] if mail.text_html else ''),
            'headers': dict(mail.headers) if mail.headers else {}
        }
    except Exception as e:
        print(f"   ⚠️  mail-parser failed: {e}, using fallback")
        return None


def extract_email_content(msg) -> str:
    """Extract text content from email (HTML or plain text) - Fallback method"""
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


# [Rest of the code would continue with the bank-specific parsers...]
# For brevity, I'll create the research document first
