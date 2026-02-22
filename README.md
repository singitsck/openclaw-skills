# OpenClaw Skills

Custom skills for OpenClaw agent.

## Available Skills

### 1. Swarm Solver (`swarm-solver/`)
Multi-Agent Swarm Solver for complex tasks with step-by-step auto-continue notification pattern.

### 2. Finance Workflow (`finance-workflow/`)
Automated Hong Kong bank/credit card finance workflow using Yahoo Mail IMAP.
- Parsers for BOC, HSBC, Apple, Steam, AEON, Alipay, WeChat Pay
- 5-layer security defense
- **Note**: Sensitive data stays local in `~/.finance/`, never pushed to GitHub

### 3. Qwen3-TTS Voice Cloning (`qwen3-tts-kapi/`)
High-quality voice cloning using Qwen3-TTS with kapi2800 wrapper and bf16 models.
- Based on kapi2800/qwen3-tts-apple-silicon project
- Uses bf16 model to avoid silent audio bug (mlx-audio Issue #405)
- Includes preset voice: Rem (Re:Zero)
- Supports Apple Silicon (M1/M2/M3)

## Security

See [AGENT_SECURITY_GUIDELINES.md](AGENT_SECURITY_GUIDELINES.md) and [SECURITY_PREVENTION_STRATEGY.md](SECURITY_PREVENTION_STRATEGY.md) for security best practices.

## License

Apache 2.0 (where applicable)
