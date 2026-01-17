# -*- coding: utf-8 -*-
"""
简化的配置文件
"""

# 目标小说目录页 URL
# 目标网站的第一章节的地址： https://m.shuhaige.net/22436/214858.html
CATALOG_URL = "/22436/214858.html"

# 根 URL，用于拼接相对路径
BASE_URL = "https://m.shuhaige.net"

# 输出设置
OUTPUT_DIR = "output"
OUTPUT_FILENAME = "book.txt"

# HTTP 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

# 每次请求之间的延迟（秒），做一个有礼貌的爬虫
REQUEST_DELAY_SECONDS = 1
