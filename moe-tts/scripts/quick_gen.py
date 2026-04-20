#!/usr/bin/env python3
"""
快速生成和泉妃愛 & 在原七海的语音
优化版本 - 一键生成
"""

import sys
import os

# 添加 MoE TTS 路径
sys.path.insert(0, os.path.expanduser("~/.openclaw/moe-tts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from moe_tts import generate_voice

def generate_hiyori(text, output_path=None, speed=1.0):
    """
    生成和泉妃愛的语音
    自动优化参数，活泼可爱风格
    """
    if output_path is None:
        output_path = f"~/.openclaw/workspace-groupchat/hiyori_{hash(text) % 10000}.wav"
    
    output_path = os.path.expanduser(output_path)
    
    print("🌸 生成和泉妃愛的语音...")
    print(f"📝 文本: {text}")
    
    # 妃愛优化参数：更活泼
    return generate_voice(
        text=text,
        role_id=1,
        speaker="和泉妃愛",
        speed=speed,
        noise_scale=0.75,      # 更活泼
        noise_scale_w=0.7,     # 自然稳定
        output_path=output_path
    )

def generate_nanami(text, output_path=None, speed=1.0):
    """
    生成在原七海的语音
    自动优化参数，温柔学妹风格
    """
    if output_path is None:
        output_path = f"~/.openclaw/workspace-groupchat/nanami_{hash(text) % 10000}.wav"
    
    output_path = os.path.expanduser(output_path)
    
    print("💙 生成在原七海的语音...")
    print(f"📝 文本: {text}")
    
    # 七海优化参数：更温柔
    return generate_voice(
        text=text,
        role_id=5,
        speaker="在原七海",
        speed=speed,
        noise_scale=0.6,       # 更温柔
        noise_scale_w=0.8,     # 自然
        output_path=output_path
    )

def generate_both(text, speed=1.0):
    """
    同时生成妃愛和七海的语音
    返回两个文件路径
    """
    import random
    rand = random.randint(1000, 9999)
    
    hiyori_path = f"~/.openclaw/workspace-groupchat/hiyori_{rand}.wav"
    nanami_path = f"~/.openclaw/workspace-groupchat/nanami_{rand}.wav"
    
    print("=" * 50)
    print("🎭 同时生成两位角色的语音")
    print("=" * 50)
    
    hiyori_file = generate_hiyori(text, hiyori_path, speed)
    print()
    nanami_file = generate_nanami(text, nanami_path, speed)
    
    print("\n" + "=" * 50)
    print("✅ 生成完成!")
    print(f"🌸 妃愛: {hiyori_file}")
    print(f"💙 七海: {nanami_file}")
    print("=" * 50)
    
    return hiyori_file, nanami_file

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='快速生成妃愛和七海的语音')
    parser.add_argument('text', help='要合成的文本')
    parser.add_argument('--character', '-c', choices=['hiyori', 'nanami', 'both'], 
                       default='both', help='选择角色 (hiyori=妃愛, nanami=七海, both=两者)')
    parser.add_argument('--speed', '-s', type=float, default=1.0, help='语速 (0.5-2.0)')
    parser.add_argument('--output', '-o', default=None, help='输出文件路径')
    
    args = parser.parse_args()
    
    if args.character == 'hiyori':
        output = generate_hiyori(args.text, args.output, args.speed)
        print(f"\n📁 输出: {output}")
    elif args.character == 'nanami':
        output = generate_nanami(args.text, args.output, args.speed)
        print(f"\n📁 输出: {output}")
    else:
        generate_both(args.text, args.speed)

if __name__ == "__main__":
    main()
