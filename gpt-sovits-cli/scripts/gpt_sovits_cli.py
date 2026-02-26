#!/usr/bin/env python3
"""
GPT-SoVITS CLI Tool
封装 API 调用和模型管理
"""

import os
import sys
import argparse
import requests
import urllib.parse
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    "gpt_sovits_dir": "/Volumes/SSD/GPT-SoVITS",
    "api_host": "127.0.0.1",
    "api_port": 9880,
    "character_models_dir": "GPT_SoVITS/character_models"
}

# 角色预设配置
CHARACTER_PRESETS = {
    "roxy": {
        "name": "洛琪希·米格路迪亞 (Roxy Migurdia)",
        "description": "無職轉生 - 水聖級魔術師，藍髮師傅",
        "gpt_model": "洛琪希.ckpt",
        "sovits_model": "洛琪希.pth",
        "ref_audios": {
            "normal": {
                "path": "ref_audios/roxy_normal.wav",
                "text": "はいそうですねルディ身長大きくなりましたね",
                "description": "正常語氣，欣慰"
            },
            "shy": {
                "path": "ref_audios/roxy_shy.wav",
                "text": "えっと、ルーデオスさん、その、ありがとうございました",
                "description": "害羞、靦腆"
            },
            "battle": {
                "path": "ref_audios/roxy_battle.wav",
                "text": "はあ姉よ全てを押し流しあらゆるものを駆逐せよ",
                "description": "戰鬥、魔法詠唱"
            }
        },
        "default_lang": "ja"
    }
}

