"""
Python元组(Tuple)使用详解

元组是Python中的不可变序列类型，一旦创建就不能修改。
元组通常用于存储相关但不同类型的数据，如坐标点、数据库记录等。

学习目标：
1. 掌握元组的创建和特性
2. 理解元组的不可变性质
3. 学会元组的解包操作
4. 掌握命名元组的使用
5. 了解元组与列表的区别和使用场景
"""

# ============================================================================
# 1. 元组的创建和基本特性
# ============================================================================

print("=" * 50)
print("1. 元组的创建和基本特性")
print("=" * 50)

# 创建元组的几种方法
empty_tuple1 = ()
empty_tuple2 = tuple()
print(f"空元组1: {empty_tuple1}")
print(f"空元组2: {empty_tuple2}")

# 创建包含元素的元组
coordinates = (3, 4)
rgb_color = (255, 128, 0)
mixed_tuple = (1, "hello", 3.14, True)
print(f"坐标点: {coordinates}")
print(f"RGB颜色: {rgb_color}")
print(f"混合类型元组: {mixed_tuple}")

# 单元素元组（注意逗号）
single_element = (42,)  # 注意逗号，否则是普通的括号表达式
not_tuple = (42)        # 这不是元组，是整数
print(f"单元素元组: {single_element}, 类型: {type(single_element)}")
print(f"不是元组: {not_tuple}, 类型: {type(not_tuple)}")

# 不使用括号创建元组（逗号是关键）
point = 10, 20
person = "张三", 25, "工程师"
print(f"坐标点(无括号): {point}")
print(f"人员信息: {person}")

# 嵌套元组
nested_tuple = ((1, 2), (3, 4), (5, 6))
print(f"嵌套元组: {nested_tuple}")

# ============================================================================
# 2. 元组的访问和操作
# ============================================================================

print("\n" + "=" * 50)
print("2. 元组的访问和操作")
print("=" * 50)

fruits = ("苹果", "香蕉", "橙子", "葡萄", "草莓")
print(f"水果元组: {fruits}")

# 索引访问（与列表相同）
print(f"第一个水果: {fruits[0]}")
print(f"最后一个水果: {fruits[-1]}")

# 切片操作
print(f"前三个水果: {fruits[:3]}")
print(f"后两个水果: {fruits[-2:]}")

# 元组长度和成员检查
print(f"水果总数: {len(fruits)}")
print(f"'苹果'在元组中: {'苹果' in fruits}")

# 元组的方法（只有两个）
numbers = (1, 2, 3, 2, 4, 2, 5)
print(f"数字元组: {numbers}")
print(f"数字2的索引: {numbers.index(2)}")
print(f"数字2出现次数: {numbers.count(2)}")

# ============================================================================
# 3. 元组的不可变性
# ============================================================================

print("\n" + "=" * 50)
print("3. 元组的不可变性")
print("=" * 50)

# 元组本身不可变
point = (1, 2)
print(f"原始坐标: {point}")

# 以下操作会报错（取消注释查看）
# point[0] = 10  # TypeError: 'tuple' object does not support item assignment
# point.append(3)  # AttributeError: 'tuple' object has no attribute 'append'

# 但可以重新赋值整个元组
point = (10, 20)
print(f"重新赋值后: {point}")

# 包含可变对象的元组
mutable_content = ([1, 2], [3, 4])
print(f"包含列表的元组: {mutable_content}")

# 可以修改内部的可变对象
mutable_content[0][0] = 99
print(f"修改内部列表后: {mutable_content}")

# 但不能替换元组中的元素
# mutable_content[0] = [99, 99]  # 这会报错

# ============================================================================
# 4. 元组解包（Tuple Unpacking）
# ============================================================================

print("\n" + "=" * 50)
print("4. 元组解包（Tuple Unpacking）")
print("=" * 50)

# 基本解包
point = (3, 4)
x, y = point
print(f"坐标点 {point} 解包为: x={x}, y={y}")

# 多个值的解包
person_info = ("李明", 28, "北京", "软件工程师")
name, age, city, job = person_info
print(f"姓名: {name}, 年龄: {age}, 城市: {city}, 职业: {job}")

# 使用星号收集剩余元素
numbers = (1, 2, 3, 4, 5, 6)
first, second, *rest = numbers
print(f"第一个: {first}, 第二个: {second}, 其余: {rest}")

first, *middle, last = numbers
print(f"第一个: {first}, 中间: {middle}, 最后: {last}")

