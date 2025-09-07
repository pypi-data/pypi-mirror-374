"""
Python字典(Dictionary)操作详解

字典是Python中的映射类型，存储键值对(key-value pairs)。
字典是可变的、无序的（Python 3.7+保持插入顺序），键必须是不可变类型。

学习目标：
1. 掌握字典的创建和初始化
2. 理解字典的键值对操作
3. 学会使用字典的各种方法
4. 掌握字典推导式的使用
5. 了解字典的性能特点和使用场景
"""

# ============================================================================
# 1. 字典的创建和初始化
# ============================================================================

print("=" * 50)
print("1. 字典的创建和初始化")
print("=" * 50)

# 创建空字典的几种方法
empty_dict1 = {}
empty_dict2 = dict()
print(f"空字典1: {empty_dict1}")
print(f"空字典2: {empty_dict2}")

# 创建包含数据的字典
student = {
    "name": "张三",
    "age": 20,
    "major": "计算机科学",
    "gpa": 3.8
}
print(f"学生信息: {student}")

# 使用dict()构造函数
colors = dict(red=255, green=128, blue=0)
coordinates = dict([("x", 10), ("y", 20)])
print(f"颜色字典: {colors}")
print(f"坐标字典: {coordinates}")

# 使用zip()创建字典
keys = ["name", "age", "city"]
values = ["李四", 25, "北京"]
person = dict(zip(keys, values))
print(f"人员信息: {person}")

# 使用字典推导式创建
squares = {x: x**2 for x in range(1, 6)}
print(f"平方数字典: {squares}")

# 嵌套字典
company = {
    "name": "科技公司",
    "employees": {
        "001": {"name": "张三", "department": "开发部"},
        "002": {"name": "李四", "department": "设计部"}
    },
    "locations": ["北京", "上海", "深圳"]
}
print(f"公司信息: {company}")

# ============================================================================
# 2. 字典的访问和修改
# ============================================================================

print("\n" + "=" * 50)
print("2. 字典的访问和修改")
print("=" * 50)

# 访问字典值
student = {"name": "王五", "age": 22, "major": "数学"}
print(f"学生字典: {student}")

# 使用键访问值
print(f"学生姓名: {student['name']}")
print(f"学生年龄: {student['age']}")

# 使用get()方法（推荐，更安全）
print(f"专业: {student.get('major')}")
print(f"GPA: {student.get('gpa', '未设置')}")  # 提供默认值

# 检查键是否存在
print(f"'name'键存在: {'name' in student}")
print(f"'gpa'键存在: {'gpa' in student}")

# 修改现有键的值
student['age'] = 23
print(f"修改年龄后: {student}")

# 添加新的键值对
student['gpa'] = 3.9
student['email'] = 'wangwu@example.com'
print(f"添加信息后: {student}")

# 删除键值对
del student['email']
print(f"删除邮箱后: {student}")

# 使用pop()删除并返回值
removed_gpa = student.pop('gpa')
print(f"删除的GPA: {removed_gpa}")
print(f"删除GPA后: {student}")

# 使用popitem()删除并返回最后一个键值对
last_item = student.popitem()
print(f"删除的最后项: {last_item}")
print(f"最终字典: {student}")

# ============================================================================
# 3. 字典的方法
# ============================================================================

print("\n" + "=" * 50)
print("3. 字典的方法")
print("=" * 50)

# 重新创建示例字典
inventory = {
    "苹果": 50,
    "香蕉": 30,
    "橙子": 25,
    "葡萄": 40
}
print(f"库存字典: {inventory}")

# keys(), values(), items()
print(f"所有键: {list(inventory.keys())}")
print(f"所有值: {list(inventory.values())}")
print(f"所有键值对: {list(inventory.items())}")

# 遍历字典
print(f"\n遍历字典:")
for fruit in inventory:  # 默认遍历键
    print(f"{fruit}: {inventory[fruit]}个")

print(f"\n使用items()遍历:")
for fruit, count in inventory.items():
    print(f"{fruit}: {count}个")

# update()方法 - 更新字典
new_items = {"西瓜": 15, "草莓": 35}
inventory.update(new_items)
print(f"更新后的库存: {inventory}")

