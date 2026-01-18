#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目主入口文件 (Application Entry Point)

职责:
1. 配置日志等基础环境。
2. 调用核心业务逻辑。
3. 捕获顶层异常并退出。
"""

import sys
import os
import logging

# 从 src 包中导入核心工作流函数
from src.run_spider import get_catalog, get_content
from src.config import OUTPUT_DIR
from src.exporter import EpubExporter


def main():
    """主函数"""
    # 1. 配置基础环境
    # 关键修复：在配置日志之前，必须确保日志文件所在的目录已经存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(OUTPUT_DIR, "spider.log"),
    )

    # 2. 启动核心业务逻辑
    logging.info("=" * 60)
    logging.info("启动小说爬虫")
    logging.info("=" * 60)
    try:
        get_catalog()
        get_content()
        export = EpubExporter()
        export.run()

    except Exception:
        # 捕获从工作流抛出的任何未处理异常
        logging.critical("程序因致命错误而终止。")
        sys.exit(1)


if __name__ == "__main__":
    main()
