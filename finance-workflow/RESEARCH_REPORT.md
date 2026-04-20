# 財務自動化 Workflow - 研究報告與改進建議

## 目錄
1. [研究背景](#研究背景)
2. [國際最佳實踐](#國際最佳實踐)
3. [現有系統分析](#現有系統分析)
4. [改進建議](#改進建議)
5. [實施計劃](#實施計劃)

---

## 研究背景

### 專案目標
建立自動化的香港銀行/信用卡財務管理 workflow，從 Yahoo Mail 自動：
- 提取交易通知郵件
- 解析交易資料（日期、商家、金額、幣別）
- 分類交易（飲食、交通、娛樂等）
- 生成 CSV 報表和 HTML 視覺化報告
- 發送 Discord 摘要通知

### 支援的機構
- **銀行**: BOC (中銀)、HSBC、ZA Bank、Mox、AEON
- **支付平台**: Alipay (支付寶)、WeChat Pay (微信支付)
- **商家**: Apple、Steam

---

## 國際最佳實踐

### 參考專案分析

#### 1. Actual Budget (Node.js)
- **GitHub**: https://github.com/actualbudget/actual
- **特點**:
  - 本地優先 (local-first) 架構
  - 支援多種資料匯入方式（CSV、OFX、QFX）
  - 跨平台同步
  - 開源免費
- **適合參考**: ⭐⭐⭐⭐⭐
- **學習點**: 
  - 資料庫設計
  - 多平台同步機制
  - 開放式架構

#### 2. Firefly III (PHP)
- **GitHub**: https://github.com/firefly-iii/firefly-iii
- **特點**:
  - 自架式個人財務管理
  - 強大的規則引擎 (Rule Engine)
  - REST API
  - 多種財務報告
- **適合參考**: ⭐⭐⭐⭐⭐
- **學習點**:
  - 規則引擎設計
  - 自動分類機制
  - REST API 設計

#### 3. mail-parser (Python)
- **PyPI**: https://pypi.org/project/mail-parser/
- **特點**:
  - 專業郵件解析庫
  - 支援 Outlook .msg 格式
  - 自動處理編碼問題
  - 提取附件
- **適合參考**: ⭐⭐⭐⭐⭐
- **學習點**:
  - 郵件結構解析
  - 編碼處理
  - 附件提取

---

## 現有系統分析

### 優勢
1. ✅ 支援多種香港本地銀行格式
2. ✅ 支援 Alipay/WeChat Pay
3. ✅ 自動去重機制
4. ✅ 郵件日期解析
5. ✅ Discord 通知整合

### 不足之處
1. ❌ 使用手動 regex 解析，維護成本高
2. ❌ 缺乏資料驗證機制
3. ❌ 去重依賴檔案名，不穩定
4. ❌ 所有解析邏輯集中在一個函數
5. ❌ 缺乏錯誤處理和日誌

---

## 改進建議

### 🔴 短期目標 (1-2 週)

#### 1. 使用專業郵件解析庫
**現狀**: 手動解析郵件內容  
**建議**: 使用 `mail-parser` 庫

```python
import mailparser

def parse_email(file_path):
    mail = mailparser.parse_from_file(file_path)
    return {
        'date': mail.date,
        'from': mail.from_,
        'subject': mail.subject,
        'body': mail.text_plain[0] if mail.text_plain else mail.text_html[0],
        'attachments': mail.attachments
    }
```

**好處**:
- 正確處理各種郵件格式
- 自動解碼亞洲語言編碼
- 減少維護成本

#### 2. 添加資料驗證機制
**建議實現**:

```python
def validate_transaction(tx):
    errors = []
    
    # 金額驗證
    if tx['amount'] <= 0:
        errors.append("Amount must be positive")
    if tx['amount'] > 1000000:
        errors.append("Amount seems too large")
    
    # 日期驗證
    try:
        datetime.strptime(tx['date'], '%Y-%m-%d')
    except:
        errors.append("Invalid date format")
    
    # 商家驗證
    if not tx.get('merchant'):
        errors.append("Missing merchant")
    
    return len(errors) == 0, errors
```

#### 3. 改進去重機制
**建議**: 使用交易內容生成唯一ID

```python
import hashlib

def generate_transaction_id(tx):
    unique_string = f"{tx['date']}_{tx['merchant']}_{tx['amount']}_{tx['currency']}"
    return hashlib.md5(unique_string.encode()).hexdigest()

# 儲存已處理的交易ID
processed_ids = load_processed_ids()
```

---

### 🟡 中期目標 (1 個月)

#### 4. 插件式解析器架構
**建議設計**:

```python
class BankParser:
    """Base class for bank parsers"""
    
    def can_parse(self, email_from, subject, body):
        """Check if this parser can handle the email"""
        raise NotImplementedError
    
    def parse_transaction(self, email_data):
        """Parse transaction from email"""
        raise NotImplementedError

class BOCParser(BankParser):
    def can_parse(self, email_from, subject, body):
        return 'bochk.com' in email_from and '直接扣賬' in subject
    
    def parse_transaction(self, email_data):
        # BOC-specific parsing logic
        pass

class AlipayParser(BankParser):
    def can_parse(self, email_from, subject, body):
        return 'alipay.com' in email_from
    
    def parse_transaction(self, email_data):
        # Alipay-specific parsing logic
        pass
```

**好處**:
- 容易添加新銀行支援
- 代碼結構清晰
- 便於測試

#### 5. 添加單元測試
**建議**:
- 為每個解析器添加測試案例
- 使用 pytest 框架
- 達到 80%+ 覆蓋率

```python
def test_boc_parser():
    parser = BOCParser()
    email = load_test_email('boc_sample.txt')
    result = parser.parse_transaction(email)
    
    assert result['amount'] == 100.00
    assert result['currency'] == 'HKD'
    assert result['merchant'] == 'TEST MERCHANT'
```

---

### 🟢 長期目標 (3 個月)

#### 6. LLM 輔助解析
**適合場景**:
- 複雜的表格格式
- 多語言混合內容
- PDF 附件內容提取

**實現方式**:

```python
import openai

def extract_with_llm(email_body):
    prompt = f"""
    Extract transaction information from this email and return as JSON:
    {{
        "date": "YYYY-MM-DD",
        "merchant": "merchant name",
        "amount": 123.45,
        "currency": "HKD",
        "type": "expense"
    }}
    
    Email: {email_body}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)
```

#### 7. 自動學習機制
**想法**:
- 記錄用戶的手動修正
- 使用機器學習改進分類準確度
- 自動調整解析規則

---

## 實施計劃

### Phase 1: 基礎改進 (本週)
- [x] 安裝 mail-parser 庫
- [ ] 重構郵件解析部分
- [ ] 添加資料驗證函數
- [ ] 改進去重機制

### Phase 2: 架構重構 (下週)
- [ ] 設計插件式解析器架構
- [ ] 遷移現有解析邏輯
- [ ] 添加解析器註冊機制

### Phase 3: 測試完善 (第三週)
- [ ] 編寫單元測試
- [ ] 添加集成測試
- [ ] 測試各種郵件格式

### Phase 4: 進階功能 (第四週)
- [ ] 評估 LLM 整合可行性
- [ ] 設計用戶回饋機制
- [ ] 優化性能和錯誤處理

---

## 技術參考

### 相關文檔
- [mail-parser 文檔](https://pypi.org/project/mail-parser/)
- [Actual Budget 文檔](https://actualbudget.org/docs)
- [Firefly III 文檔](https://docs.firefly-iii.org)

### 工具推薦
- **郵件解析**: `mail-parser` (Python)
- **PDF 解析**: `pdfplumber` (已在使用)
- **測試框架**: `pytest`
- **日誌記錄**: `logging` (標準庫)

---

## 結論

現有系統已經能滿足基本需求，但還有很大的改進空間。建議按照短期→中期→長期的順序逐步實施，優先解決穩定性和可維護性問題，再考慮進階功能。

**核心改進點**:
1. 使用專業郵件解析庫減少維護成本
2. 添加資料驗證確保資料質量
3. 改進架構便於擴展新銀行支援

---

*報告生成時間*: 2026-02-20  
*作者*: 雷姆 (OpenClaw Agent)  
*版本*: v1.0