# 也可以用关键字参数更新
inventory.update(苹果=60, 柠檬=20)
print(f"再次更新后: {inventory}")

# setdefault()方法 - 如果键不存在则设置默认值
inventory.setdefault("芒果", 10)
inventory.setdefault("苹果", 100)  # 键已存在，不会改变
print(f"使用setdefault后: {inventory}")

# clear()方法 - 清空字典
temp_dict = {"a": 1, "b": 2}
temp_dict.clear()
print(f"清空后的字典: {temp_dict}")

# copy()方法 - 浅复制
original = {"a": [1, 2], "b": [3, 4]}
copied = original.copy()
print(f"原字典: {original}")
print(f"复制字典: {copied}")

# 修改嵌套对象会影响所有浅复制
original["a"][0] = 99
print(f"修改后原字典: {original}")
print(f"修改后复制字典: {copied}")

# ============================================================================
# 4. 字典推导式
# ============================================================================

print("\n" + "=" * 50)
print("4. 字典推导式")
print("=" * 50)

# 基本字典推导式
squares = {x: x**2 for x in range(1, 6)}
print(f"平方数: {squares}")

# 带条件的字典推导式
even_squares = {x: x**2 for x in range(1, 11) if x % 2 == 0}
print(f"偶数平方: {even_squares}")

# 字符串处理
words = ["hello", "world", "python"]
word_lengths = {word: len(word) for word in words}
print(f"单词长度: {word_lengths}")

# 转换现有字典
celsius = {"北京": 25, "上海": 28, "广州": 32}
fahrenheit = {city: temp * 9/5 + 32 for city, temp in celsius.items()}
print(f"摄氏度: {celsius}")
print(f"华氏度: {fahrenheit}")

# 过滤字典
scores = {"张三": 85, "李四": 92, "王五": 78, "赵六": 96}
excellent = {name: score for name, score in scores.items() if score >= 90}
print(f"所有成绩: {scores}")
print(f"优秀成绩: {excellent}")

# 嵌套字典推导式
matrix = {f"row_{i}": {f"col_{j}": i*j for j in range(3)} for i in range(3)}
print(f"矩阵字典: {matrix}")

# ============================================================================
# 5. 字典的高级操作
# ============================================================================

print("\n" + "=" * 50)
print("5. 字典的高级操作")
print("=" * 50)

# 字典合并（Python 3.9+）
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}
dict3 = {"b": 20, "e": 5}

# 使用 | 操作符合并
merged = dict1 | dict2 | dict3
print(f"字典1: {dict1}")
print(f"字典2: {dict2}")
print(f"字典3: {dict3}")
print(f"合并结果: {merged}")

# 使用 ** 解包合并（适用于所有Python版本）
merged_unpack = {**dict1, **dict2, **dict3}
print(f"解包合并: {merged_unpack}")

# 字典的默认值处理
from collections import defaultdict

# 使用defaultdict自动创建默认值
word_count = defaultdict(int)
text = "hello world hello python world"
for word in text.split():
    word_count[word] += 1
print(f"单词计数: {dict(word_count)}")

# 分组操作
students = [
    {"name": "张三", "class": "A", "score": 85},
    {"name": "李四", "class": "B", "score": 92},
    {"name": "王五", "class": "A", "score": 78},
    {"name": "赵六", "class": "B", "score": 96}
]

# 按班级分组
class_groups = defaultdict(list)
for student in students:
    class_groups[student["class"]].append(student)

print(f"按班级分组:")
for class_name, students_list in class_groups.items():
    print(f"  {class_name}班: {[s['name'] for s in students_list]}")

# ============================================================================
# 6. 嵌套字典操作
# ============================================================================

print("\n" + "=" * 50)
print("6. 嵌套字典操作")
print("=" * 50)

