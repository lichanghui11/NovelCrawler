# -*- coding: utf-8 -*-
import requests
from lxml import etree
import time
import logging

from src.config import HEADERS, REQUEST_DELAY_SECONDS


def _parse_content(html_text: str):
    """从 HTML 中解析正文内容"""
    tree = etree.HTML(html_text)
    if tree is None:
        return None

    p_elements = tree.xpath('//body[@id="chapter"]/div[@class="content"]/p')
    paragraphs = []
    for p in p_elements:
        text = p.text_content().strip()
        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs) if paragraphs else None


def run_fetcher(chapters_to_fetch: list):
    """
    抓取阶段：接收章节列表，抓取内容，返回包含内容的完整列表。
    Args:
        chapters_to_fetch (list): 从 discovery 阶段获取的章节信息列表。
    Returns:
        list: 包含完整内容的章节列表 [{'title': str, 'content': str}]。
    """
    logging.info(f"开始抓取 {len(chapters_to_fetch)} 个章节...")
    completed_chapters = []
    total = len(chapters_to_fetch)

    for i, chapter_info in enumerate(chapters_to_fetch, 1):
        url = chapter_info["url"]
        title = chapter_info["title"]
        logging.info(f"  -> 正在抓取 [{i}/{total}]: {title}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            response.encoding = "utf-8"

            content = _parse_content(response.text)
            if content:
                completed_chapters.append({"title": title, "content": content})
            else:
                logging.warning(f"  - 警告: 未能从 {url} 提取到正文内容。")

        except requests.RequestException as e:
            logging.error(f"  - 错误: 抓取章节失败 {url} - {e}")

        # 礼貌性延迟
        time.sleep(REQUEST_DELAY_SECONDS)

    logging.info(f"抓取完成。成功获取 {len(completed_chapters)}/{total} 个章节的内容。")
    return completed_chapters
