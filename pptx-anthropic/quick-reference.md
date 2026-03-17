# 📊 PPT 設計快速參考卡

## 🎯 核心原則（記住這三個）

### 1. 字體層次（CRAP 對比原則）
```
主標題: 48-52pt (2x)
頁標題: 32-36pt (1.5x)  
內文: 20-24pt (1x)
```

### 2. 6×6 法則（簡潔原則）
- 每頁 ≤ 6 行
- 每行 ≤ 6 個詞

### 3. 留白空間（呼吸原則）
- 邊距 ≥ 0.5"
- 元素間距 ≥ 0.3"

---

## 🎨 設計系統

### 字體（跨平台）
```python
FONT = "Microsoft JhengHei"  # 微軟正黑體
```

### 顏色（Slate + 主色）
```python
DARK = (15, 23, 42)          # 主文字
GRAY = (71, 85, 105)         # 次要文字
PRIMARY = (37, 99, 235)      # 主色（藍）
```

### 間距
```python
MARGIN = Inches(0.6)
LINE_SPACING = Pt(28)
```

---

## 📐 版面選擇指南

| 內容類型 | 推薦版面 | 視覺效果 |
|---------|---------|---------|
| 開場/結尾 | 全屏深色 | 震撼、聚焦 |
| 介紹概念 | 兩欄圖文 | 平衡、易讀 |
| 比較特點 | 三欄卡片 | 並列、清晰 |
| 四大重點 | 2×2 網格 | 整齊、對稱 |
| 深度講解 | 左側色條 | 專業、權威 |
| 步驟流程 | 三圓流程 | 動態、引導 |
| 功能列表 | 圖標列表 | 現代、簡潔 |
| 應用場景 | 四圓分佈 | 活潑、多元 |

---

## ⚡ 快速模板

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# 設計系統
FONT = "Microsoft JhengHei"
H1, H2, H3, BODY = Pt(52), Pt(36), Pt(28), Pt(22)
MARGIN = Inches(0.6)
DARK = (15, 23, 42)
PRIMARY = (37, 99, 235)

def set_font(run, size, bold=False, color=DARK):
    run.font.name = FONT
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = RGBColor(*color)

# 標題頁
def add_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # 深色背景
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(*PRIMARY)
    bg.line.fill.background()
    # 標題
    box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.3), Inches(1.5))
    p = box.text_frame.paragraphs[0]
    p.text = title
    set_font(p.runs[0], H1, True, (255,255,255))
    p.alignment = PP_ALIGN.CENTER
    # 副標題
    box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12.3), Inches(1))
    p = box.text_frame.paragraphs[0]
    p.text = subtitle
    set_font(p.runs[0], H3, False, (191,219,254))
    p.alignment = PP_ALIGN.CENTER
```

---

## ✅ 最終檢查清單

發布前確認：
- [ ] 標題:內文字體比例 ≥ 2:1
- [ ] 每頁 ≤ 6 行文字
- [ ] 邊距 ≥ 0.5"
- [ ] 使用 Microsoft JhengHei
- [ ] 版面不重複（至少3種變化）
- [ ] 顏色統一（主色+輔色+強調色）

---

## 📚 完整參考

- 詳細原則：`SKILL.md` → "Professional Design Principles"
- 程式碼範例：`design-examples.md`
- 完整實作：`create_refined_ppt.py`
