#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python变量和数据类型详细示例

本文件演示Python中的基本数据类型、变量定义、命名规范和类型转换。
学习目标：
1. 理解Python变量的动态类型特性
2. 掌握基本数据类型的使用方法
3. 学会变量命名的最佳实践
4. 掌握类型转换和类型检查的方法
"""

# =============================================================================
# 1. 变量命名规范和最佳实践
# =============================================================================

print("=" * 50)
print("1. 变量命名规范示例")
print("=" * 50)

# 正确的变量命名（推荐）
user_name = "张三"           # 使用下划线分隔单词（snake_case）
user_age = 25               # 使用有意义的名称
is_student = True           # 布尔变量使用is_前缀
MAX_RETRY_COUNT = 3         # 常量使用大写字母和下划线

# 不推荐但合法的命名
userName = "李四"            # 驼峰命名法（不符合Python规范）
a = 30                      # 单字母变量名（不够描述性）

# 错误的变量命名（会导致语法错误）
# 2user = "错误"            # 不能以数字开头
# user-name = "错误"        # 不能包含连字符
# class = "错误"            # 不能使用Python关键字

print(f"用户姓名: {user_name}")
print(f"用户年龄: {user_age}")
print(f"是否为学生: {is_student}")
print(f"最大重试次数: {MAX_RETRY_COUNT}")

# =============================================================================
# 2. 基本数据类型详细示例
# =============================================================================

print("\n" + "=" * 50)
print("2. 基本数据类型示例")
print("=" * 50)

# 2.1 整数类型 (int)
print("\n--- 整数类型 (int) ---")
positive_number = 42        # 正整数
negative_number = -17       # 负整数
zero = 0                    # 零
large_number = 1000000      # 大整数

# 不同进制的整数表示
binary_number = 0b1010      # 二进制 (10)
octal_number = 0o12         # 八进制 (10)
hex_number = 0xa            # 十六进制 (10)

print(f"正整数: {positive_number}")
print(f"负整数: {negative_number}")
print(f"零: {zero}")
print(f"大整数: {large_number}")
print(f"二进制0b1010 = {binary_number}")
print(f"八进制0o12 = {octal_number}")
print(f"十六进制0xa = {hex_number}")

# 2.2 浮点数类型 (float)
print("\n--- 浮点数类型 (float) ---")
pi = 3.14159                # 普通浮点数
scientific_notation = 1.5e-4  # 科学计数法 (0.00015)
negative_float = -2.5       # 负浮点数

print(f"圆周率: {pi}")
print(f"科学计数法1.5e-4 = {scientific_notation}")
print(f"负浮点数: {negative_float}")

# 浮点数精度问题演示
result = 0.1 + 0.2
print(f"0.1 + 0.2 = {result}")  # 可能不等于0.3
print(f"是否等于0.3: {result == 0.3}")

# 2.3 字符串类型 (str)
print("\n--- 字符串类型 (str) ---")
single_quote_string = '单引号字符串'
double_quote_string = "双引号字符串"
triple_quote_string = """三引号字符串
可以跨越多行
保持格式"""

# 字符串转义字符
escape_string = "包含\"引号\"和\n换行符的字符串"
raw_string = r"原始字符串\n不会转义"

# 字符串格式化
name = "Python"
version = 3.9
formatted_string = f"欢迎使用{name} {version}"  # f-string格式化

print(f"单引号: {single_quote_string}")
print(f"双引号: {double_quote_string}")
print(f"三引号字符串:\n{triple_quote_string}")
print(f"转义字符串: {escape_string}")
print(f"原始字符串: {raw_string}")
print(f"格式化字符串: {formatted_string}")

# 2.4 布尔类型 (bool)
print("\n--- 布尔类型 (bool) ---")
is_true = True
is_false = False

# 布尔值的真假判断
print(f"True的值: {is_true}")
print(f"False的值: {is_false}")
print(f"空字符串的布尔值: {bool('')}")
print(f"非空字符串的布尔值: {bool('hello')}")
print(f"零的布尔值: {bool(0)}")
print(f"非零数字的布尔值: {bool(42)}")
print(f"空列表的布尔值: {bool([])}")
print(f"非空列表的布尔值: {bool([1, 2, 3])}")

# 2.5 空值类型 (NoneType)
print("\n--- 空值类型 (NoneType) ---")
empty_value = None
print(f"空值: {empty_value}")
print(f"None的类型: {type(empty_value)}")
print(f"None的布尔值: {bool(empty_value)}")

# =============================================================================
# 3. 类型检查和获取类型信息
# =============================================================================

print("\n" + "=" * 50)
print("3. 类型检查和获取类型信息")
print("=" * 50)

# 使用type()函数获取类型
sample_int = 42
sample_float = 3.14
sample_string = "Hello"
sample_bool = True
sample_none = None

print(f"{sample_int} 的类型: {type(sample_int)}")
print(f"{sample_float} 的类型: {type(sample_float)}")
print(f"{sample_string} 的类型: {type(sample_string)}")
print(f"{sample_bool} 的类型: {type(sample_bool)}")
print(f"{sample_none} 的类型: {type(sample_none)}")

# 使用isinstance()函数检查类型
print(f"\n使用isinstance()检查类型:")
print(f"42 是整数吗? {isinstance(42, int)}")
print(f"3.14 是浮点数吗? {isinstance(3.14, float)}")
print(f"'Hello' 是字符串吗? {isinstance('Hello', str)}")
print(f"True 是布尔值吗? {isinstance(True, bool)}")
print(f"True 也是整数吗? {isinstance(True, int)}")  # True，因为bool是int的子类

# =============================================================================
# 4. 类型转换示例
# =============================================================================

print("\n" + "=" * 50)
print("4. 类型转换示例")
print("=" * 50)

# 4.1 转换为整数
print("--- 转换为整数 ---")
float_to_int = int(3.14)           # 浮点数转整数（截断小数部分）
string_to_int = int("123")         # 字符串转整数
bool_to_int = int(True)            # 布尔值转整数

print(f"3.14 转为整数: {float_to_int}")
print(f"'123' 转为整数: {string_to_int}")
print(f"True 转为整数: {bool_to_int}")

# 4.2 转换为浮点数
print("\n--- 转换为浮点数 ---")
int_to_float = float(42)           # 整数转浮点数
string_to_float = float("3.14")   # 字符串转浮点数

print(f"42 转为浮点数: {int_to_float}")
print(f"'3.14' 转为浮点数: {string_to_float}")

# 4.3 转换为字符串
print("\n--- 转换为字符串 ---")
int_to_string = str(123)           # 整数转字符串
float_to_string = str(3.14)       # 浮点数转字符串
bool_to_string = str(True)         # 布尔值转字符串
list_to_string = str([1, 2, 3])   # 列表转字符串

print(f"123 转为字符串: '{int_to_string}'")
print(f"3.14 转为字符串: '{float_to_string}'")
print(f"True 转为字符串: '{bool_to_string}'")
print(f"[1, 2, 3] 转为字符串: '{list_to_string}'")

# 4.4 转换为布尔值
print("\n--- 转换为布尔值 ---")
print(f"0 转为布尔值: {bool(0)}")
print(f"1 转为布尔值: {bool(1)}")
print(f"'' 转为布尔值: {bool('')}")
print(f"'hello' 转为布尔值: {bool('hello')}")

# 4.5 类型转换中的错误处理
print("\n--- 类型转换错误处理 ---")
try:
    invalid_conversion = int("abc")  # 这会引发ValueError
except ValueError as e:
    print(f"转换错误: {e}")

try:
    invalid_conversion = float("xyz")  # 这会引发ValueError
except ValueError as e:
    print(f"转换错误: {e}")

# =============================================================================
# 5. 变量的动态类型特性
# =============================================================================

print("\n" + "=" * 50)
print("5. 变量的动态类型特性")
print("=" * 50)

# Python变量可以在运行时改变类型
dynamic_var = 42                    # 开始是整数
print(f"初始值: {dynamic_var}, 类型: {type(dynamic_var)}")

dynamic_var = "现在是字符串"          # 改为字符串
print(f"新值: {dynamic_var}, 类型: {type(dynamic_var)}")

dynamic_var = [1, 2, 3]            # 改为列表
print(f"新值: {dynamic_var}, 类型: {type(dynamic_var)}")

dynamic_var = True                  # 改为布尔值
print(f"新值: {dynamic_var}, 类型: {type(dynamic_var)}")

# =============================================================================
# 6. 实际应用场景示例
# =============================================================================

print("\n" + "=" * 50)
print("6. 实际应用场景示例")
print("=" * 50)

# 场景1: 用户输入处理
print("--- 场景1: 用户输入处理 ---")
def process_user_input():
    """模拟处理用户输入的函数"""
    # 模拟用户输入（实际中使用input()函数）
    user_input = "25"  # input()函数总是返回字符串
    
    try:
        age = int(user_input)  # 转换为整数
        if age >= 18:
            status = "成年人"
        else:
            status = "未成年人"
        
        print(f"年龄: {age}, 状态: {status}")
        return True
    except ValueError:
        print("输入的不是有效的数字")
        return False

process_user_input()

# 场景2: 数据验证
print("\n--- 场景2: 数据验证 ---")
def validate_data(data):
    """验证数据类型的函数"""
    if isinstance(data, str) and data.strip():
        print(f"有效的字符串: '{data}'")
    elif isinstance(data, (int, float)) and data > 0:
        print(f"有效的正数: {data}")
    elif isinstance(data, bool):
        print(f"布尔值: {data}")
    else:
        print(f"无效的数据: {data}")

# 测试不同类型的数据
test_data = ["Hello", 42, -5, True, "", None, 3.14]
for item in test_data:
    validate_data(item)

# 场景3: 配置文件处理
print("\n--- 场景3: 配置文件处理 ---")
def parse_config():
    """模拟解析配置文件的函数"""
    # 模拟从配置文件读取的字符串数据
    config_data = {
        "port": "8080",
        "debug": "True",
        "timeout": "30.5",
        "name": "MyApp"
    }
    
    # 转换为适当的类型
    parsed_config = {}
    
    # 端口号转为整数
    parsed_config["port"] = int(config_data["port"])
    
    # 调试标志转为布尔值
    parsed_config["debug"] = config_data["debug"].lower() == "true"
    
    # 超时时间转为浮点数
    parsed_config["timeout"] = float(config_data["timeout"])
    
    # 名称保持字符串
    parsed_config["name"] = config_data["name"]
    
    print("解析后的配置:")
    for key, value in parsed_config.items():
        print(f"  {key}: {value} ({type(value).__name__})")

parse_config()

# =============================================================================
# 7. 常见错误和注意事项
# =============================================================================

print("\n" + "=" * 50)
print("7. 常见错误和注意事项")
print("=" * 50)

# 错误1: 浮点数精度问题
print("--- 错误1: 浮点数精度问题 ---")
a = 0.1
b = 0.2
c = 0.3

print(f"0.1 + 0.2 = {a + b}")
print(f"0.1 + 0.2 == 0.3: {a + b == c}")

# 正确的浮点数比较方法
import math
print(f"使用math.isclose()比较: {math.isclose(a + b, c)}")

# 错误2: 整数除法的类型变化
print("\n--- 错误2: 整数除法的类型变化 ---")
result1 = 10 / 3    # 普通除法，结果是浮点数
result2 = 10 // 3   # 整数除法，结果是整数

print(f"10 / 3 = {result1} (类型: {type(result1)})")
print(f"10 // 3 = {result2} (类型: {type(result2)})")

# 错误3: 字符串和数字的连接
print("\n--- 错误3: 字符串和数字的连接 ---")
name = "Python"
version = 3.9

# 错误的方式（会报错）
# result = name + version  # TypeError

# 正确的方式
result1 = name + str(version)           # 转换为字符串后连接
result2 = f"{name} {version}"           # 使用f-string
result3 = "{} {}".format(name, version) # 使用format方法

print(f"方式1: {result1}")
print(f"方式2: {result2}")
print(f"方式3: {result3}")

print("\n" + "=" * 50)
print("变量和数据类型学习完成！")
print("=" * 50)

if __name__ == "__main__":
    print("\n这个文件可以直接运行来查看所有示例的输出结果。")