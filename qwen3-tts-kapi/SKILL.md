# SKILL.md - Qwen3-TTS Voice Cloning v2.0

Generate high-quality voice cloning using Qwen3-TTS with kapi2800 wrapper, bf16 models, and emotion control on Apple Silicon.

## Overview

This skill provides voice cloning capabilities using Qwen3-TTS on Apple Silicon Macs. It uses the kapi2800/qwen3-tts-apple-silicon project with bf16 models to avoid the silent audio bug present in 8bit quantized models.

**v2.0 New Features:**
- 🎭 **Emotion Control** - Add emotional tone to generated speech
- 🚀 **Shell Wrapper** - Convenient `tts` command for quick generation
- 🎯 **Per-Voice Emotions** - Custom emotion prompts for each character

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.10+
- mlx-audio installed
- ~4GB disk space for bf16 model
- ~6-8GB RAM during generation

## Installation

### 1. Install Dependencies

```bash
pip install mlx-audio huggingface-hub
```

### 2. Download bf16 Model

```bash
huggingface-cli download \
  mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --local-dir ~/.cache/qwen3-tts/bf16
```

### 3. Add tts Command to PATH

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/.agents/skills/qwen3-tts-kapi/scripts:$PATH"
```

## Usage

### Quick Start with Shell Command

```bash
# Basic usage
tts izumi "ひよひよ～主人好！"

# With emotion
tts izumi "太好了！" --emotion happy
tts rem "主人晚安～" --emotion gentle

# Custom output
tts izumi "測試語音" --output ~/test.wav

# Output to workspace-groupchat (for 妃愛)
tts izumi "妃愛在這裡哦～" --to-groupchat
```

### Using Python Script Directly

```bash
# Method 1: Using v2.0 with emotion support
python3 ~/.agents/skills/qwen3-tts-kapi/scripts/qwen3_kapi_v2.py \
  --text "你好，我是雷姆" \
  --voice rem \
  --emotion happy \
  --output ~/output.wav

# Method 2: Legacy script (no emotion)
python3 ~/.agents/skills/qwen3-tts-kapi/scripts/qwen3_kapi_bf16.py \
  --text "你好，我是雷姆" \
  --voice rem \
  --output ~/output.wav
```

### Python API Usage

```python
from qwen3_kapi_v2 import generate_voice, PRESET_VOICES

# Generate with emotion
output = generate_voice(
    text="主人，今天過得怎麼樣？",
    ref_audio="~/.openclaw/references/izumi_hiyori/reference.wav",
    ref_text="いやめっちゃ持ちあげるけども、普段通りでいいよ普段通りで",
    output_path="~/output.wav",
    emotion="happy"  # 新增：情緒控制
)
print(f"Generated: {output}")
```

## Available Preset Voices

### 🌸 Izumi Hiyori (和泉妃愛)
- **Character**: 和泉妃愛 from 恋愛、はじめまして
- **Style**: 活潑可愛的學妹，帶有「ひよひよ」口頭禪
- **Reference**: ~/.openclaw/references/izumi_hiyori/reference.wav
- **Text**: 「いやめっちゃ持ちあげるけども、普段通りでいいよ普段通りで」

**Supported Emotions:**
| Emotion | Description | Sample Text |
|---------|-------------|-------------|
| normal | 正常語氣 | 「いやめっちゃ持ちあげるけども...」 |
| happy | 開心、興奮 | 「ひよひよ～！今天もいい天気だね～」 |
| gentle | 溫柔、柔和 | 「主人、お疲れ様。お茶淹れてあげるね」 |
| sad | 悲傷、難過 | 「そんな…ひよひよ…」 |
| teasing | 調皮、捉弄 | 「へへ～、主人ったら照れてる？ひよひよ～」 |
| surprised | 驚訝、震驚 | 「えっ！？マジで！？ひよひよ！？」 |
| shy | 害羞、靦腆 | 「あ、あの…その…ひよひよ…」 |
| excited | 超級興奮 | 「わぁ～！すっごい！ひよひよ～！」 |

### 💙 Rem (雷姆)
- **Character**: Rem from Re:Zero
- **Style**: 日系女僕，溫柔忠誠
- **Reference**: ~/.openclaw/references/rem/rem_reference.wav
- **Text**: 「ここから始めましょう。1から…いいえ、ゼロから」

**Supported Emotions:**
| Emotion | Description |
|---------|-------------|
| normal | 正常語氣 |
| happy | 開心興奮 |
| gentle | 溫柔體貼 |
| sad | 悲傷難過 |
| determined | 堅定決心 |

### 💧 Roxy (洛琪希·米格路迪亞)
- **Character**: 洛琪希·米格路迪亞 from 無職轉生
- **Style**: 水聖級魔術師，冷靜沉著的藍髮師傅，帶有魔術詠唱的莊嚴感
- **Reference**: ~/.openclaw/references/roxy/reference.wav
- **Text**: 「はいそうですねルディ身長大きくなりましたね」

**Supported Emotions:**
| Emotion | Description | Sample Text |
|---------|-------------|-------------|
| normal | 正常語氣 | 「はいそうですねルディ身長大きくなりましたね」 |
| happy | 開心、欣慰 | 「おめでとうございますこれであなたは彗星級魔術師です」 |
| gentle | 溫柔、安慰 | 「すぐに怖くなくなりますよ。私がついていますから安心してください」 |
| sad | 悲傷、遺憾 | 「残念です。これで本当に私が教えられることもなくなってしまいました」 |
| shy | 害羞、靦腆 | 「えっと、ルーデオスさん、その、ありがとうございました」 |
| teasing | 調皮、捉弄 | 「ははーん、さては怖いんですねー」 |
| proud | 自豪、驕傲 | 「ちっちゃくありませんあれは私の髪を見て驚いてたんですよ」 |
| worried | 擔心、憂慮 | 「そうですね落ち込んでいるというのは少し心配ですが」 |
- **Reference**: ~/.openclaw/references/rem/rem_reference.wav
- **Text**: 「ここから始めましょう。1から…いいえ、ゼロから」

**Supported Emotions:**
| Emotion | Description |
|---------|-------------|
| normal | 正常語氣 |
| happy | 開心興奮 |
| gentle | 溫柔體貼 |
| sad | 悲傷難過 |
| determined | 堅定決心 |

## Emotion System

### How It Works

Qwen3-TTS supports emotion control through reference text modification. The v2.0 script uses character-specific emotion prompts to guide the voice generation.

### Available Emotions (Global)

| Emotion | 描述 | Use Case |
|---------|------|----------|
| `normal` | 正常語氣 | 日常對話 |
| `happy` | 開心、興奮 | 好消息、慶祝 |
| `gentle` | 溫柔、柔和 | 安慰、晚安 |
| `sad` | 悲傷、難過 | 失落、道歉 |
| `angry` | 生氣、憤怒 | 抱怨、抗議 |
| `surprised` | 驚訝、震驚 | 意外、驚喜 |
| `shy` | 害羞、靦腆 | 表白、撒嬌 |
| `teasing` | 調皮、捉弄 | 開玩笑、惡作劇 |

### Adding Custom Emotions

Edit `~/.agents/skills/qwen3-tts-kapi/scripts/qwen3_kapi_v2.py`:

```python
# Add to EMOTION_PROMPTS
custom_emotions = {
    "excited": {
        "prefix": "",
        "suffix": "（超級興奮地）",
        "description": "超級興奮的語氣"
    }
}

