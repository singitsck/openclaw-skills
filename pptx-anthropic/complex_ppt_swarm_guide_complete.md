# 複雜 PPT 生成 - Swarm Solver 完整方案（中文版）

## 🎯 方案概述

使用 **Swarm Solver + 多樣化版面 + Algorithmic Art** 生成專業級 FYP 簡報。

## 🏗️ 完整架構

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: 設計系統創建 (Supervisor)                      │
│  - 創建 design-system.json（中文配置）                   │
│  - 定義 8 種版面模板                                     │
│  - 配置 Algorithmic Art 背景參數                         │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
        ▼            ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────┐
   │Chapter │  │Chapter │  │Chapter │  │   Visual   │
   │ Agent 1│  │ Agent 2│  │ Agent 3│  │   Agent    │
   │(版面   │  │(版面   │  │(版面   │  │ (Algorithmic
   │ 1-3)   │  │ 4-5)   │  │ 6-8)   │  │   Art BG)  │
   └────┬───┘  └────┬───┘  └────┬───┘  └─────┬──────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Merge & Polish       │
        │  (python-pptx)         │
        │  - 合併所有章節        │
        │  - 插入 Algorithmic Art│
        │  - 統一母版            │
        └───────────┬────────────┘
                    │
                    ▼
             ┌────────────┐
             │  Final PPT │
             │ (多樣化版面)│
             └────────────┘
```

## 📋 設計系統配置

### design-system.json（中文配置）

```json
{
  "name": "AI 使用形態演進 FYP 簡報",
  "theme": "科技藍",
  "color_palette": {
    "primary": "#1E3A5F",
    "secondary": "#3B82F6", 
    "accent": "#10B981",
    "background_dark": "#0F172A",
    "background_light": "#F8FAFC",
    "text_dark": "#0F172A",
    "text_light": "#F8FAFC",
    "muted": "#64748B"
  },
  "typography": {
    "h1_size": 52,
    "h2_size": 36,
    "h3_size": 28,
    "body_size": 22,
    "caption_size": 16,
    "font": "Microsoft JhengHei"
  },
  "spacing": {
    "margin": "0.6in",
    "line_spacing": 28
  },
  "algorithmic_art": {
    "style": "Azure Depth",
    "hue_base": 210,
    "particle_count": 3000,
    "flow_speed": 2.0
  }
}
```

## 🎨 8 種多樣化版面設計

### 版面 1: 全屏深色標題頁
```python
def layout_fullscreen_title(slide, title, subtitle):
    """Algorithmic Art 背景 + 大字標題"""
    # 深色背景
    bg = slide.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(15, 23, 42)
    
    # Algorithmic Art: 流場線條
    for i in range(20):
        line = slide.shapes.add_shape(
            1, Inches(random_x), Inches(random_y), 
            Inches(2), Pt(2)
        )
        line.fill.fore_color.rgb = RGBColor(30, 80, 150+rand)
        line.rotation = random_angle
    
    # 標題 52pt
    add_text(title, size=52, bold=True, color=white)
    add_text(subtitle, size=28, color=gray_blue)
```

### 版面 2: 兩欄圖文
```python
def layout_two_column(slide, emoji, title, bullets):
    """左欄文字 + 右欄大圓形"""
    # 左欄: 標題 36pt + 內容 22pt
    add_text(title, left=0.6, top=0.5, size=36)
    add_bullets(bullets, left=0.6, top=1.8, size=22)
    
    # 右欄: 大圓形 + Emoji
    circle = add_circle(left=8, top=2, size=4, color=primary)
    add_text(emoji, left=8, top=3.5, size=72, center=True)
```

### 版面 3: 三欄卡片
```python
def layout_three_cards(slide, title, cards):
    """三個並排卡片"""
    for i, (card_title, desc, color) in enumerate(cards):
        x = 0.6 + i * 4.2
        # 卡片背景
        card = add_rectangle(x, 2, 3.8, 4.5, white)
        # 頂部色條
        bar = add_rectangle(x, 2, 3.8, 0.1, color)
        # 編號 + 標題 + 描述
        add_text(f"0{i+1}", x, 2.8, size=48, color=color, center=True)
        add_text(card_title, x+0.2, 3.8, size=28, center=True)
