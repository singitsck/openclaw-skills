# Next.js 貢獻指南 (Contributing Guide)

> 這份指南基於 Vercel Next.js 專案的官方貢獻文件整理而成。
> 適用版本：v16.2.1-canary.2 (canary branch)

---

## 📋 目錄

1. [前置需求與環境設定](#1-前置需求與環境設定)
2. [建置專案](#2-建置專案)
3. [執行測試](#3-執行測試)
4. [程式碼規範](#4-程式碼規範)
5. [PR 流程](#5-pr-流程)

---

## 1. 前置需求與環境設定

### 1.1 系統需求

| 工具 | 版本要求 |
|------|----------|
| **Node.js** | >= 20.9.0 |
| **pnpm** | 9.6.0 (由 `packageManager` 欄位指定) |
| **Rust** | nightly (用於 Turbopack/WASM 建置) |
| **Git** | 最新版 |

### 1.2 複製專案

```bash
# 複製儲存庫
git clone https://github.com/vercel/next.js.git
cd next.js

# 切換到 canary 分支 (最新開發分支)
git checkout canary
```

### 1.3 安裝依賴

```bash
# 安裝所有依賴 (使用 pnpm)
pnpm install
```

### 1.4 目錄結構說明

```
next.js/
├── packages/          # 核心套件 (next, create-next-app, eslint-plugin, swc, fonts)
├── test/              # 測試套件
│   ├── e2e/          # 端對端測試
│   ├── development/  # 開發模式測試
│   ├── production/   # 生產模式測試
│   ├── integration/  # 整合測試
│   └── unit/         # 單元測試
├── contributing/      # 貢獻文件
├── crates/            # Rust crates (Turbopack, SWC transforms)
├── turbopack/         # Turbopack CLI 和開發伺服器
├── docs/              # 官方文件
├── errors/            # 錯誤定義與連結文件
├── examples/          # 範例應用程式
└── scripts/           # 建置/發布/工具腳本
```

---

## 2. 建置專案

### 2.1 完整建置

在執行任何測試或開發前，**必須先建置所有套件**：

```bash
# 建置所有套件 (透過 turbo)
pnpm build
```

### 2.2 開發模式

```bash
# 平行執行開發模式 (排除 bundle-analyzer-ui)
pnpm dev

# 使用本地 Next CLI 執行
pnpm next
```

### 2.3 建立本地套件供外部測試

```bash
# 產生本地建置的 tarball
pnpm pack-next

# 套用到外部專案
pnpm pack-next --project ~/my-app/

# 解壓 tarball 到專案的 node_modules
pnpm unpack-next ~/my-app
```

---

## 3. 執行測試

### 3.1 測試類型概覽

| 測試類型 | 位置 | 說明 |
|----------|------|------|
| **e2e** | `test/e2e/` | 針對 `next dev`、`next start`、Vercel 部署 |
| **development** | `test/development/` | 僅針對 `next dev` 模式 |
| **production** | `test/production/` | 僅針對 `next start` 模式 |
| **integration** | `test/integration/` | 雜項檢查 (非隔離，不建議新增) |
| **unit** | `test/unit/` | 快速測試，無需瀏覽器 |

### 3.2 執行單元測試

```bash
# 執行單元測試 (Jest)
pnpm test-unit
```

### 3.3 執行 E2E/整合測試

**⚠️ 重要：執行測試前請先 `pnpm build`**

#### 基本測試指令

```bash
# 開發模式測試 (next dev)
pnpm test-dev test/e2e/app-dir/app/

# 生產模式測試 (next build + next start)
pnpm test-start test/e2e/app-dir/app/

# 部署測試 (部署到 Vercel)
pnpm test-deploy test/e2e/app-dir/app/
```

#### 變體測試 (不同 bundler)

```bash
# 使用 Webpack
pnpm test-dev-webpack test/e2e/app-dir/app/

# 使用 Turbopack
pnpm test-dev-turbo test/e2e/app-dir/app/

# 使用 Rspack
pnpm test-dev-rspack test/e2e/app-dir/app/

# 實驗性 Turbopack
pnpm test-dev-experimental-turbo test/e2e/app-dir/app/
```

#### 除錯模式測試

```bash
# 除錯模式 (可看見瀏覽器視窗)
pnpm testonly-start test/e2e/app-dir/app/

# 無頭模式 (無瀏覽器視窗，適合 CI)
pnpm testheadless
```

### 3.4 同時測試多種模式

```bash
# 同時針對 Webpack 和 Turbopack 執行測試
pnpm test-dev test/e2e/app-dir/app/ --projects jest.config.*
```

### 3.5 環境變數 (除錯用)

| 變數 | 說明 |
|------|------|
| `NEXT_TEST_SKIP_CLEANUP=1` | 保留暫存資料夾以供除錯 |
| `NEXT_SKIP_ISOLATE=1` | 在儲存庫內執行 (非暫存資料夾，本地執行更快) |
| `NEXT_TEST_MODE=dev\|start\|deploy` | 切換測試模式 |
| `NEXT_TEST_PREFER_OFFLINE=1` | 安裝時使用 `--prefer-offline` |
| `NEXT_E2E_TEST_TIMEOUT=0` | 停用測試逾時 |
| `NEXT_TEST_TRACE=1` | 啟用效能分析 |

**範例：**
```bash
# 保留暫存檔並使用本地執行 (加速除錯)
NEXT_TEST_SKIP_CLEANUP=1 NEXT_SKIP_ISOLATE=1 pnpm test-dev test/e2e/app-dir/app/
```

### 3.6 建立新測試

```bash
# 互動式測試模板產生器
pnpm new-test
```

---

## 4. 程式碼規範

### 4.1 執行程式碼檢查

```bash
# 完整檢查 (型別、Prettier、ESLint、AST-grep、Alex)
pnpm lint

# 自動修正檢查問題
pnpm lint-fix

# 僅檢查型別
pnpm types
pnpm test-types

# 僅修正 Prettier 格式
pnpm prettier-fix
```

### 4.2 檢查項目

| 檢查工具 | 用途 |
|----------|------|
| **TypeScript** | 型別檢查 |
| **Prettier** | 程式碼格式化 |
| **ESLint** | JavaScript/TypeScript 語法檢查 |
| **AST-grep** | AST 層級的程式碼分析 |
| **Alex** | 包容性語言檢查 |

### 4.3 建立新錯誤定義

```bash
# 互動式錯誤定義產生器
pnpm new-error
```

---

## 5. PR 流程

### 5.1 貢獻前準備

1. **觀看教學影片**：官方提供 [40分鐘貢獻流程教學](https://www.youtube.com/watch?v=cuoNzXFLitc)
2. **閱讀完整文件**：
   - `contributing/` 目錄下的所有文件
   - `contributing/core/` - 核心開發指南
   - `contributing/docs/` - 文件貢獻指南
   - `contributing/repository/` - 儲存庫維護指南
   - `contributing/turbopack/` - Turbopack 相關指南

### 5.2 分支策略

```bash
# 確保在 canary 分支上開發
git checkout canary
git pull origin canary

# 建立功能分支
git checkout -b feature/your-feature-name
```

### 5.3 提交前檢查清單

- [ ] 執行 `pnpm build` 並成功
- [ ] 執行 `pnpm lint` 無錯誤
- [ ] 相關測試通過 (`pnpm test-unit`, `pnpm test-dev`, `pnpm test-start`)
- [ ] 新增功能有對應測試
- [ ] 文件已更新 (如需要)

### 5.4 PR 描述格式

Next.js 專案要求 PR 描述包含以下資訊：

```markdown
## 變更說明
<!-- 描述這個 PR 做了什麼 -->

## 相關 Issue
Fixes #issue-number

## 測試
<!-- 說明如何測試這些變更 -->
- [ ] 單元測試
- [ ] E2E 測試
- [ ] 手動測試

## 檢查清單
- [ ] 我已閱讀貢獻指南
- [ ] 我的程式碼符合專案風格
- [ ] 我已執行所有相關測試
```

### 5.5 發布通道

Next.js 使用多個發布通道：

| 通道 | 說明 |
|------|------|
| **canary** | 最新不穩定版本 (主要開發分支) |
| **stable** | 穩定版本 |
| **experimental** | 實驗性功能 |

**貢獻者應以 `canary` 分支為基礎進行開發。**

---

## 📚 額外資源

- [Next.js 官方文件](https://nextjs.org/docs)
- [貢獻教學影片 (40分鐘)](https://www.youtube.com/watch?v=cuoNzXFLitc)
- [GitHub Issues](https://github.com/vercel/next.js/issues)
- [GitHub Discussions](https://github.com/vercel/next.js/discussions)

---

## 🆘 常見問題

### Q: 測試失敗說找不到 `next` 指令？
**A:** 請先執行 `pnpm build` 建置所有套件。

### Q: 如何只測試特定檔案？
**A:** 直接在指令後面加上測試路徑，例如：`pnpm test-dev test/e2e/app-dir/app/index.test.ts`

### Q: Turbopack 測試需要什麼？
**A:** 需要安裝 Rust 工具鏈，並使用 nightly 版本。

### Q: 如何加速本地測試？
**A:** 使用 `NEXT_SKIP_ISOLATE=1` 環境變數，讓測試在儲存庫內執行而非暫存資料夾。

---

> 💡 **提示**：這份指南整理自 Next.js 官方貢獻文件，如有更新請參考官方文件為準。

---

**生成時間：** 2025年3月20日  
**適用版本：** Next.js v16.2.1-canary.2  
**原始來源：** [vercel/next.js](https://github.com/vercel/next.js) (canary branch)
