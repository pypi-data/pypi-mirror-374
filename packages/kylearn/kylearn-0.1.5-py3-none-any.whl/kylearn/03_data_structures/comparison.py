"""
Python数据结构对比分析

本文件详细对比Python中四种主要的内置数据结构：
列表(List)、元组(Tuple)、字典(Dictionary)、集合(Set)

学习目标：
1. 理解各种数据结构的特点和差异
2. 掌握不同场景下的数据结构选择
3. 了解性能差异和使用建议
4. 学会数据结构之间的转换
"""

import sys
import time
from collections import defaultdict

# ============================================================================
# 1. 数据结构特性对比
# ============================================================================

print("=" * 60)
print("1. 数据结构特性对比")
print("=" * 60)

# 创建示例数据
sample_list = [1, 2, 3, 2, 4]
sample_tuple = (1, 2, 3, 2, 4)
sample_dict = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
sample_set = {1, 2, 3, 4}  # 注意：集合自动去重

print("示例数据:")
print(f"列表:   {sample_list}")
print(f"元组:   {sample_tuple}")
print(f"字典:   {sample_dict}")
print(f"集合:   {sample_set}")

# 特性对比表
print(f"\n{'特性':<12} {'列表':<8} {'元组':<8} {'字典':<8} {'集合':<8}")
print("-" * 50)
print(f"{'可变性':<12} {'可变':<8} {'不可变':<8} {'可变':<8} {'可变':<8}")
print(f"{'有序性':<12} {'有序':<8} {'有序':<8} {'有序*':<8} {'无序':<8}")
print(f"{'重复元素':<12} {'允许':<8} {'允许':<8} {'键唯一':<8} {'不允许':<8}")
print(f"{'索引访问':<12} {'支持':<8} {'支持':<8} {'键访问':<8} {'不支持':<8}")
print(f"{'可哈希':<12} {'否':<8} {'是':<8} {'否':<8} {'否':<8}")

print("\n注：*字典在Python 3.7+保持插入顺序")

# ============================================================================
# 2. 内存使用对比
# ============================================================================

print("\n" + "=" * 60)
print("2. 内存使用对比")
print("=" * 60)

# 创建相同数据的不同结构
data = list(range(1000))

list_data = data
tuple_data = tuple(data)
dict_data = {i: i for i in data}
set_data = set(data)

print("1000个元素的内存使用:")
print(f"列表: {sys.getsizeof(list_data):>8} 字节")
print(f"元组: {sys.getsizeof(tuple_data):>8} 字节")
print(f"字典: {sys.getsizeof(dict_data):>8} 字节")
print(f"集合: {sys.getsizeof(set_data):>8} 字节")

# 内存效率分析
tuple_efficiency = sys.getsizeof(tuple_data) / sys.getsizeof(list_data)
dict_efficiency = sys.getsizeof(dict_data) / sys.getsizeof(list_data)
set_efficiency = sys.getsizeof(set_data) / sys.getsizeof(list_data)

print(f"\n相对于列表的内存使用比例:")
print(f"元组: {tuple_efficiency:.2f}x")
print(f"字典: {dict_efficiency:.2f}x")
print(f"集合: {set_efficiency:.2f}x")

# ============================================================================
# 3. 性能对比测试
# ============================================================================

print("\n" + "=" * 60)
print("3. 性能对比测试")
print("=" * 60)

# 创建测试数据
test_size = 10000
test_list = list(range(test_size))
test_tuple = tuple(range(test_size))
test_dict = {i: i for i in range(test_size)}
test_set = set(range(test_size))

def time_operation(operation, iterations=1000):
    """测试操作的执行时间"""
    start = time.time()
    for _ in range(iterations):
        operation()
    return time.time() - start

# 3.1 访问性能测试
print("3.1 元素访问性能 (1000次操作):")
target_index = test_size // 2

