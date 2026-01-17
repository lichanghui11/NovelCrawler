# Python 魔法方法完全指南

**魔法方法**（Magic Methods）又称**特殊方法**（Special Methods）或 **Dunder Methods**（Double Underscore），是 Python 中以双下划线 `__` 开头和结尾的预定义方法。

> **重要提示**：魔法方法的名称都是 Python 固定的，不能随意修改！

---

## 目录

1. [对象生命周期](#1-对象生命周期-⭐⭐⭐⭐⭐)
2. [字符串表示](#2-字符串表示-⭐⭐⭐⭐⭐)
3. [比较运算符](#3-比较运算符-⭐⭐⭐⭐)
4. [算术运算符](#4-算术运算符-⭐⭐⭐)
5. [容器类型](#5-容器类型-⭐⭐⭐⭐)
6. [上下文管理器](#6-上下文管理器-⭐⭐⭐⭐)
7. [属性访问](#7-属性访问-⭐⭐⭐)
8. [可调用对象](#8-可调用对象-⭐⭐)
9. [其他常用方法](#9-其他常用方法)

**星级说明**：⭐ 越多表示实际业务中越常用

---

## 1. 对象生命周期 ⭐⭐⭐⭐⭐

### `__new__(cls, ...)`
**调用时机**：创建对象时（在 `__init__` 之前）  
**用途**：控制对象的创建过程  
**常用场景**：单例模式、不可变类型

```python
# ⭐⭐⭐⭐⭐ 最常见：单例模式
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

config1 = Config()
config2 = Config()
print(config1 is config2)  # True（同一个对象）
```

---

### `__init__(self, ...)`
**调用时机**：初始化对象时（在 `__new__` 之后）  
**用途**：初始化实例属性  
**常用场景**：几乎所有类都需要

```python
# ⭐⭐⭐⭐⭐ 最常用的魔法方法
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

user = User("Alice", 25)
```

**重要规则**：
- 第一个参数必须是 `self`
- 不需要返回值（返回 `None`）
- 可以有任意数量的参数

---

### `__del__(self)`
**调用时机**：对象被销毁时（垃圾回收）  
**用途**：清理资源  
**常用场景**：关闭文件、释放连接

```python
# ⭐⭐ 不太常用（Python 有自动垃圾回收）
class FileHandler:
    def __init__(self, filename):
        self.file = open(filename, 'w')
    
    def __del__(self):
        self.file.close()
        print("文件已关闭")

# 不推荐这样做！应该用上下文管理器（with 语句）
```

**注意**：不保证一定会被调用，推荐用上下文管理器代替。

---

## 2. 字符串表示 ⭐⭐⭐⭐⭐

### `__repr__(self)`
**调用时机**：`repr(obj)` 或在交互式环境中  
**用途**：返回开发者友好的字符串表示  
**常用场景**：调试、日志

```python
# ⭐⭐⭐⭐⭐ 强烈推荐实现
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __repr__(self):
        return f"User(name='{self.name}', age={self.age})"

user = User("Alice", 25)
print(repr(user))  # User(name='Alice', age=25)
print(user)        # User(name='Alice', age=25)（没有 __str__ 时会调用 __repr__）
```

**最佳实践**：应该返回能重新创建对象的字符串
```python
# 理想情况
user = User("Alice", 25)
repr_str = repr(user)  # "User(name='Alice', age=25)"
# 应该能执行：eval(repr_str) 得到相同的对象
```

---

### `__str__(self)`
**调用时机**：`str(obj)` 或 `print(obj)`  
**用途**：返回用户友好的字符串表示  
**常用场景**：显示给最终用户

```python
# ⭐⭐⭐⭐ 常用于用户界面
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __repr__(self):
        return f"User(name='{self.name}', age={self.age})"
    
    def __str__(self):
        return f"{self.name}（{self.age}岁）"

user = User("Alice", 25)
print(str(user))   # Alice（25岁）
print(repr(user))  # User(name='Alice', age=25)
```

**区别总结**：
| 方法 | 目标受众 | 用途 | 优先级 |
|------|---------|------|-------|
| `__repr__` | 开发者 | 调试、日志 | 高（建议总是实现） |
| `__str__` | 最终用户 | 显示 | 中（可选） |

---

### `__format__(self, format_spec)`
**调用时机**：`format(obj, spec)` 或 f-string  
**用途**：自定义格式化输出  
**常用场景**：数值、日期格式化

```python
# ⭐⭐ 高级用法
class Money:
    def __init__(self, amount):
        self.amount = amount
    
    def __format__(self, format_spec):
        if format_spec == 'cn':
            return f"¥{self.amount:.2f}"
        elif format_spec == 'us':
            return f"${self.amount:.2f}"
        return str(self.amount)

money = Money(100)
print(f"{money:cn}")  # ¥100.00
print(f"{money:us}")  # $100.00
```

---

## 3. 比较运算符 ⭐⭐⭐⭐

### `__eq__(self, other)` - 相等 `==`
**常用场景**：判断两个对象是否相等

```python
# ⭐⭐⭐⭐⭐ 非常常用
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

p1 = Point(1, 2)
p2 = Point(1, 2)
p3 = Point(2, 3)

print(p1 == p2)  # True
print(p1 == p3)  # False
```

---

### `__ne__(self, other)` - 不等 `!=`
**常用场景**：判断不相等（通常不需要实现，Python 会自动用 `not __eq__`）

```python
# ⭐ 很少需要手动实现
class Point:
    # 只实现 __eq__ 就够了
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    # Python 会自动处理 !=
    # 如果需要自定义：
    # def __ne__(self, other):
    #     return not self.__eq__(other)
```

---

### `__lt__(self, other)` - 小于 `<`
### `__le__(self, other)` - 小于等于 `<=`
### `__gt__(self, other)` - 大于 `>`
### `__ge__(self, other)` - 大于等于 `>=`

**常用场景**：排序、比较

```python
# ⭐⭐⭐⭐ 排序时常用
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score
    
    def __lt__(self, other):
        return self.score < other.score
    
    def __repr__(self):
        return f"Student({self.name}, {self.score})"

students = [
    Student("Alice", 85),
    Student("Bob", 92),
    Student("Charlie", 78)
]

sorted_students = sorted(students)
print(sorted_students)  # 按分数排序
# [Student(Charlie, 78), Student(Alice, 85), Student(Bob, 92)]
```

**提示**：可以使用 `@functools.total_ordering` 装饰器，只需实现 `__eq__` 和一个比较方法，其他自动生成。

```python
from functools import total_ordering

@total_ordering
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score
    
    def __eq__(self, other):
        return self.score == other.score
    
    def __lt__(self, other):
        return self.score < other.score
    
    # __le__, __gt__, __ge__ 自动生成
```

---

## 4. 算术运算符 ⭐⭐⭐

### 基本算术运算

| 方法 | 运算符 | 用途 |
|------|--------|------|
| `__add__(self, other)` | `+` | 加法 |
| `__sub__(self, other)` | `-` | 减法 |
| `__mul__(self, other)` | `*` | 乘法 |
| `__truediv__(self, other)` | `/` | 除法 |
| `__floordiv__(self, other)` | `//` | 整除 |
| `__mod__(self, other)` | `%` | 取模 |
| `__pow__(self, other)` | `**` | 幂运算 |

```python
# ⭐⭐⭐ 数学/科学计算常用
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2      # Vector(4, 6)
v4 = v1 * 2       # Vector(2, 4)
```

### 反向算术运算

当左操作数不支持运算时，Python 会尝试右操作数的反向方法。

```python
# ⭐⭐ 支持 数字 + 对象
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):  # 反向乘法
        return self.__mul__(scalar)

v = Vector(1, 2)
v1 = v * 2    # 调用 __mul__
v2 = 2 * v    # 调用 __rmul__
```

### 增量赋值

| 方法 | 运算符 |
|------|--------|
| `__iadd__(self, other)` | `+=` |
| `__isub__(self, other)` | `-=` |
| `__imul__(self, other)` | `*=` |

```python
# ⭐⭐ 
class Counter:
    def __init__(self, count=0):
        self.count = count
    
    def __iadd__(self, other):
        self.count += other
        return self  # 必须返回 self

counter = Counter(10)
counter += 5  # 调用 __iadd__
print(counter.count)  # 15
```

---

## 5. 容器类型 ⭐⭐⭐⭐

### `__len__(self)`
**调用时机**：`len(obj)`  
**用途**：返回容器长度

```python
# ⭐⭐⭐⭐⭐ 自定义容器必备
class MyList:
    def __init__(self):
        self.items = []
    
    def __len__(self):
        return len(self.items)
    
    def add(self, item):
        self.items.append(item)

my_list = MyList()
my_list.add("apple")
my_list.add("banana")
print(len(my_list))  # 2
```

---

### `__getitem__(self, key)`
**调用时机**：`obj[key]`  
**用途**：获取元素

```python
# ⭐⭐⭐⭐⭐ 索引访问
class MyList:
    def __init__(self):
        self.items = []
    
    def __getitem__(self, index):
        return self.items[index]
    
    def add(self, item):
        self.items.append(item)

my_list = MyList()
my_list.add("apple")
my_list.add("banana")
print(my_list[0])  # apple
print(my_list[1])  # banana
```

**支持切片**：
```python
class MyList:
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.items[key]  # 切片
        return self.items[key]      # 索引

my_list = MyList()
my_list.add("a")
my_list.add("b")
my_list.add("c")
print(my_list[0:2])  # ['a', 'b']
```

---

### `__setitem__(self, key, value)`
**调用时机**：`obj[key] = value`  
**用途**：设置元素

```python
# ⭐⭐⭐⭐ 可变容器
class MyDict:
    def __init__(self):
        self.data = {}
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value

my_dict = MyDict()
my_dict['name'] = 'Alice'
print(my_dict['name'])  # Alice
```

---

### `__delitem__(self, key)`
**调用时机**：`del obj[key]`  
**用途**：删除元素

```python
# ⭐⭐⭐
class MyDict:
    def __delitem__(self, key):
        del self.data[key]

my_dict = MyDict()
my_dict['name'] = 'Alice'
del my_dict['name']  # 调用 __delitem__
```

---

### `__contains__(self, item)`
**调用时机**：`item in obj`  
**用途**：成员检测

```python
# ⭐⭐⭐⭐
class MyList:
    def __init__(self):
        self.items = []
    
    def __contains__(self, item):
        return item in self.items

my_list = MyList()
my_list.items = ['apple', 'banana']
print('apple' in my_list)  # True
print('orange' in my_list)  # False
```

---

### `__iter__(self)`
**调用时机**：`for item in obj`  
**用途**：返回迭代器

```python
# ⭐⭐⭐⭐⭐ 可迭代对象
class MyRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __iter__(self):
        current = self.start
        while current < self.end:
            yield current
            current += 1

for num in MyRange(1, 5):
    print(num)  # 1, 2, 3, 4
```

---

### `__next__(self)`
**调用时机**：`next(obj)`  
**用途**：迭代器协议

```python
# ⭐⭐⭐ 实现迭代器
class Counter:
    def __init__(self, max):
        self.current = 0
        self.max = max
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.max:
            raise StopIteration
        self.current += 1
        return self.current

counter = Counter(3)
print(next(counter))  # 1
print(next(counter))  # 2
print(next(counter))  # 3
# print(next(counter))  # StopIteration
```

---

## 6. 上下文管理器 ⭐⭐⭐⭐

### `__enter__(self)`
### `__exit__(self, exc_type, exc_val, exc_tb)`

**调用时机**：`with` 语句  
**用途**：资源管理（自动清理）

```python
# ⭐⭐⭐⭐⭐ 资源管理最佳实践
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        # 返回 False 表示不抑制异常
        return False

# 使用
with FileManager('test.txt', 'w') as f:
    f.write('Hello')
# 文件自动关闭
```

**异步版本**：
```python
# ⭐⭐⭐⭐ 异步资源管理
class AsyncHTTPClient:
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

# 使用
async with AsyncHTTPClient() as client:
    # 使用 client
    pass
# session 自动关闭
```

---

## 7. 属性访问 ⭐⭐⭐

### `__getattr__(self, name)`
**调用时机**：访问不存在的属性时  
**用途**：动态属性、代理模式

```python
# ⭐⭐⭐ 动态属性
class DynamicObject:
    def __getattr__(self, name):
        return f"属性 {name} 不存在，返回默认值"

obj = DynamicObject()
print(obj.any_attribute)  # 属性 any_attribute 不存在，返回默认值
```

---

### `__setattr__(self, name, value)`
**调用时机**：设置属性时 `obj.attr = value`  
**用途**：属性验证、拦截

```python
# ⭐⭐ 属性验证
class Person:
    def __setattr__(self, name, value):
        if name == 'age' and value < 0:
            raise ValueError("年龄不能为负数")
        super().__setattr__(name, value)

person = Person()
person.age = 25  # 正常
# person.age = -1  # ValueError
```

**注意**：在 `__init__` 中也会触发 `__setattr__`

---

### `__delattr__(self, name)`
**调用时机**：`del obj.attr`  
**用途**：删除属性

```python
# ⭐ 很少用
class Example:
    def __delattr__(self, name):
        if name == 'protected':
            raise AttributeError("不能删除 protected 属性")
        super().__delattr__(name)
```

---

### `__getattribute__(self, name)`
**调用时机**：访问任何属性时（包括存在的）  
**用途**：属性访问拦截（危险！容易无限递归）

```python
# ⭐ 高级用法，慎用！
class LoggedAccess:
    def __init__(self):
        self.value = 42
    
    def __getattribute__(self, name):
        print(f"访问属性: {name}")
        return super().__getattribute__(name)

obj = LoggedAccess()
print(obj.value)  
# 输出：
# 访问属性: value
# 42
```

---

## 8. 可调用对象 ⭐⭐

### `__call__(self, ...)`
**调用时机**：`obj(...)`  
**用途**：让对象可以像函数一样调用

```python
# ⭐⭐⭐ 函数式编程、装饰器
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

**实用示例：计数器**
```python
class Counter:
    def __init__(self):
        self.count = 0
    
    def __call__(self):
        self.count += 1
        return self.count

counter = Counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

---

## 9. 其他常用方法

### `__hash__(self)`
**调用时机**：`hash(obj)`  
**用途**：让对象可以作为字典键或集合成员

```python
# ⭐⭐⭐⭐ 不可变对象
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

p1 = Point(1, 2)
p2 = Point(1, 2)

# 可以作为字典键
data = {p1: "点1"}
print(data[p2])  # "点1"

# 可以放入集合
points = {p1, p2}
print(len(points))  # 1（因为 p1 == p2）
```

**重要规则**：
- 如果实现了 `__eq__`，必须实现 `__hash__`
- 可哈希对象必须是不可变的

---

### `__bool__(self)`
**调用时机**：`bool(obj)` 或 `if obj:`  
**用途**：真值测试

```python
# ⭐⭐⭐ 自定义真值
class MyList:
    def __init__(self):
        self.items = []
    
    def __bool__(self):
        return len(self.items) > 0

my_list = MyList()
if my_list:
    print("列表不为空")
else:
    print("列表为空")  # 这个会执行
```

**默认行为**：
- 有 `__bool__` → 使用它
- 否则有 `__len__` → `len(obj) != 0`
- 否则 → 总是 `True`

---

### `__bytes__(self)`
**调用时机**：`bytes(obj)`  
**用途**：转换为字节串

```python
# ⭐⭐ 序列化
class Message:
    def __init__(self, text):
        self.text = text
    
    def __bytes__(self):
        return self.text.encode('utf-8')

msg = Message("Hello")
print(bytes(msg))  # b'Hello'
```

---

## 完整速查表

### 按使用频率排序

| 星级 | 方法 | 用途 | 业务场景 |
|------|------|------|---------|
| ⭐⭐⭐⭐⭐ | `__init__` | 初始化 | 几乎所有类 |
| ⭐⭐⭐⭐⭐ | `__repr__` | 字符串表示 | 调试、日志 |
| ⭐⭐⭐⭐⭐ | `__str__` | 用户友好显示 | UI、报告 |
| ⭐⭐⭐⭐⭐ | `__eq__` | 相等比较 | 对象比较、去重 |
| ⭐⭐⭐⭐⭐ | `__len__` | 长度 | 自定义容器 |
| ⭐⭐⭐⭐⭐ | `__getitem__` | 索引访问 | 自定义容器 |
| ⭐⭐⭐⭐⭐ | `__iter__` | 迭代 | 可迭代对象 |
| ⭐⭐⭐⭐ | `__enter__` / `__exit__` | 上下文管理 | 资源管理 |
| ⭐⭐⭐⭐ | `__lt__` / `__le__` 等 | 比较 | 排序 |
| ⭐⭐⭐⭐ | `__setitem__` | 设置元素 | 可变容器 |
| ⭐⭐⭐⭐ | `__contains__` | 成员检测 | `in` 运算符 |
| ⭐⭐⭐⭐ | `__hash__` | 哈希 | 字典键、集合 |
| ⭐⭐⭐ | `__add__` 等 | 算术运算 | 数学对象 |
| ⭐⭐⭐ | `__bool__` | 真值测试 | 条件判断 |
| ⭐⭐⭐ | `__call__` | 可调用 | 函数对象 |
| ⭐⭐⭐ | `__getattr__` | 动态属性 | 代理对象 |
| ⭐⭐ | `__new__` | 创建对象 | 单例、不可变类 |
| ⭐⭐ | `__setattr__` | 设置属性 | 属性验证 |
| ⭐⭐ | `__format__` | 格式化 | 自定义格式 |
| ⭐ | `__del__` | 析构 | 资源清理（不推荐） |

---

## 最佳实践建议

### 1. 必须实现的方法

对于大多数自定义类：
```python
class MyClass:
    def __init__(self, ...):  # ✅ 必须
        pass
    
    def __repr__(self):       # ✅ 强烈推荐
        pass
    
    def __eq__(self, other):  # ✅ 如果需要比较
        pass
```

### 2. 容器类型

```python
class MyContainer:
    def __len__(self):        # ✅ 必须
        pass
    
    def __getitem__(self, key):  # ✅ 必须
        pass
    
    def __iter__(self):       # ✅ 推荐
        pass
    
    def __contains__(self, item):  # ✅ 推荐
        pass
```

### 3. 数学对象

```python
class Vector:
    def __add__(self, other):  # ✅ 加法
        pass
    
    def __mul__(self, scalar): # ✅ 乘法
        pass
    
    def __eq__(self, other):   # ✅ 比较
        pass
    
    def __repr__(self):        # ✅ 表示
        pass
```

### 4. 资源管理

```python
class ResourceHandler:
    def __enter__(self):       # ✅ with 语句
        pass
    
    def __exit__(self, ...):   # ✅ 清理
        pass
```

---

## 项目中的实际应用

### 示例 1：Config 类（单例）
```python
class Config:
    _instance = None
    
    def __new__(cls):  # ← 控制对象创建
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 示例 2：ChapterInfo（数据类）
```python
class ChapterInfo:
    def __init__(self, chapter_index, title, url):  # ← 初始化
        self.chapter_index = chapter_index
        self.title = title
        self.url = url
    
    def __repr__(self):  # ← 调试
        return f"ChapterInfo(...)"
    
    def __eq__(self, other):  # ← 比较
        return (self.chapter_index == other.chapter_index and 
                self.title == other.title)
```

### 示例 3：AsyncHTTPClient（上下文管理器）
```python
class AsyncHTTPClient:
    async def __aenter__(self):  # ← 进入上下文
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, ...):  # ← 退出上下文
        await self.session.close()
```

---

## 总结

1. **必须掌握**：`__init__`, `__repr__`, `__str__`, `__eq__`
2. **容器类型**：`__len__`, `__getitem__`, `__iter__`
3. **资源管理**：`__enter__`, `__exit__`
4. **高级特性**：`__new__`（单例），`__call__`（可调用对象）

记住：**魔法方法名称都是固定的，不能修改！**

---

**参考资源**：
- [Python 官方文档 - Data Model](https://docs.python.org/3/reference/datamodel.html)
- [Python 魔法方法指南](https://rszalski.github.io/magicmethods/)
