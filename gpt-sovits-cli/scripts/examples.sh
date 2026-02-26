#!/bin/bash
#
# GPT-SoVITS CLI 使用示例
#

# 设置路径
export GPT_SOVITS_DIR="/Volumes/SSD/GPT-SoVITS"
cd "$GPT_SOVITS_DIR"
source venv/bin/activate

# 角色模型目录
NAHIDA_DIR="$GPT_SOVITS_DIR/GPT_SoVITS/character_models/nahida"
KOKOMI_DIR="$GPT_SOVITS_DIR/GPT_SoVITS/character_models/kokomi"

echo "🎙️ GPT-SoVITS CLI 示例脚本"
echo "=========================="
echo ""

# 检查 API 是否运行
if ! curl -s http://127.0.0.1:9880/docs > /dev/null; then
    echo "⚠️  API 服务未运行，正在启动..."
    nohup python3 api_v2.py -a 127.0.0.1 -p 9880 > /tmp/gptsovits_api.log 2>&1 &
    sleep 10
fi

echo "✅ API 服务运行中"
echo ""

# 示例1: 生成纳西妲语音
echo "🌱 示例1: 生成纳西妲语音"
python3 ~/.agents/skills/gpt-sovits-cli/scripts/gpt_sovits_cli.py generate \
  --text "你好，我是纳西妲。初次见面，我已经关注你很久了。" \
  --ref-audio "$NAHIDA_DIR/ref_audios/Nahida.wav" \
  --ref-text "嗯，這是只存在於理論中的舉動，我甚至不確定有誰敢做這樣的事" \
  --output ~/nahida_demo.wav \
  --lang zh

echo ""

# 示例2: 生成珊瑚宮心海语音
echo "💙 示例2: 生成珊瑚宮心海语音"
python3 ~/.agents/skills/gpt-sovits-cli/scripts/gpt_sovits_cli.py generate \
  --text "你好，我是珊瑚宮心海。" \
  --ref-audio "$KOKOMI_DIR/kokomi/kokomi2_e15_s2295.pth" \
  --ref-text "こんにちは" \
  --output ~/kokomi_demo.wav \
  --lang ja

echo ""
echo "✅ 示例完成！"
echo "输出文件: ~/nahida_demo.wav, ~/kokomi_demo.wav"
