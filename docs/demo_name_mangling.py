"""
演示 Python 的名称改写（Name Mangling）机制
"""


class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner  # 公开属性
        self._balance = balance  # 单下划线：约定私有
        self.__password = "123456"  # 双下划线：名称改写


# 创建实例
account = BankAccount("Alice", 1000)

print("=" * 60)
print("1. 公开属性（无下划线）")
print("=" * 60)
print(f"访问 account.owner: {account.owner}")  # ✅ 正常访问
print()

print("=" * 60)
print("2. 约定私有（单下划线 _balance）")
print("=" * 60)
print(f"访问 account._balance: {account._balance}")  # ✅ 可以访问（但不建议）
print("注意：单下划线只是约定，实际上可以访问")
print()

print("=" * 60)
print("3. 名称改写（双下划线 __password）")
print("=" * 60)

# ❌ 直接访问会报错
try:
    print(f"访问 account.__password: {account.__password}")
except AttributeError as e:
    print(f"❌ 错误：{e}")
    print("原因：__password 已经被改名了！")
print()

# ✅ 查看所有属性（找到改名后的真实名称）
print("查看对象的所有属性：")
attrs = [attr for attr in dir(account) if not attr.startswith("__")]
for attr in attrs:
    print(f"  - {attr}")
print()

# ✅ 通过改名后的名称访问
print(f"访问 account._BankAccount__password: {account._BankAccount__password}")
print()

print("=" * 60)
print("改名规则总结")
print("=" * 60)
print("原始代码: self.__password = '123456'")
print("实际存储: self._BankAccount__password = '123456'")
print("改名公式: _类名__属性名")
print()


# ========== 更复杂的例子：继承场景 ==========

print("=" * 60)
print("4. 继承场景中的名称改写")
print("=" * 60)


class Parent:
    def __init__(self):
        self.__secret = "父类的秘密"  # 改写为 _Parent__secret

    def show_parent_secret(self):
        print(f"父类的 __secret: {self.__secret}")


class Child(Parent):
    def __init__(self):
        super().__init__()
        self.__secret = "子类的秘密"  # 改写为 _Child__secret（不同名称！）

    def show_child_secret(self):
        print(f"子类的 __secret: {self.__secret}")


child = Child()

# 两个 __secret 不会冲突，因为改名不同
print("\n调用父类方法：")
child.show_parent_secret()  # 输出：父类的秘密

print("\n调用子类方法：")
child.show_child_secret()  # 输出：子类的秘密

print("\n查看实际存储的属性名：")
secrets = [attr for attr in dir(child) if "secret" in attr.lower()]
for attr in secrets:
    value = getattr(child, attr)
    print(f"  {attr} = '{value}'")

print()
print("解释：")
print("  - 父类的 self.__secret → 改名为 _Parent__secret")
print("  - 子类的 self.__secret → 改名为 _Child__secret")
print("  - 两者互不干扰！这就是名称改写的作用")
