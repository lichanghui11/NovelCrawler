"""
Phase 3: 导出阶段
将抓取的章节生成 EPUB 电子书
"""

import logging
import os
from ebooklib import epub

from src.utils import Config, Database


class EPUBGenerator:
    """EPUB 生成器"""
    
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
        self.logger = logging.getLogger('novel_crawler.epub')
    
    def generate(self, output_path: Optional[str] = None):
        """
        生成 EPUB 文件
        
        Args:
            output_path: 输出文件路径（默认使用配置中的路径）
        """
        if output_path is None:
            output_path = self.config.get('output.epub_file', 'output/book.epub')
        
        self.logger.info(f"开始生成 EPUB: {output_path}")
        
        # 获取已完成的章节
        chapters = self.db.get_done_chapters()
        
        if not chapters:
            self.logger.error("没有已完成的章节，无法生成 EPUB")
            return
        
        self.logger.info(f"找到 {len(chapters)} 个已完成章节")
        
        # 创建 EPUB 对象
        book = epub.EpubBook()
        
        # 设置元数据
        book_title = self.db.get_metadata('book_title') or self.config.get('book.title', '未命名小说')
        book_author = self.db.get_metadata('book_author') or self.config.get('book.author', '未知作者')
        book_language = self.config.get('book.language', 'zh')
        
        book.set_identifier(f'novel_{hash(book_title)}')
        book.set_title(book_title)
        book.set_language(book_language)
        book.add_author(book_author)
        
        self.logger.info(f"书名: {book_title}, 作者: {book_author}")
        
        # 添加章节
        epub_chapters = []
        spine = ['nav']
        
        for chapter_index, title, content_path in chapters:
            try:
                # 读取章节内容
                if not os.path.exists(content_path):
                    self.logger.warning(f"章节文件不存在: {content_path}")
                    continue
                
                with open(content_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 创建 EPUB 章节
                chapter_filename = f'chapter_{chapter_index:04d}.xhtml'
                epub_chapter = epub.EpubHtml(
                    title=title,
                    file_name=chapter_filename,
                    lang=book_language
                )
                epub_chapter.set_content(content)
                
                book.add_item(epub_chapter)
                epub_chapters.append(epub_chapter)
                spine.append(epub_chapter)
                
            except Exception as e:
                self.logger.error(f"添加章节失败 [{chapter_index}] {title}: {e}")
        
        if not epub_chapters:
            self.logger.error("没有成功添加任何章节")
            return
        
        # 添加目录
        book.toc = epub_chapters
        
        # 添加必需的文件
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # 设置阅读顺序
        book.spine = spine
        
        # 写入文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        epub.write_epub(output_path, book, {})
        
        self.logger.info(f"✓ EPUB 生成成功: {output_path} ({len(epub_chapters)} 章)")


def run_exporter(output_path: Optional[str] = None):
    """运行导出阶段的入口函数"""
    from src.utils import setup_logger
    
    logger = setup_logger()
    config = Config()
    
    db = Database(config.get('database.path'))
    generator = EPUBGenerator(db)
    
    generator.generate(output_path)
