"""
Python集合(Set)运算详解

集合是Python中的无序、不重复元素的集合类型。
集合主要用于去重、成员测试和数学集合运算（并集、交集、差集等）。

学习目标：
1. 掌握集合的创建和基本特性
2. 理解集合的去重功能
3. 学会集合的数学运算
4. 掌握集合推导式的使用
5. 了解frozenset的使用场景
"""

# ============================================================================
# 1. 集合的创建和基本特性
# ============================================================================

print("=" * 50)
print("1. 集合的创建和基本特性")
print("=" * 50)

# 创建集合的几种方法
empty_set = set()  # 注意：{}创建的是空字典，不是空集合
print(f"空集合: {empty_set}")

# 从列表创建集合（自动去重）
numbers_list = [1, 2, 3, 2, 4, 3, 5]
numbers_set = set(numbers_list)
print(f"原列表: {numbers_list}")
print(f"转换为集合: {numbers_set}")

# 直接创建集合
fruits = {"苹果", "香蕉", "橙子", "苹果"}  # 重复的"苹果"会被自动去除
print(f"水果集合: {fruits}")

# 从字符串创建集合
char_set = set("hello")
print(f"字符集合: {char_set}")

# 从其他可迭代对象创建
tuple_set = set((1, 2, 3, 2, 1))
range_set = set(range(1, 6))
print(f"从元组创建: {tuple_set}")
print(f"从range创建: {range_set}")

# 集合的基本特性
print(f"\n集合特性:")
print(f"- 无序：集合中的元素没有固定顺序")
print(f"- 唯一：集合自动去除重复元素")
print(f"- 可变：可以添加和删除元素")
print(f"- 元素必须是不可变类型")

# ============================================================================
# 2. 集合的基本操作
# ============================================================================

print("\n" + "=" * 50)
print("2. 集合的基本操作")
print("=" * 50)

colors = {"红", "绿", "蓝"}
print(f"颜色集合: {colors}")

# 添加元素
colors.add("黄")
print(f"添加黄色后: {colors}")

# 添加多个元素
colors.update(["紫", "橙", "黑"])
print(f"添加多个颜色后: {colors}")

# 也可以用集合更新
colors.update({"白", "灰"})
print(f"用集合更新后: {colors}")

# 删除元素
colors.remove("黑")  # 如果元素不存在会报错
print(f"删除黑色后: {colors}")

colors.discard("粉")  # 如果元素不存在不会报错
print(f"尝试删除粉色后: {colors}")

# 随机删除并返回一个元素
removed_color = colors.pop()
print(f"随机删除的颜色: {removed_color}")
print(f"删除后的集合: {colors}")

# 清空集合
temp_set = {"a", "b", "c"}
temp_set.clear()
print(f"清空后的集合: {temp_set}")

# 集合长度和成员测试
numbers = {1, 2, 3, 4, 5}
print(f"\n数字集合: {numbers}")
print(f"集合长度: {len(numbers)}")
print(f"3在集合中: {3 in numbers}")
print(f"6在集合中: {6 in numbers}")

# ============================================================================
# 3. 集合的数学运算
# ============================================================================

print("\n" + "=" * 50)
print("3. 集合的数学运算")
print("=" * 50)

# 创建示例集合
set_a = {1, 2, 3, 4, 5}
set_b = {4, 5, 6, 7, 8}
set_c = {1, 2, 3}

print(f"集合A: {set_a}")
print(f"集合B: {set_b}")
print(f"集合C: {set_c}")

# 并集 (Union) - 所有元素的集合
union1 = set_a | set_b  # 使用 | 操作符
union2 = set_a.union(set_b)  # 使用方法
print(f"\nA ∪ B (并集): {union1}")
print(f"A.union(B): {union2}")

# 交集 (Intersection) - 共同元素的集合
intersection1 = set_a & set_b  # 使用 & 操作符
intersection2 = set_a.intersection(set_b)  # 使用方法
print(f"\nA ∩ B (交集): {intersection1}")
print(f"A.intersection(B): {intersection2}")

# 差集 (Difference) - 在A中但不在B中的元素
difference1 = set_a - set_b  # 使用 - 操作符
difference2 = set_a.difference(set_b)  # 使用方法
print(f"\nA - B (差集): {difference1}")
print(f"A.difference(B): {difference2}")
print(f"B - A (差集): {set_b - set_a}")

