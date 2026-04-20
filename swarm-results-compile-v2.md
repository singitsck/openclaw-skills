# Next.js 開源項目貢獻指南

> 本文檔為想要貢獻 Next.js 項目的開發者提供完整指引，涵蓋環境搭建、構建流程、測試方法及代碼規範。

---

## 📋 目錄

1. [前置需求](#前置需求)
2. [構建流程](#構建流程)
3. [測試指南](#測試指南)
4. [代碼規範](#代碼規範)
5. [PR 工作流程](#pr-工作流程)

---

## 前置需求

### 系統要求

| 工具 | 版本要求 | 用途 |
|------|----------|------|
| **Node.js** | >= 20.9.0 | JavaScript 運行環境 |
| **pnpm** | 9.6.0 | 包管理工具 |
| **Rust** | 最新穩定版 | SWC / Turbopack 構建 |
| **Git** | 最新版 | 版本控制 |

### 安裝步驟

```bash
# 1. 克隆倉庫
git clone https://github.com/vercel/next.js.git
cd next.js

# 2. 安裝 pnpm (如果尚未安裝)
npm install -g pnpm@9.6.0

# 3. 安裝依賴
pnpm install

# 4. 驗證環境
node --version    # >= v20.9.0
pnpm --version    # >= 9.6.0
rustc --version   # 檢查 Rust
```

### 項目結構總覽

```
next.js/
├── packages/          # 20+ 個核心包
│   ├── next/          # 核心框架
│   ├── create-next-app/
│   ├── eslint-config-next/
│   └── ...
├── crates/            # 11 個 Rust crate
│   ├── next-core/     # Turbopack 集成
│   ├── next-swc/      # SWC 編譯器綁定
│   └── ...
├── test/              # 測試目錄
│   ├── unit/          # 單元測試
│   ├── development/   # 開發模式測試
│   ├── e2e/           # 端到端測試
│   ├── integration/   # 集成測試
│   └── production/    # 生產構建測試
└── ...
```

---

## 構建流程

### 核心構建命令

| 命令 | 說明 | 用於 |
|------|------|------|
| `pnpm build` | 構建所有包 | 日常開發 |
| `pnpm build-all` | 完整構建（含原生二進制） | 首次設置 / CI |
| `pnpm swc-build-native` | 構建 SWC 原生綁定 | Rust 修改後 |
| `pnpm swc-build-wasm` | 構建 WASM 版本 | WebAssembly 測試 |
| `cargo build -p turbopack-cli --release` | 構建 Turbopack CLI | Turbopack 開發 |

### 開發模式

| 命令 | 說明 |
|------|------|
| `pnpm dev` | 並行啟動開發模式 |
| `pnpm next` | 本地運行 Next.js |
| `pnpm debug` | 調試模式 |
| `pnpm debug-brk` | 調試模式（帶斷點） |

### 構建步驟示例

```bash
# 完整首次構建流程
pnpm install
pnpm build-all

# 僅 JavaScript/TypeScript 修改後
pnpm build

# Rust 代碼修改後
pnpm swc-build-native
pnpm build

# 驗證構建
pnpm next --version
```

---

## 測試指南

### 測試概述

Next.js 擁有 **633+ 個測試目錄**，分佈於 5 個主要類別：

| 類別 | 目錄數 | 用途 |
|------|--------|------|
| `test/unit/` | 60+ | 單元測試 |
| `test/development/` | 45+ | 開發模式測試 |
| `test/e2e/` | 171+ | 端到端測試 |
| `test/integration/` | 281+ | 集成測試 |
| `test/production/` | 76+ | 生產構建測試 |

### 測試執行命令

#### 單元測試

```bash
pnpm test-unit          # 運行所有單元測試
pnpm test-types         # TypeScript 類型檢查
```

#### 開發模式測試 (Dev Mode)

| 命令 | 說明 |
|------|------|
| `pnpm test-dev` | 開發模式測試（預設 bundler） |
| `pnpm test-dev-webpack` | Webpack 版本 |
| `pnpm test-dev-rspack` | Rspack 版本 |
| `pnpm test-dev-turbo` | Turbopack 版本 |
| `pnpm test-dev-experimental` | 實驗性功能測試 |
| `pnpm test-dev-experimental-webpack` | 實驗性 + Webpack |
| `pnpm test-dev-experimental-rspack` | 實驗性 + Rspack |
| `pnpm test-dev-experimental-turbo` | 實驗性 + Turbopack |

#### 啟動模式測試 (Start Mode)

| 命令 | 說明 |
|------|------|
| `pnpm test-start` | 啟動模式測試 |
| `pnpm test-start-webpack` | Webpack 版本 |
| `pnpm test-start-rspack` | Rspack 版本 |
| `pnpm test-start-turbo` | Turbopack 版本 |
| `pnpm test-start-experimental` | 實驗性功能 |

#### 部署測試 (Deploy Mode)

```bash
pnpm test-deploy          # 部署測試
pnpm test-deploy-webpack  # Webpack 版本
pnpm test-deploy-turbo    # Turbopack 版本
```

### 測試工具命令

| 命令 | 說明 |
|------|------|
| `pnpm test` | 運行所有測試 |
| `pnpm testheadless` | 無頭模式測試（CI 用） |
| `pnpm get-test-timings` | 獲取測試耗時統計 |
| `pnpm eval` | 運行評估測試 |

### 測試執行建議

```bash
# 開發時針對特定 bundler 測試
pnpm test-dev-webpack --testNamePattern="app-dir"

# 運行特定測試文件
pnpm test-dev test/development/app-dir/basic.test.ts

# 調試特定測試
pnpm test-dev --debug test/development/app-dir/basic.test.ts
```

---

## 代碼規範

### 代碼風格

| 工具 | 用途 | 命令 |
|------|------|------|
| **ESLint** | JavaScript/TypeScript 代碼檢查 | `pnpm lint` |
| **Prettier** | 代碼格式化 | `pnpm format` |
| **TypeScript** | 類型檢查 | `pnpm test-types` |
| **Rust Clippy** | Rust 代碼檢查 | `cargo clippy` |
| **Rustfmt** | Rust 格式化 | `cargo fmt` |

### 檢查命令

```bash
# JavaScript / TypeScript
pnpm lint                    # 運行 ESLint 檢查
pnpm lint --fix              # 自動修復問題
pnpm format                  # 格式化代碼

# Rust
cd crates/next-core
cargo clippy                 # 檢查 Rust 代碼
cargo fmt --check            # 檢查格式化
cargo fmt                    # 格式化

# 完整檢查
pnpm test-types              # 類型檢查
```

### 提交規範

- 使用清晰的提交信息
- 一個 PR 專注於一個功能或修復
- 確保所有測試通過後再提交 PR
- 包含必要的文檔更新

---

## PR 工作流程

### 貢獻流程

```
1. Fork 倉庫
    ↓
2. 創建功能分支 (git checkout -b feature/my-feature)
    ↓
3. 開發並本地測試
    ↓
4. 運行完整測試套件
    ↓
5. 提交 PR
    ↓
6. 等待 CI 檢查和代碼審查
    ↓
7. 合併到主分支
```

### 提交前檢查清單

| 檢查項 | 命令 |
|--------|------|
| ✅ 代碼構建成功 | `pnpm build` |
| ✅ 類型檢查通過 | `pnpm test-types` |
| ✅ Lint 檢查通過 | `pnpm lint` |
| ✅ 單元測試通過 | `pnpm test-unit` |
| ✅ 相關開發測試通過 | `pnpm test-dev-webpack` |
| ✅ 提交信息清晰 | - |

### 常見問題

#### Q: 修改 Rust 代碼後測試失敗？
```bash
# 重新構建 Rust 組件
pnpm swc-build-native
pnpm build
```

#### Q: 測試運行緩慢？
```bash
# 僅運行特定 bundler 的測試
pnpm test-dev-webpack
# 或指定測試文件
pnpm test-dev --testPathPattern="app-dir"
```

#### Q: 緩存問題？
```bash
# 清理並重新安裝
rm -rf node_modules pnpm-lock.yaml
pnpm install
pnpm build
```

---

## 快速參考表

### 常用命令速查

| 場景 | 命令 |
|------|------|
| 首次設置 | `pnpm install && pnpm build-all` |
| 日常開發 | `pnpm dev` |
| 快速測試 | `pnpm test-unit` |
| Webpack 測試 | `pnpm test-dev-webpack` |
| Turbopack 測試 | `pnpm test-dev-turbo` |
| 類型檢查 | `pnpm test-types` |
| 代碼檢查 | `pnpm lint` |

### 多 Bundler 測試矩陣

| 測試類型 | Webpack | Rspack | Turbopack |
|----------|---------|--------|-----------|
| 開發模式 | `test-dev-webpack` | `test-dev-rspack` | `test-dev-turbo` |
| 啟動模式 | `test-start-webpack` | `test-start-rspack` | `test-start-turbo` |
| 部署模式 | `test-deploy-webpack` | - | `test-deploy-turbo` |
| 實驗性功能 | `test-dev-experimental-webpack` | `test-dev-experimental-rspack` | `test-dev-experimental-turbo` |

---

## 資源鏈接

- [Next.js 官方文檔](https://nextjs.org/docs)
- [GitHub 倉庫](https://github.com/vercel/next.js)
- [Issue Tracker](https://github.com/vercel/next.js/issues)
- [Discussions](https://github.com/vercel/next.js/discussions)

---

*本文檔基於 Next.js 倉庫研究結果編寫，涵蓋 20+ packages、11+ Rust crates、633+ 測試目錄的貢獻指南。*
