"""
Python列表(List)操作详解

列表是Python中最常用的数据结构之一，它是一个有序的、可变的集合。
列表可以存储不同类型的数据，支持索引访问、切片操作和各种内置方法。

学习目标：
1. 掌握列表的创建和初始化方法
2. 理解列表的索引和切片操作
3. 学会使用列表的各种内置方法
4. 掌握列表推导式的使用
5. 了解列表的性能特点和优化技巧
"""

# ============================================================================
# 1. 列表的创建和初始化
# ============================================================================

print("=" * 50)
print("1. 列表的创建和初始化")
print("=" * 50)

# 创建空列表的几种方法
empty_list1 = []
empty_list2 = list()
print(f"空列表1: {empty_list1}")
print(f"空列表2: {empty_list2}")

# 创建包含元素的列表
numbers = [1, 2, 3, 4, 5]
mixed_list = [1, "hello", 3.14, True, None]
nested_list = [[1, 2], [3, 4], [5, 6]]

print(f"数字列表: {numbers}")
print(f"混合类型列表: {mixed_list}")
print(f"嵌套列表: {nested_list}")

# 使用range()创建列表
range_list = list(range(1, 11))
even_numbers = list(range(0, 21, 2))
print(f"1-10的列表: {range_list}")
print(f"0-20的偶数: {even_numbers}")

# 使用重复操作创建列表
repeated_list = [0] * 5
repeated_string = ["hello"] * 3
print(f"重复数字: {repeated_list}")
print(f"重复字符串: {repeated_string}")

# ============================================================================
# 2. 列表的访问和索引
# ============================================================================

print("\n" + "=" * 50)
print("2. 列表的访问和索引")
print("=" * 50)

fruits = ["苹果", "香蕉", "橙子", "葡萄", "草莓"]
print(f"水果列表: {fruits}")

# 正向索引（从0开始）
print(f"第一个水果: {fruits[0]}")
print(f"第三个水果: {fruits[2]}")

# 反向索引（从-1开始）
print(f"最后一个水果: {fruits[-1]}")
print(f"倒数第二个水果: {fruits[-2]}")

# 获取列表长度
print(f"水果总数: {len(fruits)}")

# 检查元素是否存在
print(f"'苹果'在列表中: {'苹果' in fruits}")
print(f"'西瓜'在列表中: {'西瓜' in fruits}")

# ============================================================================
# 3. 列表的切片操作
# ============================================================================

print("\n" + "=" * 50)
print("3. 列表的切片操作")
print("=" * 50)

numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(f"原始列表: {numbers}")

# 基本切片 [start:end]
print(f"前5个元素: {numbers[:5]}")
print(f"后5个元素: {numbers[5:]}")
print(f"中间3个元素: {numbers[3:6]}")

# 带步长的切片 [start:end:step]
print(f"偶数索引元素: {numbers[::2]}")
print(f"奇数索引元素: {numbers[1::2]}")
print(f"反向列表: {numbers[::-1]}")

# 负索引切片
print(f"除了最后2个: {numbers[:-2]}")
print(f"从倒数第3个开始: {numbers[-3:]}")

# ============================================================================
# 4. 列表的修改操作
# ============================================================================

print("\n" + "=" * 50)
print("4. 列表的修改操作")
print("=" * 50)

# 修改单个元素
colors = ["红", "绿", "蓝"]
print(f"原始颜色: {colors}")
colors[1] = "黄"
print(f"修改后: {colors}")

# 修改多个元素（切片赋值）
numbers = [1, 2, 3, 4, 5]
print(f"原始数字: {numbers}")
numbers[1:4] = [20, 30, 40]
print(f"切片修改后: {numbers}")

# 插入元素（切片插入）
numbers[2:2] = [25, 35]
print(f"插入元素后: {numbers}")

# ============================================================================
# 5. 列表的内置方法
# ============================================================================

print("\n" + "=" * 50)
print("5. 列表的内置方法")
print("=" * 50)

# 添加元素的方法
shopping_list = ["牛奶", "面包"]
print(f"购物清单: {shopping_list}")

# append() - 在末尾添加单个元素
shopping_list.append("鸡蛋")
print(f"添加鸡蛋后: {shopping_list}")

# insert() - 在指定位置插入元素
shopping_list.insert(1, "水果")
print(f"插入水果后: {shopping_list}")

# extend() - 添加多个元素
shopping_list.extend(["蔬菜", "肉类"])
print(f"扩展后: {shopping_list}")

