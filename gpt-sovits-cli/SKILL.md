# SKILL.md - GPT-SoVITS CLI Tool

GPT-SoVITS 命令行工具封装，支持 Zero-shot TTS 语音生成和模型训练。

## Agent 共享配置 (多 Agent 使用)

### 環境要求
所有 Agent 使用此 Skill 時需要確保：

1. **GPT-SoVITS 已部署** 到 `/Volumes/SSD/GPT-SoVITS`
2. **SV 模型已下載** `pretrained_models/sv/pretrained_eres2netv2w24s4ep4.ckpt` (103MB)
3. **洛琪希模型文件** 存在於 `character_models/roxy/`

### 快速生成範例 (供其他 Agent 使用)

```python
import sys
sys.path.insert(0, '/Volumes/SSD/GPT-SoVITS')

import torch
import soundfile as sf
import numpy as np
from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config

def generate_roxy_voice(text, output_path, emotion="normal"):
    '''
    生成洛琪希語音
    
    Args:
        text: 日文文本
        output_path: 輸出文件路徑
        emotion: normal/shy/battle
    '''
    # 情緒配置
    emotions = {
        "normal": {
            "ref": "character_models/roxy/ref_audios/roxy_normal.wav",
            "text": "はいそうですねルディ身長大きくなりましたね"
        },
        "shy": {
            "ref": "character_models/roxy/ref_audios/roxy_shy.wav", 
            "text": "えっと、ルーデオスさん、その、ありがとうございました"
        },
        "battle": {
            "ref": "character_models/roxy/ref_audios/roxy_battle.wav",
            "text": "はあ姉よ全てを押し流しあらゆるものを駆逐せよ"
        }
    }
    
    config = TTS_Config("/Volumes/SSD/GPT-SoVITS/GPT_SoVITS/configs/tts_infer.yaml")
    tts = TTS(config)
    tts.init_vits_weights("/Volumes/SSD/GPT-SoVITS/GPT_SoVITS/character_models/roxy/洛琪希.pth")
    tts.init_t2s_weights("/Volumes/SSD/GPT-SoVITS/GPT_SoVITS/character_models/roxy/洛琪希.ckpt")
    
    emo = emotions.get(emotion, emotions["normal"])
    
    inputs = {
        "text": text,
        "text_lang": "ja",
        "ref_audio_path": f"/Volumes/SSD/GPT-SoVITS/GPT_SoVITS/{emo['ref']}",
        "prompt_text": emo["text"],
        "prompt_lang": "ja",
        "text_split_method": "cut5",
        "batch_size": 1,
        "speed_factor": 1.0,
    }
    
    all_audio = []
    sample_rate = 32000
    for item in tts.run(inputs):
        if isinstance(item, tuple):
            sample_rate, audio = item
            all_audio.append(audio)
    
    if all_audio:
        final_audio = np.concatenate(all_audio)
        sf.write(output_path, final_audio, sample_rate)
        return f"Generated: {output_path}, Duration: {len(final_audio)/sample_rate:.2f}s"
    return "Failed"

# 使用範例
generate_roxy_voice("ルディ、お疲れ様です", "/path/to/output.wav", "normal")
```

### 重要提醒
- **必須使用直接推理方式**，不要使用 API 方式 (API 會有問題)
- **參考音頻文本必須正確匹配**，否則會輸出火星語
- **SV 模型必須存在**，否則會有電音問題

## Overview

基于 GPT-SoVITS 项目的 CLI 封装，提供：
- 🎙️ **Zero-shot TTS**: 5秒样本即可克隆声音
- 🚀 **API 推理**: 通过 HTTP API 生成语音
- 🎓 **CLI 训练**: 支持 GPT 和 SoVITS 模型训练
- 📦 **模型管理**: 自动下载角色模型

## 关键经验 (Critical Lessons)

### ⚠️ 参考音频文本必须正确！
**这是最重要的经验！**

- ❌ **错误**: `prompt_text="你好"` (随便写) → 输出火星语
- ✅ **正确**: `prompt_text="嗯，這是只存在於理論中的舉動..."` (匹配音频内容) → 输出清晰中文

**原因**: GPT-SoVITS 需要准确的参考文本对齐音频，否则语义理解会混乱。

### 📁 模型存储结构
```
GPT_SoVITS/character_models/
├── {character_name}/
│   ├── GPT_models/{char}/{char}-e15.ckpt
│   └── VITS_models/{char}/{char}_e8_s1200.pth
└── ref_audios/
    └── {char}.wav  (参考音频)
```

### 🔧 常见问题修复

1. **chinese-hubert-base 下载失败**
   - 问题: `huggingface_hub.snapshot_download` 返回 404
   - 解决: 手动下载 `pytorch_model.bin`, `config.json`

2. **fast-langdetect 缓存目录**
   - 问题: `Cache directory not found`
   - 解决: `mkdir -p GPT_SoVITS/pretrained_models/fast_langdetect`

3. **torchcodec 缺失**
   - 问题: `TorchCodec is required`
   - 解决: `pip install torchcodec`

## Prerequisites

- **存储**: SSD 至少 20GB 空间 (模型 + 数据)
- **内存**: 8GB+ (CPU 推理)
- **Python**: 3.9-3.12
- **平台**: macOS (CPU) / Linux (GPU推荐)

## Installation

