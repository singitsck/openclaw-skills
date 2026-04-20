---
name: mac-vnc-remote
version: 1.0.0
description: 透過指令啟用 macOS 遠端管理 (VNC)，支援遠端桌面控制
trigger: "VNC|遠端桌面|Remote Management|螢幕共享"
tools: [shell, exec]
---

# mac-vnc-remote

透過指令啟用 macOS 的 Remote Management (VNC) 功能，實現遠端桌面控制。

## 功能

1. **啟用 Remote Management** - 啟用 macOS 內建的遠端管理服務
2. **設定 VNC 密碼** - 設定 VNC 訪問密碼
3. **設定用戶權限** - 指定可訪問的用戶
4. **查詢狀態** - 查看 VNC 服務是否正常運行

## 前置要求

- macOS 設備
- 管理員權限（sudo/管理員密碼）
- 已安裝 `expect`（用於自動化密碼輸入）

```bash
# 檢查是否已安裝 expect
which expect
```

## 使用方法

### 1. 基本啟用（需要管理員密碼）

```bash
# 使用 expect 自動輸入密碼
expect -c '
spawn sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -on -restart -agent -clientopts -setvnclegacy -vnclegacy yes -setvncpw -vncpw YOUR_PASSWORD
expect "Password:"
send "YOUR_MAC_PASSWORD\r"
expect eof
'
```

### 2. 完整設定（指定用戶 + VNC 密碼）

```bash
expect -c '
set timeout 60
spawn sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -configure -access -on -privs -all -users YOUR_USERNAME -clientopts -setvnclegacy -vnclegacy yes -setvncpw -vncpw YOUR_VNC_PASSWORD
expect "Password:"
send "YOUR_MAC_PASSWORD\r"
expect eof
'
```

### 3. 查詢 VNC 服務狀態

```bash
# 檢查 Port 5900 是否監聽
netstat -an | grep 5900 | grep LISTEN

# 或使用 lsof
lsof -i :5900
```

### 4. 查詢內網 IP

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### 5. 查詢公網 IP

```bash
curl -s ifconfig.me
```

## 參數說明

| 參數 | 說明 |
|------|------|
| `-activate` | 啟用 Remote Management |
| `-configure` | 進行配置 |
| `-access -on` | 允許訪問 |
| `-restart -agent` | 重啟 ARD Agent |
| `-clientopts -setvnclegacy -vnclegacy yes` | 啟用 VNC 兼容模式 |
| `-setvncpw -vncpw PASSWORD` | 設定 VNC 密碼 |
| `-users USERNAME` | 指定可訪問的用戶 |
| `-privs -all` | 給予全部權限 |

## 常見問題

### Q: 連接時顯示「密碼錯誤」？
A: 確認 VNC 密碼是否正確設定，以及用戶是否有遠端管理權限。

### Q: 無法從公網連接？
A: 需要在路由器設定 Port Forwarding（將外部 Port 590 轉發到內網 Mac 的 Port 5900）。

### Q: kickstart 需要 root 權限？
A: 是的，必須使用 sudo 或管理員權限執行。

## 路由器端口轉發設定

若要從外網訪問，需要設定路由器：

1. 登入路由器管理頁面
2. 找到「Port Forwarding」或「端口轉發」設定
3. 添加規則：
   - 外部端口：590
   - 內部 IP：你的 Mac 內網 IP
   - 內部端口：5900
   - 協議：TCP

## 安全建議

- VNC 密碼不要與本地用戶密碼相同
- 建議使用 VPN 連接而非直接暴露公網
- 使用後可隨時用 `-deactivate` 關閉服務

```bash
# 關閉 Remote Management
expect -c '
spawn sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -deactivate
expect "Password:"
send "YOUR_MAC_PASSWORD\r"
expect eof
'
```

## 參考資料

- [Apple 官方文檔 - 設定執行 VNC 軟體的電腦](https://support.apple.com/zh-hk/guide/remote-desktop/apdbed09830/mac)
- [kickstart 命令詳解](https://developer.apple.com/library/archive/Documentation/Darwin/Reference/ManPages/man8/kickstart.8.html)
