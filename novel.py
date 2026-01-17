# 发送请求
# 使用 requests 模块
import requests
import sys

from lxml import etree  # 这个包的作用是解析html

# 目标地址
url = "https://m.shuhaige.net/22436/48145760.html"
# 伪装浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
}

try:
    res = requests.get(url, headers=headers, timeout=10)
    print(f"请求状态码: {res.status_code}")

    # 1. 检查请求是否成功 (例如 200 OK)。如果状态码是 4xx 或 5xx，会抛出异常。
    res.raise_for_status()

    res.encoding = "utf-8"

    # 使用etree解析html
    html = etree.HTML(res.text)

    # 2. 关键检查：如果html解析失败返回None，就无法调用.xpath()方法
    if html is None:
        print("错误: HTML解析失败，返回了None。无法继续执行。")
        print("服务器返回内容的前200个字符:", res.text[:200])
        sys.exit(1)  # 退出程序

    # 3. 这是一个更健壮的解析方式，先找到所有<p>标签，再提取它们的文本
    p_elements = html.xpath('//body[@id="chapter"]/div[@class="content"]/p')
    content_list = []
    for p in p_elements:
        # .strip()可以去除文本两端的空白字符（包括换行）
        text = etree.tostring(p, method="text", encoding="unicode").strip()
        if text:  # 确保不是空段落
            content_list.append(text)

    # 使用两个换行符连接段落，这样阅读体验更好
    content = "\n\n".join(content_list)

    if not content:
        print("警告: 未能解析到任何内容。请检查XPath或网页结构是否已更改。")
        sys.exit(1)

    # 保存
    with open("赘婿节选.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("成功抓取内容并保存到 '赘婿节选.txt'")

except requests.exceptions.RequestException as e:
    print(f"网络请求错误: {e}")
except Exception as e:
    print(f"发生了一个错误: {e}")
