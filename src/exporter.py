# -*- coding: utf-8 -*-
import os
import json
import logging
from ebooklib import epub
from config import OUTPUT_DIR

# 配置日志
logger = logging.getLogger(__name__)


class EpubExporter:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.meta_path = os.path.join(OUTPUT_DIR, "book_meta.json")
        self.catalog_path = os.path.join(OUTPUT_DIR, "catalog_meta.json")

    def load_json(self, path):
        """辅助函数：读取JSON文件"""
        if not os.path.exists(path):
            logger.error(f"找不到文件: {path}")
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run(self):
        logger.info("开始执行 EPUB 导出...")

        # 1. 加载元数据
        book_meta = self.load_json(self.meta_path)
        catalog = self.load_json(self.catalog_path)

        if not book_meta or not catalog:
            logger.error("缺少必要的数据文件，请先在主工作目录运行 `python3 main.py`。")
            return

        # 2. 创建 EPUB 书籍对象
        book = epub.EpubBook()

        # 设置基础信息
        book.set_identifier(
            str(book_meta.get("url", "novel_crawler_001"))
        )  # 设定一个默认值
        book.set_title(book_meta.get("title", "未命名小说"))
        book.set_language("zh-cn")
        book.add_author(book_meta.get("author", "佚名"))

        # 尝试添加封面
        cover_filename = book_meta.get("cover_file_name")
        if cover_filename:
            cover_path = os.path.join(self.output_dir, cover_filename)
            default_cover_path = os.path.join(self.output_dir, "default_cover.jpg")
            if os.path.exists(cover_path):
                with open(cover_path, "rb") as f:
                    book.set_cover("cover.jpg", f.read())
                logger.info("已添加封面图片")
            elif os.path.exists(default_cover_path):
                with open(default_cover_path, "rb") as f:
                    book.set_cover("cover.jpg", f.read())
                logger.info("已添加默认封面图片")
            else:
                logger.warning(f"封面图片文件不存在: {cover_path}")

        # 3. 遍历目录，添加章节
        chapters_objs = []
        for chapter_info in catalog:
            # 这里的 status check 是关键：只导出下载成功的章节
            # 下载成功的目录元数据中 status 字段为 "completed"
            if chapter_info.get("status") == "completed":
                continue

            chapter_file = chapter_info.get("file_name")
            chapter_full_path = os.path.join(self.output_dir, "chapters", chapter_file)

            content_html = ""
            if os.path.exists(chapter_full_path):
                with open(chapter_full_path, "r", encoding="utf-8") as f:
                    # 内容为 JSON 格式的
                    content_text = f.read()
                    content_text = json.loads(content_text)
                    # 简单转换成 html 格式
                    content_html = f"<h1>{chapter_info['title']}</h1>"
                    # 段落信息存在 lines 字段里面
                    paras = content_text.get("lines", [])
                    for p in paras:
                        if p.strip():
                            content_html += f"<p>{p.strip()}</p>"
            else:
                # 文件不存在（可能还没下载），创建一个占位
                content_html = (
                    f"<h1>{chapter_info['title']}</h1><p>（章节内容尚未下载）</p>"
                )

            # 创建 EPUB 章节对象
            c = epub.EpubHtml(
                title=chapter_info["title"],
                file_name=f"chapter_{chapter_info['id']}.xhtml",
                lang="zh-cn",
            )
            c.content = content_html

            # 添加到书里
            book.add_item(c)
            chapters_objs.append(c)

        # 4. 设置目录 (TOC) 和 阅读顺序 (Spine)
        book.toc = tuple(chapters_objs)  # 简单的一平铺目录

        # 必须添加 NCX 和 Nav 文件 (这是 EPUB 标准要求的导航文件)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # 设置 CSS 样式 (可选，但推荐)
        style = 'body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; } h1 { text-align: center; } p { text-indent: 2em; margin-top: 0.5em; }'
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )
        book.add_item(nav_css)

        # 设置 Spine (书脊 - 阅读的线性顺序)
        book.spine = ["nav"] + chapters_objs

        # 5. 保存文件
        output_name = f"{book_meta.get('title', 'book')}.epub"
        output_path = os.path.join(self.output_dir, output_name)

        epub.write_epub(output_path, book, {})
        logger.info(f"🎉 电子书打包完成！已保存到: {output_path}")


if __name__ == "__main__":
    # 配置最简单的控制台日志，方便直接运行测试
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(OUTPUT_DIR, "exporter.log"),
        filemode="w",
    )

    exporter = EpubExporter()
    exporter.run()
