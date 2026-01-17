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
import logging

# 从 src 包中导入核心工作流函数
from src.app import run_workflow


def main():
    """主函数"""
    # 1. 配置基础环境
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    # 2. 启动核心业务逻辑
    logging.info("=" * 60)
    logging.info("启动小说爬虫")
    logging.info("=" * 60)
    try:
        run_workflow()
    except Exception:
        # 捕获从工作流抛出的任何未处理异常
        logging.critical("程序因致命错误而终止。")
        sys.exit(1)


if __name__ == "__main__":
    main()
