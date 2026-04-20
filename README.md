# OpenClaw Skills

Custom skills for OpenClaw agent.

## Available Skills

### Anthropic Skills (Adapted for OpenClaw)

Professional skills originally from Anthropic, adapted for OpenClaw with `metadata.openclaw` configuration.

#### Creative & Design

**1. PPTX Anthropic (`pptx-anthropic/`)** 📊
Professional PowerPoint creation with advanced design principles.
- **New**: Professional Design Principles for refined presentations
  - Typography hierarchy (52pt/36pt/22pt system)
  - 6×6 Rule (max 6 lines per slide)
  - Spacing system (0.6" margins, 28pt line spacing)
  - 8 layout templates (full-screen, two-column, three-column cards, 2×2 grid, etc.)
  - Cross-platform Chinese font: Microsoft JhengHei
- **Guides**: `design-examples.md`, `quick-reference.md`
- Parallel slide creation with `sessions_spawn`

**2. Algorithmic Art (`algorithmic-art/`)** 🎨
Generative art creation using p5.js with seeded randomness.
- Flow fields, particle systems, noise functions
- Interactive parameter exploration
- Seeded randomness for reproducible art
- Output: HTML artifacts with embedded p5.js

**3. Theme Factory (`theme-factory/`)** 🎭
Theme creation and management system.
- Pre-built themes: Arctic Frost, Botanical Garden, Desert Rose, etc.
- Theme showcase and documentation
- Consistent design language across projects

**4. Slack GIF Creator (`slack-gif-creator/`)** 🎬
Custom GIF creation optimized for Slack.
- Frame composition and animation
- Easing functions for smooth transitions
- Optimized file sizes for Slack compatibility

#### Document Skills

**5. PDF Anthropic (`pdf-anthropic/`)** 📄
PDF form filling and manipulation utilities.
- Fill fillable PDF forms
- Extract form field information
- Convert PDF to images for validation
- Create validation images with bounding boxes

**6. DOCX Anthropic (`docx/`)** 📝
Word document processing and editing.
- Document creation and formatting
- Track changes and comments
- Accept/reject changes programmatically
- Office Open XML manipulation

**7. XLSX Anthropic (`xlsx/`)** 📊
Excel spreadsheet processing.
- Spreadsheet creation and editing
- Formula calculation and recalculation
- Data validation and formatting
- Chart generation

#### Development & Technical

**8. Frontend Design (`frontend-design/`)** 💻
Frontend development and design utilities.
- Component-based design system
- Responsive layout patterns
- CSS and styling best practices

**9. MCP Builder (`mcp-builder/`)** 🔧
MCP (Model Context Protocol) server generator.
- Generate MCP servers in Node.js or Python
- Best practices for MCP implementation
- Server evaluation and testing tools

**10. Webapp Testing (`webapp-testing/`)** 🧪
Web application testing automation.
- Playwright-based browser automation
- Element discovery and interaction
- Console logging and error detection
- Static HTML automation examples

**11. Web Artifacts Builder (`web-artifacts-builder/`)** 🌐
Interactive web artifact creation.
- Single-file HTML artifacts
- Shadcn UI components integration
- Bundle and deployment scripts

#### Enterprise & Communication

**12. Doc Coauthoring (`doc-coauthoring/`)** ✍️
Document collaboration and coauthoring workflows.
- Multi-user editing patterns
- Version control for documents
- Collaborative review processes

**13. Skill Creator Anthropic (`skill-creator-anthropic/`)** 🛠️
Skill creation and management utilities.
- Skill packaging and validation
- Benchmark aggregation
- Description improvement tools
- Evaluation report generation

### Original Skills

#### 4. Swarm Solver (`swarm-solver/`)
Multi-Agent Swarm Solver for complex tasks with step-by-step auto-continue notification pattern.

#### 5. Finance Workflow (`finance-workflow/`)
Automated Hong Kong bank/credit card finance workflow using Yahoo Mail IMAP.
- Parsers for BOC, HSBC, Apple, Steam, AEON, Alipay, WeChat Pay
- 5-layer security defense
- **Note**: Sensitive data stays local in `~/.finance/`, never pushed to GitHub

#### 6. Qwen3-TTS Voice Cloning (`qwen3-tts-kapi/`)
High-quality voice cloning using Qwen3-TTS with kapi2800 wrapper and bf16 models.
- Based on kapi2800/qwen3-tts-apple-silicon project
- Uses bf16 model to avoid silent audio bug (mlx-audio Issue #405)
- Includes preset voice: Rem (Re:Zero)
- Supports Apple Silicon (M1/M2/M3)

## Security

See [AGENT_SECURITY_GUIDELINES.md](AGENT_SECURITY_GUIDELINES.md) and [SECURITY_PREVENTION_STRATEGY.md](SECURITY_PREVENTION_STRATEGY.md) for security best practices.

## License

Apache 2.0 (where applicable)
