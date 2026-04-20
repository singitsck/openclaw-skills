# Qwen3-TTS Voice Cloning 项目记录

> 创建日期: 2026-02-25
> 作者: 雷姆
> 为 singit 主人服务 💙

---

## 📋 项目概述

基于 kapi2800/qwen3-tts-apple-silicon 项目的 Qwen3-TTS 语音克隆工具，使用 bf16 模型避免静音 Bug，并添加了情绪控制功能。

### 核心特性

- 🎙️ **高质量语音克隆** - 基于 Qwen3-TTS 模型
- 🎭 **情绪控制** - 8 种情绪风格（normal, happy, gentle, sad, angry, surprised, shy, teasing）
- 🚀 **便捷接口** - Shell 快捷命令 `tts`
- 🌸 **角色预设** - 妃愛和雷姆的专属语音配置

---

## 📁 文件结构

```
~/.agents/skills/qwen3-tts-kapi/
├── SKILL.md                    # 项目文档
├── scripts/
│   ├── qwen3_kapi_bf16.py     # 原始 v1.0 脚本
│   ├── qwen3_kapi_v2.py       # 新版 v2.0（含情绪控制）
│   └── tts                     # Shell 快捷命令
```

---

## 🚀 快速开始

### 添加到 PATH（推荐）

```bash
# 添加到 ~/.zshrc
export PATH="$HOME/.agents/skills/qwen3-tts-kapi/scripts:$PATH"
```

### 基础用法

```bash
# 正常语气
tts izumi "ひよひよ～主人好！"

# 带情绪
tts izumi "太好了！" --emotion happy
tts izumi "主人晚安～" --emotion gentle
tts izumi "えっ！？" --emotion surprised

# 自定义输出
tts izumi "测试语音" --output ~/test.wav

# 输出到 workspace-groupchat（供妃愛使用）
tts izumi "妃愛在这里哦～" --to-groupchat
```

### 查看选项

```bash
tts --list-voices    # 显示可用声音
tts --list-emotions  # 显示可用情绪
```

---

## 🎭 情绪系统

### 全局情绪选项

| 情绪 | 描述 | 示例用法 |
|------|------|----------|
| `normal` | 正常语气 | `tts izumi "你好"` |
| `happy` | 开心、兴奋 | `--emotion happy` |
| `gentle` | 温柔、柔和 | `--emotion gentle` |
| `sad` | 悲伤、难过 | `--emotion sad` |
| `angry` | 生气、愤怒 | `--emotion angry` |
| `surprised` | 惊讶、震惊 | `--emotion surprised` |
| `shy` | 害羞、腼腆 | `--emotion shy` |
| `teasing` | 调皮、捉弄 | `--emotion teasing` |

### 妃愛（Izumi Hiyori）专属情绪

| 情绪 | 参考文本示例 |
|------|-------------|
| `normal` | 「いやめっちゃ持ちあげるけども...」 |
| `happy` | 「ひよひよ～！今天もいい天気だね～」 |
| `gentle` | 「主人、お疲れ様。お茶淹れてあげるね」 |
| `sad` | 「そんな…ひよひよ…」 |
| `teasing` | 「へへ～、主人ったら照れてる？ひよひよ～」 |
| `surprised` | 「えっ！？マジで！？ひよひよ！？」 |
| `shy` | 「あ、あの…その…ひよひよ…」 |
| `excited` | 「わぁ～！すっごい！ひよひよ～！」 |

### 雷姆（Rem）专属情绪

| 情绪 | 参考文本示例 |
|------|-------------|
| `normal` | 「ここから始めましょう。1から…いいえ、ゼロから」 |
| `happy` | 「スバルくん、おかえりなさい！」 |
| `gentle` | 「スバルくんのこと、信じてます」 |
| `sad` | 「スバルくん…どうして…」 |
| `determined` | 「雷ムは、スバルくんのために頑張ります」 |

---

## 🔧 技术细节

### 为什么使用 bf16？

| 模型 | 大小 | 内存 | 时间 | 结果 |
|------|------|------|------|------|
| 8bit | 2.3GB | 3-4GB | ~7s | ❌ 静音 |
| **bf16** | **4GB** | **6-8GB** | **~17s** | ✅ **正常** |

> 8bit 量化模型存在静音 Bug（mlx-audio Issue #405），必须使用 bf16。

### 语音参考文件位置

```
~/.openclaw/references/
├── izumi_hiyori/
│   ├── reference.wav      # 妃愛声音参考
│   └── reference.txt      # 参考文本
└── rem/
    └── rem_reference.wav  # 雷姆声音参考
```

### 输出生成位置

```
~/.openclaw/tts_output/           # 默认输出目录
~/.openclaw/workspace-groupchat/  # --to-groupchat 输出
~/.openclaw/media/outbound/       # Discord 发送用
```

---

## 🎙️ Python API 使用

```python
from qwen3_kapi_v2 import generate_voice, PRESET_VOICES

# 生成带情绪的语音
output = generate_voice(
    text="主人，今天过得怎么样？",
    ref_audio="~/.openclaw/references/izumi_hiyori/reference.wav",
    ref_text="いやめっちゃ持ちあげるけども、普段通りでいいよ",
    output_path="~/output.wav",
    emotion="happy"  # 情绪控制
)
print(f"Generated: {output}")
```

---

## 📥 安装依赖

```bash
pip install mlx-audio huggingface-hub
```

### 下载 bf16 模型

```bash
huggingface-cli download \
  mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --local-dir ~/.cache/qwen3-tts/bf16
```

---

## 🔗 相关链接

- kapi2800 Project: https://github.com/kapi2800/qwen3-tts-apple-silicon
- mlx-audio: https://github.com/Blaizzy/mlx-audio
- Qwen3-TTS: https://huggingface.co/collections/Qwen/qwen3-tts
- Known Issue: https://github.com/Blaizzy/mlx-audio/issues/405

---

## 📝 更新日志

### v2.0 (2026-02-25)

- ✅ 添加情绪控制功能（8 种情绪）
- ✅ 添加 `tts` Shell 快捷命令
- ✅ 为妃愛和雷姆添加专属情绪配置
- ✅ 优化输出路径处理（--to-groupchat）
- ✅ 更新文档

### v1.0 (2026-02-22)

- ✅ 基础语音克隆功能
- ✅ bf16 模型支持
- ✅ 预设声音配置（rem, izumi）

---

## 💡 使用场景

1. **妃愛 Discord 语音发送**
   ```bash
   tts izumi "妃愛在这里哦～" --to-groupchat
   # 然后妃愛可以通过 message 工具发送该文件
   ```

2. **生成个性化语音**
   ```bash
   tts izumi "主人早安！" --emotion happy --output ~/morning.wav
   ```

3. **批量生成**
   ```bash
   for emotion in happy gentle surprised; do
     tts izumi "测试" --emotion $emotion --output ~/test_$emotion.wav
   done
   ```

---

## ⚠️ 注意事项

1. **必须使用 bf16 模型**，8bit 会产生静音
2. **需要 6-8GB RAM**，关闭其他应用以确保生成成功
3. **首次使用需要下载模型**（约 4GB）
4. **生成时间较长**（6-17 秒），请耐心等待

---

*为 singit 主人服务 💙*