```

### 版面 4: 大圓+清單
```python
def layout_big_circle_list(slide, emoji, title, points):
    """左側大圓 + 右側清單"""
    # 左側: 大圓形
    circle = add_circle(0.8, 1.5, 4.5, accent_green)
    add_text(emoji, 0.8, 3, size=72, center=True, color=white)
    
    # 右側: 標題 + 清單
    add_text(title, 5.5, 0.5, size=40, color=accent_green)
    add_checklist(points, 5.5, 1.6, size=22)
```

### 版面 5: 2x2 網格
```python
def layout_grid_2x2(slide, title, items):
    """2x2 彩色方塊網格"""
    positions = [(0.5, 1.6), (6.8, 1.6), (0.5, 4.6), (6.8, 4.6)]
    colors = [blue, purple, red, orange]
    
    for (x, y), (emoji, item_title, desc), color in zip(positions, items, colors):
        rect = add_rectangle(x, y, 5.8, 2.5, color)
        add_text(emoji, x, y+0.3, size=40, color=white)
        add_text(item_title, x+0.2, y+1.1, size=28, color=white)
```

### 版面 6: 左側大色條
```python
def layout_left_sidebar(slide, title, subtitle, points):
    """左側色條 + 右側內容"""
    # 左側: 大色塊
    bar = add_rectangle(0, 0, 2.2, 7.5, primary_blue)
    add_text("核心概念", 0.3, 2.5, size=32, color=white, vertical=True)
    
    # 右側: 標題 + 副標題 + 清單
    add_text(title, 2.6, 0.5, size=36)
    add_text(subtitle, 2.6, 1.5, size=28, color=primary_blue)
    add_bullets(points, 2.6, 2.5, size=22)
```

### 版面 7: 流程步驟
```python
def layout_flow_steps(slide, title, steps):
    """三圓流程 + 箭頭連接"""
    for i, (num, step_title, desc) in enumerate(steps):
        x = 0.8 + i * 4.2
        # 圓形編號
        circle = add_circle(x+1.3, 1.8, 1.4, accent_red)
        add_text(num, x+1.3, 2.1, size=36, center=True, color=white)
        # 標題 + 描述
        add_text(step_title, x, 3.4, size=28, center=True, color=accent_red)
        # 箭頭（除了最後一個）
        if i < 2:
            add_arrow(x+3.9, 2.3, color=gray)
```

### 版面 8: 圖標列表
```python
def layout_icon_list(slide, title, items):
    """色條 + Emoji + 標題 + 描述"""
    for i, (emoji, item_title, desc, color) in enumerate(items):
        y = 1.4 + i * 1.4
        # 左側色條
        bar = add_rectangle(0.6, y, 0.08, 1.1, color)
        # Emoji
        add_text(emoji, 0.9, y+0.1, size=32, color=color)
        # 標題 + 描述
        add_text(item_title, 1.7, y+0.1, size=24, bold=True)
        add_text(desc, 1.7, y+0.7, size=18, color=gray)
```

## 🔧 Algorithmic Art 背景生成

### 使用 algorithmic-art skill 生成封面

```python
# 生成演算法背景
algorithmic_config = {
    "style": "Azure Depth",
    "philosophy": "Flow fields driven by layered Perlin noise",
    "particles": 3000,
    "noise_scale": 0.008,
    "color_palette": {
        "background": "#0F172A",
        "particles": ["#1E3A5F", "#3B82F6", "#60A5FA"],
        "accents": ["#10B981", "#34D399"]
    }
}

# 輸出: cover_background.html
# 截圖後作為 PPT 封面背景
```

### 在 PPT 中使用背景

```python
# 將 HTML 渲染為圖片後嵌入
from pptx.util import Inches

# 添加背景圖片
background = slide.shapes.add_picture(
    "algorithmic_bg.png",
    Inches(0), Inches(0),
    width=prs.slide_width,
    height=prs.slide_height
)

