"""
Phase 2: 抓取阶段（简化版）
顺序抓取章节内容，解析、存储为 TXT
"""

import logging
import os
import requests
from lxml import etree

from src.utils import Config, Database


class ContentParser:
    """章节内容解析器"""

    def __init__(self):
        self.logger = logging.getLogger("novel_crawler.content_parser")

    def parse(self, html: str, default_title: str = ""):
        """
        解析章节内容

        Args:
            html: 章节页 HTML
            default_title: 默认标题（如果解析失败）

        Returns:
            (title, content) 元组
        """
        tree = etree.HTML(html)

        # 解析标题
        title_xpath_options = [
            '//div[@id="chapter"]//h1//text()',
            '//div[@class="content"]//h1//text()',
            '//h1[@class="title"]//text()',
            "//h1//text()",
        ]

        title = default_title
        for xpath in title_xpath_options:
            title_elem = tree.xpath(xpath)
            if title_elem:
                title = title_elem[0].strip()
                break

        # 解析正文段落
        content_xpath_options = [
            '//body[@id="chapter"]/div[@class="content"]/p',
            '//div[@class="content"]/p',
            '//div[@id="content"]/p',
            "//article//p",
        ]

        paragraphs = []
        for xpath in content_xpath_options:
            p_elems = tree.xpath(xpath)
            if p_elems:
                for p in p_elems:
                    text = etree.tostring(p, method="text", encoding="unicode").strip()
                    if text and len(text) > 10:  # 过滤太短的段落
                        paragraphs.append(text)
                break

        if not paragraphs:
            self.logger.warning(f"未解析到正文内容: {title}")
            raise ValueError("未找到章节内容")

        # 合并段落
        content = "\n\n".join(paragraphs)

        return title, content


class SimpleFetcher:
    """简化的章节抓取器（同步、顺序执行）"""

    def __init__(self):
        self.config = Config()
        self.db = Database(self.config.get("database.path"))
        self.logger = logging.getLogger("novel_crawler.fetcher")
        self.parser = ContentParser()

        # 输出目录
        self.chapters_dir = self.config.get("output.chapters_dir", "output/chapters")
        os.makedirs(self.chapters_dir, exist_ok=True)

        # 创建 HTTP session（复用连接）
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.config.get(
                    "http.user_agent", "Mozilla/5.0 (compatible; NovelCrawler/1.0)"
                )
            }
        )

    def fetch_chapter(self, task):
        """
        抓取单个章节

        Args:
            task: ChapterTask 对象
        """
        self.logger.info(f"[{task.chapter_index}] 开始抓取: {task.title}")

        try:
            # 1. 发送 HTTP 请求
            response = self.session.get(
                task.url, timeout=self.config.get("http.read_timeout", 30)
            )
            response.raise_for_status()  # 检查 HTTP 错误
            response.encoding = "utf-8"  # 设置编码
            html = response.text

            # 2. 解析标题和内容
            title, content = self.parser.parse(html, default_title=task.title)

            # 3. 保存为 TXT 文件
            file_path = os.path.join(
                self.chapters_dir, f"{task.chapter_index:04d}_{title}.txt"
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"{title}\n\n")
                f.write(content)

            # 4. 更新数据库状态
            self.db.update_task_status(task.id, status="done", content_path=file_path)

            self.logger.info(f"[{task.chapter_index}] ✓ 完成: {task.title}")

        except requests.HTTPError as e:
            # HTTP 错误
            self.logger.error(f"[{task.chapter_index}] HTTP 错误: {e}")
            self.db.update_task_status(
                task.id, status="failed", error=f"HTTP {e.response.status_code}"
            )

        except ValueError as e:
            # 解析失败
            self.logger.warning(f"[{task.chapter_index}] 解析失败: {e}")
            self.db.update_task_status(task.id, status="skipped", error=str(e))

        except Exception as e:
            # 其他错误
            self.logger.error(f"[{task.chapter_index}] 未知错误: {e}")
            self.db.update_task_status(task.id, status="failed", error=str(e))

    def run(self):
        """
        运行抓取流程（顺序执行）
        """
        self.logger.info("开始抓取章节...")

        # 获取所有待处理任务
        tasks = self.db.get_pending_tasks()

        if not tasks:
            self.logger.info("没有待处理任务")
            return

        self.logger.info(f"找到 {len(tasks)} 个待处理章节")

        # 顺序处理每个章节
        for index, task in enumerate(tasks, 1):
            self.fetch_chapter(task)

            # 打印进度
            if index % 10 == 0:  # 每 10 章打印一次
                self._print_progress()

        # 最终进度
        self._print_progress()
        self.logger.info("抓取完成！")

    def _print_progress(self):
        """打印进度统计"""
        stats = self.db.get_progress_stats()
        progress_pct = (stats.done / stats.total * 100) if stats.total > 0 else 0

        self.logger.info(
            f"进度: {stats.done}/{stats.total} ({progress_pct:.1f}%) | "
            f"待处理: {stats.pending} | 失败: {stats.failed} | 跳过: {stats.skipped}"
        )


def run_fetcher():
    """运行抓取阶段的入口函数"""
    from src.utils import setup_logger

    setup_logger()
    fetcher = SimpleFetcher()
    fetcher.run()
