# -*- coding: utf-8 -*-
import requests
from lxml import etree
from urllib.parse import urljoin
import logging

from src.config import CATALOG_URL, BASE_URL, HEADERS


def run_discovery():
    """
    发现阶段：从目录页获取书籍元数据和所有章节。
    Returns:
        (dict, list): 一个包含书籍元数据(title, author)的字典, 以及一个包含章节信息({'title': str, 'url': str})的列表。
    """
    logging.info(f"开始发现章节: {CATALOG_URL}")
    try:
        response = requests.get(CATALOG_URL, headers=HEADERS, timeout=15)
        print("这里获得的response.text: ", response.text)
        response.raise_for_status()
        response.encoding = "utf-8"

        tree = etree.HTML(response.text)
        if tree is None:
            logging.error("无法解析目录页 HTML。")
            return {}, []

        book_title = tree.xpath('//div[@class="block_txt2"]//h2/a/text()')[0].strip()
        book_author = tree.xpath('//div[@class="block_txt2"]//p[1]/a/text()')[0].strip()
        book_meta = {"title": book_title, "author": book_author}

        chapter_nodes = tree.xpath('//div[@id="chapterlist"]//p/a')
        chapters = []
        for node in chapter_nodes:
            title = node.text.strip()
            relative_url = node.get("href")
            if title and relative_url:
                chapters.append(
                    {"title": title, "url": urljoin(BASE_URL, relative_url)}
                )

        logging.info(f"发现书籍:《{book_title}》 作者: {book_author}")
        logging.info(f"共发现 {len(chapters)} 个章节。")
        return book_meta, chapters

    except requests.RequestException as e:
        logging.error(f"请求目录页失败: {e}")
        return {}, []
    except IndexError:
        logging.error("解析书名或作者失败，请检查 XPath。")
        return {}, []