# 忽略不需要的值
data = ("用户001", "张三", 25, "manager", 50000)
user_id, name, _, _, salary = data  # 使用_忽略不需要的值
print(f"用户ID: {user_id}, 姓名: {name}, 薪资: {salary}")

# 嵌套解包
nested_data = (("张三", 25), ("李四", 30))
(name1, age1), (name2, age2) = nested_data
print(f"人员1: {name1}({age1}岁), 人员2: {name2}({age2}岁)")

# ============================================================================
# 5. 函数返回多个值
# ============================================================================

print("\n" + "=" * 50)
print("5. 函数返回多个值")
print("=" * 50)

def get_name_age():
    """返回姓名和年龄"""
    return "王五", 35

def calculate_stats(numbers):
    """计算统计信息"""
    total = sum(numbers)
    count = len(numbers)
    average = total / count if count > 0 else 0
    return total, count, average

def get_coordinates():
    """返回坐标信息"""
    return (10, 20), (30, 40)

# 使用返回的元组
name, age = get_name_age()
print(f"从函数获取: 姓名={name}, 年龄={age}")

# 统计信息
data = [1, 2, 3, 4, 5]
total, count, avg = calculate_stats(data)
print(f"数据 {data} 的统计: 总和={total}, 数量={count}, 平均={avg:.2f}")

# 嵌套元组返回
point1, point2 = get_coordinates()
print(f"坐标1: {point1}, 坐标2: {point2}")

# ============================================================================
# 6. 命名元组（Named Tuple）
# ============================================================================

print("\n" + "=" * 50)
print("6. 命名元组（Named Tuple）")
print("=" * 50)

from collections import namedtuple

# 定义命名元组类型
Point = namedtuple('Point', ['x', 'y'])
Person = namedtuple('Person', ['name', 'age', 'city'])
Color = namedtuple('Color', 'red green blue')  # 也可以用字符串

# 创建命名元组实例
p1 = Point(3, 4)
p2 = Point(x=10, y=20)
print(f"点1: {p1}")
print(f"点2: {p2}")

# 访问字段
print(f"点1的x坐标: {p1.x}")
print(f"点1的y坐标: {p1.y}")

# 也可以像普通元组一样访问
print(f"点1[0]: {p1[0]}, 点1[1]: {p1[1]}")

# 创建人员信息
person = Person("赵六", 32, "上海")
print(f"人员信息: {person}")
print(f"姓名: {person.name}, 年龄: {person.age}, 城市: {person.city}")

# 命名元组的方法
print(f"\n命名元组的特殊方法:")
print(f"字段名: {person._fields}")
print(f"转为字典: {person._asdict()}")

# 替换字段值（返回新的命名元组）
new_person = person._replace(age=33)
print(f"原人员: {person}")
print(f"新人员: {new_person}")

# 从可迭代对象创建
data = ["钱七", 28, "广州"]
person2 = Person._make(data)
print(f"从列表创建: {person2}")

# ============================================================================
# 7. 元组与列表的对比
# ============================================================================

print("\n" + "=" * 50)
print("7. 元组与列表的对比")
print("=" * 50)

import sys
import time

# 内存使用对比
list_data = [1, 2, 3, 4, 5]
tuple_data = (1, 2, 3, 4, 5)

print(f"列表内存使用: {sys.getsizeof(list_data)} 字节")
print(f"元组内存使用: {sys.getsizeof(tuple_data)} 字节")

# 创建速度对比
def time_creation(func, iterations=100000):
    start = time.time()
    for _ in range(iterations):
        func()
    return time.time() - start

list_time = time_creation(lambda: [1, 2, 3, 4, 5])
tuple_time = time_creation(lambda: (1, 2, 3, 4, 5))

print(f"创建列表耗时: {list_time:.6f}秒")
print(f"创建元组耗时: {tuple_time:.6f}秒")

# 访问速度对比（基本相同）
def access_test(container, iterations=100000):
    start = time.time()
    for _ in range(iterations):
        _ = container[2]
    return time.time() - start

list_access_time = access_test(list_data)
tuple_access_time = access_test(tuple_data)

print(f"列表访问耗时: {list_access_time:.6f}秒")
print(f"元组访问耗时: {tuple_access_time:.6f}秒")

