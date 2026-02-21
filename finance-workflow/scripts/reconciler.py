#!/usr/bin/env python3
"""
財務混合模式工作流 - 合併 Email 交易 + PDF 月結單
Finance Hybrid Workflow - Merge Email transactions + PDF statements
"""

import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import csv

class FinanceReconciler:
    """合併 Email 交易與 PDF 月結單，生成完整記錄"""
    
    def __init__(self, base_dir: str = "~/.finance"):
        self.base_dir = Path(base_dir).expanduser()
        self.transactions_dir = self.base_dir / "transactions"
        self.statements_dir = self.base_dir / "statements"
        self.reconciled_dir = self.base_dir / "reconciled"
        
        # 確保目錄存在
        for d in [self.transactions_dir, self.statements_dir, self.reconciled_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def load_email_transactions(self, year_month: str) -> List[Dict]:
        """載入指定月份的 Email 交易記錄"""
        email_file = self.transactions_dir / f"{year_month}-email.json"
        
        if not email_file.exists():
            print(f"⚠️  未找到 Email 交易記錄: {email_file}")
            return []
        
        with open(email_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        transactions = data.get('transactions', [])
        print(f"📧 載入 {len(transactions)} 筆 Email 交易記錄")
        return transactions
    
    def load_pdf_transactions(self, year_month: str, bank: str) -> List[Dict]:
        """
        載入 PDF 解析後的交易記錄
        這裡預留接口，實際需要 PDF parsing 實現
        """
        pdf_file = self.statements_dir / year_month / f"{bank}.json"
        
        if not pdf_file.exists():
            print(f"⚠️  未找到 PDF 交易記錄: {pdf_file}")
            return []
        
        with open(pdf_file, 'r', encoding='utf-8') as f:
            transactions = json.load(f)
        
        print(f"📄 載入 {len(transactions)} 筆 {bank.upper()} PDF 交易記錄")
        return transactions
    
    def generate_transaction_key(self, txn: Dict) -> tuple:
        """
        生成交易匹配鍵（用於去重）
        使用日期 + 金額（四捨五入到整數）作為主要匹配條件
        """
        date = txn.get('date', '')
        amount = float(txn.get('amount', 0))
        # 金額四捨五入到 2 位小數，處理浮點數精度問題
        amount_key = round(amount, 2)
        return (date, amount_key)
    
    def descriptions_match(self, desc1: str, desc2: str) -> bool:
        """
        檢查兩個描述是否匹配（模糊匹配）
        提取關鍵詞進行比較
        """
        if not desc1 or not desc2:
            return False
        
        # 標準化：轉大寫，移除非字母數字
        def normalize(s):
            return re.sub(r'[^A-Za-z0-9\u4e00-\u9fff]', '', s.upper())
        
        norm1 = normalize(desc1)
        norm2 = normalize(desc2)
        
        # 如果一個包含另一個，認為匹配
        if norm1 in norm2 or norm2 in norm1:
            return True
        
        # 提取關鍵詞（長度 >= 3 的子串）
        def extract_keywords(s, min_len=4):
            keywords = set()
            for i in range(len(s) - min_len + 1):
                keywords.add(s[i:i+min_len])
            return keywords
        
        kw1 = extract_keywords(norm1)
        kw2 = extract_keywords(norm2)
        
        if not kw1 or not kw2:
            return False
        
        # 計算 Jaccard 相似度
        intersection = len(kw1 & kw2)
        union = len(kw1 | kw2)
        
        if union == 0:
            return False
        
        similarity = intersection / union
        return similarity >= 0.3  # 30% 相似度閾值
    
    def reconcile(self, year_month: str, banks: List[str] = None) -> Dict:
        """
        合併 Email 和 PDF 交易記錄
        
        Args:
            year_month: 格式 "2026-01"
            banks: 銀行列表，如 ['hsbc', 'boc', 'zabank']
        
        Returns:
            合併結果統計
        """
        if banks is None:
            banks = ['hsbc', 'boc', 'zabank', 'mox', 'aeon']
        
        print(f"\n{'='*60}")
        print(f"🔄 開始對帳: {year_month}")
        print(f"{'='*60}\n")
        
        # 1. 載入 Email 交易
        email_transactions = self.load_email_transactions(year_month)
        
        # 2. 載入各銀行 PDF 交易
        pdf_transactions = []
        for bank in banks:
            pdf_txns = self.load_pdf_transactions(year_month, bank)
            for txn in pdf_txns:
                txn['source'] = f'pdf_{bank}'
            pdf_transactions.extend(pdf_txns)
        
        # 3. 智能去重合併
        all_transactions = []
        seen_keys = {}  # key -> transaction
        duplicates_found = []
        
        # 先處理 Email 交易
        for txn in email_transactions:
            txn['source'] = 'email'
            key = self.generate_transaction_key(txn)
            
            if key not in seen_keys:
                txn['id'] = hashlib.md5(f"{key}".encode()).hexdigest()[:12]
                seen_keys[key] = txn
                all_transactions.append(txn)
        
        # 再處理 PDF 交易（智能合併）
        pdf_only_count = 0
        for txn in pdf_transactions:
            key = self.generate_transaction_key(txn)
            
            if key in seen_keys:
                # 找到重複！合併資訊
                existing = seen_keys[key]
                
                # 記錄重複資訊
                duplicates_found.append({
                    'date': txn.get('date'),
                    'amount': txn.get('amount'),
                    'email_desc': existing.get('description'),
                    'pdf_desc': txn.get('description'),
                    'bank': txn.get('bank')
                })
                
                # 保留更詳細的描述（PDF 通常更完整）
                if len(txn.get('description', '')) > len(existing.get('description', '')):
                    existing['description'] = txn.get('description')
                
                # 標記為混合來源
                existing['source'] = 'email+pdf'
                
            else:
                # 新交易，來自 PDF
                txn['source'] = f'pdf_{txn.get("bank", "unknown")}'
                txn['id'] = hashlib.md5(f"{key}".encode()).hexdigest()[:12]
                seen_keys[key] = txn
                all_transactions.append(txn)
                pdf_only_count += 1
        
        # 4. 按日期排序
        all_transactions.sort(key=lambda x: x.get('date', ''))
        
        # 5. 打印重複檢測結果
        if duplicates_found:
            print(f"⚠️  發現 {len(duplicates_found)} 筆重複交易（已合併）：")
            for dup in duplicates_found[:5]:  # 只顯示前 5 筆
                print(f"   - {dup['date']} {dup['bank']}: {dup['email_desc'][:30]}...")
        
        # 6. 生成報告
        result = {
            'year_month': year_month,
            'email_count': len(email_transactions),
            'pdf_count': len(pdf_transactions),
            'merged_count': len(all_transactions),
            'pdf_only_count': pdf_only_count,
            'transactions': all_transactions,
            'generated_at': datetime.now().isoformat()
        }
        
        # 6. 保存合併結果（本地）
        output_file = self.reconciled_dir / f"{year_month}-complete.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # 7. 同時輸出 CSV 方便 Excel 查看
        csv_file = self.reconciled_dir / f"{year_month}-complete.csv"
        self._export_to_csv(all_transactions, csv_file)
        
        # 8. 同步到 iCloud Drive
        self._sync_to_icloud(year_month, output_file, csv_file)
        
        # 9. 打印摘要
        self._print_summary(result)
        
        return result
    
    def _export_to_csv(self, transactions: List[Dict], csv_file: Path):
        """匯出為 CSV 格式"""
        if not transactions:
            return
        
        # 確定所有可能的欄位
        all_keys = set()
        for txn in transactions:
            all_keys.update(txn.keys())
        
        # 優先欄位順序
        priority_fields = ['date', 'bank', 'amount', 'currency', 'description', 'category', 'source', 'id']
        fieldnames = [f for f in priority_fields if f in all_keys]
        fieldnames += [f for f in sorted(all_keys) if f not in priority_fields]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for txn in transactions:
                writer.writerow({k: txn.get(k, '') for k in fieldnames})
    
    def _print_summary(self, result: Dict):
        """打印對帳摘要"""
        print(f"\n{'='*60}")
        print("📊 對帳結果摘要")
        print(f"{'='*60}")
        print(f"📅 月份: {result['year_month']}")
        print(f"📧 Email 交易: {result['email_count']} 筆")
        print(f"📄 PDF 交易: {result['pdf_count']} 筆")
        print(f"✅ 合併後總數: {result['merged_count']} 筆")
        print(f"🔍 PDF 補齊: {result['pdf_only_count']} 筆")
        print(f"\n💾 輸出檔案:")
        print(f"   - JSON: reconciled/{result['year_month']}-complete.json")
        print(f"   - CSV:  reconciled/{result['year_month']}-complete.csv")
        print(f"   - iCloud: ~/iCloudDrive/Documents/Finance/Reports/{result['year_month']}/")
        print(f"{'='*60}\n")
    
    def _sync_to_icloud(self, year_month: str, json_file: Path, csv_file: Path):
        """同步報表到 iCloud Drive"""
        try:
            # iCloud Drive 路徑
            icloud_base = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Documents/Finance/Reports"
            icloud_dir = icloud_base / year_month
            icloud_dir.mkdir(parents=True, exist_ok=True)
            
            # 複製檔案
            import shutil
            shutil.copy2(json_file, icloud_dir / f"{year_month}-complete.json")
            shutil.copy2(csv_file, icloud_dir / f"{year_month}-complete.csv")
            
            # 同時生成簡潔版報告
            report_file = icloud_dir / f"{year_month}-report.txt"
            self._generate_icloud_report(year_month, report_file)
            
            print(f"☁️  已同步到 iCloud: {icloud_dir}")
            
        except Exception as e:
            print(f"⚠️  iCloud 同步失敗: {e}")
    
    def _generate_icloud_report(self, year_month: str, report_file: Path):
        """生成 iCloud 簡潔版報告"""
        # 載入合併數據
        json_file = self.reconciled_dir / f"{year_month}-complete.json"
        if not json_file.exists():
            return
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        transactions = data.get('transactions', [])
        
        # 計算統計
        total_spent = sum(float(t.get('amount', 0)) for t in transactions if float(t.get('amount', 0)) < 0)
        total_income = sum(float(t.get('amount', 0)) for t in transactions if float(t.get('amount', 0)) > 0)
        
        # 按銀行分組
        by_bank = {}
        for t in transactions:
            bank = t.get('bank', 'Unknown')
            by_bank[bank] = by_bank.get(bank, 0) + 1
        
        # 按類別分組
        by_category = {}
        for t in transactions:
            cat = t.get('category', 'Uncategorized')
            amt = float(t.get('amount', 0))
            if amt < 0:
                by_category[cat] = by_category.get(cat, 0) + abs(amt)
        
        report = f"""📈 {year_month} 財務月度報告
{'='*50}

💰 收支概覽:
   總支出: HKD {abs(total_spent):,.2f}
   總收入: HKD {total_income:,.2f}
   淨收支: HKD {(total_income + total_spent):,.2f}

🏦 交易分布 (按銀行):
"""
        for bank, count in sorted(by_bank.items()):
            report += f"   {bank.upper()}: {count} 筆\n"
        
        report += f"\n📊 支出分類:\n"
        for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            report += f"   {cat}: HKD {amount:,.2f}\n"
        
        report += f"\n{'='*50}\n"
        report += f"\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def generate_monthly_report(self, year_month: str) -> str:
        """生成月度財務報告"""
        reconciled_file = self.reconciled_dir / f"{year_month}-complete.json"
        
        if not reconciled_file.exists():
            return f"❌ 未找到 {year_month} 的合併記錄，請先執行對帳"
        
        with open(reconciled_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        transactions = data.get('transactions', [])
        
        # 計算統計數據
        total_spent = sum(
            float(t.get('amount', 0)) 
            for t in transactions 
            if float(t.get('amount', 0)) < 0
        )
        
        total_income = sum(
            float(t.get('amount', 0)) 
            for t in transactions 
            if float(t.get('amount', 0)) > 0
        )
        
        # 按銀行分組
        by_bank = {}
        for t in transactions:
            bank = t.get('bank', 'Unknown')
            by_bank[bank] = by_bank.get(bank, 0) + 1
        
        # 按類別分組
        by_category = {}
        for t in transactions:
            cat = t.get('category', 'Uncategorized')
            amt = float(t.get('amount', 0))
            if amt < 0:  # 只統計支出
                by_category[cat] = by_category.get(cat, 0) + abs(amt)
        
        report = f"""
{'='*60}
📈 {year_month} 財務月度報告
{'='*60}

💰 收支概覽:
   總支出: HKD {abs(total_spent):,.2f}
   總收入: HKD {total_income:,.2f}
   淨收支: HKD {(total_income + total_spent):,.2f}

🏦 交易分布 (按銀行):
"""
        for bank, count in sorted(by_bank.items()):
            report += f"   {bank.upper()}: {count} 筆\n"
        
        report += f"\n📊 支出分類:\n"
        for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            report += f"   {cat}: HKD {amount:,.2f}\n"
        
        report += f"\n{'='*60}\n"
        
        # 保存報告
        report_file = self.reconciled_dir / f"{year_month}-report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


def main():
    """命令行入口"""
    import sys
    
    reconciler = FinanceReconciler()
    
    if len(sys.argv) < 2:
        print("使用方式:")
        print(f"  python {sys.argv[0]} reconcile 2026-01    # 對帳指定月份")
        print(f"  python {sys.argv[0]} report 2026-01       # 生成月度報告")
        print(f"  python {sys.argv[0]} setup                # 初始化目錄結構")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        print("✅ 目錄結構已初始化")
        print(f"   基礎目錄: {reconciler.base_dir}")
        
    elif command == "reconcile" and len(sys.argv) >= 3:
        year_month = sys.argv[2]
        reconciler.reconcile(year_month)
        
    elif command == "report" and len(sys.argv) >= 3:
        year_month = sys.argv[2]
        report = reconciler.generate_monthly_report(year_month)
        print(report)
        
    else:
        print("❌ 未知命令")


if __name__ == "__main__":
    main()
