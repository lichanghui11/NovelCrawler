# 日志与工程配置笔记

## 1. Logging 模块配置

### filename vs stream
`logging.basicConfig` 中这两个参数通常互斥：
*   **`filename`**：接收一个**字符串路径**，日志写入文件。
*   **`stream`**：接收一个**流对象**（如 `sys.stdout`），日志输出到控制台。

### 常见报错：FileNotFoundError
```text
FileNotFoundError: [Errno 2] No such file or directory: '.../output/spider.log'
```
**原因**：`logging` 模块可以自动创建日志文件，但**不会自动创建文件夹**。
**解决**：在配置日志之前，必须先检查并创建目录。

```python
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(filename=...)
```

### 常见报错：AttributeError (write)
如果在 `stream` 参数中传入了文件路径字符串，会报错。因为字符串没有 `.write()` 方法。

## 2. 异常处理原则

*   **网络请求**：必须包裹在 `try...except` 中，防止因超时或断网导致程序崩溃。
*   **response.raise_for_status()**：强烈建议使用。`requests` 默认只在网络不通时报错，如果服务器返回 404 或 500，它不会报错。使用此方法可以主动捕获 HTTP 错误。
*   **主程序保护**：在 `main()` 函数的最外层包裹 `try...except`，捕获所有未处理异常，防止程序静默退出，并记录致命错误日志。