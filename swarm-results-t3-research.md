# Python asyncio 官方文檔研究總結

**來源：** Python 3.14 官方文檔 (`docs.python.org/3/library/asyncio.html`, `asyncio-task.html`, `asyncio-runner.html`)
**調研時間：** 2026-03-20

---

## 1. 核心概念

### 1.1 Event Loop（事件循環）

事件循環是 asyncio 的核心發動機，負責：
- 運行和控制所有異步任務的調度
- 處理 I/O 操作和系統信號
- 執行回調和網絡 IPC

**重要限制：**
- 在同一線程中，`asyncio.run()` 不能被重入調用
- 建議將 `asyncio.run()` 只用作**單一主入口**，只調用一次

```python
# 正確姿勢
async def main():
    await asyncio.sleep(1)

asyncio.run(main())  # 只在程序入口調用一次
```

### 1.2 Coroutines（協程）

**兩種形式：**
- 協程函數：`async def` 定義的函數
- 協程對象：調用協程函數返回的對象

**關鍵陷阱：**
```python
async def main():
    nested()  # ❌ 只創建了協程對象，但根本不會執行！且會產生 RuntimeWarning

    await nested()  # ✅ 正確：必須 await 才會執行
```

### 1.3 Tasks（任務）

任務是包裹協程的封裝，將協程**自動调度**到事件循環中並行執行。

```python
task = asyncio.create_task(coro())
await task  # 等待任務完成
```

**內存注意事項：**
事件循環對 Task 僅持有**弱引用（weak reference）**。如果 Task 沒有其他外部引用，可能在執行完成前被 GC 回收。

```python
# 可靠地保存後台任務引用
background_tasks = set()
for i in range(10):
    task = asyncio.create_task(some_coro(param=i))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
```

### 1.4 Futures

低級 awaitable 對象，代表異步操作的最終結果。應用層代碼一般不需直接創建 Futures，但 `loop.run_in_executor()` 等低級 API 會返回 Future。

```python
async def main():
    await function_that_returns_a_future_object()
    await asyncio.gather(
        function_that_returns_a_future_object(),
        some_python_coroutine()
    )
```

---

## 2. 常見模式

### 2.1 async / await

```python
async def main():
    print('hello')
    await asyncio.sleep(1)  # 掛起當前任務，讓出執行權
    print('world')
```

**注意：** `await` 表達式只能用在 `async def` 函數內部。

### 2.2 asyncio.gather() — 並發執行多個協程

```python
async def main():
    results = await asyncio.gather(
        factorial("A", 2),
        factorial("B", 3),
        factorial("C", 4),
    )
    print(results)  # [2, 6, 24]
```

**行為規則：**
- `return_exceptions=False`（默認）：第一個異常立即傳播，其他任務**不會被取消**，繼續運行
- `return_exceptions=True`：異常被當作正常結果匯總到結果列表
- `gather()` 被取消時，所有未完成的 awaitable 也會被取消

### 2.3 asyncio.create_task() — 創建並發任務

```python
async def main():
    task1 = asyncio.create_task(say_after(1, 'hello'))
    task2 = asyncio.create_task(say_after(2, 'world'))
    await task1
    await task2  # 總耗時 ≈ 2 秒（不是 3 秒）
```

**參數（Python 3.7+）：**
- `name`：任務名稱（便於調試）
- `context`：自定義 contextvars.Context
- `eager_start`（Python 3.14+）：`True` 時任務在創建時立即開始執行，而非调度到事件循環

### 2.4 asyncio.TaskGroup — 結構化並發（Python 3.11+）

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(some_coro(...))
        task2 = tg.create_task(another_coro(...))
    # 所有任務完成後才退出 async with
```

**相比 gather() 的優勢：**
- **自動取消**：任一任務拋出異常（非 CancelledError）時，剩餘任務自動被取消
- **異常聚合**：多個任務失敗時，異常被包裝在 ExceptionGroup 中一次性拋出
- **語義更清晰**：用 `async with` 明確任務組的邊界

### 2.5 asyncio.timeout() / asyncio.timeout_at() — 超時控制（Python 3.11+）

```python
async def main():
    try:
        async with asyncio.timeout(10):  # 最多等 10 秒
            await long_running_task()
    except TimeoutError:
        print("操作超時")
```

### 2.6 asyncio.shield() — 保護任務不被取消

```python
async def main():
    task = asyncio.create_task(something())
    try:
        res = await shield(task)  # 外部取消不會殺死 something()
    except CancelledError:
        res = None
```

### 2.7 asyncio.wait_for() — 帶超時的等待

```python
async def main():
    try:
        await asyncio.wait_for(eternity(), timeout=1.0)
    except TimeoutError:
        print('timeout!')
```

### 2.8 asyncio.to_thread() — 在線程中運行阻塞代碼

```python
async def main():
    await asyncio.gather(
        asyncio.to_thread(blocking_io),  # 在單獨線程執行，不阻塞事件循環
        asyncio.sleep(1)
    )
```

---

## 3. 常見陷阱與解決方案

### 陷阱 1：忘記 await 協程

```python
# ❌ 錯誤
async def main():
    nested()  # RuntimeWarning: coroutine 'nested' was never awaited

# ✅ 正確
async def main():
    await nested()
```

### 陷阱 2：在事件循環外調用異步函數

```python
# ❌ 錯誤
result = asyncio.run(async_func())  # 嵌套的 asyncio.run() 會報錯

# ✅ 正確：在同一事件循環內調用
async def main():
    await async_func()