# 特性对比表
print(f"\n特性对比:")
print(f"{'特性':<15} {'列表':<10} {'元组':<10}")
print(f"{'-'*35}")
print(f"{'可变性':<15} {'可变':<10} {'不可变':<10}")
print(f"{'内存使用':<15} {'较大':<10} {'较小':<10}")
print(f"{'创建速度':<15} {'较慢':<10} {'较快':<10}")
print(f"{'访问速度':<15} {'快':<10} {'快':<10}")
print(f"{'方法数量':<15} {'多':<10} {'少(2个)':<10}")
print(f"{'用途':<15} {'动态数据':<10} {'固定数据':<10}")

# ============================================================================
# 8. 实际应用场景
# ============================================================================

print("\n" + "=" * 50)
print("8. 实际应用场景")
print("=" * 50)

# 场景1：数据库记录
print("场景1：数据库记录")
# 模拟数据库查询结果
database_records = [
    (1, "张三", "工程师", 8000),
    (2, "李四", "设计师", 7500),
    (3, "王五", "经理", 12000)
]

Employee = namedtuple('Employee', 'id name position salary')
employees = [Employee(*record) for record in database_records]

for emp in employees:
    print(f"ID: {emp.id}, 姓名: {emp.name}, 职位: {emp.position}, 薪资: {emp.salary}")

# 场景2：配置信息
print(f"\n场景2：配置信息")
DatabaseConfig = namedtuple('DatabaseConfig', 'host port username password database')
config = DatabaseConfig('localhost', 5432, 'admin', 'secret', 'myapp')
print(f"数据库配置: {config}")

# 场景3：坐标和几何计算
print(f"\n场景3：坐标和几何计算")
def distance(point1, point2):
    """计算两点间距离"""
    x1, y1 = point1
    x2, y2 = point2
    return ((x2-x1)**2 + (y2-y1)**2)**0.5

p1 = (0, 0)
p2 = (3, 4)
dist = distance(p1, p2)
print(f"点{p1}到点{p2}的距离: {dist}")

# 场景4：函数参数和返回值
print(f"\n场景4：函数参数和返回值")
def process_rgb(color):
    """处理RGB颜色"""
    r, g, b = color
    # 计算灰度值
    gray = int(0.299 * r + 0.587 * g + 0.114 * b)
    return gray, f"rgb({r},{g},{b})"

red_color = (255, 0, 0)
gray_value, color_string = process_rgb(red_color)
print(f"红色 {red_color} 的灰度值: {gray_value}, 字符串: {color_string}")

# 场景5：字典的键
print(f"\n场景5：作为字典的键")
# 元组可以作为字典的键（因为不可变），列表不行
coordinate_data = {
    (0, 0): "原点",
    (1, 0): "x轴上的点",
    (0, 1): "y轴上的点",
    (1, 1): "对角点"
}

for coord, description in coordinate_data.items():
    print(f"坐标 {coord}: {description}")

# ============================================================================
# 9. 常见错误和最佳实践
# ============================================================================

print("\n" + "=" * 50)
print("9. 常见错误和最佳实践")
print("=" * 50)

print("常见错误:")
print("1. 忘记单元素元组的逗号")
print("2. 尝试修改元组元素")
print("3. 混淆元组和列表的使用场景")

# 演示常见错误
print(f"\n错误演示:")
# 错误：忘记逗号
wrong_tuple = (42)
correct_tuple = (42,)
print(f"错误的单元素'元组': {wrong_tuple}, 类型: {type(wrong_tuple)}")
print(f"正确的单元素元组: {correct_tuple}, 类型: {type(correct_tuple)}")

print(f"\n最佳实践:")
print("✓ 用元组存储不会改变的相关数据")
print("✓ 用元组作为函数的多返回值")
print("✓ 用命名元组提高代码可读性")
print("✓ 用元组作为字典的键")
print("✓ 在需要不可变序列时选择元组")
print("✓ 用元组解包简化变量赋值")

# 性能提示
print(f"\n性能提示:")
print("- 元组比列表占用更少内存")
print("- 元组创建速度比列表快")
print("- 元组可以作为字典键，列表不行")
print("- 大量固定数据优先使用元组")

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("元组学习完成！")
    print("=" * 50)
    print("你已经学会了:")
    print("✓ 元组的创建和特性")
    print("✓ 元组的不可变性质")
    print("✓ 元组解包操作")
    print("✓ 命名元组的使用")
    print("✓ 元组与列表的区别")
    print("✓ 实际应用场景")
    print("\n继续学习字典吧！")