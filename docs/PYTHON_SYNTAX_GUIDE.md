# Python 语法指南（面向前端开发者）

本文档总结了项目中使用的 Python 核心语法，并与 JavaScript 进行对比。

---

## 目录

1. [类的定义与使用](#1-类的定义与使用)
2. [构造函数 `__init__`](#2-构造函数-__init__)
3. [`self` 关键字](#3-self-关键字)
4. [私有方法与属性](#4-私有方法与属性)
5. [函数定义](#5-函数定义)
6. [类型注解](#6-类型注解)
7. [条件语句](#7-条件语句)
8. [循环语句](#8-循环语句)
9. [异常处理](#9-异常处理)
10. [其他重要语法](#10-其他重要语法)

---

## 1. 类的定义与使用

### JavaScript

```javascript
class CatalogParser {
    constructor() {
        this.baseUrl = 'https://example.com';
    }
    
    parse(html) {
        return this.extractData(html);
    }
}

// 实例化（需要 new）
const parser = new CatalogParser();
parser.parse(htmlContent);
```

### Python

```python
class CatalogParser:  # 注意：冒号不是花括号
    def __init__(self):  # 构造函数
        self.base_url = 'https://example.com'
    
    def parse(self, html):  # 必须有 self 参数
        return self.extract_data(html)

# 实例化（不需要 new）
parser = CatalogParser()
parser.parse(html_content)
```

### 关键差异

| 特性 | JavaScript | Python |
|------|-----------|--------|
| 类定义 | `class Name { }` | `class Name:` |
| 实例化 | `new Class()` | `Class()` |
| 代码块 | 花括号 `{ }` | **缩进**（4个空格） |

### 项目实例

```python
# src/discovery.py
class Discoverer:
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
        self.logger = logging.getLogger('novel_crawler.discover')
        self.parser = CatalogParser()
    
    async def discover(self):
        # 实现逻辑
        pass
```

---

## 2. 构造函数 `__init__`

### JavaScript

```javascript
class Worker {
    constructor(database, client) {
        this.db = database;
        this.client = client;
        this.logger = getLogger('worker');
    }
}
```

### Python

```python
class Worker:
    def __init__(self, database, client):  # 双下划线 __init__
        self.db = database                 # 实例属性
        self.client = client
        self.logger = logging.getLogger('worker')
```

### 关键点

1. **名称固定**：必须是 `__init__`（前后各两个下划线）
2. **必须有 self**：第一个参数必须是 `self`
3. **无需 return**：构造函数不需要返回值
4. **立即执行**：实例化时自动调用

### 项目实例

```python
# src/fetcher.py
class WorkerPool:
    def __init__(self, database: Database):
        self.db = database
        self.config = Config()
        self.logger = logging.getLogger('novel_crawler.pool')
        self.max_workers = self.config.get('concurrency.max_workers', 5)
```

---

## 3. `self` 关键字

### 核心概念

`self` 代表**实例本身**，等同于 JavaScript 的 `this`，但有重要区别：

### JavaScript（隐式）

```javascript
class Example {
    constructor() {
        this.name = 'test';  // this 隐式绑定
    }
    
    greet() {
        console.log(this.name);  // 自动有 this
    }
}
```

### Python（显式）

```python
class Example:
    def __init__(self):
        self.name = 'test'  # self 必须显式写
    
    def greet(self):  # 必须声明 self 参数
        print(self.name)  # 使用 self 访问属性
```

### 为什么必须写 self？

```python
# Python 方法调用的本质
worker = Worker(db, client)
worker.process(task)

# 等价于：
Worker.process(worker, task)  # self 就是实例本身！
```

### 规则总结

| 场景 | 是否需要 self |
|------|--------------|
| 实例方法的第一个参数 | ✅ 必须 |
| 访问实例属性 | ✅ 必须 `self.attr` |
| 调用实例方法 | ✅ 必须 `self.method()` |
| 调用时传参 | ❌ 自动传入，不需要写 |

### 项目实例

```python
# src/fetcher.py
class Worker:
    def __init__(self, database: Database, client: AsyncHTTPClient):
        self.db = database        # 创建实例属性
        self.client = client
        self.parser = ContentParser()  # 另一个实例
    
    async def process_task(self, task: ChapterTask):
        html = await self.client.fetch(task.url)  # 访问实例属性
        content = self.parser.parse(html)         # 调用实例方法
        self.db.update_task_status(...)           # 访问另一个实例
```

---

## 4. 私有方法与属性

### JavaScript（ES2022+）

```javascript
class Parser {
    #privateField = 'secret';  // 真正私有
    publicField = 'public';
    
    #privateMethod() {  // 真正私有
        return this.#privateField;
    }
    
    publicMethod() {
        return this.#privateMethod();
    }
}
```

### Python（约定而非强制）

```python
class Parser:
    def __init__(self):
        self.public_field = 'public'      # 公开
        self._protected_field = 'internal'  # 约定：内部使用
        self.__private_field = 'secret'   # 名称改写（弱私有）
    
    def _private_method(self):  # 约定：下划线开头表示私有
        return self._protected_field
    
    def public_method(self):
        return self._private_method()
```

### 命名约定

| 前缀 | 含义 | 可访问性 |
|------|------|----------|
| 无前缀 `public` | 公开 | 完全公开 |
| 单下划线 `_internal` | **约定私有** | 可访问，但不建议 |
| 双下划线 `__private` | 名称改写 | 可访问（`_ClassName__private`） |

### 项目实例

```python
# src/discovery.py
class CatalogParser:
    def parse(self, html: str) -> List[ChapterInfo]:
        # 公开方法
        tree = etree.HTML(html)
        chapters = []
        # ...
        return chapters
    
    def _is_chapter_link(self, url: str, title: str) -> bool:
        # 私有方法（约定）：只在类内部使用
        exclude_keywords = ['目录', '书架', '首页']
        for keyword in exclude_keywords:
            if keyword in title.lower():
                return False
        return True
```

---

## 5. 函数定义

### 基本语法对比

#### JavaScript

```javascript
// 普通函数
function add(a, b) {
    return a + b;
}

// 箭头函数
const multiply = (a, b) => a * b;

// 异步函数
async function fetchData(url) {
    const response = await fetch(url);
    return response.text();
}
```

#### Python

```python
# 普通函数
def add(a, b):
    return a + b

# Lambda 表达式（类似箭头函数）
multiply = lambda a, b: a * b

# 异步函数
async def fetch_data(url):
    response = await aiohttp.get(url)
    return await response.text()
```

### 参数类型

#### 1. 位置参数

```python
def greet(name, age):
    print(f"{name} is {age} years old")

greet("Alice", 25)  # 必须按顺序传参
```

#### 2. 默认参数

```python
def greet(name, age=18):  # age 有默认值
    print(f"{name} is {age} years old")

greet("Bob")        # age 使用默认值 18
greet("Alice", 25)  # age 使用传入的 25
```

#### 3. 关键字参数

```python
def create_user(name, age, city):
    return {'name': name, 'age': age, 'city': city}

# 可以指定参数名（顺序无关）
user = create_user(age=30, name="Charlie", city="Beijing")
```

#### 4. 可变参数

```python
# *args: 接收任意数量的位置参数（元组）
def sum_all(*numbers):
    return sum(numbers)

sum_all(1, 2, 3, 4)  # 10

# **kwargs: 接收任意数量的关键字参数（字典）
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="Shanghai")
```

### 项目实例

```python
# src/utils.py
def atomic_write(file_path: str, content: str):
    """普通函数"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    tmp_path = f"{file_path}.tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    os.replace(tmp_path, file_path)


# src/utils.py
class Database:
    def get_pending_tasks(self, limit: Optional[int] = None) -> List[ChapterTask]:
        """
        方法示例：
        - limit 有默认值 None
        - 返回类型是 List[ChapterTask]
        """
        # ...
        return tasks
```

---

## 6. 类型注解

### 为什么需要类型注解？

Python 是**动态类型**语言，但类型注解可以：
- 提高代码可读性
- IDE 自动补全和类型检查
- 帮助发现潜在错误

> **注意**：类型注解**不是强制**的，只是提示！运行时不会检查。

### JavaScript（TypeScript）

```typescript
function add(a: number, b: number): number {
    return a + b;
}

let name: string = "Alice";
let age: number = 25;
```

### Python

```python
def add(a: int, b: int) -> int:
    return a + b

name: str = "Alice"
age: int = 25
```

### 常用类型注解

#### 基本类型

```python
# 基础类型
name: str = "Alice"
age: int = 25
price: float = 19.99
is_active: bool = True

# 列表
numbers: list = [1, 2, 3]
names: List[str] = ["Alice", "Bob"]  # 指定元素类型

# 字典
user: dict = {"name": "Alice"}
user: Dict[str, int] = {"age": 25}  # 指定键值类型

# 元组
point: Tuple[int, int] = (10, 20)

# 可选类型（可以为 None）
result: Optional[str] = None
result: Optional[str] = "success"
```

#### 函数注解

```python
# 基本函数
def greet(name: str) -> str:
    return f"Hello, {name}"

# 无返回值
def log(message: str) -> None:
    print(message)

# 可选参数
def divide(a: int, b: int = 1) -> float:
    return a / b

# 列表返回值
def get_names() -> List[str]:
    return ["Alice", "Bob"]
```

#### 类型导入

```python
from typing import List, Dict, Tuple, Optional, Union

# Union: 多种类型之一
def process(data: Union[str, int]) -> None:
    pass

# 可以接收 str 或 int
process("hello")
process(123)
```

### 项目实例

```python
# src/utils.py
@dataclass
class ChapterInfo:
    """数据类：自动生成 __init__ 等方法"""
    chapter_index: int
    title: str
    url: str


# src/discovery.py
class CatalogParser:
    def parse(self, html: str) -> List[ChapterInfo]:
        """
        参数 html 是字符串
        返回值是 ChapterInfo 对象的列表
        """
        tree = etree.HTML(html)
        chapters: List[ChapterInfo] = []  # 声明类型
        # ...
        return chapters
    
    def _is_chapter_link(self, url: str, title: str) -> bool:
        """返回布尔值"""
        return True


# src/utils.py
class Database:
    def get_pending_tasks(self, limit: Optional[int] = None) -> List[ChapterTask]:
        """
        limit 可以是 int 或 None
        返回 ChapterTask 列表
        """
        # ...
        return tasks
```

---

## 7. 条件语句

### JavaScript

```javascript
if (status === 'success') {
    console.log('成功');
} else if (status === 'pending') {
    console.log('处理中');
} else {
    console.log('失败');
}

// 三元运算符
const message = age >= 18 ? '成人' : '未成年';
```

### Python

```python
if status == 'success':  # 注意：冒号，单个等号比较
    print('成功')
elif status == 'pending':  # elif 不是 else if
    print('处理中')
else:
    print('失败')

# 三元表达式（顺序不同！）
message = '成人' if age >= 18 else '未成年'
```

### 关键差异

| 特性 | JavaScript | Python |
|------|-----------|--------|
| 判断语法 | `if (condition) { }` | `if condition:` |
| else if | `else if` | `elif` |
| 布尔值 | `true` / `false` | `True` / `False`（首字母大写） |
| 相等比较 | `===` | `==` |
| 不等比较 | `!==` | `!=` |
| 逻辑与 | `&&` | `and` |
| 逻辑或 | `||` | `or` |
| 逻辑非 | `!` | `not` |

### 真值判断

```python
# Python 中的假值（Falsy）
if 0:           # False
if None:        # False
if '':          # False
if []:          # False（空列表）
if {}:          # False（空字典）

# 真值（Truthy）
if 1:           # True
if 'hello':     # True
if [1, 2]:      # True
```

### 项目实例

```python
# src/discovery.py
def _is_chapter_link(self, url: str, title: str) -> bool:
    exclude_keywords = ['目录', '书架', '首页']
    for keyword in exclude_keywords:
        if keyword in title.lower() or keyword in url.lower():
            return False
    
    if '.html' in url and any(char.isdigit() for char in url):
        return True
    
    return False


# src/utils.py
def get_pending_tasks(self, limit: Optional[int] = None) -> List[ChapterTask]:
    query = "SELECT * FROM chapters WHERE status IN ('pending', 'failed')"
    
    if limit:  # 如果 limit 不为 None
        query += " LIMIT ?"
```

---

## 8. 循环语句

### for 循环

#### JavaScript

```javascript
// 数组遍历
const names = ['Alice', 'Bob', 'Charlie'];
for (const name of names) {
    console.log(name);
}

// 带索引
names.forEach((name, index) => {
    console.log(`${index}: ${name}`);
});

// 传统 for
for (let i = 0; i < 10; i++) {
    console.log(i);
}
```

#### Python

```python
# 列表遍历
names = ['Alice', 'Bob', 'Charlie']
for name in names:
    print(name)

# 带索引（使用 enumerate）
for index, name in enumerate(names):
    print(f"{index}: {name}")

# 指定起始索引
for index, name in enumerate(names, start=1):
    print(f"{index}: {name}")  # 从 1 开始

# 范围循环（类似传统 for）
for i in range(10):  # 0 到 9
    print(i)

for i in range(1, 11):  # 1 到 10
    print(i)

for i in range(0, 10, 2):  # 0, 2, 4, 6, 8（步长为 2）
    print(i)
```

### while 循环

```python
# Python
count = 0
while count < 5:
    print(count)
    count += 1
```

### 循环控制

| 语句 | JavaScript | Python |
|------|-----------|--------|
| 跳出循环 | `break` | `break` |
| 跳过当前迭代 | `continue` | `continue` |

```python
for i in range(10):
    if i == 3:
        continue  # 跳过 3
    if i == 7:
        break     # 在 7 处停止
    print(i)  # 输出 0, 1, 2, 4, 5, 6
```

### 字典遍历

```python
user = {'name': 'Alice', 'age': 25, 'city': 'Beijing'}

# 遍历键
for key in user:
    print(key)

# 遍历值
for value in user.values():
    print(value)

# 遍历键值对
for key, value in user.items():
    print(f"{key}: {value}")
```

### 项目实例

```python
# src/discovery.py
def parse(self, html: str) -> List[ChapterInfo]:
    chapter_links = tree.xpath('//a[contains(@href, ".html")]')
    
    # enumerate 带索引遍历
    for index, link in enumerate(chapter_links, start=1):
        try:
            title = link.xpath('string(.)').strip()
            url = link.get('href', '')
            
            if not title or not url:
                continue  # 跳过空数据
            
            chapters.append(ChapterInfo(
                chapter_index=index,
                title=title,
                url=absolute_url
            ))
        except Exception as e:
            self.logger.error(f"解析章节链接失败: {e}")
    
    return chapters


# src/fetcher.py
async def run(self):
    while True:  # 无限循环
        tasks = self.db.get_pending_tasks(limit=self.max_workers * 2)
        
        if not tasks:
            break  # 没有任务则退出
        
        await asyncio.gather(...)
```

---

## 9. 异常处理

### JavaScript

```javascript
try {
    const data = JSON.parse(jsonString);
    console.log(data);
} catch (error) {
    console.error('解析失败:', error.message);
} finally {
    console.log('清理资源');
}

// 抛出异常
throw new Error('自定义错误');
```

### Python

```python
try:
    data = json.loads(json_string)
    print(data)
except ValueError as e:  # 捕获特定异常
    print(f'解析失败: {e}')
except Exception as e:   # 捕获所有异常
    print(f'未知错误: {e}')
else:                    # 没有异常时执行
    print('成功')
finally:                 # 总是执行
    print('清理资源')

# 抛出异常
raise ValueError('自定义错误')
```

### 常见异常类型

```python
# ValueError: 值错误
int('abc')  # ValueError: invalid literal

# KeyError: 键不存在
user = {'name': 'Alice'}
user['age']  # KeyError: 'age'

# FileNotFoundError: 文件不存在
open('/nonexistent/file.txt')

# TypeError: 类型错误
'10' + 10  # TypeError: can only concatenate str

# AttributeError: 属性不存在
obj.nonexistent_method()

# IndexError: 索引超出范围
list = [1, 2, 3]
list[10]  # IndexError: list index out of range
```

### 多个异常处理

```python
try:
    result = int(user_input) / divisor
except ValueError:
    print('输入不是数字')
except ZeroDivisionError:
    print('除数不能为零')
except (TypeError, AttributeError) as e:  # 捕获多个异常
    print(f'类型或属性错误: {e}')
```

### 项目实例

```python
# src/fetcher.py
async def process_task(self, task: ChapterTask):
    try:
        # 1. 抓取 HTML
        html = await self.client.fetch(task.url)
        
        # 2. 解析内容
        content = self.parser.parse(html, default_title=task.title)
        
        # 3. 保存文件
        file_path = os.path.join(self.chapters_dir, f"{task.chapter_index:04d}.xhtml")
        atomic_write(file_path, content.content_html)
        
        # 4. 更新数据库
        self.db.update_task_status(task.id, status='done', content_path=file_path)
        
    except ValueError as e:
        # 解析失败，标记为跳过
        self.logger.warning(f"[{task.chapter_index}] 跳过: {e}")
        self.db.update_task_status(task.id, status='skipped', error=str(e))
    
    except Exception as e:
        # 其他错误，标记为失败并增加重试次数
        self.logger.error(f"[{task.chapter_index}] ✗ 失败: {e}")
        self.db.update_task_status(
            task.id, status='failed', error=str(e), increment_retries=True
        )


# src/discovery.py
async def discover(self):
    try:
        async with AsyncHTTPClient() as client:
            html = await client.fetch(catalog_url)
        
        chapters = self.parser.parse(html)
        # ...
    except Exception as e:
        self.logger.error(f"发现阶段失败: {e}", exc_info=True)
        raise  # 重新抛出异常
```

---

## 10. 其他重要语法

### 10.1 字符串格式化

#### JavaScript

```javascript
const name = "Alice";
const age = 25;

// 模板字符串
const message = `${name} is ${age} years old`;
```

#### Python

```python
name = "Alice"
age = 25

# f-string（推荐，Python 3.6+）
message = f"{name} is {age} years old"

# 格式化输出
print(f"进度: {done}/{total} ({done/total*100:.1f}%)")  # .1f 保留1位小数

# 填充零
print(f"{chapter_index:04d}")  # 0001, 0002, ...
```

### 10.2 列表推导式

```python
# JavaScript
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(x => x * 2);
const evens = numbers.filter(x => x % 2 === 0);

# Python（更简洁）
numbers = [1, 2, 3, 4, 5]
doubled = [x * 2 for x in numbers]           # [2, 4, 6, 8, 10]
evens = [x for x in numbers if x % 2 == 0]   # [2, 4]
```

### 10.3 None（空值）

```python
# JavaScript: null, undefined
let value = null;

# Python: None
value = None

# 判断
if value is None:
    print("值为空")

if value is not None:
    print("值不为空")
```

### 10.4 上下文管理器（with）

```python
# 自动资源管理（类似 try-finally）
with open('file.txt', 'r') as f:
    content = f.read()
# 文件自动关闭，即使出错

# 项目中的使用
async with AsyncHTTPClient() as client:
    html = await client.fetch(url)
# client 自动关闭连接
```

### 10.5 导入模块

```python
# 导入整个模块
import os
import logging

# 导入特定函数/类
from lxml import etree
from typing import List, Optional

# 别名导入
import asyncio as aio

# 从项目内部导入
from src.utils import Config, Database
```

---

## 快速对照表

| 功能 | JavaScript | Python |
|------|-----------|--------|
| 定义变量 | `let x = 1` | `x = 1` |
| 常量 | `const X = 1` | `X = 1`（约定大写） |
| 字符串 | `'hello'` 或 `"hello"` | `'hello'` 或 `"hello"` |
| 模板字符串 | `` `${x}` `` | `f"{x}"` |
| 数组/列表 | `[1, 2, 3]` | `[1, 2, 3]` |
| 对象/字典 | `{key: value}` | `{'key': value}` |
| 注释 | `// 单行` `/* 多行 */` | `# 单行` `"""多行"""` |
| 函数 | `function f() { }` | `def f():` |
| 箭头函数 | `(x) => x * 2` | `lambda x: x * 2` |
| 等于 | `===` | `==` |
| 不等 | `!==` | `!=` |
| 且 | `&&` | `and` |
| 或 | `||` | `or` |
| 非 | `!` | `not` |
| 空值 | `null` | `None` |
| 真 | `true` | `True` |
| 假 | `false` | `False` |

---

## 学习建议

1. **关注缩进**：Python 用缩进表示代码块，混乱会报错
2. **记住 self**：实例方法第一个参数必须是 `self`
3. **类型注解是可选的**：但建议使用，提高可读性
4. **异常处理很重要**：善用 try-except 捕获错误
5. **阅读项目代码**：最好的学习方式是看真实代码

---

## 推荐练习

尝试在 Python REPL 中练习：

```bash
python3
>>> name = "Alice"
>>> f"Hello, {name}"
'Hello, Alice'
>>> [x * 2 for x in range(5)]
[0, 2, 4, 6, 8]
```

祝学习顺利！🚀