# 复杂的嵌套字典
school = {
    "name": "示例中学",
    "classes": {
        "高一A班": {
            "teacher": "张老师",
            "students": [
                {"name": "小明", "age": 16, "scores": {"数学": 95, "语文": 88}},
                {"name": "小红", "age": 15, "scores": {"数学": 92, "语文": 94}}
            ]
        },
        "高一B班": {
            "teacher": "李老师",
            "students": [
                {"name": "小刚", "age": 16, "scores": {"数学": 87, "语文": 90}},
                {"name": "小丽", "age": 15, "scores": {"数学": 98, "语文": 85}}
            ]
        }
    }
}

print(f"学校名称: {school['name']}")

# 访问嵌套数据
first_class = list(school["classes"].keys())[0]
teacher = school["classes"][first_class]["teacher"]
print(f"{first_class}的老师: {teacher}")

# 遍历嵌套结构
for class_name, class_info in school["classes"].items():
    print(f"\n{class_name}:")
    print(f"  老师: {class_info['teacher']}")
    print(f"  学生:")
    for student in class_info["students"]:
        avg_score = sum(student["scores"].values()) / len(student["scores"])
        print(f"    {student['name']} (年龄: {student['age']}, 平均分: {avg_score:.1f})")

# 安全访问嵌套字典
def safe_get(dictionary, *keys, default=None):
    """安全获取嵌套字典的值"""
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary:
            dictionary = dictionary[key]
        else:
            return default
    return dictionary

# 使用安全访问
# 注意：这里需要先获取学生列表，然后访问第一个学生
students_list = safe_get(school, "classes", "高一A班", "students")
if students_list and len(students_list) > 0:
    math_score = safe_get(students_list[0], "scores", "数学")
else:
    math_score = None
print(f"\n小明的数学成绩: {math_score}")

nonexistent = safe_get(school, "classes", "高二A班", "teacher", default="未找到")
print(f"不存在的班级老师: {nonexistent}")

# ============================================================================
# 7. 字典的性能特点
# ============================================================================

print("\n" + "=" * 50)
print("7. 字典的性能特点")
print("=" * 50)

import time
import sys

# 创建大字典进行性能测试
large_dict = {i: f"value_{i}" for i in range(10000)}
large_list = [(i, f"value_{i}") for i in range(10000)]

print(f"字典大小: {len(large_dict)} 项")
print(f"字典内存: {sys.getsizeof(large_dict)} 字节")
print(f"列表内存: {sys.getsizeof(large_list)} 字节")

# 查找性能对比
def time_lookup(container, key, iterations=1000):
    start = time.time()
    for _ in range(iterations):
        if isinstance(container, dict):
            _ = container.get(key)
        else:  # 列表
            _ = next((v for k, v in container if k == key), None)
    return time.time() - start

# 测试查找性能
search_key = 5000
dict_time = time_lookup(large_dict, search_key)
list_time = time_lookup(large_list, search_key)

print(f"字典查找耗时: {dict_time:.6f}秒")
print(f"列表查找耗时: {list_time:.6f}秒")
print(f"字典比列表快: {list_time/dict_time:.1f}倍")

# 字典的时间复杂度
print(f"\n时间复杂度:")
print(f"- 查找/插入/删除: O(1) 平均情况")
print(f"- 最坏情况: O(n) (哈希冲突)")
print(f"- 遍历: O(n)")

# ============================================================================
# 8. 实际应用场景
# ============================================================================

print("\n" + "=" * 50)
print("8. 实际应用场景")
print("=" * 50)

# 场景1：配置管理
print("场景1：配置管理")
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp",
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    },
    "cache": {
        "type": "redis",
        "ttl": 3600
    },
    "debug": True
}

def get_config(path, default=None):
    """获取配置值"""
    keys = path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value

print(f"数据库主机: {get_config('database.host')}")
print(f"缓存TTL: {get_config('cache.ttl')}")
print(f"不存在的配置: {get_config('nonexistent.key', '默认值')}")

# 场景2：数据统计
print(f"\n场景2：数据统计")
sales_data = [
    {"product": "手机", "category": "电子", "amount": 5000},
    {"product": "笔记本", "category": "电子", "amount": 8000},
    {"product": "衬衫", "category": "服装", "amount": 200},
    {"product": "裤子", "category": "服装", "amount": 300},
    {"product": "手机", "category": "电子", "amount": 5500}
]

