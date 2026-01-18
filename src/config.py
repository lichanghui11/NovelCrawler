# -*- coding: utf-8 -*-
import os

"""
简化的配置文件
"""

# 目标小说目录页 URL
# 目标网站的第一章节的地址： https://m.shuhaige.net/22436/214858.html
CATALOG_URL = "/22436/"

# 根 URL，用于拼接相对路径
BASE_URL = "https://m.shuhaige.net"


# 获取项目根目录 (即当前 config.py 所在目录 src/ 的上一级目录)
# __file__ 是当前文件的绝对路径
# os.path.dirname(__file__) 拿到当前文件的父目录，即 src/
# 再包一层 os.path.dirname(...) 拿到当前文件的父目录的父目录，即 NovelCrawler/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 输出设置：使用绝对路径，避免因为运行目录不同导致找不到文件夹
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# HTTP 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

# 每次请求之间的延迟（秒），做一个有礼貌的爬虫
REQUEST_DELAY_SECONDS = 1
