#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python运算符详细示例

本文件演示Python中所有类型的运算符，包括算术、比较、逻辑、赋值、位运算符等。
学习目标：
1. 掌握各种运算符的使用方法
2. 理解运算符的优先级和结合性
3. 学会在实际场景中正确使用运算符
4. 避免常见的运算符使用错误
"""

# =============================================================================
# 1. 算术运算符
# =============================================================================

print("=" * 60)
print("1. 算术运算符")
print("=" * 60)

# 基本算术运算符
a = 10
b = 3

print(f"a = {a}, b = {b}")
print(f"加法 (a + b): {a + b}")           # 13
print(f"减法 (a - b): {a - b}")           # 7
print(f"乘法 (a * b): {a * b}")           # 30
print(f"除法 (a / b): {a / b}")           # 3.3333...
print(f"整数除法 (a // b): {a // b}")      # 3
print(f"取余 (a % b): {a % b}")           # 1
print(f"幂运算 (a ** b): {a ** b}")        # 1000

# 特殊情况演示
print(f"\n特殊情况:")
print(f"负数除法: {-10 // 3}")            # -4 (向下取整)
print(f"浮点数除法: {10.5 / 2}")          # 5.25
print(f"浮点数整除: {10.5 // 2}")         # 5.0
print(f"字符串重复: {'Hello' * 3}")       # HelloHelloHello
print(f"列表重复: {[1, 2] * 3}")          # [1, 2, 1, 2, 1, 2]

# =============================================================================
# 2. 比较运算符
# =============================================================================

print("\n" + "=" * 60)
print("2. 比较运算符")
print("=" * 60)

x = 5
y = 10
z = 5

print(f"x = {x}, y = {y}, z = {z}")
print(f"等于 (x == z): {x == z}")         # True
print(f"不等于 (x != y): {x != y}")       # True
print(f"小于 (x < y): {x < y}")           # True
print(f"大于 (x > y): {x > y}")           # False
print(f"小于等于 (x <= z): {x <= z}")     # True
print(f"大于等于 (y >= x): {y >= x}")     # True

# 字符串比较（按字典序）
str1 = "apple"
str2 = "banana"
str3 = "Apple"

print(f"\n字符串比较:")
print(f"'{str1}' < '{str2}': {str1 < str2}")     # True
print(f"'{str1}' > '{str3}': {str1 > str3}")     # True (小写字母ASCII值更大)

# 链式比较
age = 25
print(f"\n链式比较:")
print(f"18 <= {age} < 65: {18 <= age < 65}")     # True

# 身份比较 (is, is not)
list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

print(f"\n身份比较:")
print(f"list1 == list2: {list1 == list2}")       # True (内容相同)
print(f"list1 is list2: {list1 is list2}")       # False (不是同一个对象)
print(f"list1 is list3: {list1 is list3}")       # True (是同一个对象)

# None的比较
value = None
print(f"value is None: {value is None}")          # True (推荐方式)
print(f"value == None: {value == None}")          # True (不推荐)

# =============================================================================
# 3. 逻辑运算符
# =============================================================================

print("\n" + "=" * 60)
print("3. 逻辑运算符")
print("=" * 60)

# 基本逻辑运算
p = True
q = False

print(f"p = {p}, q = {q}")
print(f"逻辑与 (p and q): {p and q}")      # False
print(f"逻辑或 (p or q): {p or q}")        # True
print(f"逻辑非 (not p): {not p}")          # False
print(f"逻辑非 (not q): {not q}")          # True

# 短路求值演示
print(f"\n短路求值:")
def return_true():
    print("  return_true() 被调用")
    return True

def return_false():
    print("  return_false() 被调用")
    return False

print("测试 False and return_true():")
result = False and return_true()  # return_true()不会被调用
print(f"结果: {result}")

print("\n测试 True or return_false():")
result = True or return_false()   # return_false()不会被调用
print(f"结果: {result}")

# 逻辑运算符的返回值
print(f"\n逻辑运算符的返回值:")
print(f"'hello' and 'world': {'hello' and 'world'}")    # 'world'
print(f"'' and 'world': {'' and 'world'}")              # ''
print(f"'hello' or 'world': {'hello' or 'world'}")      # 'hello'
print(f"'' or 'world': {'' or 'world'}")                # 'world'

# =============================================================================
# 4. 赋值运算符
# =============================================================================

print("\n" + "=" * 60)
print("4. 赋值运算符")
print("=" * 60)

# 基本赋值
num = 10
print(f"基本赋值 num = 10: {num}")

# 复合赋值运算符
num += 5    # 等价于 num = num + 5
print(f"num += 5: {num}")

num -= 3    # 等价于 num = num - 3
print(f"num -= 3: {num}")

num *= 2    # 等价于 num = num * 2
print(f"num *= 2: {num}")

num /= 4    # 等价于 num = num / 4
print(f"num /= 4: {num}")

num //= 2   # 等价于 num = num // 2
print(f"num //= 2: {num}")

num %= 3    # 等价于 num = num % 3
print(f"num %= 3: {num}")

num **= 3   # 等价于 num = num ** 3
print(f"num **= 3: {num}")

# 多重赋值
print(f"\n多重赋值:")
a = b = c = 100
print(f"a = b = c = 100: a={a}, b={b}, c={c}")

# 序列解包赋值
x, y, z = 1, 2, 3
print(f"x, y, z = 1, 2, 3: x={x}, y={y}, z={z}")

# 交换变量
x, y = y, x
print(f"交换后: x={x}, y={y}")

# =============================================================================
# 5. 位运算符
# =============================================================================

print("\n" + "=" * 60)
print("5. 位运算符")
print("=" * 60)

# 位运算符示例
a = 60  # 二进制: 111100
b = 13  # 二进制: 001101

print(f"a = {a} (二进制: {bin(a)})")
print(f"b = {b} (二进制: {bin(b)})")

print(f"按位与 (a & b): {a & b} (二进制: {bin(a & b)})")      # 12 (001100)
print(f"按位或 (a | b): {a | b} (二进制: {bin(a | b)})")      # 61 (111101)
print(f"按位异或 (a ^ b): {a ^ b} (二进制: {bin(a ^ b)})")    # 49 (110001)
print(f"按位取反 (~a): {~a} (二进制: {bin(~a & 0xFF)})")     # -61
print(f"左移 (a << 2): {a << 2} (二进制: {bin(a << 2)})")    # 240
print(f"右移 (a >> 2): {a >> 2} (二进制: {bin(a >> 2)})")    # 15

# 位运算的实际应用
print(f"\n位运算的实际应用:")

# 检查奇偶性
number = 17
is_odd = number & 1
print(f"{number} 是奇数吗? {bool(is_odd)}")

# 权限系统示例
READ = 1    # 001
WRITE = 2   # 010
EXECUTE = 4 # 100

# 设置权限
permissions = READ | WRITE  # 011
print(f"权限设置 (READ | WRITE): {permissions}")

# 检查权限
has_read = bool(permissions & READ)
has_write = bool(permissions & WRITE)
has_execute = bool(permissions & EXECUTE)

print(f"有读权限: {has_read}")
print(f"有写权限: {has_write}")
print(f"有执行权限: {has_execute}")

# =============================================================================
# 6. 成员运算符
# =============================================================================

print("\n" + "=" * 60)
print("6. 成员运算符")
print("=" * 60)

# in 和 not in 运算符
fruits = ["苹果", "香蕉", "橙子"]
text = "Hello World"
numbers = {1, 2, 3, 4, 5}

print(f"列表: {fruits}")
print(f"'苹果' in fruits: {'苹果' in fruits}")           # True
print(f"'葡萄' in fruits: {'葡萄' in fruits}")           # False
print(f"'葡萄' not in fruits: {'葡萄' not in fruits}")   # True

print(f"\n字符串: '{text}'")
print(f"'Hello' in text: {'Hello' in text}")            # True
print(f"'hello' in text: {'hello' in text}")            # False (区分大小写)

print(f"\n集合: {numbers}")
print(f"3 in numbers: {3 in numbers}")                  # True
print(f"6 not in numbers: {6 not in numbers}")          # True

# 字典的成员运算符
person = {"name": "张三", "age": 25, "city": "北京"}
print(f"\n字典: {person}")
print(f"'name' in person: {'name' in person}")          # True (检查键)
print(f"'张三' in person: {'张三' in person}")           # False (不检查值)
print(f"'张三' in person.values(): {'张三' in person.values()}")  # True (检查值)

# =============================================================================
# 7. 运算符优先级和结合性
# =============================================================================

print("\n" + "=" * 60)
print("7. 运算符优先级和结合性")
print("=" * 60)

# 运算符优先级示例
result1 = 2 + 3 * 4        # 乘法优先级高于加法
result2 = (2 + 3) * 4      # 括号改变优先级
print(f"2 + 3 * 4 = {result1}")        # 14
print(f"(2 + 3) * 4 = {result2}")      # 20

# 幂运算的右结合性
result3 = 2 ** 3 ** 2      # 等价于 2 ** (3 ** 2)
result4 = (2 ** 3) ** 2    # 明确指定结合顺序
print(f"2 ** 3 ** 2 = {result3}")      # 512
print(f"(2 ** 3) ** 2 = {result4}")    # 64

# 比较运算符的链式特性
x = 5
result5 = 1 < x < 10       # 等价于 (1 < x) and (x < 10)
print(f"1 < {x} < 10 = {result5}")     # True

# 逻辑运算符优先级
result6 = True or False and False   # and优先级高于or
result7 = (True or False) and False # 括号改变优先级
print(f"True or False and False = {result6}")      # True
print(f"(True or False) and False = {result7}")    # False

# 完整的优先级表（从高到低）
print(f"\n运算符优先级（从高到低）:")
print("1. () [] {} - 括号、索引、切片")
print("2. ** - 幂运算（右结合）")
print("3. +x -x ~x - 一元运算符")
print("4. * / // % - 乘除运算")
print("5. + - - 加减运算")
print("6. << >> - 位移运算")
print("7. & - 按位与")
print("8. ^ - 按位异或")
print("9. | - 按位或")
print("10. == != < <= > >= is is not in not in - 比较运算")
print("11. not - 逻辑非")
print("12. and - 逻辑与")
print("13. or - 逻辑或")
print("14. = += -= *= /= //= %= **= &= |= ^= >>= <<= - 赋值运算")

# =============================================================================
# 8. 实际应用场景
# =============================================================================

print("\n" + "=" * 60)
print("8. 实际应用场景")
print("=" * 60)

# 场景1: 数学计算
print("--- 场景1: 数学计算 ---")
def calculate_circle_area(radius):
    """计算圆的面积"""
    pi = 3.14159
    area = pi * radius ** 2  # 幂运算优先级高于乘法
    return area

radius = 5
area = calculate_circle_area(radius)
print(f"半径为{radius}的圆的面积: {area:.2f}")

# 场景2: 条件判断
print("\n--- 场景2: 条件判断 ---")
def check_grade(score):
    """根据分数判断等级"""
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"

scores = [95, 85, 75, 65, 55]
for score in scores:
    grade = check_grade(score)
    print(f"分数{score}: {grade}")

# 场景3: 数据验证
print("\n--- 场景3: 数据验证 ---")
def validate_user_input(username, password, age):
    """验证用户输入"""
    # 用户名验证：长度在3-20之间，且不为空
    username_valid = 3 <= len(username) <= 20 and username.strip()
    
    # 密码验证：长度至少8位，包含字母和数字
    password_valid = (len(password) >= 8 and 
                     any(c.isalpha() for c in password) and 
                     any(c.isdigit() for c in password))
    
    # 年龄验证：在合理范围内
    age_valid = 0 < age < 150
    
    return username_valid and password_valid and age_valid

# 测试数据验证
test_cases = [
    ("alice", "password123", 25),
    ("", "123456", 30),
    ("bob", "abc", 25),
    ("charlie", "mypassword1", -5)
]

for username, password, age in test_cases:
    is_valid = validate_user_input(username, password, age)
    print(f"用户: {username}, 密码: {password}, 年龄: {age} -> 有效: {is_valid}")

# 场景4: 位运算应用
print("\n--- 场景4: 位运算应用 ---")
class FilePermissions:
    """文件权限管理类"""
    READ = 1    # 001
    WRITE = 2   # 010
    EXECUTE = 4 # 100
    
    def __init__(self, permissions=0):
        self.permissions = permissions
    
    def add_permission(self, permission):
        """添加权限"""
        self.permissions |= permission
    
    def remove_permission(self, permission):
        """移除权限"""
        self.permissions &= ~permission
    
    def has_permission(self, permission):
        """检查是否有指定权限"""
        return bool(self.permissions & permission)
    
    def __str__(self):
        perms = []
        if self.has_permission(self.READ):
            perms.append("READ")
        if self.has_permission(self.WRITE):
            perms.append("WRITE")
        if self.has_permission(self.EXECUTE):
            perms.append("EXECUTE")
        return " | ".join(perms) if perms else "NO PERMISSIONS"

# 使用权限系统
file_perms = FilePermissions()
print(f"初始权限: {file_perms}")

file_perms.add_permission(FilePermissions.READ)
print(f"添加读权限: {file_perms}")

file_perms.add_permission(FilePermissions.WRITE)
print(f"添加写权限: {file_perms}")

file_perms.add_permission(FilePermissions.EXECUTE)
print(f"添加执行权限: {file_perms}")

file_perms.remove_permission(FilePermissions.WRITE)
print(f"移除写权限: {file_perms}")

# =============================================================================
# 9. 常见错误和注意事项
# =============================================================================

print("\n" + "=" * 60)
print("9. 常见错误和注意事项")
print("=" * 60)

# 错误1: 浮点数比较
print("--- 错误1: 浮点数比较 ---")
a = 0.1 + 0.2
b = 0.3
print(f"0.1 + 0.2 = {a}")
print(f"0.3 = {b}")
print(f"0.1 + 0.2 == 0.3: {a == b}")  # False!

# 正确的浮点数比较
import math
epsilon = 1e-9
is_equal = abs(a - b) < epsilon
print(f"使用epsilon比较: {is_equal}")
print(f"使用math.isclose(): {math.isclose(a, b)}")

# 错误2: 链式赋值的陷阱
print("\n--- 错误2: 链式赋值的陷阱 ---")
# 对于不可变对象，链式赋值是安全的
a = b = c = 5
a += 1
print(f"不可变对象: a={a}, b={b}, c={c}")  # a=6, b=5, c=5

# 对于可变对象，链式赋值可能有问题
list1 = list2 = list3 = [1, 2, 3]
list1.append(4)
print(f"可变对象: list1={list1}, list2={list2}, list3={list3}")  # 都变了!

# 正确的方式
list4 = [1, 2, 3]
list5 = [1, 2, 3]  # 或者 list5 = list4.copy()
list4.append(4)
print(f"正确方式: list4={list4}, list5={list5}")

# 错误3: 逻辑运算符的误用
print("\n--- 错误3: 逻辑运算符的误用 ---")
# 错误的写法
x = 5
# if x == 1 or 2 or 3:  # 这总是True，因为2和3都是真值

# 正确的写法
if x == 1 or x == 2 or x == 3:
    print("x是1、2或3")
else:
    print("x不是1、2或3")

# 更好的写法
if x in [1, 2, 3]:
    print("x是1、2或3")
else:
    print("x不是1、2或3")

print("\n" + "=" * 60)
print("运算符学习完成！")
print("=" * 60)

if __name__ == "__main__":
    print("\n这个文件演示了Python中所有重要的运算符及其使用方法。")
    print("建议结合实际编程练习来加深理解。")