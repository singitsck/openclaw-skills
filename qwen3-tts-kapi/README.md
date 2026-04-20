# Qwen3-TTS Voice Cloning Skill

基於 kapi2800/qwen3-tts-apple-silicon 項目的 Qwen3-TTS 語音克隆 Skill，使用 bf16 模型避免靜音 Bug。

## 快速開始

```bash
# 使用預設雷姆聲音
python3 qwen3_kapi_bf16.py --text "你好" --voice rem

# 使用自定義參考音頻
python3 qwen3_kapi_bf16.py --text "你好" --ref_audio voice.wav --ref_text "參考文本"
```

## 詳細文檔

- [SKILL.md](SKILL.md) - 完整使用指南
- [EXPERIENCE.md](EXPERIENCE.md) - 經驗總結與問題排查

## 依賴

```bash
pip install mlx-audio huggingface-hub
```

## License

Apache 2.0
