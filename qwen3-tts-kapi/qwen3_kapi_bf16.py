#!/usr/bin/env python3
"""
Qwen3-TTS Voice Cloning Tool (kapi2800 + bf16)

基於 kapi2800/qwen3-tts-apple-silicon 項目，使用 bf16 模型避免靜音 Bug。

用法:
    python3 qwen3_kapi_bf16.py --text "你好" --ref_audio voice.wav --ref_text "參考文本"
    python3 qwen3_kapi_bf16.py --text "你好" --voice rem  # 使用預設聲音

作者: 雷姆
日期: 2026-02-22
"""

import os
import sys
import time
import argparse
from pathlib import Path

# 預設配置
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.openclaw/tts_output")
DEFAULT_VOICES_DIR = os.path.expanduser("~/.openclaw/references")
DEFAULT_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"

# 預設聲音配置
PRESET_VOICES = {
    "rem": {
        "name": "雷姆 (Rem)",
        "audio": "rem/rem_reference.wav",
        "text": "ここから始めましょう。1から…いいえ、ゼロから",
        "description": "Re:Zero 雷姆角色聲音，日系女僕風格"
    },
    "izumi": {
        "name": "和泉妃愛 (Izumi Hiyori)",
        "audio": "izumi_hiyori/reference.wav",
        "text": "いやめっちゃ持ちあげるけども、普段通りでいいよ普段通りで。私と話すときみたいに",
        "description": "和泉妃愛角色聲音，活潑可愛的學妹風格，帶有ひよひよ口頭禪"
    }
}


def find_voice_file(audio_path: str) -> str:
    """
    查找聲音文件，支持多個路徑：
    1. ~/.openclaw/references/
    2. 腳本所在目錄的 references/
    3. 當前工作目錄的 references/
    """
    # 可能的路徑
    possible_paths = [
        os.path.join(DEFAULT_VOICES_DIR, audio_path),
        os.path.join(os.path.dirname(__file__), "references", audio_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "references", audio_path),
        os.path.join(os.getcwd(), "references", audio_path),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 如果都找不到，返回第一個路徑（讓後續報錯）
    return possible_paths[0]


def check_model_downloaded(model_id: str) -> bool:
    """檢查模型是否已下載"""
    from huggingface_hub import try_to_load_from_cache
    
    try:
        result = try_to_load_from_cache(model_id, "config.json")
        return result is not None and str(result) != "_CACHED_NO_EXIST_"
    except:
        return False


def download_model(model_id: str):
    """下載模型"""
    from huggingface_hub import snapshot_download
    
    print(f"📥 下載模型: {model_id}")
    print("這可能需要幾分鐘（約 4GB）...")
    
    snapshot_download(repo_id=model_id, local_files_only=False)
    print("✅ 模型下載完成")


def generate_voice(
    text: str,
    ref_audio: str,
    ref_text: str,
    output_path: str = None,
    model_id: str = DEFAULT_MODEL,
    verbose: bool = True
) -> str:
    """
    生成語音
    
    Args:
        text: 要合成的文本
        ref_audio: 參考音頻路徑
        ref_text: 參考音頻對應的文本
        output_path: 輸出路徑（可選）
        model_id: 模型 ID
        verbose: 是否顯示詳細信息
    
    Returns:
        生成的音頻文件路徑
    """
    from mlx_audio.tts.utils import load_model
    from mlx_audio.tts.generate import generate_audio
    
    # 檢查參考音頻
    if not os.path.exists(ref_audio):
        raise FileNotFoundError(f"參考音頻不存在: {ref_audio}")
    
    # 檢查並下載模型
    if not check_model_downloaded(model_id):
        if verbose:
            print(f"🔍 模型未下載，開始下載...")
        download_model(model_id)
    
    if verbose:
        print(f"🎙️ Qwen3-TTS Voice Cloning")
        print(f"=" * 60)
        print(f"📝 文本: {text}")
        print(f"🔊 參考: {ref_audio}")
        print(f"🤖 模型: {model_id}")
        print()
        print("📦 載入模型...")
    
    # 載入模型
    model = load_model(model_id)
    
    if verbose:
        print("✅ 模型載入完成")
        print()
        print("🎙️ 生成中...")
    
    # 準備輸出
    if output_path is None:
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        output_prefix = os.path.join(DEFAULT_OUTPUT_DIR, f"qwen3_{int(time.time())}")
    else:
        output_prefix = output_path.replace(".wav", "")
    
    # 生成
    start_time = time.time()
    generate_audio(
        model=model,
        text=text,
        ref_audio=ref_audio,
        ref_text=ref_text,
        file_prefix=output_prefix,
        audio_format="wav"
    )
    elapsed = time.time() - start_time
    
    output_file = f"{output_prefix}_000.wav"
    
    if verbose:
        print()
        print(f"✅ 生成完成!")
        print(f"⏱️ 耗時: {elapsed:.1f}秒")
        print(f"🎵 輸出: {output_file}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Qwen3-TTS 語音克隆工具 (kapi2800 + bf16)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --text "你好" --ref_audio voice.wav --ref_text "參考文本"
  %(prog)s --text "主人好" --voice rem --output ~/rem.wav
  %(prog)s --list-voices
        """
    )
    
    parser.add_argument("--text", "-t", required=True, help="要合成的文本")
    parser.add_argument("--ref_audio", "-a", help="參考音頻路徑")
    parser.add_argument("--ref_text", "-r", help="參考音頻對應的文本")
    parser.add_argument("--voice", "-v", help=f"使用預設聲音: {', '.join(PRESET_VOICES.keys())}")
    parser.add_argument("--output", "-o", help="輸出文件路徑（可選）")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"模型ID（默認: {DEFAULT_MODEL}）")
    parser.add_argument("--list-voices", action="store_true", help="列出所有預設聲音")
    parser.add_argument("--quiet", "-q", action="store_true", help="安靜模式")
    
    args = parser.parse_args()
    
    # 列出預設聲音
    if args.list_voices:
        print("🎭 可用預設聲音:")
        for key, info in PRESET_VOICES.items():
            print(f"  {key}: {info['name']}")
            print(f"    {info['description']}")
            print()
        return
    
    # 處理預設聲音
    if args.voice:
        if args.voice not in PRESET_VOICES:
            print(f"❌ 未知聲音: {args.voice}")
            print(f"可用聲音: {', '.join(PRESET_VOICES.keys())}")
            sys.exit(1)
        
        voice_info = PRESET_VOICES[args.voice]
        ref_audio = find_voice_file(voice_info["audio"])
        ref_text = voice_info["text"]
    else:
        if not args.ref_audio or not args.ref_text:
            print("❌ 請提供 --ref_audio 和 --ref_text，或使用 --voice 選擇預設聲音")
            sys.exit(1)
        ref_audio = args.ref_audio
        ref_text = args.ref_text
    
    # 生成
    try:
        output_file = generate_voice(
            text=args.text,
            ref_audio=ref_audio,
            ref_text=ref_text,
            output_path=args.output,
            model_id=args.model,
            verbose=not args.quiet
        )
        
        if args.quiet:
            print(output_file)
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