class GPTSoVITSClient:
    """GPT-SoVITS API 客户端"""
    
    def __init__(self, host="127.0.0.1", port=9880):
        self.base_url = f"http://{host}:{port}"
        self.check_service()
    
    def check_service(self):
        """检查 API 服务是否运行"""
        try:
            resp = requests.get(f"{self.base_url}/docs", timeout=5)
            if resp.status_code == 200:
                print(f"✅ GPT-SoVITS API 服务运行中: {self.base_url}")
                return True
        except:
            pass
        print(f"❌ API 服务未运行，请先启动: python3 api_v2.py -a 127.0.0.1 -p 9880")
        return False
    
    def set_model(self, gpt_path, sovits_path):
        """设置模型权重"""
        # 设置 GPT 模型
        resp = requests.get(f"{self.base_url}/set_gpt_weights", 
                          params={"weights_path": gpt_path})
        if resp.status_code != 200:
            print(f"⚠️  设置 GPT 模型失败: {resp.text}")
            return False
        
        # 设置 SoVITS 模型
        resp = requests.get(f"{self.base_url}/set_sovits_weights",
                          params={"weights_path": sovits_path})
        if resp.status_code != 200:
            print(f"⚠️  设置 SoVITS 模型失败: {resp.text}")
            return False
        
        print("✅ 模型设置成功")
        return True
    
    def generate(self, text, ref_audio, ref_text, output_path,
                 text_lang="zh", ref_lang="zh", **kwargs):
        """
        生成语音
        
        Args:
            text: 要合成的文本
            ref_audio: 参考音频路径
            ref_text: 参考音频的准确文本内容 (重要！)
            output_path: 输出文件路径
            text_lang: 文本语言 (zh/ja/en)
            ref_lang: 参考音频语言
        """
        params = {
            "text": text,
            "text_lang": text_lang,
            "ref_audio_path": ref_audio,
            "prompt_lang": ref_lang,
            "prompt_text": ref_text,  # 必须匹配音频内容！
            "text_split_method": kwargs.get("split_method", "cut5"),
            "batch_size": kwargs.get("batch_size", 1),
            "speed_factor": kwargs.get("speed", 1.0),
            "media_type": "wav",
            "streaming_mode": False
        }
        
        # 可选参数
        if "top_k" in kwargs:
            params["top_k"] = kwargs["top_k"]
        if "top_p" in kwargs:
            params["top_p"] = kwargs["top_p"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        
        url = f"{self.base_url}/tts?{urllib.parse.urlencode(params)}"
        
        print(f"🎙️  生成语音...")
        print(f"   文本: {text}")
        print(f"   参考: {ref_text[:30]}...")
        
        try:
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('audio'):
                with open(output_path, 'wb') as f:
                    f.write(resp.content)
                print(f"✅ 生成成功: {output_path}")
                return output_path
            else:
                print(f"❌ 生成失败: {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"❌ 请求错误: {e}")
            return None


def download_character_model(repo_id, character_name, base_dir=None):
    """
    从 HuggingFace 下载角色模型
    
    Args:
        repo_id: HuggingFace 仓库 ID
        character_name: 角色名称
        base_dir: 基础目录 (默认: /Volumes/SSD/GPT-SoVITS)
    """
    try:
        from huggingface_hub import hf_hub_download, list_repo_files
    except ImportError:
        print("❌ 请先安装 huggingface_hub: pip install huggingface_hub")
        return False
    
    if base_dir is None:
        base_dir = DEFAULT_CONFIG["gpt_sovits_dir"]
    
    char_dir = os.path.join(base_dir, DEFAULT_CONFIG["character_models_dir"], character_name)
    os.makedirs(char_dir, exist_ok=True)
    
    print(f"📥 下载角色模型: {character_name}")
    print(f"   来源: {repo_id}")
    
    try:
        files = list_repo_files(repo_id)
        
        # 下载 GPT 和 SoVITS 模型
        model_files = [f for f in files if f.endswith(('.pth', '.ckpt', '.safetensors'))]
        
        for f in model_files[:4]:  # 限制下载数量
            print(f"   下载: {f}")
            hf_hub_download(
                repo_id=repo_id,
                filename=f,
                local_dir=char_dir,
                local_dir_use_symlinks=False
            )
        
        # 下载参考音频
        ref_files = [f for f in files if 'ref' in f.lower() and f.endswith('.wav')]
        for f in ref_files[:2]:
            print(f"   下载参考音频: {f}")
            hf_hub_download(
                repo_id=repo_id,
                filename=f,
                local_dir=char_dir,
                local_dir_use_symlinks=False
            )
        
        print(f"✅ {character_name} 模型下载完成!")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def get_character_preset(character_name, emotion="normal"):
    """
    获取角色预设配置
    
    Args:
        character_name: 角色名称 (如 "roxy")
        emotion: 情绪类型 (normal/shy/battle)
    
    Returns:
        dict: 包含 gpt_path, sovits_path, ref_audio, ref_text, lang
    """
    if character_name not in CHARACTER_PRESETS:
        print(f"❌ 未知角色: {character_name}")
        print(f"可用角色: {', '.join(CHARACTER_PRESETS.keys())}")
        return None
    
    preset = CHARACTER_PRESETS[character_name]
    base_dir = os.path.join(
        DEFAULT_CONFIG["gpt_sovits_dir"],
        DEFAULT_CONFIG["character_models_dir"],
        character_name
    )
    
    # 获取参考音频配置
    if emotion not in preset["ref_audios"]:
        print(f"⚠️  未知情绪 '{emotion}'，使用 normal")
        emotion = "normal"
    
    ref_config = preset["ref_audios"][emotion]
    
    return {
        "gpt_path": os.path.join(base_dir, preset["gpt_model"]),
        "sovits_path": os.path.join(base_dir, preset["sovits_model"]),
        "ref_audio": os.path.join(base_dir, ref_config["path"]),
        "ref_text": ref_config["text"],
        "lang": preset.get("default_lang", "ja")
    }


def main():
    parser = argparse.ArgumentParser(description="GPT-SoVITS CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成语音")
    gen_parser.add_argument("--text", "-t", required=True, help="要合成的文本")
    gen_parser.add_argument("--character", "-c", help=f"使用预设角色: {', '.join(CHARACTER_PRESETS.keys())}")
    gen_parser.add_argument("--emotion", "-e", default="normal", help="情绪类型 (normal/shy/battle)")
    gen_parser.add_argument("--ref-audio", "-r", help="参考音频路径 (不使用预设时必填)")
    gen_parser.add_argument("--ref-text", "-p", help="参考音频的准确文本内容 (不使用预设时必填)")
    gen_parser.add_argument("--output", "-o", default="output.wav", help="输出文件路径")
    gen_parser.add_argument("--lang", "-l", help="语言 (zh/ja/en，默认使用角色预设)")
    gen_parser.add_argument("--speed", "-s", type=float, default=1.0, help="语速")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出可用角色")
    
    # download 命令
    dl_parser = subparsers.add_parser("download", help="下载角色模型")
    dl_parser.add_argument("--repo", required=True, help="HuggingFace 仓库 ID")
    dl_parser.add_argument("--name", "-n", required=True, help="角色名称")
    
    # check 命令
    subparsers.add_parser("check", help="检查 API 服务状态")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        client = GPTSoVITSClient()
        
        # 使用预设角色
        if args.character:
            preset = get_character_preset(args.character, args.emotion)
            if not preset:
                sys.exit(1)
            
            # 设置模型
            if not client.set_model(preset["gpt_path"], preset["sovits_path"]):
                print("❌ 模型设置失败")
                sys.exit(1)
            
            ref_audio = preset["ref_audio"]
            ref_text = preset["ref_text"]
            lang = args.lang or preset["lang"]
        else:
            # 手动指定参数
            if not args.ref_audio or not args.ref_text:
                print("❌ 请提供 --ref-audio 和 --ref-text，或使用 --character 选择预设角色")
                sys.exit(1)
            ref_audio = args.ref_audio
            ref_text = args.ref_text
            lang = args.lang or "zh"
        
        client.generate(
            text=args.text,
            ref_audio=ref_audio,
            ref_text=ref_text,
            output_path=args.output,
            text_lang=lang,
            ref_lang=lang,
            speed=args.speed
        )
    
    elif args.command == "list":
        print("🎭 可用角色预设:")
        for char_key, char_info in CHARACTER_PRESETS.items():
            print(f"\n  {char_key}: {char_info['name']}")
            print(f"    {char_info['description']}")
            print(f"    支持情绪: {', '.join(char_info['ref_audios'].keys())}")
    
    elif args.command == "download":
        download_character_model(args.repo, args.name)
    
    elif args.command == "check":
        client = GPTSoVITSClient()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
