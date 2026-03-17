# Algorithmic Art + PPTX 整合指南

結合 `algorithmic-art` 和 `pptx-anthropic` 兩個 skill，為 PPT 創建獨特的演算法背景！

## 🎯 工作流程

```
Step 1: algorithmic-art
   ↓ 生成演算法藝術 (HTML + p5.js)
   ↓ 渲染為 PNG 圖片
   
Step 2: pptx-anthropic
   ↓ 使用 PNG 作為 PPT 背景
   ↓ 創建專業簡報
```

## 📋 詳細步驟

### 1. 生成演算法背景

使用 algorithmic-art skill 創建背景：

```
創建一個適合簡報背景的演算法藝術：
- 主題：深海藍色流動
- 風格：柔和、不搶眼
- 適合：PowerPoint 標題頁背景
```

**關鍵參數調整**：
- 降低 `trailAlpha` (透明度) - 讓背景更柔和
- 選擇較暗的色相 - 白色文字才能清晰顯示
- 較低的 `flowSpeed` - 創建更平靜的效果

### 2. 渲染為圖片

#### 方法一：瀏覽器截圖
1. 在瀏覽器打開生成的 HTML
2. 調整到滿意的效果
3. 使用截圖工具或 `Download PNG` 按鈕

#### 方法二：Python 自動化
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 設置無頭瀏覽器
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)
driver.get("file:///path/to/art.html")

# 等待渲染
time.sleep(3)

# 截圖
driver.save_screenshot("background.png")
driver.quit()
```

#### 方法三：p5.js 直接輸出
修改 p5.js 代碼，添加自動保存：
```javascript
function keyPressed() {
  if (key === 's') {
    saveCanvas('background', 'png');
  }
}
```

### 3. 在 PPT 中使用背景

```python
from pptx import Presentation
from pptx.util import Inches

# 創建 PPT
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 添加幻燈片
slide = prs.slides.add_slide(prs.slide_layouts[6])

# 添加背景圖片
background = slide.shapes.add_picture(
    "background.png",
    Inches(0), Inches(0),
    width=prs.slide_width,
    height=prs.slide_height
)

# 將背景移到最底層
spTree = slide.shapes._spTree
sp = background._element
spTree.remove(sp)
spTree.insert(2, sp)  # 插入到最底層

# 添加標題文字
title_box = slide.shapes.add_textbox(
    Inches(0.5), Inches(2.5),
    Inches(12.333), Inches(1.5)
)
tf = title_box.text_frame
p = tf.paragraphs[0]
p.text = "標題文字"
p.font.size = Pt(52)
p.font.color.rgb = RGBColor(255, 255, 255)  # 白色
```

## 🎨 推薦的背景風格

### 風格 1: Azure Depth (深海藍)
- **適合**: 科技、專業簡報
- **參數**: `hueBase: 210`, 暗色調
- **種子範例**: 42, 123, 456

### 風格 2: Golden Hour (黃金時刻)
- **適合**: 創意、溫暖主題
- **參數**: `hueBase: 45`, 琥珀色
- **種子範例**: 77, 888, 999

### 風格 3: Forest Canopy (森林冠層)
- **適合**: 環保、自然主題
- **參數**: `hueBase: 140`, 綠色調
- **種子範例**: 33, 666, 777

### 風格 4: Cosmic Dust (宇宙塵埃)
- **適合**: 科幻、未來主題
- **參數**: `hueBase: 280`, 紫色調
- **種子範例**: 111, 222, 333

## 🔧 自動化腳本範例

創建一個完整的自動化流程：

```python
#!/usr/bin/env python3
"""
生成演算法背景並創建 PPT
"""

import subprocess
import time
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def generate_art_background(seed, style="azure"):
    """生成演算法背景"""
    # 這裡會調用 algorithmic-art 的生成邏輯
    # 返回生成的圖片路徑
    pass

def create_ppt_with_background(title, background_path, output_path):
    """創建帶背景的 PPT"""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # 標題頁
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 添加背景
    bg = slide.shapes.add_picture(
        background_path, 0, 0,
        width=prs.slide_width,
        height=prs.slide_height
    )
    
    # 移動到底層
    spTree = slide.shapes._spTree
    sp = bg._element
    spTree.remove(sp)
    spTree.insert(2, sp)
    
    # 添加標題
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(2.5),
        Inches(12.333), Inches(1.5)
    )
    p = title_box.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(52)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER
    
    prs.save(output_path)
    print(f"✅ PPT 已創建: {output_path}")

# 使用範例
if __name__ == "__main__":
    # 生成背景
    bg_path = generate_art_background(seed=42, style="azure")
    
    # 創建 PPT
    create_ppt_with_background(
        title="OpenClaw 入門指南",
        background_path=bg_path,
        output_path="presentation_with_art_bg.pptx"
    )
```

## 💡 進階技巧

### 1. 統一種子系列
使用同一個種子產生不同變體：
```javascript
// 主背景 (完整畫布)
// 側邊欄背景 (裁剪左側)
// 頁尾裝飾 (裁剪底部)
```

### 2. 動態背景效果
在 PPT 中嵌入動畫：
- 將 p5.js 嵌入為 Web Object
- 或使用 GIF 動畫背景

### 3. 漸變遮罩
在背景上添加漸變形狀提升文字可讀性：
```python
# 添加半透明遮罩
overlay = slide.shapes.add_shape(
    1, 0, 0, prs.slide_width, prs.slide_height
)
overlay.fill.solid()
overlay.fill.fore_color.rgb = RGBColor(0, 0, 0)
overlay.fill.fore_color.brightness = 0.3  # 30% 透明度
```

## 📚 相關檔案

- `Azure_Serenity_Generative_Art.html` - 演算法藝術範例
- `pptx-anthropic/design-examples.md` - PPT 版面範例
- 結合兩者創建獨一無二的簡報！

---

**下次創建 PPT 時，先用 algorithmic-art 生成專屬背景吧！** 🎨
