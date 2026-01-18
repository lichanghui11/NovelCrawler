# -*- coding: utf-8 -*-

# 系统的自带模块
import requests
from urllib.parse import urljoin
import logging
import sys
from pprint import pprint
import json
import os
import time

# 第三方模块
from lxml import etree

# 自定义模块
from src.config import (
    CATALOG_URL,
    BASE_URL,
    HEADERS,
    OUTPUT_DIR,
)  # 如果直接运行当前的文件，就直接从 config 导入，如果要放在入口文件执行，这里需要改为 src.config

logger = logging.getLogger(__name__)


def get_catalog():
    """
    该函数用于获取本书的元数据和目录元数据
    """
    book_meta_path = os.path.join(OUTPUT_DIR, "book_meta.json")
    catalog_meta_path = os.path.join(OUTPUT_DIR, "catalog_meta.json")
    if os.path.exists(book_meta_path) and os.path.exists(catalog_meta_path):
        logger.info("书籍元数据和目录元数据已存在，跳过获取")
        return

    fullUrl = urljoin(BASE_URL, CATALOG_URL)
    logger.info(f"《赘婿》小说爬取的整个目录第一页地址： {fullUrl}")
    try:
        response = requests.get(fullUrl, headers=HEADERS, timeout=5)
        response.raise_for_status()  # 主动检查 HTTP 请求是否成功，如果出错立即报错，如果成功则继续执行（如果不使用这个方法，requests默认处理非常宽容，404也会继续执行）
        response.encoding = "utf-8"

        tree = etree.HTML(response.text)
        if tree is None:
            logger.error("无法解析目录页 HTML。")
            return

        # 下面字段用于存储一部分书本的元信息
        book_title = tree.xpath('//*[@id="read"]/div[2]/div[2]/p[1]/strong/text()')[
            0
        ].strip()
        book_author = tree.xpath('//*[@id="read"]/div[2]/div[2]/p[2]/a/text()')[
            0
        ].strip()
        book_latest_chapter = tree.xpath("//*[@id='read']/div[2]/div[2]/p[4]/a/text()")[
            0
        ].strip()
        book_updated_at = tree.xpath("//*[@id='read']/div[2]/div[2]/p[5]/text()")[
            0
        ].strip()
        book_genre = tree.xpath("//*[@id='read']/div[2]/div[2]/p[3]/a/text()")[
            0
        ].strip()
        book_status_text = tree.xpath(
            "//*[@id='read']/div[2]/div[2]/p[3]/span[1]/text()"
        )[0].strip()
        book_word_count = tree.xpath(
            "//*[@id='read']/div[2]/div[2]/p[3]/span[2]/text()"
        )[0].strip()
        cover_img_node = tree.xpath("//*[@id='read']/div[2]/div[2]/img")[0]
        src = cover_img_node.get("src").strip()
        alt = cover_img_node.get("alt").strip()
        cover_img_url = urljoin(BASE_URL, src)
        try:
            logger.info(f"正在下载封面图片：{cover_img_url}")
            # src="https://img.shuhaige.net/22436/42.jpg"
            cover_img_response = requests.get(
                "https://img.shuhaige.net/22436/42.jpg", headers=HEADERS, timeout=15
            )
            cover_img_response.raise_for_status()
            cover_img_response.encoding = "utf-8"
            cover_file_path = os.path.join(OUTPUT_DIR, alt + ".jpg")
            # 保存二进制文件，使用 "wb" Write Binary 模式
            with open(cover_file_path, "wb") as file:
                file.write(cover_img_response.content)
            logger.info(f"封面图片已保存到 {cover_file_path}")
        except Exception as e:
            logger.error(f"获取封面图片失败： {e}")

        book_meta = {
            "title": book_title,
            "cover_file_name": alt + ".jpg",
            "author": book_author,
            "latest_chapter": book_latest_chapter,
            "updated_at": book_updated_at,
            "genre": book_genre,
            "word_count": book_word_count,
            "is_finished": True if book_status_text == "已完结" else False,
        }
        # 这里把构造的元文件存储到本地 json 文件
        if not os.path.exists(OUTPUT_DIR):
            # 如果不存则创建这个文件夹
            os.makedirs(OUTPUT_DIR)
        meta_file_path = os.path.join(OUTPUT_DIR, "book_meta.json")

        # 写入操作
        """
        1. with 是上下文管理器 Context Manager，保证不管在什么情况下，在离开缩紧块时，一定自动把文件关掉
        2. Exception 是一个错误基类，包含所有的错误类型
        3. ValueError (值不对), TypeError (类型不对), FileNotFoundError (文件找不到), IndexError (数组越界), ...
        4. json.loads: 字符串转字典
        5. json.dumps: 字典转字符串
        6. json.load: 从文件读取
        7. json.dump: 写入文件
        """
        try:
            with open(meta_file_path, "w", encoding="utf-8") as file:
                json.dump(book_meta, file, ensure_ascii=False, indent=2)
            logger.info(f"书籍元数据已保存到 {meta_file_path}")
        except Exception as e:
            logger.error(f"保存失败： {e}")

        """
        1. 直接选中所有的a标签，用到xpath的//语法，用于选中所有后代中的某个元素
        2. 也可以先选中外层的ul元素，在循环里面找到当前元素里面的a标签，也会用到xpath的//语法
        """
        catalog = []
        current_url = fullUrl
        idx = 0
        while current_url:
            catalog_nodes = tree.xpath(
                '//*[@id="read"]/div[2]/ul[2]//a'
            )  # 直接选中ul里面的所有a标签   title = node.text.strip()
            for node in catalog_nodes:
                relative_url = node.get("href")
                title = node.text.strip()
                if title and relative_url:
                    catalog.append(
                        {
                            "id": idx,
                            "title": title,
                            "url": urljoin(BASE_URL, relative_url),
                            "status": "pending",
                            "file_name": f"{str(idx).zfill(4)}_{title}.json",
                        }
                    )
                idx += 1
            # logger.info(f"当前页目录解析完成，共 {len(catalog)} 章节")
            next_page_node = tree.xpath(
                '//*[@id="read"]/div[2]/div[4]//a[contains(text(), "下一页")] | //*[@id="read"]/div[2]/div[4]//span[contains(text(), "下一页")]'
            )
            if (
                next_page_node
                and next_page_node[0] is not None
                and next_page_node[0].tag == "a"
            ):
                next_page_url = next_page_node[0].get("href")
                current_url = urljoin(BASE_URL, next_page_url)
                try:
                    # 重新发起请求，重新构建 tree
                    response = requests.get(current_url, headers=HEADERS, timeout=5)
                    response.raise_for_status()
                    response.encoding = "utf-8"
                    tree = etree.HTML(response.text)
                except Exception as err:
                    logger.error(f"下一页翻页请求失败： {err}")
            else:
                break

        # 把目录元数据存入文件
        catalog_file_path = os.path.join(OUTPUT_DIR, "catalog_meta.json")
        try:
            with open(catalog_file_path, "w", encoding="utf-8") as file:
                json.dump(catalog, file, ensure_ascii=False, indent=2)
            logger.info(f"目录元数据已保存到 {catalog_file_path}")
        except Exception as e:
            logger.error(f"保存失败：{e}")

    except requests.RequestException as e:
        logger.error(f"请求目录页失败: {e}")
    except IndexError:
        logger.error("解析书名或作者失败，请检查 XPath。")