# 按类别统计销售额
category_sales = defaultdict(int)
product_sales = defaultdict(int)

for sale in sales_data:
    category_sales[sale["category"]] += sale["amount"]
    product_sales[sale["product"]] += sale["amount"]

print(f"按类别统计: {dict(category_sales)}")
print(f"按产品统计: {dict(product_sales)}")

# 场景3：缓存系统
print(f"\n场景3：简单缓存系统")
class SimpleCache:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, key):
        if key in self.cache:
            # 更新访问顺序
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key, value):
        if key in self.cache:
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            if len(self.cache) >= self.max_size:
                # 删除最久未使用的项
                oldest = self.access_order.pop(0)
                del self.cache[oldest]
            
            self.cache[key] = value
            self.access_order.append(key)

# 使用缓存
cache = SimpleCache(max_size=3)
cache.set("user_1", {"name": "张三", "age": 25})
cache.set("user_2", {"name": "李四", "age": 30})
cache.set("user_3", {"name": "王五", "age": 28})

print(f"缓存用户1: {cache.get('user_1')}")
cache.set("user_4", {"name": "赵六", "age": 35})  # 会删除user_2
print(f"缓存用户2: {cache.get('user_2')}")  # None，已被删除

# 场景4：数据转换和映射
print(f"\n场景4：数据转换和映射")
# HTTP状态码映射
status_codes = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    401: "Unauthorized",
    404: "Not Found",
    500: "Internal Server Error"
}

def get_status_message(code):
    return status_codes.get(code, "Unknown Status")

print(f"状态码200: {get_status_message(200)}")
print(f"状态码999: {get_status_message(999)}")

# 数据格式转换
raw_data = [
    "name:张三,age:25,city:北京",
    "name:李四,age:30,city:上海",
    "name:王五,age:28,city:广州"
]

def parse_data(data_string):
    """解析数据字符串为字典"""
    result = {}
    for item in data_string.split(','):
        key, value = item.split(':')
        # 尝试转换为数字
        try:
            value = int(value)
        except ValueError:
            pass
        result[key] = value
    return result

parsed_data = [parse_data(item) for item in raw_data]
print(f"解析后的数据: {parsed_data}")

# ============================================================================
# 9. 常见错误和最佳实践
# ============================================================================

print("\n" + "=" * 50)
print("9. 常见错误和最佳实践")
print("=" * 50)

print("常见错误:")
print("1. 使用可变对象作为键")
print("2. 直接访问可能不存在的键")
print("3. 在遍历时修改字典")
print("4. 混淆字典的浅复制和深复制")

# 演示错误
print(f"\n错误演示:")

# 错误1：使用列表作为键（会报错）
try:
    bad_dict = {[1, 2]: "value"}  # TypeError
except TypeError as e:
    print(f"错误1 - 使用列表作为键: {e}")

# 错误2：直接访问不存在的键
try:
    test_dict = {"a": 1}
    value = test_dict["b"]  # KeyError
except KeyError as e:
    print(f"错误2 - 访问不存在的键: {e}")

# 正确做法
test_dict = {"a": 1}
value = test_dict.get("b", "默认值")
print(f"正确做法 - 使用get(): {value}")

print(f"\n最佳实践:")
print("✓ 使用get()方法安全访问字典")
print("✓ 用in操作符检查键是否存在")
print("✓ 使用字典推导式简化代码")
print("✓ 合理使用defaultdict处理默认值")
print("✓ 键使用不可变类型（字符串、数字、元组）")
print("✓ 避免在遍历时修改字典结构")

# 性能提示
print(f"\n性能提示:")
print("- 字典查找是O(1)时间复杂度")
print("- 字典比列表查找快得多")
print("- 合理的键设计可以避免哈希冲突")
print("- 大量数据时优先使用字典而不是列表查找")

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("字典学习完成！")
    print("=" * 50)
    print("你已经学会了:")
    print("✓ 字典的创建和操作")
    print("✓ 字典的各种方法")
    print("✓ 字典推导式")
    print("✓ 嵌套字典处理")
    print("✓ 字典的性能特点")
    print("✓ 实际应用场景")
    print("\n继续学习集合吧！")