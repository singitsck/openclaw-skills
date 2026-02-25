# SKILL.md - MoE TTS Voice Generation

Generate character voices using MoE TTS (Mixture of Experts Text-to-Speech) with multiple anime-style characters.

## Overview

MoE TTS is a multi-speaker, multi-lingual TTS system featuring anime/game characters. This skill provides easy voice generation for agents.

**Characters Available:**
- Role 1: 和泉妃愛, 常盤華乃, 錦あすみ, etc. (Japanese cleaners)
- Role 5: 綾地寧々, 在原七海, etc. (ZH/JA mixture cleaners)

## Prerequisites

- Python 3.10+
- PyTorch
- ~150MB per character model

## Installation

```bash
# Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install librosa numba scipy pyopenjtalk jamo pypinyin phonemizer
```

## Quick Start

```bash
# Generate voice using the CLI
python3 scripts/moe_tts.py --text "こんにちは" --role 1 --speaker "和泉妃愛"

# Or with auto language detection
python3 scripts/moe_tts.py --text "おはよう" --role 1 --speaker "和泉妃愛" --output hello.wav
```

## Python API

```python
from scripts.moe_tts import generate_voice

# Generate voice
output_path = generate_voice(
    text="おはようございます",
    role_id=1,
    speaker="和泉妃愛",
    output_path="output.wav"
)
```

## Role Reference

| Role | Speakers | Cleaner | Language Format |
|------|----------|---------|-----------------|
| 1 | 和泉妃愛, 常盤華乃, etc. | japanese_cleaners2 | Plain Japanese |
| 5 | 綾地寧々, 在原七海, etc. | zh_ja_mixture_cleaners | Use [JA]...[/JA] |

## Important Notes

⚠️ **Critical Differences Between Roles:**

### Role 1 (japanese_cleaners2)
- Use plain Japanese text: `おはようございます`
- Do NOT use `[JA]` markers
- Optimized for pure Japanese

### Role 5 (zh_ja_mixture_cleaners)
- MUST use language markers: `[JA]おはよう[/JA]`
- Supports mixed Chinese/Japanese
- Required for proper text processing

## Model Download

Models are downloaded from HuggingFace on first use:
```bash
cd ~/.openclaw/moe-tts
git lfs pull --include="saved_model/1/*"
```

## Troubleshooting

### Silent/Short Output
- Check if using correct text format for the role
- Role 1: Plain text
- Role 5: Must use [JA] markers

### Model Not Found
- Ensure models are downloaded via git lfs
- Check `saved_model/{role_id}/model.pth` exists

## References

- Original MoE TTS: https://huggingface.co/spaces/skytnt/moe-tts
- Based on VITS architecture

## Author

Created for singit 主人 💙