list_access_time = time_operation(lambda: test_list[target_index])
tuple_access_time = time_operation(lambda: test_tuple[target_index])
dict_access_time = time_operation(lambda: test_dict[target_index])

print(f"列表索引访问: {list_access_time:.6f}秒")
print(f"元组索引访问: {tuple_access_time:.6f}秒")
print(f"字典键访问:   {dict_access_time:.6f}秒")

# 3.2 查找性能测试
print(f"\n3.2 元素查找性能 (100次操作):")
target_value = test_size // 2

list_search_time = time_operation(lambda: target_value in test_list, 100)
tuple_search_time = time_operation(lambda: target_value in test_tuple, 100)
dict_search_time = time_operation(lambda: target_value in test_dict, 100)
set_search_time = time_operation(lambda: target_value in test_set, 100)

print(f"列表查找: {list_search_time:.6f}秒")
print(f"元组查找: {tuple_search_time:.6f}秒")
print(f"字典查找: {dict_search_time:.6f}秒")
print(f"集合查找: {set_search_time:.6f}秒")

# 查找性能比较
fastest_search = min(list_search_time, tuple_search_time, dict_search_time, set_search_time)
print(f"\n查找性能比较 (相对于最快的):")
print(f"列表: {list_search_time/fastest_search:.1f}x")
print(f"元组: {tuple_search_time/fastest_search:.1f}x")
print(f"字典: {dict_search_time/fastest_search:.1f}x")
print(f"集合: {set_search_time/fastest_search:.1f}x")

# 3.3 添加元素性能测试
print(f"\n3.3 添加元素性能 (1000次操作):")

# 列表添加
list_append_time = time_operation(lambda: test_list.append(99999) or test_list.pop())

# 字典添加
dict_add_time = time_operation(lambda: test_dict.update({99999: 99999}) or test_dict.pop(99999))

# 集合添加
set_add_time = time_operation(lambda: test_set.add(99999) or test_set.discard(99999))

print(f"列表末尾添加: {list_append_time:.6f}秒")
print(f"字典添加:     {dict_add_time:.6f}秒")
print(f"集合添加:     {set_add_time:.6f}秒")

# ============================================================================
# 4. 使用场景分析
# ============================================================================

print("\n" + "=" * 60)
print("4. 使用场景分析")
print("=" * 60)

print("4.1 列表 (List) - 最适合场景:")
print("✓ 需要保持元素顺序")
print("✓ 需要通过索引访问元素")
print("✓ 需要频繁添加/删除元素")
print("✓ 允许重复元素")
print("✓ 需要切片操作")

print(f"\n示例：学生成绩列表")
grades = [85, 92, 78, 85, 96]  # 允许重复成绩
print(f"成绩: {grades}")
print(f"第一个成绩: {grades[0]}")
print(f"前三个成绩: {grades[:3]}")
grades.append(88)
print(f"添加成绩后: {grades}")

print(f"\n4.2 元组 (Tuple) - 最适合场景:")
print("✓ 数据不需要修改")
print("✓ 作为字典的键")
print("✓ 函数返回多个值")
print("✓ 配置信息存储")
print("✓ 坐标、RGB值等固定结构")

print(f"\n示例：坐标点和配置信息")
point = (10, 20)  # 坐标点
config = ("localhost", 5432, "database")  # 数据库配置
coordinates_dict = {(0, 0): "原点", (1, 1): "对角"}  # 作为字典键
print(f"坐标点: {point}")
print(f"配置: {config}")
print(f"坐标字典: {coordinates_dict}")

print(f"\n4.3 字典 (Dictionary) - 最适合场景:")
print("✓ 键值对映射关系")
print("✓ 快速查找和访问")
print("✓ 配置管理")
print("✓ 缓存系统")
print("✓ 计数和分组")

print(f"\n示例：用户信息和计数")
user_info = {"name": "张三", "age": 25, "city": "北京"}
word_count = defaultdict(int)
for word in "hello world hello".split():
    word_count[word] += 1