# 对称差集 (Symmetric Difference) - 在A或B中但不在两者交集中的元素
sym_diff1 = set_a ^ set_b  # 使用 ^ 操作符
sym_diff2 = set_a.symmetric_difference(set_b)  # 使用方法
print(f"\nA △ B (对称差集): {sym_diff1}")
print(f"A.symmetric_difference(B): {sym_diff2}")

# 集合关系判断
print(f"\n集合关系:")
print(f"C是A的子集: {set_c.issubset(set_a)}")
print(f"A是C的超集: {set_a.issuperset(set_c)}")
print(f"A和B是否不相交: {set_a.isdisjoint({9, 10, 11})}")
print(f"A和B是否相交: {not set_a.isdisjoint(set_b)}")

# ============================================================================
# 4. 集合的就地修改操作
# ============================================================================

print("\n" + "=" * 50)
print("4. 集合的就地修改操作")
print("=" * 50)

# 创建可修改的集合副本
set_x = {1, 2, 3, 4}
set_y = {3, 4, 5, 6}

print(f"原始集合X: {set_x}")
print(f"原始集合Y: {set_y}")

# 就地并集更新
set_x_copy = set_x.copy()
set_x_copy |= set_y  # 等同于 set_x_copy.update(set_y)
print(f"X |= Y 后: {set_x_copy}")

# 就地交集更新
set_x_copy = set_x.copy()
set_x_copy &= set_y  # 等同于 set_x_copy.intersection_update(set_y)
print(f"X &= Y 后: {set_x_copy}")

# 就地差集更新
set_x_copy = set_x.copy()
set_x_copy -= set_y  # 等同于 set_x_copy.difference_update(set_y)
print(f"X -= Y 后: {set_x_copy}")

# 就地对称差集更新
set_x_copy = set_x.copy()
set_x_copy ^= set_y  # 等同于 set_x_copy.symmetric_difference_update(set_y)
print(f"X ^= Y 后: {set_x_copy}")

# ============================================================================
# 5. 集合推导式
# ============================================================================

print("\n" + "=" * 50)
print("5. 集合推导式")
print("=" * 50)

# 基本集合推导式
squares = {x**2 for x in range(1, 6)}
print(f"平方数集合: {squares}")

# 带条件的集合推导式
even_squares = {x**2 for x in range(1, 11) if x % 2 == 0}
print(f"偶数平方集合: {even_squares}")

# 字符串处理
words = ["hello", "world", "python", "hello"]
unique_lengths = {len(word) for word in words}
print(f"单词: {words}")
print(f"唯一长度: {unique_lengths}")

# 从嵌套结构提取唯一值
data = [
    {"name": "张三", "skills": ["Python", "Java"]},
    {"name": "李四", "skills": ["Python", "C++", "Go"]},
    {"name": "王五", "skills": ["Java", "JavaScript"]}
]

all_skills = {skill for person in data for skill in person["skills"]}
print(f"所有技能: {all_skills}")

# 数学运算
multiples_of_3 = {x for x in range(1, 31) if x % 3 == 0}
multiples_of_5 = {x for x in range(1, 31) if x % 5 == 0}
print(f"3的倍数: {multiples_of_3}")
print(f"5的倍数: {multiples_of_5}")
print(f"3和5的公倍数: {multiples_of_3 & multiples_of_5}")

# ============================================================================
# 6. 冻结集合 (frozenset)
# ============================================================================

print("\n" + "=" * 50)
print("6. 冻结集合 (frozenset)")
print("=" * 50)

# 创建frozenset
frozen_numbers = frozenset([1, 2, 3, 4, 5])
frozen_colors = frozenset({"红", "绿", "蓝"})

print(f"冻结数字集合: {frozen_numbers}")
print(f"冻结颜色集合: {frozen_colors}")

# frozenset是不可变的
print(f"frozenset特性:")
print(f"- 不可变：创建后不能修改")
print(f"- 可哈希：可以作为字典的键或集合的元素")
print(f"- 支持所有集合运算")

# frozenset的运算
frozen_a = frozenset([1, 2, 3])
frozen_b = frozenset([2, 3, 4])

