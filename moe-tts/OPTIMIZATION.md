# MoE TTS 语音优化指南

## 🎙️ 关键参数调优

### 1. Inference 参数 (最重要)

在 `model.infer()` 中的三个关键参数：

```python
audio = model.infer(
    x_tst, x_tst_lengths,
    sid=sid,
    noise_scale=0.667,      # 控制音高/音质变化
    noise_scale_w=0.8,      # 控制语速变化
    length_scale=1.0 / speed  # 控制整体语速
)[0][0, 0].data.cpu().float().numpy()
```

| 参数 | 默认值 | 范围 | 效果 |
|------|--------|------|------|
| `noise_scale` | 0.667 | 0.0 - 1.0 | 越高越自然，但可能失真 |
| `noise_scale_w` | 0.8 | 0.0 - 1.0 | 控制语速波动 |
| `length_scale` | 1.0 | 0.5 - 2.0 | <1 更快，>1 更慢 |

### 推荐配置

```python
# 更自然的语音
noise_scale=0.8, noise_scale_w=0.8, length_scale=1.0

# 更稳定的语音
noise_scale=0.5, noise_scale_w=0.5, length_scale=1.0

# 更慢的清晰语音
noise_scale=0.667, noise_scale_w=0.8, length_scale=1.2
```

---

## 📝 文本优化

### 1. 日文优化

**好的文本：**
- 使用完整的句子
- 句尾加语气词：「ね」「よ」「わ」「か」
- 避免太短的文本（至少 10 个字符）

```python
# ✅ 好
"おはようございます、和泉妃愛ですね"
"今日も一日頑張りましょうよ"

# ❌ 不好
"おはよう"  # 太短
"はい"      # 太短
```

### 2. 避免的问题

- ❌ 混合语言（中日混用）
- ❌ 太长的句子（>50 字符）
- ❌ 特殊符号过多
- ❌ 英文单词

---

## 🔧 音频后处理

### 1. 音量标准化

```python
import numpy as np

# 自动增益控制
def normalize_audio(audio, target_db=-20):
    """标准化音频到目标分贝"""
    current_db = 20 * np.log10(np.max(np.abs(audio)))
    gain = 10 ** ((target_db - current_db) / 20)
    return np.clip(audio * gain, -1.0, 1.0)
```

### 2. 降噪（如果需要）

```python
import noisereduce as nr

# 简单降噪
reduced_noise = nr.reduce_noise(y=audio, sr=sample_rate)
```

### 3. 淡入淡出

```python
def fade_in_out(audio, fade_length=1000):
    """添加淡入淡出效果"""
    fade_in = np.linspace(0, 1, fade_length)
    fade_out = np.linspace(1, 0, fade_length)
    
    audio[:fade_length] *= fade_in
    audio[-fade_length:] *= fade_out
    return audio
```

---

## 🎯 角色特定优化

### 和泉妃愛 (Role 1)

```python
# 妃愛推荐参数
config = {
    "noise_scale": 0.75,      # 稍微活泼一点
    "noise_scale_w": 0.7,     # 稳定但自然
    "length_scale": 1.0,      # 正常语速
    "text_suffix": "ね"       # 加妃愛口癖
}
```

### 在原七海 (Role 5)

```python
# 七海推荐参数
config = {
    "noise_scale": 0.6,       # 更温柔
    "noise_scale_w": 0.8,
    "length_scale": 1.1,      # 稍微慢一点
}
```

**🌏 混合语言支持！**

Role 5 支持同时说日文和中文：

```python
# 日文 + 中文
"[JA]おはようございます。[JA][ZH]你好，我是七海。[ZH]"

# 中文 + 日文  
"[ZH]你好，我是七海。[ZH][JA]よろしくね。[JA]"
```

- `[JA]...[/JA]` - 日文段落
- `[ZH]...[/ZH]` - 中文段落

---

## 📊 质量评估

### 快速检查清单

- [ ] 音频长度合理（与文本长度成正比）
- [ ] 音量适中（不爆音，不太小）
- [ ] 无明显杂音
- [ ] 语速自然
- [ ] 发音清晰

### 诊断代码

```python
def diagnose_audio(audio, sample_rate=22050):
    """诊断音频质量"""
    duration = len(audio) / sample_rate
    max_amp = np.max(np.abs(audio))
    mean_amp = np.mean(np.abs(audio))
    
    print(f"时长: {duration:.2f}s")
    print(f"最大振幅: {max_amp:.4f} (应该 < 1.0)")
    print(f"平均振幅: {mean_amp:.4f} (应该 > 0.01)")
    
    if max_amp > 0.99:
        print("⚠️ 可能有爆音")
    if mean_amp < 0.01:
        print("⚠️ 音量可能太小")
    if duration < 1.0:
        print("⚠️ 时长太短")
```

---

## 🚀 高级技巧

### 1. 多次采样选择最佳

```python
def generate_best_voice(text, speaker, n_samples=3):
    """生成多个样本，选择质量最好的"""
    best_audio = None
    best_score = -1
    
    for i in range(n_samples):
        audio = generate_voice(text, speaker)
        # 评分：音量适中 + 长度合理
        score = calculate_quality_score(audio)
        if score > best_score:
            best_score = score
            best_audio = audio
    
    return best_audio
```

### 2. 动态参数调整

```python
def adjust_params_by_text(text):
    """根据文本长度动态调整参数"""
    length = len(text)
    
    if length < 10:
        # 短文本：慢一点，更清晰
        return {"length_scale": 1.2, "noise_scale": 0.6}
    elif length > 40:
        # 长文本：稍微快一点
        return {"length_scale": 0.9, "noise_scale": 0.7}
    else:
        # 正常
        return {"length_scale": 1.0, "noise_scale": 0.667}
```

---

## 📝 总结

| 优化方面 | 推荐做法 |
|---------|----------|
| **参数** | noise_scale=0.6-0.8, length_scale=1.0-1.2 |
| **文本** | 完整句子，加语气词，避免太短 |
| **后处理** | 音量标准化，淡入淡出 |
| **质量** | 多次采样，选择最佳 |

---

*为 singit 主人服务 💙*
