"""
Novel Crawler - 小说爬虫主程序
支持断点续爬、并发抓取、EPUB 导出

使用方法:
    python main.py discover              # 发现章节列表
    python main.py fetch                 # 抓取章节内容
    python main.py export                # 导出 EPUB
    python main.py status                # 查看进度
    python main.py run                   # 运行完整流程 (discover + fetch + export)
"""

import asyncio
import argparse
import sys

from src.utils import Config, Database, setup_logger
from src.discovery import run_discovery
from src.fetcher import run_fetcher
from src.exporter import run_exporter


def show_status():
    """显示抓取进度"""
    logger = setup_logger()
    config = Config()
    db = Database(config.get("database.path"))

    stats = db.get_progress_stats()

    print("\n" + "=" * 50)
    print("抓取进度统计")
    print("=" * 50)
    print(f"总章节数:   {stats.total}")
    print(
        f"已完成:     {stats.done} ({stats.done/stats.total*100:.1f}%)"
        if stats.total > 0
        else "已完成:     0"
    )
    print(f"待处理:     {stats.pending}")
    print(f"处理中:     {stats.in_progress}")
    print(f"失败:       {stats.failed}")
    print(f"已跳过:     {stats.skipped}")
    print("=" * 50)

    # 显示书籍信息
    book_title = db.get_metadata("book_title")
    book_author = db.get_metadata("book_author")
    if book_title or book_author:
        print(f"\n书名: {book_title or '未知'}")
        print(f"作者: {book_author or '未知'}")
        print("=" * 50)

    print()


async def run_full_workflow():
    """运行完整流程：发现 → 抓取 → 导出"""
    logger = setup_logger()

    try:
        logger.info("=" * 60)
        logger.info("开始完整流程")
        logger.info("=" * 60)

        # Phase 1: 发现
        logger.info("\n[Phase 1/3] 发现章节列表")
        await run_discovery()

        # Phase 2: 抓取
        logger.info("\n[Phase 2/3] 抓取章节内容")
        run_fetcher()  # 现在是同步的

        # Phase 3: 导出
        logger.info("\n[Phase 3/3] 导出 EPUB")
        run_exporter()

        logger.info("=" * 60)
        logger.info("✓ 完整流程执行完成！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"流程执行失败: {e}", exc_info=True)
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Novel Crawler - 小说爬虫工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py discover              发现章节列表
  python main.py fetch                 抓取章节内容
  python main.py export                导出 EPUB
  python main.py export -o book.epub   导出到指定文件
  python main.py status                查看进度
  python main.py run                   运行完整流程
        """,
    )

    parser.add_argument(
        "command",
        choices=["discover", "fetch", "export", "status", "run"],
        help="要执行的命令",
    )

    parser.add_argument(
        "-o", "--output", help="导出文件路径（仅用于 export 命令）", default=None
    )

    args = parser.parse_args()

    # 执行对应命令
    if args.command == "status":
        show_status()

    elif args.command == "discover":
        asyncio.run(run_discovery())

    elif args.command == "fetch":
        run_fetcher()  # 现在是同步的

    elif args.command == "export":
        run_exporter(output_path=args.output)

    elif args.command == "run":
        asyncio.run(run_full_workflow())

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
