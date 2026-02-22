# Qwen3-TTS 語音克隆經驗總結

## 📋 問題背景

嘗試在 M2 Mac Mini 上本地運行 Qwen3-TTS 進行雷姆(Re:Zero)角色語音克隆。

## 🔍 遇到的問題

### 1. 8bit 量化模型靜音問題
- 使用 `mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit` 模型
- 生成檔案結構正確（RIFF/WAVE header、正確時長）但**無聲音**
- 這是 mlx-audio 已知 Bug (GitHub Issue #405)

### 2. 嘗試過的解決方案
| 方案 | 結果 |
|------|------|
| 使用 kapi2800 項目 | 底層仍用 mlx-audio，同樣問題 |
| 使用不同參考音頻 | 無效 |
| 使用官方 mlx-audio CLI | 同樣靜音 |

## ✅ 最終解決方案

### 使用 bf16 模型（非 8bit 量化）

```python
# ✅ 正確配置
model = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"

# ❌ 錯誤配置（產生靜音）
model = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
```

### 修改 kapi2800 項目

修改 `main.py` 中的模型配置：
```python
MODELS = {
    # Pro (1.7B) - 使用 bf16 而非 8bit
    "3": {"name": "Voice Cloning", "folder": "Qwen3-TTS-12Hz-1.7B-Base-bf16", ...},
    ...
}
```

## 📊 性能對比

| 模型 | 大小 | 記憶體 | 生成時間 | 結果 |
|------|------|--------|----------|------|
| 8bit | 2.3GB | 3-4GB | ~7秒 | ❌ 靜音 |
| **bf16** | **4GB** | **6-8GB** | **~17秒** | ✅ **正常** |

## 🎯 關鍵發現

1. **mlx-audio Issue #405**: Voice Cloning with 8bit models produces silent audio
2. **bf16 模型正常工作**: 雖然資源占用較多，但有聲音
3. **kapi2800 項目可用**: 只需修改模型配置為 bf16

## 📁 參考音頻

- 來源: Bilibili BV1v7411L7Ux
- 時長: 10秒
- 文本: 「ここから始めましょう。1から…いいえ、ゼロから!こんにちは、今日もご一緒できて光栄です」
- 位置: `~/.openclaw/references/rem_reference.wav`

## 🔧 使用方法

```bash
# 1. 確保模型已下載
huggingface-cli download \
  mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16 \
  --local-dir models/Qwen3-TTS-12Hz-1.7B-Base-bf16

# 2. 使用 tool 生成
python3 ~/.openclaw/tools/qwen3_kapi_bf16.py \
  --text "你好，我是雷姆" \
  --ref_audio ~/.openclaw/references/rem_reference.wav \
  --ref_text "ここから始めましょう..." \
  --output ~/rem_voice.wav
```

## 💡 經驗教訓

1. **不要盲目追求量化**: 8bit 雖然省資源，但有 Bug
2. **bf16 是穩定選擇**: Apple Silicon 上 bf16 是最佳平衡
3. **參考音頻很重要**: 雷姆的日文台詞效果最佳
