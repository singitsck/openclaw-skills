# SKILL.md - Qwen3-TTS Voice Cloning

Generate high-quality voice cloning using Qwen3-TTS with kapi2800 wrapper and bf16 models on Apple Silicon.

## Overview

This skill provides voice cloning capabilities using Qwen3-TTS on Apple Silicon Macs. It uses the kapi2800/qwen3-tts-apple-silicon project with bf16 models to avoid the silent audio bug present in 8bit quantized models.

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

### 3. Clone kapi2800 Project (Optional)

```bash
git clone https://github.com/kapi2800/qwen3-tts-apple-silicon.git ~/qwen3-tts-apple-silicon
```

## Usage

### Method 1: Using the Tool Script

```bash
python3 ~/.openclaw/tools/qwen3_kapi_bf16.py \
  --text "你好，我是雷姆" \
  --voice rem \
  --output ~/output.wav
```

### Method 2: Direct Python Usage

```python
from tools.qwen3_kapi_bf16 import generate_voice

output = generate_voice(
    text="你好，我是雷姆",
    ref_audio="~/.openclaw/references/rem_reference.wav",
    ref_text="ここから始めましょう。1から…いいえ、ゼロから",
    output_path="~/output.wav"
)
print(f"Generated: {output}")
```

### Method 3: Using mlx-audio CLI

```bash
python -m mlx_audio.tts.generate \
  --model mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --text "你好" \
  --ref_audio voice.wav \
  --ref_text "reference text" \
  --file_prefix output
```

## Available Preset Voices

### Rem (雷姆)
- **Character**: Rem from Re:Zero
- **Style**: Japanese maid, gentle and loyal
- **Reference**: Bilibili BV1v7411L7Ux
- **Text**: 「ここから始めましょう。1から…いいえ、ゼロから」

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--text` | Text to synthesize | Required |
| `--ref_audio` | Reference audio path | Required if no --voice |
| `--ref_text` | Reference text | Required if no --voice |
| `--voice` | Preset voice name (rem) | None |
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

## References

- kapi2800 Project: https://github.com/kapi2800/qwen3-tts-apple-silicon
- mlx-audio: https://github.com/Blaizzy/mlx-audio
- Qwen3-TTS: https://huggingface.co/collections/Qwen/qwen3-tts
- Known Issue: https://github.com/Blaizzy/mlx-audio/issues/405

## License

Apache 2.0 (same as Qwen3-TTS)

## Author

Created by 雷姆 for singit 主人 💙
