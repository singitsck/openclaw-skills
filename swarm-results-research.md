# Next.js Repository Analysis (vercel/next.js - canary branch)

## 1. CONTRIBUTING.md Content

The root `contributing.md` links to a structured contribution guide with these sections:

### Repository
- Triaging
- Linting
- Release Channels and Publishing
- Pull Request Descriptions

### Documentation
- Adding Documentation

### Core
- Developing
- **Building**
- **Testing**
- Adding Error Links
- Adding a new feature
- Developing Using Local App

### Turbopack
- Tracing

**Key link:** [40-minute walkthrough video on how to contribute](https://www.youtube.com/watch?v=cuoNzXFLitc)

---

## 2. Key Directory Structure

The repo is a **pnpm monorepo** with workspaces under `packages/*`. Key top-level directories:

| Directory | Purpose |
|-----------|---------|
| `packages/` | All core packages (next, create-next-app, swc, fonts, eslint-plugin, etc.) |
| `test/` | Integration, e2e, unit, development, production test suites |
| `contributing/` | Contribution docs (core/, docs/, repository/, turbopack/) |
| `crates/` | Rust crates (Turbopack core, SWC transforms, wasm bindings) |
| `turbopack/` | Turbopack CLI and dev server |
| `docs/` | Next.js documentation |
| `errors/` | Error definitions with linked docs |
| `examples/` | Example applications |
| `bench/` | Performance benchmarking tools |
| `evals/` | Evaluation fixtures and runners |
| `scripts/` | Build/release/utilities scripts |
| `apps/` | Internal apps (bundle-analyzer, etc.) |
| `patches/` | Patches for third-party dependencies |
| `rspack/` | Rspack compatibility bindings |

**Special directories:**
- `.claude-plugin/` — Claude Code plugin marketplace with cache-components skill
- `.agents/skills/` — Agent skills (e.g., pr-status-triage)
- `.github/` — GitHub Actions workflows
- `.devcontainer/` — Dev Container config

---

## 3. package.json Scripts (Key Commands)

### Build & Dev
```bash
pnpm build          # Build all packages via turbo
pnpm dev            # Run dev in parallel (excluding bundle-analyzer-ui)
pnpm next           # Run next CLI with local dev settings
```

### Testing
```bash
# Unit tests
pnpm test-unit      # jest test/unit/ packages/next/ packages/font

# E2E / Integration tests (with multiple modes)
pnpm test-dev test/e2e/app-dir/app/       # next dev mode
pnpm test-start test/e2e/app-dir/app/     # next build + start (production)
pnpm test-deploy test/e2e/app-dir/app/     # deploy to Vercel

# Variants: -webpack, -turbo, -rspack, -experimental
pnpm test-dev-webpack
pnpm test-dev-turbo
pnpm test-dev-rspack
pnpm test-dev-experimental-turbo

# Headless (no browser window)
pnpm testheadless   # cross-env HEADLESS=true pnpm testonly

# Debug mode (see browser)
pnpm testonly-start test/e2e/app-dir/app/
```

### Linting & Type Checking
```bash
pnpm lint           # Full lint: types, prettier, eslint, ast-grep, alex
pnpm lint-fix       # Auto-fix linting issues
pnpm types          # lerna run types across packages
pnpm test-types     # tsc
```

### Utilities
```bash
pnpm new-error      # turbo gen error (create new error definition)
pnpm new-test       # turbo gen test (create new test from template)
pnpm pack-next      # Create tarball of local next build for external testing
pnpm eval           # Run evals (node run-evals.js)
pnpm prettier-fix   # Auto-fix prettier formatting
```

---

## 4. Test Setup Instructions (from `contributing/core/testing.md`)

### Prerequisites — Build First
```bash
pnpm build
```

### Running Tests
```bash
# Production mode (next build + next start)
pnpm test-start test/e2e/app-dir/app/

# Development mode (next dev)
pnpm test-dev test/e2e/app-dir/app/

# Debug mode (visible browser window)
pnpm testonly-start test/e2e/app-dir/app/
```

### Test Types
| Type | Location | Description |
|------|----------|-------------|
| **e2e** | `test/e2e/` | Against `next dev`, `next start`, deployed to Vercel |
| **development** | `test/development/` | Against `next dev` only |
| **production** | `test/production/` | Against `next start` only |
| **integration** | `test/integration/` | Misc checks — not isolated, avoid adding new tests here |
| **unit** | `test/unit/` | Fast tests without browser |

### Key Environment Variables for Debugging
```bash
NEXT_TEST_SKIP_CLEANUP=1    # Keep temp folder for debugging
NEXT_SKIP_ISOLATE=1          # Run inside repo instead of temp (faster local)
NEXT_TEST_MODE=dev|start|deploy   # Toggle test mode
NEXT_TEST_PREFER_OFFLINE=1   # Use --prefer-offline during install
NEXT_E2E_TEST_TIMEOUT=0      # Disable test timeout
NEXT_TEST_TRACE=1            # Enable profiling
```

### Turbopack Testing
```bash
# Run with Turbopack instead of webpack
pnpm test-dev-turbo test/e2e/app-dir/app/

# Run against BOTH webpack and Turbopack
pnpm test-dev test/e2e/app-dir/app/ --projects jest.config.*
```

### Creating New Tests
```bash
pnpm new-test    # Interactive template generator
```

### External/Local Build Testing
```bash
pnpm pack-next                    # Generate tarball of local build
pnpm pack-next --project ~/my-app/  # Apply to external project
pnpm unpack-next ~/my-app         # Extract tarball into project's node_modules
```

---

## Notes

- **Node.js:** >=20.9.0 required
- **pnpm:** 9.6.0 required (via `packageManager` field)
- **Rust:** Required for turbopack/wasm builds (`rust-toolchain.toml` specifies nightly)
- **Test isolation:** e2e/development/production tests run in system temp folder (`/tmp`), fully isolated from monorepo
- **Canary branch:** Analysis targets the `canary` branch (latest unstable)
- **React version:** Uses React 19 canary (19.3.0-canary-3f0b9e61-20260317)
- **Current version:** v16.2.1-canary.2 (based on latest commits)