# 將背景移到最底層
spTree = slide.shapes._spTree
sp = background._element
spTree.remove(sp)
spTree.insert(2, sp)
```

## 🚀 完整工作流程

### Step 1: 創建設計系統

```bash
# 創建設計系統配置文件
cat > design-system.json << 'EOF'
{
  "name": "AI 演進 FYP 簡報",
  "theme": "科技藍",
  "color_palette": {...},
  "typography": {...},
  "layouts": ["fullscreen", "two-column", "three-cards", 
              "big-circle", "grid-2x2", "sidebar", 
              "flow-steps", "icon-list"]
}
EOF
```

### Step 2: 並行生成章節

```python
# Swarm Plan: 並行啟動多個 Agent
chapters = [
    {"id": 1, "agent": "ppt-creator-1", "layouts": [1, 8, 2]},
    {"id": 2, "agent": "ppt-creator-2", "layouts": [6, 4, 3]},
    {"id": 3, "agent": "ppt-creator-3", "layouts": [5, 7, 2]},
]

for chapter in chapters:
    sessions_spawn(
        task=f"生成第 {chapter['id']} 章",
        config={
            "layouts": chapter["layouts"],
            "design_system": "design-system.json",
            "language": "zh-TW"
        }
    )
```

### Step 3: 生成 Algorithmic Art 背景

```python
# Visual Agent 生成背景
sessions_spawn(
    task="生成封面背景",
    skill="algorithmic-art",
    params={
        "theme": "Azure Depth",
        "seed": 42,
        "output": "cover_bg.png"
    }
)
```

### Step 4: 合併與精煉

```python
from pptx import Presentation

# 創建最終 PPT
final_prs = Presentation()

# 添加 Algorithmic Art 封面
cover_slide = final_prs.slides.add_slide(...)
add_algorithmic_background(cover_slide, "cover_bg.png")
add_title_text(cover_slide, "AI 使用形態的演進")

# 合併各章節（使用不同版面）
for chapter_file in chapter_files:
    chapter_prs = Presentation(chapter_file)
    for slide in chapter_prs.slides:
        copy_slide_with_layout(slide, final_prs)

# 保存
final_prs.save("AI_Evolution_FYP_Final.pptx")
```

## 📊 與傳統方法的對比

| 特性 | 傳統方法 | Swarm + 多樣化 + Algorithmic Art |
|------|---------|--------------------------------|
| **內容語言** | 英文 | ✅ **中文** |
| **版面風格** | 單一重複 | ✅ **8 種版面輪替** |
| **封面背景** | 純色/漸層 | ✅ **Algorithmic Art 演算法生成** |
| **視覺效果** | 單調 | ✅ **豐富多樣** |
| **內容結構** | 單一 Agent | ✅ **多 Agent 並行** |
| **設計一致性** | 難控制 | ✅ **設計系統統一管理** |

## 📝 中文內容設計原則

### 字體選擇
```python
FONT = "Microsoft JhengHei"  # 跨平台繁體中文
```

### 排版注意事項
- 標題使用粗體，內文使用正常字重
- 避免過長的句子，每行 20-25 字為宜
- 使用繁體中文標點符號（，。：；）
- 專業術語保持一致（如：Agent、MCP、Skills）

### 內容結構範例
```
第 1 章：緒論
  - 研究背景
  - 研究動機
  - 目錄

第 2 章：GPT 時代
  - GPT-3 突破
  - GPT-4 多模態
  - ChatGPT 現象
  - 局限性分析

第 3 章：Agent 革命
  - Agent 概念
  - ReAct 框架
  - 多 Agent 系統

第 4 章：MCP 與 Skills
  - MCP 協議
  - Skills 系統
  - 整合應用

第 5 章：未來展望
  - 技術演進
  - 產業影響
  - 結論
```

## 🎯 成功標準

- [x] **中文內容** - 全部使用繁體中文
- [x] **Algorithmic Art 背景** - 封面使用演算法生成背景
- [x] **多樣化版面** - 8 種版面輪替，避免單調
- [x] **專業設計** - 符合 pptx-anthropic 設計規範
- [x] **Swarm 方法** - 多 Agent 並行生成

## 📚 相關文件

- `design-examples.md` - 版面範例詳細說明
- `quick-reference.md` - 快速參考卡
- `algorithmic-art-integration.md` - Algorithmic Art 整合指南

---

**使用此方案生成的 PPT 特色：**
- 🎨 8 種專業版面輪替
- 🌊 Algorithmic Art 演算法背景
- 📝 繁體中文學術內容
- 🚀 Swarm 並行高效生成
- 💙 真正 FYP 專業級品質