print(f"\nfrozenset运算:")
print(f"A: {frozen_a}")
print(f"B: {frozen_b}")
print(f"A ∪ B: {frozen_a | frozen_b}")
print(f"A ∩ B: {frozen_a & frozen_b}")
print(f"A - B: {frozen_a - frozen_b}")

# frozenset作为字典键
nested_sets = {
    frozenset([1, 2]): "第一组",
    frozenset([3, 4]): "第二组",
    frozenset([5, 6]): "第三组"
}
print(f"\n以frozenset为键的字典: {nested_sets}")

# frozenset作为集合元素
set_of_sets = {
    frozenset([1, 2]),
    frozenset([3, 4]),
    frozenset([1, 2])  # 重复的会被去除
}
print(f"集合的集合: {set_of_sets}")

# ============================================================================
# 7. 实际应用场景
# ============================================================================

print("\n" + "=" * 50)
print("7. 实际应用场景")
print("=" * 50)

# 场景1：数据去重
print("场景1：数据去重")
user_ids = [1001, 1002, 1003, 1002, 1004, 1001, 1005]
unique_users = set(user_ids)
print(f"原始用户ID: {user_ids}")
print(f"去重后: {unique_users}")
print(f"去重后的列表: {list(unique_users)}")

# 场景2：权限管理
print(f"\n场景2：权限管理")
admin_permissions = {"read", "write", "delete", "admin"}
user_permissions = {"read", "write"}
guest_permissions = {"read"}

print(f"管理员权限: {admin_permissions}")
print(f"用户权限: {user_permissions}")
print(f"访客权限: {guest_permissions}")

# 检查权限
def check_permission(user_perms, required_perm):
    return required_perm in user_perms

print(f"用户是否有写权限: {check_permission(user_permissions, 'write')}")
print(f"访客是否有删除权限: {check_permission(guest_permissions, 'delete')}")

# 权限差异分析
missing_perms = admin_permissions - user_permissions
print(f"用户缺少的权限: {missing_perms}")

# 场景3：标签系统
print(f"\n场景3：标签系统")
article1_tags = {"Python", "编程", "教程", "初学者"}
article2_tags = {"Python", "高级", "性能优化"}
article3_tags = {"Java", "编程", "面向对象"}

print(f"文章1标签: {article1_tags}")
print(f"文章2标签: {article2_tags}")
print(f"文章3标签: {article3_tags}")

# 找到相关文章（有共同标签）
common_tags_1_2 = article1_tags & article2_tags
common_tags_1_3 = article1_tags & article3_tags
print(f"文章1和2的共同标签: {common_tags_1_2}")
print(f"文章1和3的共同标签: {common_tags_1_3}")

# 所有标签
all_tags = article1_tags | article2_tags | article3_tags
print(f"所有标签: {all_tags}")

# 场景4：数据分析 - 用户行为分析
print(f"\n场景4：用户行为分析")
monday_users = {1001, 1002, 1003, 1004, 1005}
tuesday_users = {1002, 1003, 1006, 1007, 1008}
wednesday_users = {1001, 1003, 1004, 1009, 1010}

print(f"周一活跃用户: {monday_users}")
print(f"周二活跃用户: {tuesday_users}")
print(f"周三活跃用户: {wednesday_users}")

# 连续活跃用户
continuous_users = monday_users & tuesday_users & wednesday_users
print(f"连续三天活跃用户: {continuous_users}")

# 流失用户（周一活跃但周二周三不活跃）
churned_users = monday_users - tuesday_users - wednesday_users
print(f"流失用户: {churned_users}")

# 新增用户（周三活跃但之前不活跃）
new_users = wednesday_users - monday_users - tuesday_users
print(f"周三新增用户: {new_users}")

# 总活跃用户
total_active = monday_users | tuesday_users | wednesday_users
print(f"三天内总活跃用户数: {len(total_active)}")

# 场景5：算法应用 - 找出两个列表的差异
print(f"\n场景5：找出两个列表的差异")
list1 = ["apple", "banana", "cherry", "date"]
list2 = ["banana", "cherry", "elderberry", "fig"]

set1 = set(list1)
set2 = set(list2)

print(f"列表1: {list1}")
print(f"列表2: {list2}")
print(f"只在列表1中: {set1 - set2}")
print(f"只在列表2中: {set2 - set1}")
print(f"两个列表共有: {set1 & set2}")
print(f"两个列表合并去重: {set1 | set2}")

