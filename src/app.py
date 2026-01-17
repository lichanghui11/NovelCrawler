# -*- coding: utf-8 -*-
# 系统的自带模块
import logging
import sys

# 自定义的模块内容
from src.discovery import run_discovery
from src.fetcher import run_fetcher
from src.exporter import run_exporter


def run_workflow():
    """
    小说爬虫的核心工作流。
    这个函数封装了所有的业务逻辑，可以被任何入口点调用。
    """
    try:
        # 1. 发现阶段
        logging.info("\n[Phase 1/3] 发现章节列表...")
        book_meta, chapters_to_fetch = run_discovery()

        if not chapters_to_fetch:
            logging.warning("未能发现任何章节，程序退出。")
            return

        # 2. 抓取阶段
        logging.info("\n[Phase 2/3] 抓取章节内容...")
        completed_chapters = run_fetcher(chapters_to_fetch)

        if not completed_chapters:
            logging.warning("未能抓取到任何章节内容，程序退出。")
            return

        # 3. 导出阶段
        logging.info("\n[Phase 3/3] 导出为 TXT 文件...")
        run_exporter(book_meta, completed_chapters)

        logging.info("\n" + "=" * 60)
        logging.info("✓ 工作流执行完毕！")
        logging.info("=" * 60)

    except Exception as e:
        logging.error(f"工作流发生严重错误: {e}", exc_info=True)
        # 将异常向上抛出，让调用者（顶层 main.py）决定如何处理
        raise