print(f"用户信息: {user_info}")
print(f"单词计数: {dict(word_count)}")

print(f"\n4.4 集合 (Set) - 最适合场景:")
print("✓ 去除重复元素")
print("✓ 快速成员测试")
print("✓ 数学集合运算")
print("✓ 权限管理")
print("✓ 标签系统")

print(f"\n示例：去重和权限管理")
user_ids = [1001, 1002, 1001, 1003, 1002]
unique_ids = set(user_ids)
admin_perms = {"read", "write", "delete"}
user_perms = {"read", "write"}
missing_perms = admin_perms - user_perms
print(f"原始ID: {user_ids}")
print(f"去重后: {unique_ids}")
print(f"缺少权限: {missing_perms}")

# ============================================================================
# 5. 数据结构转换
# ============================================================================

print("\n" + "=" * 60)
print("5. 数据结构转换")
print("=" * 60)

# 原始数据
original_list = [1, 2, 3, 2, 4, 3, 5]
print(f"原始列表: {original_list}")

# 各种转换
print(f"\n5.1 从列表转换:")
to_tuple = tuple(original_list)
to_set = set(original_list)  # 自动去重
to_dict_enumerate = dict(enumerate(original_list))  # 索引作为键
to_dict_zip = dict(zip(original_list, original_list))  # 值作为键和值

print(f"转为元组: {to_tuple}")
print(f"转为集合: {to_set}")
print(f"转为字典(枚举): {to_dict_enumerate}")
print(f"转为字典(zip): {to_dict_zip}")

print(f"\n5.2 从字典转换:")
sample_dict = {"a": 1, "b": 2, "c": 3}
print(f"原始字典: {sample_dict}")

dict_to_list_keys = list(sample_dict.keys())
dict_to_list_values = list(sample_dict.values())
dict_to_list_items = list(sample_dict.items())
dict_to_set_keys = set(sample_dict.keys())

print(f"键转列表: {dict_to_list_keys}")
print(f"值转列表: {dict_to_list_values}")
print(f"项转列表: {dict_to_list_items}")
print(f"键转集合: {dict_to_set_keys}")

print(f"\n5.3 复杂转换示例:")
# 学生数据处理
students = [
    {"name": "张三", "age": 20, "subjects": ["数学", "物理"]},
    {"name": "李四", "age": 21, "subjects": ["化学", "生物"]},
    {"name": "王五", "age": 20, "subjects": ["数学", "化学"]}
]

# 提取所有科目（去重）
all_subjects = set()
for student in students:
    all_subjects.update(student["subjects"])

# 按年龄分组
age_groups = defaultdict(list)
for student in students:
    age_groups[student["age"]].append(student["name"])

# 科目-学生映射
subject_students = defaultdict(list)
for student in students:
    for subject in student["subjects"]:
        subject_students[subject].append(student["name"])

print(f"所有科目: {all_subjects}")
print(f"年龄分组: {dict(age_groups)}")
print(f"科目-学生映射: {dict(subject_students)}")

# ============================================================================
# 6. 选择决策树
# ============================================================================

print("\n" + "=" * 60)
print("6. 数据结构选择决策指南")
print("=" * 60)

def recommend_data_structure(requirements):
    """根据需求推荐数据结构"""
    recommendations = []
    
    print("根据您的需求分析:")
    
    if requirements.get("ordered", False):
        if requirements.get("mutable", False):
            if requirements.get("key_value", False):
                recommendations.append("字典 - 有序的键值对映射")
            else:
                recommendations.append("列表 - 有序且可变的序列")
        else:
            recommendations.append("元组 - 有序且不可变的序列")
    else:
        if requirements.get("unique_only", False):
            recommendations.append("集合 - 无序且唯一的元素集合")
        elif requirements.get("key_value", False):
            recommendations.append("字典 - 键值对映射")
    
    if requirements.get("fast_lookup", False):
        recommendations.append("字典或集合 - O(1)查找性能")
    
    if requirements.get("hashable_needed", False):
        recommendations.append("元组或frozenset - 可作为字典键")
    
    return recommendations