asyncio.run(main())
```

### 陷阱 3：Task 引用被 GC 回收

```python
# ❌ 危險：沒有保存 Task 引用，任務可能悄然消失
asyncio.create_task(some_coro())  # 可能在 GC 時被中斷

# ✅ 安全：保存引用
background_tasks = set()
task = asyncio.create_task(some_coro())
background_tasks.add(task)
task.add_done_callback(background_tasks.discard)
```

### 陷阱 4：在 gather() 中 Swallowing 異常後以為任務已取消

```python
# ❌ 誤解：任務 A 失敗後，任務 B/C 不會被自動取消
results = await asyncio.gather(coro_a(), coro_b(), coro_c(), return_exceptions=True)

# ✅ 如需任一失敗時全部取消，使用 TaskGroup
async with asyncio.TaskGroup() as tg:
    tg.create_task(coro_a())
    tg.create_task(coro_b())
    tg.create_task(coro_c())
# 任一失敗，其他任務自動取消
```

### 陷阱 5：捕獲 CancelledError 但忘記調用 uncancel()

```python
# ⚠️ 不推薦：僅僅捕獲 CancelledError 是不夠的
try:
    await task
except asyncio.CancelledError:
    # 任務可能仍然處於"取消中"狀態
    pass

# ✅ 如果確實要抑制取消，必須調用 uncancel()
try:
    await task
except asyncio.CancelledError:
    task.uncancel()  # 完全清除取消狀態
```

### 陷阱 6：混合線程與 asyncio 不當

```python
# ❌ 錯誤：從另一個線程調用 asyncio.run()
import threading
def in_thread():
    asyncio.run(async_func())  # 會崩潰

# ✅ 正確：使用 run_coroutine_threadsafe
def in_thread(loop):
    future = asyncio.run_coroutine_threadsafe(async_func(), loop)
    result = future.result(timeout=5)
```

### 陷阱 7：fire-and-forget 任務未被正確跟蹤

```python
# ❌ 不良實踐
async def background_task():
    await do_something()

async def main():
    asyncio.create_task(background_task())  # 無法保證任務執行完成
    # main() 退出後，事件循環關閉，後台任務可能來不及執行

# ✅ 正確：明確等待或使用跟蹤集合
async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(background_task())
    # TaskGroup 確保所有任務完成後才退出
```

---

## 4. 最佳實踐

### 4.1 入口點：只用一次 asyncio.run()

```python
# ✅ 推薦
async def main():
    ...

asyncio.run(main())

# ✅ 也可使用 Runner（多次復用同一事件循環）
with asyncio.Runner() as runner:
    runner.run(main())
    runner.run(another_main())
```

### 4.2 優先使用結構化並發

- 優先使用 `asyncio.TaskGroup` 而非 `gather()`
- 優先使用 `asyncio.timeout()` 而非 `wait_for()`
- 優先使用 `asyncio.create_task()` + `TaskGroup` 而非裸 `gather()`

### 4.3 始終保存 Task 引用

對任何非同步等待的 Task，保持強引用直到完成。

### 4.4 善用屏蔽與超時

- 用 `shield()` 保護關鍵任務不被外部取消
- 用 `timeout()` / `timeout_at()` 防止無限期等待

### 4.5 阻塞代碼交給線程池

```python
# 阻塞 I/O 或 CPU密集型操作
result = await asyncio.to_thread(blocking_func)
```

### 4.6 正確處理 CancelledError

在 `try/finally` 中做清理，**不要**隨意捕獲並吞掉 `CancelledError`：

```python
async def cancel_me():
    try:
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await cleanup()  # 執行清理
        raise  # 重新拋出，讓調度器知道取消已完成
    finally:
        print("始終執行")
```

### 4.7 使用 name 参数调试

```python
task = asyncio.create_task(coro(), name="database-query")
```

### 4.8 Eager Task Factory（Python 3.12+）

對於**同步完成**（不走 I/O）的協程，用 eager_start 避免不必要的調度開銷：

```python
task = asyncio.create_task(coro(), eager_start=True)
```

### 4.9 調試模式

```python
# 開發環境開啟調試
asyncio.run(main(), debug=True)
# 或設置全局
export PYTHONASYNCIODEBUG=1
```

---

## 5. 快速對照表

| 場景 | 推薦 API |
|------|---------|
| 並發執行多個協程 | `asyncio.gather()` 或 `TaskGroup` |
| 創建後台任務 | `asyncio.create_task()` |
| 任務組 + 自動取消 | `asyncio.TaskGroup` |
| 超時控制 | `asyncio.timeout()` |
| 保護不被取消 | `asyncio.shield()` |
| 阻塞 I/O 線程化 | `asyncio.to_thread()` |
| 等待第一個完成 | `asyncio.wait(..., return_when=FIRST_COMPLETED)` |
| 迭代完成順序 | `asyncio.as_completed()` |
| 程序入口 | `asyncio.run()` 或 `asyncio.Runner` |

---

## 6. 版本演進摘要

| 版本 | 新增功能 |
|------|---------|
| 3.7 | `asyncio.run()`, `create_task()`, `current_task()`, `all_tasks()` |
| 3.8 | Task `name` 參數 |
| 3.9 | `asyncio.to_thread()` |
| 3.11 | `TaskGroup`, `asyncio.timeout()`, `asyncio.timeout_at()`, `Runner` |
| 3.12 | Eager Task Factory |
| 3.14 | `eager_start` 參數進入 `create_task()`，policy system 標記廢棄 |