def get_content():
    """
    抓取每一章的内容，支持页内翻页和广告过滤
    """
    # 1. 读取目录文件
    catalog_path = os.path.join(OUTPUT_DIR, "catalog_meta.json")
    if not os.path.exists(catalog_path):
        logger.error("未找到目录文件 catalog_meta.json，请先执行 get_catalog()")
        return

    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            chapters = json.load(f)
    except Exception as e:
        logger.error(f"读取目录文件失败: {e}")
        return

    # 2. 创建章节存储目录
    chapters_dir = os.path.join(OUTPUT_DIR, "chapters")
    if not os.path.exists(chapters_dir):
        os.makedirs(chapters_dir)

    total_chapters = len(chapters)
    # 广告关键词列表
    ad_keywords = [
        "m.shuhaige.net",
        "书海阁小说网",
        "更新速度",
        "书海阁",
        "免费阅读",
        "本章完",
        "请大家收藏",
        "本章还未完",
        "点击下一页",
        "后面更精彩",
        "求推荐票",
        "****",
        "投票",
        "三江",
        "码字",
        "~~~",
        "未完待续",
        "新书阶段",
    ]

    for i, chapter in enumerate(chapters):
        chapter_id = chapter["id"]
        title = chapter["title"]
        url = chapter["url"]
        file_name = chapter["file_name"]
        file_path = os.path.join(chapters_dir, file_name)

        # 断点续爬：如果文件已存在，跳过
        if os.path.exists(file_path):
            logger.info(f"[{i + 1}/{total_chapters}] 已存在，跳过: {title}")
            continue

        logger.info(f"[{i + 1}/{total_chapters}] 正在抓取: {title}")

        chapter_lines = []
        current_page_url = url

        # 获取下一章的 URL，用于判断翻页是否跳到了下一章
        next_chapter_url = None
        if i + 1 < total_chapters:
            next_chapter_url = chapters[i + 1]["url"]

        # 页内翻页循环
        while current_page_url:
            try:
                response = requests.get(current_page_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                response.encoding = "utf-8"

                tree = etree.HTML(response.text)
                if tree is None:
                    break

                # 提取正文段落
                content_nodes = tree.xpath(
                    '//*[@id="chapter"]/div[5]//p'
                )  # 拿到这一页的所有 p 标签

                page_lines = []
                for node in content_nodes:
                    text = node.text.strip()
                    if text:
                        page_lines.append(text)

                # 广告过滤：检查最后几行
                if page_lines:
                    # 从后往前检查，只要是广告就移除
                    while page_lines:
                        last_line = page_lines[-1]
                        is_ad = False
                        for keyword in ad_keywords:
                            if keyword in last_line:
                                is_ad = True
                                break
                        if is_ad:
                            page_lines.pop()
                        else:
                            break

                chapter_lines.extend(page_lines)

                # 寻找“下一页”按钮
                next_nodes = tree.xpath('//a[contains(text(), "下一页")]')

                should_continue = False
                if next_nodes:
                    next_href = next_nodes[0].get("href")
                    if next_href:
                        next_full_url = urljoin(current_page_url, next_href)

                        # 判断逻辑：
                        # 1. 如果下一页链接 == 下一章链接 -> 本章结束
                        if next_chapter_url and next_full_url == next_chapter_url:
                            should_continue = False
                        # 2. 如果下一页链接 == 当前页链接 -> 结束
                        elif next_full_url == current_page_url:
                            should_continue = False
                        # 3. 如果是其他链接（通常是 _2.html），继续翻页
                        else:
                            current_page_url = next_full_url
                            should_continue = True

                if not should_continue:
                    # 将当前章节对应的目录元数据的 status 设置为 completed
                    catalog[chapter_id]["status"] = "completed"
                    break

            except Exception as e:
                logger.error(f"抓取页面失败 {current_page_url}: {e}")
                break

        # 保存章节
        if chapter_lines:
            chapter_data = {
                "index": chapter_id,
                "title": title,
                "url": url,
                "lines": chapter_lines,
            }
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(chapter_data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"保存章节失败 {title}: {e}")

        # 章节间延时
        time.sleep(1)


# --- 用于独立测试的入口 ---
"""
1. 如果一个文件没有被执行，会被挂在一个模块名字上面: __name__ = 'src.discovery'
2. 如果一个文件被直接执行，那么就会被挂在一个叫做"__main__"的变量上面: __name__ = '__main__'
3. 通过判断这个环境，在条件分支里面去触发需要执行的逻辑
4. __main__是一个特殊的硬编码字符串，是 Python 的一个约定
5. __name__是 Python 的一个内置变量，表示当前模块的名称
"""
if __name__ == "__main__":  # __name__ 表示当前的模块的名称
    # 1. 配置一个简单的日志记录器，以便在控制台中看到输出
    logging.basicConfig(
        level=logging.INFO,
        # 这里和 Python 的 f"" 语法不一样，这是 logging 定义的模版规则
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    # 2. 执行核心函数
    get_catalog()
    get_content()
