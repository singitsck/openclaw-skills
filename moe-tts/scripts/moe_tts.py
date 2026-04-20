#!/usr/bin/env python3
"""
MoE TTS Voice Generation Tool
Multi-role, multi-speaker TTS for anime/game characters
"""

import argparse
import os
import sys
import torch
import numpy as np
import scipy.io.wavfile as wavfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_moe_tts_path():
    """Get the MoE TTS installation path"""
    return os.path.expanduser("~/.openclaw/moe-tts")

def setup_environment():
    """Setup the environment for MoE TTS"""
    moe_path = get_moe_tts_path()
    if not os.path.exists(moe_path):
        raise RuntimeError(f"MoE TTS not found at {moe_path}. Please clone from HuggingFace first.")
    
    sys.path.insert(0, moe_path)
    
    # Import MoE TTS modules
    global utils, commons, SynthesizerTrn, text_to_sequence
    from torch import no_grad, LongTensor
    import utils
    import commons
    from models import SynthesizerTrn
    from text import text_to_sequence
    
    return no_grad, LongTensor

def get_text(text, hps, is_symbol=False, no_grad=None, LongTensor=None):
    """Convert text to sequence"""
    text_norm = text_to_sequence(text, hps.symbols, [] if is_symbol else hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm

def detect_cleaner_type(role_id):
    """Detect which cleaner type a role uses"""
    moe_path = get_moe_tts_path()
    config_path = f"{moe_path}/saved_model/{role_id}/config.json"
    
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    cleaners = config.get('data', {}).get('text_cleaners', [])
    return cleaners[0] if cleaners else 'japanese_cleaners2'

def format_text_for_role(text, role_id):
    """Automatically format text based on role's cleaner type"""
    cleaner = detect_cleaner_type(role_id)
    
    # Check if already formatted
    if text.startswith('[JA]') or text.startswith('[ZH]'):
        return text
    
    if cleaner == 'zh_ja_mixture_cleaners':
        # Need language markers
        if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
            return f"[JA]{text}[JA]"
        else:
            return f"[ZH]{text}[ZH]"
    else:
        # japanese_cleaners2 - plain text
        return text

def generate_voice(text, role_id=1, speaker=None, speed=1.0, 
                   noise_scale=None, noise_scale_w=None, length_scale=None,
                   output_path=None, device='cpu'):
    """
    Generate voice using MoE TTS
    
    Args:
        text: Text to synthesize
        role_id: Role number (1, 5, etc.)
        speaker: Speaker name (if None, uses first speaker)
        speed: Speech speed multiplier
        output_path: Output file path (if None, auto-generated)
        device: 'cpu' or 'cuda'
    
    Returns:
        output_path: Path to generated audio file
    """
    no_grad, LongTensor = setup_environment()
    
    moe_path = get_moe_tts_path()
    config_path = f"{moe_path}/saved_model/{role_id}/config.json"
    model_path = f"{moe_path}/saved_model/{role_id}/model.pth"
    
    # Check model exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}. Run: git lfs pull --include=\"saved_model/{role_id}/*\"")
    
    # Load config
    hps = utils.get_hparams_from_file(config_path)
    
    # Format text for role
    formatted_text = format_text_for_role(text, role_id)
    
    # Get speaker
    speakers = hps.speakers
    if speaker is None:
        speaker = speakers[0]
    speaker_id = speakers.index(speaker) if speaker in speakers else 0
    
    # Create model
    model = SynthesizerTrn(
        len(hps.symbols),
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model
    )
    
    # Load checkpoint
    utils.load_checkpoint(model_path, model, None)
    model = model.to(device).eval()
    
    # Generate
    stn_tst = get_text(formatted_text, hps, no_grad=no_grad, LongTensor=LongTensor)
    
    # Set default parameters for quality
    if noise_scale is None:
        noise_scale = 0.667
    if noise_scale_w is None:
        noise_scale_w = 0.8
    if length_scale is None:
        length_scale = 1.0 / speed
    
    # Quality optimization based on role
    cleaner = detect_cleaner_type(role_id)
    if cleaner == 'japanese_cleaners2':
        # Role 1 (Hiyori): slightly more lively
        noise_scale = min(noise_scale * 1.1, 0.8)
    
    with no_grad():
        x_tst = stn_tst.unsqueeze(0).to(device)
        x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
        sid = LongTensor([speaker_id]).to(device)
        
        audio = model.infer(
            x_tst, x_tst_lengths,
            sid=sid,
            noise_scale=noise_scale,
            noise_scale_w=noise_scale_w,
            length_scale=length_scale
        )[0][0, 0].data.cpu().float().numpy()
    
    # Post-processing for quality optimization
    # 1. Normalize volume
    max_amp = np.max(np.abs(audio))
    if max_amp > 0:
        target_db = -20  # Target -20dB
        current_db = 20 * np.log10(max_amp)
        gain = 10 ** ((target_db - current_db) / 20)
        audio = audio * gain
    
    # 2. Soft clipping to prevent distortion
    audio = np.tanh(audio)
    
    # 3. Fade in/out
    fade_length = min(1000, len(audio) // 10)
    if fade_length > 0:
        fade_in = np.linspace(0, 1, fade_length)
        fade_out = np.linspace(1, 0, fade_length)
        audio[:fade_length] *= fade_in
        audio[-fade_length:] *= fade_out
    
    # Convert to int16
    audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    
    # Save
    if output_path is None:
        output_path = f"moe_tts_role{role_id}_{speaker}.wav"
    
    wavfile.write(output_path, hps.data.sampling_rate, audio_int16)
    
    duration = len(audio_int16) / hps.data.sampling_rate
    print(f"✅ Generated: {output_path} ({duration:.2f}s)")
    
    return output_path

def list_speakers(role_id=1):
    """List available speakers for a role"""
    moe_path = get_moe_tts_path()
    config_path = f"{moe_path}/saved_model/{role_id}/config.json"
    
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    speakers = config.get('speakers', [])
    cleaner = config.get('data', {}).get('text_cleaners', ['unknown'])[0]
    
    print(f"\n🎭 Role {role_id} Speakers:")
    for i, speaker in enumerate(speakers):
        print(f"  {i}: {speaker}")
    print(f"\n🔧 Cleaner: {cleaner}")
    
    return speakers

def main():
    parser = argparse.ArgumentParser(description='MoE TTS Voice Generation')
    parser.add_argument('--text', '-t', required=True, help='Text to synthesize')
    parser.add_argument('--role', '-r', type=int, default=1, help='Role ID (1, 5, etc.)')
    parser.add_argument('--speaker', '-s', default=None, help='Speaker name')
    parser.add_argument('--speed', type=float, default=1.0, help='Speech speed')
    parser.add_argument('--noise-scale', type=float, default=None, help='Noise scale (0.0-1.0, default: auto)')
    parser.add_argument('--noise-scale-w', type=float, default=None, help='Noise scale w (0.0-1.0, default: auto)')
    parser.add_argument('--output', '-o', default=None, help='Output file path')
    parser.add_argument('--list', '-l', action='store_true', help='List speakers for role')
    
    args = parser.parse_args()
    
    if args.list:
        list_speakers(args.role)
        return
    
    output = generate_voice(
        text=args.text,
        role_id=args.role,
        speaker=args.speaker,
        speed=args.speed,
        noise_scale=args.noise_scale,
        noise_scale_w=args.noise_scale_w,
        output_path=args.output
    )
    
    print(f"\n📁 Output: {output}")

if __name__ == "__main__":
    main()