# Add per-voice emotion text in PRESET_VOICES
"izumi": {
    "emotions": {
        "excited": "わぁ～！すっごい！ひよひよ～！"
    }
}
```

## Parameters

### Shell Command (`tts`)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `voice` | 聲音名稱 (rem, izumi) | `tts izumi "..."` |
| `text` | 要合成的文本 | `tts izumi "你好"` |
| `--emotion, -e` | 情緒風格 | `--emotion happy` |
| `--output, -o` | 輸出文件路徑 | `--output ~/out.wav` |
| `--to-groupchat` | 輸出到 workspace-groupchat | `--to-groupchat` |
| `--quiet, -q` | 安靜模式 | `--quiet` |

### Python Script Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--text` | Text to synthesize | Required |
| `--voice` | Preset voice name | None |
| `--emotion` | Emotion style | `normal` |
| `--ref_audio` | Reference audio path | Required if no --voice |
| `--ref_text` | Reference text | Required if no --voice |
| `--output` | Output file path | Auto-generated |
| `--model` | Model ID | Qwen3-TTS-12Hz-1.7B-Base-bf16 |
| `--quiet` | Suppress output | False |

## Important Notes

⚠️ **Use bf16 models only**: 8bit quantized models produce silent audio due to mlx-audio Issue #405.

### Why bf16?

| Model | Size | Memory | Time | Result |
|-------|------|--------|------|--------|
| 8bit | 2.3GB | 3-4GB | ~7s | ❌ Silent |
| **bf16** | **4GB** | **6-8GB** | **~17s** | ✅ **Normal** |

## Troubleshooting

### Issue: Silent Audio
**Solution**: Ensure you're using bf16 model, not 8bit.

### Issue: Model not found
**Solution**: Run `huggingface-cli download` to download the model first.

### Issue: Out of memory
**Solution**: Close other applications. bf16 requires 6-8GB RAM.

### Issue: Permission denied on `tts` command
**Solution**: 
```bash
chmod +x ~/.agents/skills/qwen3-tts-kapi/scripts/tts
```

## File Structure

```
~/.agents/skills/qwen3-tts-kapi/
├── SKILL.md                    # This file
├── scripts/
│   ├── qwen3_kapi_bf16.py     # Legacy v1.0 script
│   ├── qwen3_kapi_v2.py       # New v2.0 with emotion support
│   └── tts                     # Shell wrapper for quick access
```

## References

- kapi2800 Project: https://github.com/kapi2800/qwen3-tts-apple-silicon
- mlx-audio: https://github.com/Blaizzy/mlx-audio
- Qwen3-TTS: https://huggingface.co/collections/Qwen/qwen3-tts
- Known Issue: https://github.com/Blaizzy/mlx-audio/issues/405

## License

Apache 2.0 (same as Qwen3-TTS)

## Author

Created by 雷姆 for singit 主人 💙
Version 2.0 - 2026-02-25