# 删除元素的方法
numbers = [1, 2, 3, 2, 4, 2, 5]
print(f"\n数字列表: {numbers}")

# remove() - 删除第一个匹配的元素
numbers.remove(2)
print(f"删除第一个2后: {numbers}")

# pop() - 删除并返回指定位置的元素（默认最后一个）
last_item = numbers.pop()
print(f"弹出最后一个元素 {last_item}: {numbers}")

second_item = numbers.pop(1)
print(f"弹出索引1的元素 {second_item}: {numbers}")

# clear() - 清空列表
temp_list = [1, 2, 3]
temp_list.clear()
print(f"清空后的列表: {temp_list}")

# 查找和统计方法
data = [1, 2, 3, 2, 4, 2, 5]
print(f"\n数据列表: {data}")

# index() - 查找元素的索引
index_of_3 = data.index(3)
print(f"数字3的索引: {index_of_3}")

# count() - 统计元素出现次数
count_of_2 = data.count(2)
print(f"数字2出现次数: {count_of_2}")

# 排序和反转方法
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"\n原始数字: {numbers}")

# sort() - 原地排序
numbers_copy1 = numbers.copy()
numbers_copy1.sort()
print(f"升序排序: {numbers_copy1}")

numbers_copy2 = numbers.copy()
numbers_copy2.sort(reverse=True)
print(f"降序排序: {numbers_copy2}")

# reverse() - 原地反转
numbers_copy3 = numbers.copy()
numbers_copy3.reverse()
print(f"反转列表: {numbers_copy3}")

# sorted() - 返回新的排序列表（不修改原列表）
sorted_numbers = sorted(numbers)
print(f"sorted()结果: {sorted_numbers}")
print(f"原列表未变: {numbers}")

# ============================================================================
# 6. 列表推导式
# ============================================================================

print("\n" + "=" * 50)
print("6. 列表推导式")
print("=" * 50)

# 基本列表推导式
squares = [x**2 for x in range(1, 6)]
print(f"1-5的平方: {squares}")

# 带条件的列表推导式
even_squares = [x**2 for x in range(1, 11) if x % 2 == 0]
print(f"1-10中偶数的平方: {even_squares}")

# 字符串处理
words = ["hello", "world", "python", "programming"]
upper_words = [word.upper() for word in words]
long_words = [word for word in words if len(word) > 5]
print(f"大写单词: {upper_words}")
print(f"长单词(>5字符): {long_words}")

# 嵌套列表推导式
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flattened = [num for row in matrix for num in row]
print(f"矩阵: {matrix}")
print(f"展平后: {flattened}")

# 复杂的列表推导式
coordinates = [(x, y) for x in range(3) for y in range(3) if x != y]
print(f"坐标对(x≠y): {coordinates}")

# ============================================================================
# 7. 列表的复制
# ============================================================================

print("\n" + "=" * 50)
print("7. 列表的复制")
print("=" * 50)

original = [1, 2, [3, 4]]
print(f"原始列表: {original}")

# 浅复制的几种方法
shallow_copy1 = original.copy()
shallow_copy2 = original[:]
shallow_copy3 = list(original)

print(f"浅复制1: {shallow_copy1}")
print(f"浅复制2: {shallow_copy2}")
print(f"浅复制3: {shallow_copy3}")

# 修改嵌套对象会影响所有浅复制
original[2][0] = 99
print(f"修改嵌套对象后:")
print(f"原始列表: {original}")
print(f"浅复制1: {shallow_copy1}")

# 深复制
import copy
deep_copy = copy.deepcopy([1, 2, [3, 4]])
original_for_deep = [1, 2, [3, 4]]
original_for_deep[2][0] = 99
print(f"深复制不受影响: {deep_copy}")

# ============================================================================
# 8. 列表的性能优化和内存管理
# ============================================================================

print("\n" + "=" * 50)
print("8. 列表的性能优化和内存管理")
print("=" * 50)

# 预分配列表大小vs动态增长
import time

# 动态增长（较慢）
start_time = time.time()
dynamic_list = []
for i in range(10000):
    dynamic_list.append(i)
dynamic_time = time.time() - start_time

# 预分配（较快）
start_time = time.time()
preallocated_list = [0] * 10000
for i in range(10000):
    preallocated_list[i] = i
preallocated_time = time.time() - start_time