### 1. 安装 GPT-SoVITS (已部署到 SSD)
```bash
cd /Volumes/SSD
source venv/bin/activate
```

### 2. 启动 API 服务
```bash
python3 api_v2.py -a 127.0.0.1 -p 9880
```

### 3. 验证安装
```bash
curl http://127.0.0.1:9880/docs
```

## Quick Start

### Python API 使用

```python
from gpt_sovits_cli import generate_voice, get_character_preset

# 生成纳西妲语音
output_path = generate_voice(
    text="你好，我是纳西妲。",
    ref_audio_path="/Volumes/SSD/GPT-SoVITS/GPT_SoVITS/character_models/nahida/ref_audios/Nahida.wav",
    ref_text="嗯，這是只存在於理論中的舉動，我甚至不確定有誰敢做這樣的事",  # 必须匹配音频内容！
    output_path="output.wav"
)

# 使用洛琪希预设
preset = get_character_preset("roxy", "normal")
output_path = generate_voice(
    text="ルディ、お疲れ様です",
    ref_audio_path=preset["ref_audio"],
    ref_text=preset["ref_text"],
    output_path="output.wav"
)
```

### CLI 推理

```bash
# 使用预设角色 (洛琪希)
python3 scripts/gpt_sovits_cli.py generate \
  --text "ルディ、お疲れ様です" \
  --character roxy \
  --emotion normal \
  --output output.wav

# 使用不同情绪
python3 scripts/gpt_sovits_cli.py generate \
  --text "えっと、その..." \
  --character roxy \
  --emotion shy \
  --output output.wav

# 手动指定参数
python3 scripts/gpt_sovits_cli.py generate \
  --text "你好，我是纳西妲" \
  --ref-audio /path/to/Nahida.wav \
  --ref-text "嗯，這是只存在於理論中的舉動..." \
  --output output.wav
```

### 列出可用角色

```bash
python3 scripts/gpt_sovits_cli.py list
```

### 下载角色模型

```bash
python3 scripts/gpt_sovits_cli.py download \
  --repo BigPancake01/GPT-SoVITS_Mihoyo \
  --name nahida
```

## CLI 训练

### 训练 GPT 模型 (s1)
```bash
python3 GPT_SoVITS/s1_train.py -c configs/s1.yaml
```

### 训练 SoVITS 模型 (s2)
```bash
python3 GPT_SoVITS/s2_train.py -c configs/s2.yaml
```

**注意**: Mac 上训练很慢 (CPU)，建议在 Linux + GPU 环境训练。

## Available Models

### 本地角色模型 (SSD)
| 角色 | 来源 | 语言 | 模型位置 |
|------|------|------|----------|
| 💧 洛琪希 (Roxy) | 本地训练 | 日文 | `character_models/roxy/` |

**洛琪希预设配置:**
```python
# 使用预设生成
from gpt_sovits_cli import CHARACTER_PRESETS

roxy = CHARACTER_PRESETS["roxy"]
# 正常語氣
ref = roxy["ref_audios"]["normal"]
# 害羞語氣
ref = roxy["ref_audios"]["shy"]
# 戰鬥/魔法詠唱
ref = roxy["ref_audios"]["battle"]
```

**参考音频:**
| 情绪 | 文件 | 参考文本 |
|------|------|----------|
| normal | `roxy_normal.wav` | 「はいそうですねルディ身長大きくなりましたね」 |
| shy | `roxy_shy.wav` | 「えっと、ルーデオスさん、その、ありがとうございました」 |
| battle | `roxy_battle.wav` | 「はあ姉よ全てを押し流しあらゆるものを駆逐せよ」 |

### HuggingFace 角色模型
| 角色 | 来源 | 语言 |
|------|------|------|
| 纳西妲 (Nahida) | BigPancake01/GPT-SoVITS_Mihoyo | 中文 |
| 珊瑚宮心海 (Kokomi) | xiaoheiqaq/GPT-Sovits-models | 多语言 |
| 芙宁娜 (Furina) | PJMixers-Dev/GPT-SoVITS-Genshin-Impact-Furina | 多语言 |
| Anime Mini | cpumaxx/SoVITS-anime-mini-tts | 日文 |

## API Reference

### /tts - 文本转语音
```
GET /tts?text={text}&text_lang=zh&ref_audio_path={path}&prompt_text={ref_text}&prompt_lang=zh
```

**关键参数**:
- `text`: 要合成的文本
- `text_lang`: 文本语言 (zh/ja/en)
- `ref_audio_path`: 参考音频路径
- `prompt_text`: 参考音频的**准确文本内容** (重要！)
- `prompt_lang`: 参考音频语言

## Troubleshooting

### 输出火星语/乱码
- ✅ 检查 `prompt_text` 是否匹配参考音频内容
- ✅ 确保参考音频采样率正常 (32kHz)

### API 连接失败
- ✅ 检查服务是否运行: `curl http://127.0.0.1:9880/docs`
- ✅ 检查端口是否被占用

### 模型加载失败
- ✅ 检查模型路径是否正确
- ✅ 确保 chinese-hubert-base 文件完整

## References

- GPT-SoVITS GitHub: https://github.com/RVC-Boss/GPT-SoVITS
- 角色模型仓库: https://huggingface.co/BigPancake01/GPT-SoVITS_Mihoyo

## Author

整理自 singit 主人的 GPT-SoVITS 部署经验 💙
Date: 2026-02-26
