# Novel Crawler - Python 学习项目 🐍

> **⚠️ 学习项目说明**  
> 这个项目主要是通过一个简单的爬虫项目来学习 Python 的一些基础知识
> 主要是根据本人已有的编程知识与前端背景来进行对比学习
> 前期通过 AI 生成了整体的项目框架

---

## 📚 项目背景

这个项目是我（一个前端开发者）学习 Python 的实践项目。通过 AI 辅助，我构建了一个包含**爬取、存储、转换**三个阶段的完整爬虫应用，并在过程中学习了 Python 的核心概念。

### 学习方法

作为前端开发者，我采用**对比学习**的方式：

- 🔄 **语法对比**：JavaScript vs Python（类、装饰器、异步等）
- 🔄 **概念映射**：npm ↔ pip，package.json ↔ requirements.txt
- 🔄 **模式对比**：ES6 模块 ↔ Python 包系统

---

## 🎯 项目概述

```
📖 Phase 1: Discovery      → 爬取目录，解析章节列表
💾 Phase 2: Fetch & Store  → 并发抓取章节，保存到文件
📱 Phase 3: Export         → 生成 EPUB 电子书
```

---

## 📁 项目结构

```
NovelCrawler/
├── main.py                  # 🚪 入口文件（CLI）
├── config.yaml              # ⚙️ 配置文件
├── requirements.txt         # 📦 依赖列表
│
├── src/                     # 📂 源代码
│   ├── discovery.py         # 📖 Phase 1: 发现阶段
│   ├── fetcher.py           # 💾 Phase 2: 抓取阶段
│   ├── exporter.py          # 📱 Phase 3: 导出阶段
│   └── utils.py             # 🛠️ 工具模块（数据库、HTTP、日志）
│
├── data/                    # 💾 数据目录
│   └── spider.db            # SQLite 数据库（状态持久化）
│
├── output/                  # 📤 输出目录
│   ├── chapters/            # XHTML 章节文件
│   └── book.epub            # 最终 EPUB 文件
│
├── logs/                    # 📋 日志目录
│   └── spider.log           # 运行日志
│
└── docs/                    # 📚 学习文档
```

---

## 🛠️ 核心技术 (异步和断点触发的功能后续添加，这里的核心技术只是简单罗列，大部分内容还没有学到)

### 技术栈

| 技术 | 用途 | 学习要点 |
|------|------|---------|
| `asyncio` | 异步编程 | 事件循环、协程、并发 |
| `aiohttp` | 异步 HTTP | ClientSession、超时、重试 |
| `lxml` | HTML 解析 | XPath 语法 |
| `sqlite3` | 数据库 | SQL 基础、事务 |
| `ebooklib` | EPUB 生成 | 电子书标准 |
| `PyYAML` | 配置文件 | YAML 格式 |

### 设计模式

- **单例模式**：`Config` 类（全局唯一配置对象）
- **工作池模式**：`WorkerPool`（并发任务调度）
- **上下文管理器**：`AsyncHTTPClient`（资源自动清理）

---

## 当前进度

- [ ] 大致了解 Python 项目的基础文件结构
- [ ] 熟悉 Python 的一些基础语法
- [ ] 通过对比 JS 里面的相关编程概念帮助理解

