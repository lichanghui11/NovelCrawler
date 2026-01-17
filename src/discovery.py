"""
Phase 1: 发现阶段
从目录页解析章节列表，写入数据库
"""

import logging
from typing import List
from lxml import etree
from urllib.parse import urljoin

from src.utils import Config, Database, AsyncHTTPClient, ChapterInfo


class CatalogParser:
    """目录页解析器"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('novel_crawler.parser')
        self.base_url = self.config.get('target.base_url')
    
    def parse(self, html: str) -> List[ChapterInfo]:
        """
        解析目录页 HTML，提取章节列表
        
        Args:
            html: 目录页 HTML 内容
            
        Returns:
            章节列表
        """
        tree = etree.HTML(html)
        chapters = []
        
        # XPath 根据实际网站结构调整
        # 书海阁的章节列表通常在 <ul class="chapter-list"> 或类似结构中
        # 这里需要根据实际 HTML 结构调整
        
        # 示例 XPath（需要根据实际网站调整）
        chapter_links = tree.xpath('//div[@class="chapter-list"]//a | //ul[@class="chapter"]//a')
        
        if not chapter_links:
            # 尝试更通用的选择器
            chapter_links = tree.xpath('//a[contains(@href, ".html")]')
            self.logger.warning(f"使用通用选择器找到 {len(chapter_links)} 个链接")
        
        for index, link in enumerate(chapter_links, start=1):
            try:
                title = link.xpath('string(.)').strip()
                url = link.get('href', '')
                
                if not title or not url:
                    continue
                
                # 转换为绝对 URL
                absolute_url = urljoin(self.base_url, url)
                
                # 过滤非章节链接（可根据实际情况调整）
                if not self._is_chapter_link(absolute_url, title):
                    continue
                
                chapters.append(ChapterInfo(
                    chapter_index=index,
                    title=title,
                    url=absolute_url
                ))
            except Exception as e:
                self.logger.error(f"解析章节链接失败: {e}")
        
        self.logger.info(f"解析到 {len(chapters)} 个章节")
        return chapters
    
    def _is_chapter_link(self, url: str, title: str) -> bool:
        """
        判断链接是否为章节链接
        可以根据 URL 模式或标题进行过滤
        """
        # 排除明显不是章节的链接
        exclude_keywords = ['目录', '书架', '首页', '排行', '搜索', 'index', 'list']
        for keyword in exclude_keywords:
            if keyword in title.lower() or keyword in url.lower():
                return False
        
        # 章节链接通常包含数字
        if '.html' in url and any(char.isdigit() for char in url):
            return True
        
        return False
    
    def parse_book_metadata(self, html: str) -> dict:
        """
        从目录页解析书籍元数据（书名、作者等）
        
        Returns:
            {'title': '书名', 'author': '作者'}
        """
        tree = etree.HTML(html)
        metadata = {}
        
        try:
            # 根据实际网站结构调整 XPath
            title_elem = tree.xpath('//h1[@class="book-title"]//text() | //div[@class="book-info"]//h1//text()')
            if title_elem:
                metadata['title'] = title_elem[0].strip()
            
            author_elem = tree.xpath('//span[@class="author"]//text() | //div[@class="author"]//text()')
            if author_elem:
                metadata['author'] = author_elem[0].strip()
        except Exception as e:
            self.logger.error(f"解析书籍元数据失败: {e}")
        
        return metadata


class Discoverer:
    """发现协调器"""
    
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
        self.logger = logging.getLogger('novel_crawler.discover')
        self.parser = CatalogParser()
    
    async def discover(self):
        """
        执行发现流程：
        1. 请求目录页
        2. 解析章节列表
        3. 写入数据库
        4. 保存书籍元数据
        """
        catalog_url = self.config.get('target.catalog_url')
        self.logger.info(f"开始发现章节: {catalog_url}")
        
        try:
            # 请求目录页
            async with AsyncHTTPClient() as client:
                html = await client.fetch(catalog_url)
            
            # 解析章节列表
            chapters = self.parser.parse(html)
            
            if not chapters:
                self.logger.error("未解析到任何章节！请检查 XPath 选择器")
                return
            
            # 写入数据库（幂等）
            inserted = self.db.insert_chapters(chapters)
            self.logger.info(f"发现完成：共 {len(chapters)} 章，新增 {inserted} 章")
            
            # 解析并保存书籍元数据
            metadata = self.parser.parse_book_metadata(html)
            if metadata.get('title'):
                self.db.set_metadata('book_title', metadata['title'])
                self.logger.info(f"书名: {metadata['title']}")
            if metadata.get('author'):
                self.db.set_metadata('book_author', metadata['author'])
                self.logger.info(f"作者: {metadata['author']}")
            
            self.db.set_metadata('total_chapters', str(len(chapters)))
            self.db.set_metadata('catalog_url', catalog_url)
            
        except Exception as e:
            self.logger.error(f"发现阶段失败: {e}", exc_info=True)
            raise


async def run_discovery():
    """运行发现阶段的入口函数"""
    from src.utils import setup_logger
    
    logger = setup_logger()
    config = Config()
    
    db = Database(config.get('database.path'))
    discoverer = Discoverer(db)
    
    await discoverer.discover()