# 示例需求场景
scenarios = [
    {
        "name": "存储用户购物车商品",
        "requirements": {"ordered": True, "mutable": True, "key_value": False},
        "description": "需要保持添加顺序，可以修改"
    },
    {
        "name": "存储数据库连接配置",
        "requirements": {"ordered": False, "mutable": False, "key_value": False},
        "description": "配置信息不变，可作为字典键"
    },
    {
        "name": "用户权限管理",
        "requirements": {"ordered": False, "mutable": True, "unique_only": True},
        "description": "权限唯一，需要快速查找"
    },
    {
        "name": "缓存系统",
        "requirements": {"ordered": False, "mutable": True, "key_value": True, "fast_lookup": True},
        "description": "键值映射，需要快速访问"
    }
]

for scenario in scenarios:
    print(f"\n场景: {scenario['name']}")
    print(f"描述: {scenario['description']}")
    recommendations = recommend_data_structure(scenario['requirements'])
    print("推荐:")
    for rec in recommendations:
        print(f"  • {rec}")

# ============================================================================
# 7. 性能总结和建议
# ============================================================================

print("\n" + "=" * 60)
print("7. 性能总结和最佳实践")
print("=" * 60)

print("7.1 时间复杂度总结:")
print(f"{'操作':<15} {'列表':<10} {'元组':<10} {'字典':<10} {'集合':<10}")
print("-" * 60)
print(f"{'访问元素':<15} {'O(1)':<10} {'O(1)':<10} {'O(1)':<10} {'N/A':<10}")
print(f"{'查找元素':<15} {'O(n)':<10} {'O(n)':<10} {'O(1)':<10} {'O(1)':<10}")
print(f"{'添加元素':<15} {'O(1)*':<10} {'N/A':<10} {'O(1)':<10} {'O(1)':<10}")
print(f"{'删除元素':<15} {'O(n)':<10} {'N/A':<10} {'O(1)':<10} {'O(1)':<10}")
print(f"{'遍历':<15} {'O(n)':<10} {'O(n)':<10} {'O(n)':<10} {'O(n)':<10}")

print("\n注：*列表末尾添加是O(1)，中间插入是O(n)")

print(f"\n7.2 最佳实践建议:")
print("• 大量查找操作 → 使用字典或集合")
print("• 需要保持顺序 → 使用列表或元组")
print("• 数据不变 → 优先使用元组")
print("• 需要去重 → 使用集合")
print("• 键值映射 → 使用字典")
print("• 频繁添加删除 → 避免在列表中间操作")
print("• 内存敏感 → 元组比列表更节省内存")
print("• 需要作为字典键 → 使用元组或frozenset")

print(f"\n7.3 常见性能陷阱:")
print("❌ 在大列表中频繁使用 'in' 操作")
print("❌ 在列表开头频繁插入删除元素")
print("❌ 用列表实现需要去重的场景")
print("❌ 用字典存储简单的有序数据")
print("❌ 在不需要修改时使用列表而不是元组")

print(f"\n7.4 优化建议:")
print("✓ 预估数据大小，选择合适的数据结构")
print("✓ 大量查找时使用字典或集合")
print("✓ 固定数据使用元组节省内存")
print("✓ 需要去重时直接使用集合")
print("✓ 合理使用数据结构的内置方法")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("数据结构对比学习完成！")
    print("=" * 60)
    print("你已经掌握了:")
    print("✓ 四种数据结构的特性差异")
    print("✓ 性能特点和使用场景")
    print("✓ 数据结构选择的决策方法")
    print("✓ 数据结构之间的转换")
    print("✓ 性能优化的最佳实践")
    print("\n现在可以开始练习了！")