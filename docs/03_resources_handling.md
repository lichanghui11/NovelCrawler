# 文件与资源处理笔记

## 1. 图片下载与保存

### 核心规则
保存图片（或音频、视频、PDF）时，必须遵守以下两点：
1.  **写入模式**：使用 `"wb"` (Write Binary)。
2.  **内容获取**：使用 `response.content` (Bytes)。

### 错误示范
*   使用 `"w"` 模式：会报错，因为 Python 试图将字节解码为字符串写入。
*   使用 `response.text`：会导致图片数据损坏（乱码），因为图片不是文本。

### 代码模板
```python
response = requests.get(img_url)
with open("cover.jpg", "wb") as f:
    f.write(response.content)
```

## 2. 路径拼接：os.path.join vs urljoin

这两个函数虽然都是拼接，但应用场景完全不同，混用会导致 Bug。

### os.path.join
*   **用途**：**本地文件系统**路径拼接。
*   **特点**：根据操作系统自动选择分隔符（Windows 用 `\`，Mac/Linux 用 `/`）。
*   **场景**：`os.path.join(OUTPUT_DIR, "chapter.json")`

### urljoin
*   **用途**：**网络 URL** 拼接。
*   **特点**：始终使用 `/`，且具备**相对路径解析能力**（类似浏览器的行为）。
*   **场景**：`urljoin("https://site.com/book/", "chapter1.html")`

### 常见坑点
如果在处理本地文件路径时使用 `urljoin`，在 Windows 系统下可能会出现路径错误；反之，在处理 URL 时使用 `os.path.join`，可能会导致 URL 变成 `http://site.com\page` 这种非法格式。