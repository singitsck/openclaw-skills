# MoE TTS 部署经验总结

## 📋 项目概述
成功在 Mac 本地部署了 MoE TTS (Mixture of Experts TTS)，支持多个动漫角色语音生成。

## 🎯 关键发现

### 1. 不同角色使用不同的 Text Cleaners

| Role | Cleaner | 文本格式 | 示例 |
|------|---------|----------|------|
| 1 | `japanese_cleaners2` | 纯日文 | `おはよう` |
| 5 | `zh_ja_mixture_cleaners` | 带标记 | `[JA]おはよう[/JA]` |

**重要教训：**
- Role 1 不需要 `[JA]` 标记，直接输入日文即可
- Role 5 必须使用 `[JA]` 标记，否则输出静音

### 2. 静默/短音频问题排查

**症状：** 音频只有 0.01-0.5 秒，或者完全静音

**原因：**
1. Text cleaner 不匹配
2. Sequence 长度太短（正常应该 > 50 tokens）

**诊断方法：**
```python
seq = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
print(f"Sequence长度: {len(seq)}")  # 应该 > 50
```

### 3. 模型下载

```bash
cd ~/.openclaw/moe-tts
# 下载特定角色
git lfs pull --include="saved_model/1/*"
git lfs pull --include="saved_model/5/*"
```

### 4. 依赖安装

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install librosa numba scipy phonemizer
pip install pyopenjtalk jamo pypinyin jieba cn2an
```

## 📊 测试结果

| 角色 | 角色ID | 测试文本 | 时长 | 质量 |
|------|--------|----------|------|------|
| 在原七海 | 5 | こんにちは | 3.97s | ✅ 良好 |
| 和泉妃愛 | 1 | おはようございます | 2.55s | ✅ 良好 |

## 🛠️ 创建的工具

### moe_tts.py CLI 工具
```bash
# 生成语音
python3 scripts/moe_tts.py --text "おはよう" --role 1 --speaker "和泉妃愛"

# 列出角色
python3 scripts/moe_tts.py --role 1 --list

# Python API
from scripts.moe_tts import generate_voice
generate_voice("おはよう", role_id=1, speaker="和泉妃愛")
```

### 自动语言检测
```python
def format_text_for_role(text, role_id):
    cleaner = detect_cleaner_type(role_id)
    if cleaner == 'zh_ja_mixture_cleaners':
        if any('\u3040' <= c <= '\u309f' for c in text):
            return f"[JA]{text}[JA]"
    return text
```

## 📝 最佳实践

1. **总是检查 cleaner 类型**
   ```python
   cleaners = hps.data.text_cleaners
   print(f"Cleaner: {cleaners}")
   ```

2. **验证 sequence 长度**
   - 如果 < 10，说明文本处理有问题
   - 正常应该 50-200 tokens

3. **使用 CPU 而不是 MPS**
   - MPS 在 Mac 上可能导致奇怪的问题
   - 强制使用 `device = torch.device('cpu')`

## 🎭 可用角色

### Role 1 (Japanese Cleaners)
- 和泉妃愛
- 常盤華乃
- 錦あすみ
- 鎌倉詩桜
- 竜閑天梨
- 和泉里
- 新川広夢
- 聖莉々子

### Role 5 (ZH/JA Mixture)
- 綾地寧々
- 在原七海
- 小茸
- 唐乐吟

## 🔗 参考链接

- HuggingFace: https://huggingface.co/spaces/skytnt/moe-tts
- GitHub Skill: https://github.com/singitsck/openclaw-skills/tree/main/moe-tts

## 👤 作者

为 singit 主人服务 💙
日期: 2026-02-25
