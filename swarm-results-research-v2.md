# Next.js Repository Research Summary

## 1. Directory Structure

### packages/ (20 packages)
| Package | Purpose |
|---------|---------|
| `create-next-app` | CLI for bootstrapping new Next.js projects |
| `eslint-config-next` | ESLint configuration preset |
| `eslint-plugin-next` | Custom ESLint rules for Next.js |
| `eslint-plugin-internal` | Internal ESLint rules |
| `font` | Next.js font optimization (@next/font) |
| `next` | Core Next.js framework (main package) |
| `next-bundle-analyzer` | Bundle analysis tool |
| `next-codemod` | Codemod utilities for migrations |
| `next-env` | Environment type definitions |
| `next-mdx` | MDX support |
| `next-playwright` | Playwright integration |
| `next-plugin-storybook` | Storybook plugin |
| `next-polyfill-module` | Module polyfills |
| `next-polyfill-nomodule` | No-module polyfills |
| `next-routing` | Routing utilities |
| `next-rspack` | Rspack bundler integration |
| `next-swc` | SWC compiler bindings |
| `react-refresh-utils` | React Fast Refresh utilities |
| `third-parties` | Third-party service integrations |

### crates/ (11 Rust crates)
| Crate | Purpose |
|-------|---------|
| `next-api` | API route handling |
| `next-build` | Build orchestration |
| `next-build-test` | Build testing utilities |
| `next-code-frame` | Error code framing |
| `next-core` | Core Turbopack integration |
| `next-custom-transforms` | SWC custom transforms |
| `next-error-code-swc-plugin` | Error code SWC plugin |
| `next-napi-bindings` | Node-API bindings |
| `next-taskless` | Taskless execution |
| `wasm` | WebAssembly utilities |

### test/ (5 main categories)
| Directory | Purpose |
|-----------|---------|
| `unit/` | Unit tests (60+ test dirs) |
| `development/` | Dev mode tests (45+ test dirs) |
| `e2e/` | End-to-end tests (171+ test dirs) |
| `integration/` | Integration tests (281+ test dirs) |
| `production/` | Production build tests (76+ test dirs) |

---

## 2. Build Commands

### Main Build Commands
```bash
# Build all packages
pnpm build

# Build with native binaries
pnpm build-all

# Build native SWC bindings
pnpm swc-build-native

# Build WASM
pnpm swc-build-wasm

# Build Turbopack CLI
cargo build -p turbopack-cli --release
```

### Development Commands
```bash
# Dev mode (parallel)
pnpm dev

# Run Next.js locally
pnpm next

# Debug mode
pnpm debug
pnpm debug-brk
```

---

## 3. Test Commands

### Test Runners
```bash
# Run all tests
pnpm test

# Unit tests only
pnpm test-unit

# Type checking
pnpm test-types
```

### Dev Mode Tests
```bash
# Dev mode (webpack)
pnpm test-dev
pnpm test-dev-webpack

# Dev mode (rspack)
pnpm test-dev-rspack

# Dev mode (turbopack)
pnpm test-dev-turbo

# Experimental dev tests
pnpm test-dev-experimental
pnpm test-dev-experimental-webpack
pnpm test-dev-experimental-rspack
pnpm test-dev-experimental-turbo
```

### Production/Start Tests
```bash
# Start mode tests
pnpm test-start
pnpm test-start-webpack
pnpm test-start-rspack
pnpm test-start-turbo

# Experimental start tests
pnpm test-start-experimental
```

### Deploy Tests
```bash
pnpm test-deploy
pnpm test-deploy-webpack
pnpm test-deploy-turbo
```

### Test Utilities
```bash
# Headless test run
pnpm testheadless

# Get test timings
pnpm get-test-timings

# Run evals
pnpm eval
```

---

## Key Observations

1. **Monorepo Structure**: Uses pnpm workspaces + Turbo for orchestration
2. **Multi-bundler Support**: Tests run against webpack, rspack, and turbopack
3. **Rust Components**: Significant Rust codebase in `crates/` for performance-critical parts
4. **Test Coverage**: ~633+ test directories across unit, dev, e2e, integration, and production suites
5. **Package Manager**: pnpm@9.6.0 required
6. **Node Version**: >=20.9.0 required
