#!/usr/bin/env python3
"""Debug script to check email structure"""

import imaplib
import email
import email.policy
import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".finance" / "config.json"

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

config = load_config()

print("🔗 Connecting to Yahoo IMAP...")
mail = imaplib.IMAP4_SSL("imap.mail.yahoo.com", 993)
mail.login(config["email"], config["app_password"])
print("✅ Login successful\n")

mail.select("inbox")

# Search for January 2026
search_query = '(SENTSINCE 01-Jan-2026 SENTBEFORE 01-Feb-2026)'
status, messages = mail.search(None, search_query)
email_ids = messages[0].decode().split()
print(f"📧 Found {len(email_ids)} emails total\n")

# Keywords to check
keywords = ["月結單", "e-Statement", "對帳單", "電子月結單", "Statement", "Transaction Summary"]

# Check first 10 emails
for i, eid in enumerate(email_ids[:15]):
    status, msg_data = mail.fetch(eid, "(RFC822)")
    if status != "OK":
        continue
    
    msg = email.message_from_bytes(msg_data[0][1], policy=email.policy.default)
    subject = msg["Subject"] or ""
    from_addr = msg["From"] or ""
    
    # Check if matches keywords
    subject_lower = subject.lower()
    matched = any(k.lower() in subject_lower for k in keywords)
    
    if matched or "statement" in subject_lower or "transaction" in subject_lower:
        print(f"📧 Email {eid}:")
        print(f"   From: {from_addr[:50]}")
        print(f"   Subject: {subject}")
        
        # Check attachments
        has_attachments = False
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                filename = part.get_filename()
                if filename:
                    print(f"   📎 Attachment: {filename} ({content_type})")
                    has_attachments = True
        
        if not has_attachments:
            print("   (No attachments found)")
        
        # Show content type structure
        if msg.is_multipart():
            print("   Structure:")
            for part in msg.walk():
                print(f"      - {part.get_content_type()}")
        else:
            print(f"   Content-Type: {msg.get_content_type()}")
        
        print()

mail.logout()
print("✅ Done")
