# -*- coding: utf-8 -*-
import os
import logging
from src.config import OUTPUT_DIR, OUTPUT_FILENAME


def run_exporter(book_meta: dict, completed_chapters: list):
    """
    导出阶段：将内存中的书籍数据写入单个 TXT 文件。
    Args:
        book_meta (dict): 包含 'title' 和 'author' 的字典。
        completed_chapters (list): 包含 {'title': str, 'content': str} 的列表。
    """
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
    logging.info(f"开始导出书籍到: {output_path}")

    try:
        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"《{book_meta.get('title', '未知书名')}》\n")
            f.write(f"作者：{book_meta.get('author', '未知作者')}\n")
            f.write("=" * 40 + "\n\n")

            for chapter in completed_chapters:
                f.write(f"{chapter['title']}\n")
                f.write("-" * 30 + "\n")
                f.write(chapter["content"] + "\n\n\n")

        logging.info(f"✓ 导出成功！文件已保存到 {output_path}")

    except IOError as e:
        logging.error(f"文件写入错误: {e}")