print(f"动态增长耗时: {dynamic_time:.6f}秒")
print(f"预分配耗时: {preallocated_time:.6f}秒")

# 列表推导式vs循环
start_time = time.time()
loop_result = []
for i in range(1000):
    if i % 2 == 0:
        loop_result.append(i**2)
loop_time = time.time() - start_time

start_time = time.time()
comprehension_result = [i**2 for i in range(1000) if i % 2 == 0]
comprehension_time = time.time() - start_time

print(f"循环方式耗时: {loop_time:.6f}秒")
print(f"列表推导式耗时: {comprehension_time:.6f}秒")

# 内存使用提示
print(f"\n内存使用提示:")
print(f"- 列表在内存中连续存储，访问速度快")
print(f"- 插入和删除操作可能需要移动大量元素")
print(f"- 在列表末尾操作（append/pop）效率最高")
print(f"- 大量数据处理时考虑使用生成器或numpy数组")

# ============================================================================
# 9. 实际应用示例
# ============================================================================

print("\n" + "=" * 50)
print("9. 实际应用示例")
print("=" * 50)

# 示例1：学生成绩管理
students_scores = [
    ("张三", 85),
    ("李四", 92),
    ("王五", 78),
    ("赵六", 96),
    ("钱七", 88)
]

print("学生成绩管理:")
print(f"所有学生: {students_scores}")

# 按成绩排序
sorted_by_score = sorted(students_scores, key=lambda x: x[1], reverse=True)
print(f"按成绩排序: {sorted_by_score}")

# 筛选优秀学生（成绩>=90）
excellent_students = [(name, score) for name, score in students_scores if score >= 90]
print(f"优秀学生: {excellent_students}")

# 计算平均分
average_score = sum(score for _, score in students_scores) / len(students_scores)
print(f"平均分: {average_score:.2f}")

# 示例2：数据清洗
raw_data = ["  hello  ", "", "world", None, "  python  ", ""]
print(f"\n原始数据: {raw_data}")

# 清洗数据：去除空值和空白字符
cleaned_data = [item.strip() for item in raw_data if item and item.strip()]
print(f"清洗后数据: {cleaned_data}")

# 示例3：批量处理文件名
file_names = ["document.txt", "image.jpg", "script.py", "data.csv"]
print(f"\n文件列表: {file_names}")

# 提取文件扩展名
extensions = [name.split('.')[-1] for name in file_names]
print(f"扩展名: {extensions}")

# 按类型分组
text_files = [name for name in file_names if name.endswith('.txt')]
image_files = [name for name in file_names if name.endswith('.jpg')]
print(f"文本文件: {text_files}")
print(f"图片文件: {image_files}")

# ============================================================================
# 10. 常见错误和注意事项
# ============================================================================

print("\n" + "=" * 50)
print("10. 常见错误和注意事项")
print("=" * 50)

print("常见错误:")
print("1. 索引越界 - 访问不存在的索引位置")
print("2. 修改正在迭代的列表 - 可能导致意外结果")
print("3. 浅复制陷阱 - 嵌套对象的修改会影响所有副本")
print("4. 列表乘法陷阱 - [[]]*3 创建的是同一个列表的引用")

# 演示列表乘法陷阱
print("\n列表乘法陷阱演示:")
wrong_matrix = [[0] * 3] * 3  # 错误方式
correct_matrix = [[0] * 3 for _ in range(3)]  # 正确方式

print(f"错误方式创建的矩阵: {wrong_matrix}")
wrong_matrix[0][0] = 1
print(f"修改[0][0]后: {wrong_matrix}")  # 所有行都被修改了！

print(f"正确方式创建的矩阵: {correct_matrix}")
correct_matrix[0][0] = 1
print(f"修改[0][0]后: {correct_matrix}")  # 只有第一行被修改

print("\n最佳实践:")
print("- 使用有意义的变量名")
print("- 优先使用列表推导式而不是循环")
print("- 在列表末尾进行添加/删除操作")
print("- 需要频繁插入/删除时考虑使用collections.deque")
print("- 大量数值计算时考虑使用numpy数组")

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("列表学习完成！")
    print("=" * 50)
    print("你已经学会了:")
    print("✓ 列表的创建和初始化")
    print("✓ 索引和切片操作")
    print("✓ 列表的各种内置方法")
    print("✓ 列表推导式的使用")
    print("✓ 性能优化技巧")
    print("✓ 实际应用场景")
    print("\n继续学习其他数据结构吧！")