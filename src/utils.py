"""
工具模块：数据库、日志、HTTP客户端、配置管理等基础设施
"""

# 系统自带的包
import os
import sqlite3
import logging
import asyncio
from typing import List, Dict, Optional, Tuple
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

# 第三方包
import yaml
import aiohttp

# 注释：已移除 dataclass 导入，因为改用普通类定义
# from dataclasses import dataclass
from datetime import datetime


# ==================== 配置管理 ====================


class Config:
    """配置管理（单例模式）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """从 YAML 文件加载配置"""
        config_path = "config.yaml"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    def get(self, key_path: str, default=None):
        """
        获取配置值，支持点分隔的路径
        例如: config.get('http.user_agent')
        """
        keys = key_path.split(".")
        value = self._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default


# ==================== 数据模型 ====================


class ChapterInfo:
    """章节信息"""

    def __init__(self, chapter_index: int, title: str, url: str):
        self.chapter_index = chapter_index
        self.title = title
        self.url = url

    def __repr__(self):
        return f"ChapterInfo(chapter_index={self.chapter_index}, title='{self.title}', url='{self.url}')"

    def __eq__(self, other):
        if not isinstance(other, ChapterInfo):
            return False
        return (
            self.chapter_index == other.chapter_index
            and self.title == other.title
            and self.url == other.url
        )


class ChapterTask:
    """章节任务（从数据库读取）"""

    def __init__(
        self,
        id: int,
        chapter_index: int,
        url: str,
        title: str,
        status: str,
        retries: int,
        content_path: Optional[str] = None,
    ):
        self.id = id
        self.chapter_index = chapter_index
        self.url = url
        self.title = title
        self.status = status
        self.retries = retries
        self.content_path = content_path

    def __repr__(self):
        return (
            f"ChapterTask(id={self.id}, chapter_index={self.chapter_index}, "
            f"url='{self.url}', title='{self.title}', status='{self.status}', "
            f"retries={self.retries}, content_path='{self.content_path}')"
        )


class ChapterContent:
    """章节内容"""

    def __init__(self, title: str, content_html: str):
        self.title = title
        self.content_html = content_html

    def __repr__(self):
        content_preview = (
            self.content_html[:50] + "..."
            if len(self.content_html) > 50
            else self.content_html
        )
        return f"ChapterContent(title='{self.title}', content_html='{content_preview}')"


class ProgressStats:
    """进度统计"""

    def __init__(
        self,
        total: int,
        pending: int,
        in_progress: int,
        done: int,
        failed: int,
        skipped: int,
    ):
        self.total = total
        self.pending = pending
        self.in_progress = in_progress
        self.done = done
        self.failed = failed
        self.skipped = skipped

    def __repr__(self):
        return (
            f"ProgressStats(total={self.total}, pending={self.pending}, "
            f"in_progress={self.in_progress}, done={self.done}, "
            f"failed={self.failed}, skipped={self.skipped})"
        )


# ==================== 日志系统 ====================


def setup_logger() -> logging.Logger:
    """设置日志系统"""
    config = Config()

    logger = logging.getLogger("novel_crawler")
    logger.setLevel(getattr(logging, config.get("logging.level", "INFO")))

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 文件 handler（带轮转）
    log_file = config.get("logging.file", "logs/spider.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.get("logging.max_bytes", 10485760),
        backupCount=config.get("logging.backup_count", 5),
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 控制台 handler
    if config.get("logging.console", True):
        console_handler = logging.StreamHandler()
        try:
            import colorlog

            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )
            console_handler.setFormatter(console_formatter)
        except ImportError:
            console_formatter = logging.Formatter("%(levelname)-8s %(message)s")
            console_handler.setFormatter(console_formatter)

        logger.addHandler(console_handler)

    return logger


# ==================== 数据库管理 ====================


class Database:
    """SQLite 数据库管理"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger("novel_crawler.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        return conn

    def _init_database(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建 chapters 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_index INTEGER UNIQUE NOT NULL,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                retries INTEGER DEFAULT 0,
                last_error TEXT,
                content_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON chapters(status)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_chapter_index ON chapters(chapter_index)"
        )

        # 创建 metadata 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        )

        conn.commit()
        conn.close()
        self.logger.info(f"数据库初始化完成: {self.db_path}")

    def insert_chapters(self, chapters: List[ChapterInfo]) -> int:
        """
        批量插入章节（幂等，已存在则跳过）
        返回插入的数量
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        inserted = 0

        for chapter in chapters:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO chapters (chapter_index, url, title)
                    VALUES (?, ?, ?)
                """,
                    (chapter.chapter_index, chapter.url, chapter.title),
                )
                if cursor.rowcount > 0:
                    inserted += 1
            except sqlite3.Error as e:
                self.logger.error(f"插入章节失败: {chapter.title}, 错误: {e}")

        conn.commit()
        conn.close()
        self.logger.info(f"插入 {inserted} 个新章节（共 {len(chapters)} 个）")
        return inserted

    def get_pending_tasks(self, limit: Optional[int] = None) -> List[ChapterTask]:
        """
        获取待处理任务（pending 或 failed 且重试次数未超限）
        """
        config = Config()
        max_retries = config.get("http.max_retries", 3)

        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, chapter_index, url, title, status, retries, content_path
            FROM chapters
            WHERE status IN ('pending', 'failed') AND retries < ?
            ORDER BY chapter_index
        """
        params = [max_retries]

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        tasks = [
            ChapterTask(
                id=row["id"],
                chapter_index=row["chapter_index"],
                url=row["url"],
                title=row["title"],
                status=row["status"],
                retries=row["retries"],
                content_path=row["content_path"],
            )
            for row in rows
        ]
        return tasks

    def update_task_status(
        self,
        task_id: int,
        status: str,
        content_path: Optional[str] = None,
        error: Optional[str] = None,
        increment_retries: bool = False,
    ):
        """更新任务状态"""
        conn = self._get_connection()
        cursor = conn.cursor()

        update_fields = ["status = ?", "updated_at = ?"]
        params = [status, datetime.now().isoformat()]

        if content_path:
            update_fields.append("content_path = ?")
            params.append(content_path)

        if error:
            update_fields.append("last_error = ?")
            params.append(error)

        if increment_retries:
            update_fields.append("retries = retries + 1")

        params.append(task_id)

        query = f"UPDATE chapters SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def get_progress_stats(self) -> ProgressStats:
        """获取进度统计"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped
            FROM chapters
        """
        )
        row = cursor.fetchone()
        conn.close()

        return ProgressStats(
            total=row["total"] or 0,
            pending=row["pending"] or 0,
            in_progress=row["in_progress"] or 0,
            done=row["done"] or 0,
            failed=row["failed"] or 0,
            skipped=row["skipped"] or 0,
        )

    def set_metadata(self, key: str, value: str):
        """设置元数据"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)", (key, value)
        )
        conn.commit()
        conn.close()

    def get_metadata(self, key: str) -> Optional[str]:
        """获取元数据"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["value"] if row else None

    def get_done_chapters(self) -> List[Tuple[int, str, str]]:
        """
        获取所有已完成的章节（用于导出）
        返回: [(chapter_index, title, content_path), ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT chapter_index, title, content_path
            FROM chapters
            WHERE status = 'done' AND content_path IS NOT NULL
            ORDER BY chapter_index
        """
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            (row["chapter_index"], row["title"], row["content_path"]) for row in rows
        ]


# ==================== 异步 HTTP 客户端 ====================


class AsyncHTTPClient:
    """异步 HTTP 客户端（带重试、速率限制）"""

    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("novel_crawler.http")
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(
            self.config.get("concurrency.max_workers", 5)
        )
        self.rate_limit = self.config.get("concurrency.rate_limit", 2)
        self.last_request_time = 0

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(
            connect=self.config.get("http.connect_timeout", 10),
            total=self.config.get("http.read_timeout", 30),
        )
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": self.config.get("http.user_agent")}, timeout=timeout
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _rate_limit_wait(self):
        """速率限制：确保请求间隔"""
        if self.rate_limit <= 0:
            return

        now = asyncio.get_event_loop().time()
        interval = 1.0 / self.rate_limit
        time_since_last = now - self.last_request_time

        if time_since_last < interval:
            await asyncio.sleep(interval - time_since_last)

        self.last_request_time = asyncio.get_event_loop().time()

    async def fetch(self, url: str) -> str:
        """
        获取 URL 内容（带重试和退避）
        """
        max_retries = self.config.get("http.max_retries", 3)
        backoff_factor = self.config.get("http.backoff_factor", 1.0)

        async with self.semaphore:  # 并发控制
            for retry in range(max_retries + 1):
                try:
                    await self._rate_limit_wait()

                    async with self.session.get(url) as response:
                        if response.status == 200:
                            text = await response.text()
                            self.logger.debug(f"成功获取: {url}")
                            return text
                        elif response.status == 404:
                            raise ValueError(f"页面不存在 (404): {url}")
                        elif response.status >= 500:
                            raise aiohttp.ClientError(f"服务器错误 ({response.status})")
                        else:
                            raise aiohttp.ClientError(f"HTTP {response.status}")

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if retry < max_retries:
                        delay = backoff_factor * (2**retry)
                        self.logger.warning(
                            f"请求失败，{delay}s 后重试 ({retry + 1}/{max_retries}): {url}, 错误: {e}"
                        )
                        await asyncio.sleep(delay)
                    else:
                        self.logger.error(f"请求最终失败: {url}, 错误: {e}")
                        raise


# ==================== 文件存储工具 ====================


def atomic_write(file_path: str, content: str):
    """
    原子写入文件（先写临时文件，再重命名）
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    tmp_path = f"{file_path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())  # 强制刷盘

    os.replace(tmp_path, file_path)  # 原子重命名
