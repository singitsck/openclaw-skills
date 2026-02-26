#!/usr/bin/env python3
"""
Qwen3-TTS Voice Cloning Tool (kapi2800 + bf16) v2.0

基於 kapi2800/qwen3-tts-apple-silicon 項目，使用 bf16 模型避免靜音 Bug。
新增：情緒控制、多種預設語音、便捷的 Shell 調用接口

用法:
    # 基礎用法
    python3 qwen3_kapi_bf16.py --text "你好" --voice izumi
    
    # 帶情緒
    python3 qwen3_kapi_bf16.py --text "太好了！" --voice izumi --emotion happy
    
    # 自定義輸出
    python3 qwen3_kapi_bf16.py --text "主人晚安" --voice izumi --output ~/goodnight.wav --emotion gentle

作者: 雷姆
日期: 2026-02-25
版本: 2.0
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

# 預設配置
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.openclaw/tts_output")
DEFAULT_VOICES_DIR = os.path.expanduser("~/.openclaw/references")
DEFAULT_MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16"

# 情緒模板 - 用於調整語氣和參考文本
EMOTION_PROMPTS = {
    "normal": {
        "prefix": "",
        "suffix": "",
        "description": "正常語氣"
    },
    "happy": {
        "prefix": "",
        "suffix": "（開心地）",
        "description": "開心、興奮的語氣"
    },
    "gentle": {
        "prefix": "",
        "suffix": "（溫柔地）",
        "description": "溫柔、柔和的語氣"
    },
    "sad": {
        "prefix": "",
        "suffix": "（難過地）",
        "description": "悲傷、難過的語氣"
    },
    "angry": {
        "prefix": "",
        "suffix": "（生氣地）",
        "description": "生氣、憤怒的語氣"
    },
    "surprised": {
        "prefix": "",
        "suffix": "（驚訝地）",
        "description": "驚訝、震驚的語氣"
    },
    "shy": {
        "prefix": "",
        "suffix": "（害羞地）",
        "description": "害羞、靦腆的語氣"
    },
    "teasing": {
        "prefix": "",
        "suffix": "（調皮地）",
        "description": "調皮、捉弄人的語氣"
    }
}

# 預設聲音配置
PRESET_VOICES = {
    "rem": {
        "name": "雷姆 (Rem)",
        "audio": "rem/rem_reference.wav",
        "text": "ここから始めましょう。1から…いいえ、ゼロから",
        "description": "Re:Zero 雷姆角色聲音，日系女僕風格",
        "emotions": {
            "normal": "ここから始めましょう。1から…いいえ、ゼロから",
            "happy": "スバルくん、おかえりなさい！",
            "gentle": "スバルくんのこと、信じてます",
            "sad": "スバルくん…どうして…",
            "determined": "雷ムは、スバルくんのために頑張ります"
        }
    },
    "roxy": {
        "name": "洛琪希·米格路迪亞 (Roxy Migurdia)",
        "audio": "roxy/reference.wav",
        "text": "はいそうですねルディ身長大きくなりましたね",
        "description": "無職轉生 洛琪希角色聲音，水聖級魔術師，藍髮師傅",
        "emotions": {
            "normal": "はいそうですねルディ身長大きくなりましたね",
            "happy": "おめでとうございますこれであなたは彗星級魔術師です",
            "gentle": "すぐに怖くなくなりますよ。ですよ。私がついていますから安心してください",
            "sad": "残念です。これで本当に私が教えられることもなくなってしまいました",
            "shy": "えっと、ルーデオスさん、その、ありがとうございました",
            "teasing": "ははーん、さては怖いんですねー",
            "proud": "ちっちゃくありませんあれは私の髪を見て驚いてたんですよ",
            "worried": "そうですね落ち込んでいるというのは少し心配ですが"
        }
    },
    "izumi": {
        "name": "和泉妃愛 (Izumi Hiyori)",
        "audio": "izumi_hiyori/reference.wav",
        "text": "いやめっちゃ持ちあげるけども、普段通りでいいよ普段通りで。私と話すときみたいに",
        "description": "和泉妃愛角色聲音，活潑可愛的學妹風格，帶有ひよひよ口頭禪",
        "emotions": {
            "normal": "いやめっちゃ持ちあげるけども、普段通りでいいよ普段通りで。私と話すときみたいに",
            "happy": "ひよひよ～！今日もいい天気だね～",
            "gentle": "主人、お疲れ様。お茶淹れてあげるね",
            "sad": "そんな…ひよひよ…",
            "teasing": "へへ～、主人ったら照れてる？ひよひよ～",
            "surprised": "えっ！？マジで！？ひよひよ！？",
            "shy": "あ、あの…その…ひよひよ…",
            "excited": "わぁ～！すっごい！ひよひよ～！"
        }
    }
}


def find_voice_file(audio_path: str) -> str:
    """
    查找聲音文件，支持多個路徑：
    1. ~/.openclaw/references/
    2. 腳本所在目錄的 references/
    3. 當前工作目錄的 references/
    """
    possible_paths = [
        os.path.join(DEFAULT_VOICES_DIR, audio_path),
        os.path.join(os.path.dirname(__file__), "references", audio_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "references", audio_path),
        os.path.join(os.getcwd(), "references", audio_path),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
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


def get_emotion_text(voice_key: str, emotion: str, base_text: str) -> str:
    """
    根據情緒和聲音獲取對應的參考文本
    
    Args:
        voice_key: 聲音名稱 (rem, izumi)
        emotion: 情緒名稱
        base_text: 基礎文本（無情緒匹配時使用）
    
    Returns:
        對應情緒的參考文本
    """
    if voice_key not in PRESET_VOICES:
        return base_text
    
    voice_info = PRESET_VOICES[voice_key]
    emotions = voice_info.get("emotions", {})
    
    # 如果該聲音有對應情緒的參考文本，使用它
    if emotion in emotions:
        return emotions[emotion]
    
    # 否則使用基礎文本
    return base_text


def generate_voice(
    text: str,
    ref_audio: str,
    ref_text: str,
    output_path: str = None,
    model_id: str = DEFAULT_MODEL,
    emotion: str = "normal",
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
        emotion: 情緒標籤
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
    
    # 處理情緒標記
    emotion_info = EMOTION_PROMPTS.get(emotion, EMOTION_PROMPTS["normal"])
    if emotion != "normal" and emotion_info["suffix"]:
        # 在文本末尾添加情緒標記（對模型有提示作用）
        display_text = f"{text} {emotion_info['suffix']}"
    else:
        display_text = text
    
    if verbose:
        print(f"🎙️ Qwen3-TTS Voice Cloning")
        print(f"=" * 60)
        print(f"📝 文本: {text}")
        if emotion != "normal":
            print(f"😊 情緒: {emotion} ({emotion_info['description']})")
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
        # 包含情緒信息的文件名
        if emotion != "normal":
            output_prefix = os.path.join(DEFAULT_OUTPUT_DIR, f"qwen3_{emotion}_{int(time.time())}")
        else:
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
        description="Qwen3-TTS 語音克隆工具 v2.0 (kapi2800 + bf16 + 情緒)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基礎用法
  %(prog)s --text "你好" --voice izumi
  
  # 帶情緒
  %(prog)s --text "太好了！" --voice izumi --emotion happy
  
  # 自定義輸出路徑
  %(prog)s --text "晚安" --voice rem --output ~/goodnight.wav --emotion gentle
  
  # 列出所有聲音和情緒
  %(prog)s --list-voices
  %(prog)s --list-emotions
        """
    )
    
    parser.add_argument("--text", "-t", help="要合成的文本")
    parser.add_argument("--ref_audio", "-a", help="參考音頻路徑")
    parser.add_argument("--ref_text", "-r", help="參考音頻對應的文本")
    parser.add_argument("--voice", "-v", help=f"使用預設聲音: {', '.join(PRESET_VOICES.keys())}")
    parser.add_argument("--emotion", "-e", default="normal", 
                       help=f"情緒風格（默認: normal）")
    parser.add_argument("--output", "-o", help="輸出文件路徑（可選）")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"模型ID（默認: {DEFAULT_MODEL}）")
    parser.add_argument("--list-voices", action="store_true", help="列出所有預設聲音")
    parser.add_argument("--list-emotions", action="store_true", help="列出所有情緒選項")
    parser.add_argument("--quiet", "-q", action="store_true", help="安靜模式（只輸出文件路徑）")
    
    args = parser.parse_args()
    
    # 列出預設聲音
    if args.list_voices:
        print("🎭 可用預設聲音:")
        for key, info in PRESET_VOICES.items():
            print(f"\n  {key}: {info['name']}")
            print(f"    {info['description']}")
            if "emotions" in info:
                print(f"    支持情緒: {', '.join(info['emotions'].keys())}")
        return
    
    # 列出情緒選項
    if args.list_emotions:
        print("😊 可用情緒選項:")
        for key, info in EMOTION_PROMPTS.items():
            print(f"  {key}: {info['description']}")
        return
    
    # 檢查必須的 text 參數（如果不是在列出選項）
    if not args.text:
        print("❌ 請提供 --text 參數，或使用 --list-voices / --list-emotions")
        parser.print_help()
        sys.exit(1)
    
    # 驗證情緒
    if args.emotion not in EMOTION_PROMPTS:
        print(f"❌ 未知情緒: {args.emotion}")
        print(f"可用情緒: {', '.join(EMOTION_PROMPTS.keys())}")
        sys.exit(1)
    
    # 處理預設聲音
    if args.voice:
        if args.voice not in PRESET_VOICES:
            print(f"❌ 未知聲音: {args.voice}")
            print(f"可用聲音: {', '.join(PRESET_VOICES.keys())}")
            sys.exit(1)
        
        voice_info = PRESET_VOICES[args.voice]
        ref_audio = find_voice_file(voice_info["audio"])
        
        # 根據情緒選擇對應的參考文本
        ref_text = get_emotion_text(args.voice, args.emotion, voice_info["text"])
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
            emotion=args.emotion,
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
