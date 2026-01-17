
# 发送请求
# 使用 requests 模块
import requests

from lxml import etree # 这个包的作用是解析html
# 目标地址
url = 'https://m.shuhaige.net/22436/48145760.html'
# 伪装浏览器访问
headers = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
}
res = requests.get(url, headers=headers)
res.encoding = 'utf-8'

# 使用etree解析html
html = etree.HTML(res.text)
content_list = html.xpath('//body[@id="chapter"]/div[@class="content"]/p/text()')
content = '\n'.join(content_list)


# 响应信息
print('html: ', html)
print('content: ', content)

# 保存
with open('赘婿节选.txt', 'w', encoding='utf-8') as f:
    f.write(content)