# ============================================================================
# 8. 性能特点和优化
# ============================================================================

print("\n" + "=" * 50)
print("8. 性能特点和优化")
print("=" * 50)

import time
import sys

# 创建测试数据
large_list = list(range(10000))
large_set = set(range(10000))

print(f"列表大小: {len(large_list)} 元素")
print(f"集合大小: {len(large_set)} 元素")
print(f"列表内存: {sys.getsizeof(large_list)} 字节")
print(f"集合内存: {sys.getsizeof(large_set)} 字节")

# 成员测试性能对比
def time_membership_test(container, value, iterations=1000):
    start = time.time()
    for _ in range(iterations):
        _ = value in container
    return time.time() - start

test_value = 5000
list_time = time_membership_test(large_list, test_value)
set_time = time_membership_test(large_set, test_value)

print(f"\n成员测试性能:")
print(f"列表查找耗时: {list_time:.6f}秒")
print(f"集合查找耗时: {set_time:.6f}秒")
print(f"集合比列表快: {list_time/set_time:.1f}倍")

# 去重性能对比
def time_deduplication_list(data):
    start = time.time()
    result = []
    for item in data:
        if item not in result:
            result.append(item)
    return time.time() - start, result

def time_deduplication_set(data):
    start = time.time()
    result = list(set(data))
    return time.time() - start, result

# 测试数据（包含重复）
test_data = list(range(1000)) * 3  # 3000个元素，每个数字重复3次

list_dedup_time, _ = time_deduplication_list(test_data)
set_dedup_time, _ = time_deduplication_set(test_data)

print(f"\n去重性能对比:")
print(f"列表方式耗时: {list_dedup_time:.6f}秒")
print(f"集合方式耗时: {set_dedup_time:.6f}秒")
print(f"集合比列表快: {list_dedup_time/set_dedup_time:.1f}倍")

# 时间复杂度说明
print(f"\n时间复杂度:")
print(f"- 成员测试: O(1) 平均情况")
print(f"- 添加/删除: O(1) 平均情况")
print(f"- 集合运算: O(len(s1) + len(s2))")
print(f"- 遍历: O(n)")

# ============================================================================
# 9. 常见错误和最佳实践
# ============================================================================

print("\n" + "=" * 50)
print("9. 常见错误和最佳实践")
print("=" * 50)

print("常见错误:")
print("1. 使用{}创建空集合（实际创建的是字典）")
print("2. 尝试向集合添加可变对象")
print("3. 期望集合保持元素顺序")
print("4. 混淆集合运算符的含义")

# 演示常见错误
print(f"\n错误演示:")

# 错误1：空集合创建
wrong_empty = {}
correct_empty = set()
print(f"错误的空集合: {wrong_empty}, 类型: {type(wrong_empty)}")
print(f"正确的空集合: {correct_empty}, 类型: {type(correct_empty)}")

# 错误2：添加可变对象
try:
    bad_set = {[1, 2, 3]}  # TypeError
except TypeError as e:
    print(f"错误2 - 添加列表到集合: {e}")

# 正确做法：使用不可变对象
good_set = {(1, 2, 3), "hello", 42}
print(f"正确的集合: {good_set}")

print(f"\n最佳实践:")
print("✓ 使用集合进行快速成员测试")
print("✓ 使用集合进行数据去重")
print("✓ 使用集合运算处理数据关系")
print("✓ 需要保持顺序时使用列表或OrderedDict")
print("✓ 需要不可变集合时使用frozenset")
print("✓ 集合元素必须是不可变类型")

# 性能提示
print(f"\n性能提示:")
print("- 大量成员测试时优先使用集合")
print("- 数据去重时使用set()比循环快得多")
print("- 集合运算比手动循环效率高")
print("- frozenset可以作为字典键使用")

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("集合学习完成！")
    print("=" * 50)
    print("你已经学会了:")
    print("✓ 集合的创建和特性")
    print("✓ 集合的数学运算")
    print("✓ 集合推导式")
    print("✓ frozenset的使用")
    print("✓ 集合的实际应用")
    print("✓ 性能优化技巧")
    print("\n继续学习数据结构对比吧！")