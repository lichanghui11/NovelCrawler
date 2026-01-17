# 爬虫练习项目说明文档（单机可恢复、可并发、可导出 EPUB）


## 1. 目标与范围

### 目标（Goals）

1. 根据目标网站目录页解析出章节列表（序号、标题、URL）。
2. 并发抓取每章内容（I/O 密集）。
3. 支持断点续爬：程序中断/断网后可继续。
4. 抓取结果可管理、可追踪（进度、失败原因、重试次数）。
5. 落盘保存章节内容，并可合成 EPUB。

## 2. 总体架构

推荐采用“三段式流水线”：

1. **发现阶段（Discover）**

* 抓目录页 → 解析章节列表 → 写入任务库（SQLite）

2. **抓取阶段（Fetch/Parse/Store）**

* 从任务库取待抓任务（pending）
* 请求章节页 → 解析正文 → 写入文件（每章一个文件）
* 更新任务状态（done/failed）

3. **导出阶段（Export）**

* 按章节顺序读取已完成章节 → 生成 EPUB（目录 + 内容）


## 3. 并发模型选型：异步

* **异步（asyncio + aiohttp）**

> 关键不是“开多少并发”，而是：**并发上限 + 速率限制 + 失败重试退避**，否则稳定性会很差。

## 4. 任务与断点续爬

断点续爬的核心：**状态必须持久化**，不要只存在内存里。
* 使用 sqlite 存储任务状态

### 4.1 状态机（建议）

* `pending`：待抓
* `in_progress`：已被 worker 领取处理中（可选）
* `done`：成功
* `failed`：失败（可重试）
* `skipped`：跳过（例如解析不到、不可访问等）

### 4.2 表设计（最小可用）

`chapters` 表建议字段：

* `id` INTEGER PRIMARY KEY
* `chapter_index` INTEGER UNIQUE（章节序号）
* `url` TEXT UNIQUE
* `title` TEXT
* `status` TEXT（pending/done/failed/...）
* `retries` INTEGER DEFAULT 0
* `last_error` TEXT
* `content_path` TEXT（对应落盘文件路径）
* `updated_at` TIMESTAMP

> 真实工程会再加：`created_at`、`http_status`、`etag/last_modified`（缓存）、`checksum`（去重）等。

---

## 5. 落盘策略：文件结构与写入原则

### 5.1 推荐目录结构

```
project/
  data/
    spider.db
  output/
    meta.json
    chapters/
      0001.xhtml
      0002.xhtml
      ...
  logs/
    spider.log
  main.py  // 主程序入口
```

### 5.2 原子写入原则

**问题**: 写入过程中断（进程崩溃、断电）可能导致文件损坏。

**解决方案**: 原子写入（Atomic Write）

```python
# 先写临时文件
tmp_path = f"{target_path}.tmp"
with open(tmp_path, 'w', encoding='utf-8') as f:
    f.write(content)
    f.flush()
    os.fsync(f.fileno())  # 强制刷盘

# 原子重命名（操作系统保证原子性）
os.replace(tmp_path, target_path)
```

**效果**: 目标文件要么完整，要么不存在，不会出现半成品。

---

## 6. 合规与稳定性策略

合规采集一般关注：

* 合理 `User-Agent`（最好表明用途）
* 对同一域名控制并发上限（例如同时 2~5）
* 超时设置（连接/读取）
* 失败重试：网络错误、超时、偶发 5xx
* **指数退避**（backoff）：失败后等更久再试，避免雪崩

> 不建议无限重试。应设定 `max_retries`，超过则进入 `failed` 并记录原因。

---

## 7. 抓取流程（推荐的标准逻辑）

### 7.1 Discover（发现章节列表）

1. 请求目录页
2. 解析出章节列表：`[(index, title, url), ...]`
3. 写入 SQLite：

   * 不存在则插入 `pending`
   * 已存在则跳过（保持幂等）

### 7.2 Worker（并发抓取）

每个 worker 循环：

1. 从 SQLite 领取一条/一批 `pending`（可标记 `in_progress`）
2. 请求章节页
3. 解析正文（抽取 title、content）
4. 写入 `output/chapters/{index:04}.xhtml`
5. 更新 DB：`status=done, content_path=...`
6. 异常则更新 DB：`status=failed, retries+1, last_error=...`

### 7.3 Resume（断点续爬）

重启程序时：

* 继续处理 `pending`
* 对 `failed` 且 `retries < max_retries` 的任务可再次尝试

---

## 8. EPUB 导出：可行性与推荐做法

结论：**完全可实现**。

### 推荐方式

1. 先把每章保存成 XHTML（或可转 XHTML 的 HTML）
2. 导出时读取：

   * 书名、作者、封面（可选）
   * 章节顺序（按 `chapter_index`）
   * 每章标题 + 内容文件
3. 生成：

   * TOC（目录）
   * spine（阅读顺序）
   * 输出 `book.epub`

常用实现路径：

* Python 库：`ebooklib`（直接生成 epub）
* 工具链：先合并 HTML/Markdown → 用 `pandoc` 转换

> 实务中一般“抓取阶段只管采集与落盘”，导出是独立步骤，不要边爬边生成 EPUB。

---


### 必做

* [ ] 章节列表可解析并写入 SQLite（幂等）
* [ ] 抓取有超时、重试、退避
* [ ] 并发受控（不要无限开）
* [ ] 落盘编码 UTF-8
* [ ] 原子写（tmp → rename）
* [ ] DB 能显示进度（done/pending/failed）
* [ ] 可恢复（重启继续跑）
* [ ] 最后可按顺序导出 EPUB
