"""
Python数据结构练习题

本文件包含列表、元组、字典、集合的综合练习题，
从基础操作到实际应用场景，帮助巩固数据结构的使用。

练习分为三个难度级别：
- 基础练习：基本操作和语法
- 进阶练习：综合应用和算法
- 实战练习：真实场景问题解决
"""

# ============================================================================
# 基础练习 - 数据结构基本操作
# ============================================================================

print("=" * 60)
print("基础练习 - 数据结构基本操作")
print("=" * 60)

def exercise_1_list_operations():
    """练习1：列表基本操作"""
    print("\n练习1：列表基本操作")
    print("-" * 30)
    
    # 题目：创建一个包含1-10的列表，然后进行以下操作
    numbers = list(range(1, 11))
    print(f"原始列表: {numbers}")
    
    # 1. 添加元素11到末尾
    numbers.append(11)
    print(f"添加11后: {numbers}")
    
    # 2. 在索引5处插入元素99
    numbers.insert(5, 99)
    print(f"插入99后: {numbers}")
    
    # 3. 删除第一个出现的99
    numbers.remove(99)
    print(f"删除99后: {numbers}")
    
    # 4. 获取并删除最后一个元素
    last = numbers.pop()
    print(f"弹出最后元素{last}后: {numbers}")
    
    # 5. 反转列表
    numbers.reverse()
    print(f"反转后: {numbers}")
    
    # 6. 排序列表
    numbers.sort()
    print(f"排序后: {numbers}")
    
    return numbers

def exercise_2_tuple_operations():
    """练习2：元组操作和解包"""
    print("\n练习2：元组操作和解包")
    print("-" * 30)
    
    # 创建学生信息元组
    student = ("张三", 20, "计算机科学", 3.8)
    print(f"学生信息: {student}")
    
    # 元组解包
    name, age, major, gpa = student
    print(f"姓名: {name}, 年龄: {age}, 专业: {major}, GPA: {gpa}")
    
    # 创建坐标列表
    coordinates = [(0, 0), (1, 2), (3, 4), (5, 6)]
    print(f"坐标列表: {coordinates}")
    
    # 计算所有点到原点的距离
    distances = []
    for x, y in coordinates:
        distance = (x**2 + y**2)**0.5
        distances.append(distance)
    
    print(f"到原点距离: {distances}")
    
    return coordinates, distances

def exercise_3_dict_operations():
    """练习3：字典操作"""
    print("\n练习3：字典操作")
    print("-" * 30)
    
    # 创建学生成绩字典
    grades = {"张三": 85, "李四": 92, "王五": 78}
    print(f"原始成绩: {grades}")
    
    # 添加新学生
    grades["赵六"] = 96
    print(f"添加赵六后: {grades}")
    
    # 更新张三的成绩
    grades["张三"] = 88
    print(f"更新张三成绩后: {grades}")
    
    # 计算平均分
    average = sum(grades.values()) / len(grades)
    print(f"平均分: {average:.2f}")
    
    # 找出最高分学生
    best_student = max(grades, key=grades.get)
    print(f"最高分学生: {best_student} ({grades[best_student]}分)")
    
    # 筛选优秀学生（>=90分）
    excellent = {name: score for name, score in grades.items() if score >= 90}
    print(f"优秀学生: {excellent}")
    
    return grades

def exercise_4_set_operations():
    """练习4：集合操作"""
    print("\n练习4：集合操作")
    print("-" * 30)
    
    # 创建两个班级的学生集合
    class_a = {"张三", "李四", "王五", "赵六"}
    class_b = {"王五", "赵六", "钱七", "孙八"}
    
    print(f"A班学生: {class_a}")
    print(f"B班学生: {class_b}")
    
    # 计算集合运算
    both_classes = class_a & class_b  # 交集
    all_students = class_a | class_b  # 并集
    only_a = class_a - class_b        # 差集
    only_b = class_b - class_a        # 差集
    different = class_a ^ class_b     # 对称差集
    
    print(f"两班都有的学生: {both_classes}")
    print(f"所有学生: {all_students}")
    print(f"只在A班的学生: {only_a}")
    print(f"只在B班的学生: {only_b}")
    print(f"不在两班交集的学生: {different}")
    
    return all_students

# 运行基础练习
print("开始基础练习...")
result1 = exercise_1_list_operations()
result2 = exercise_2_tuple_operations()
result3 = exercise_3_dict_operations()
result4 = exercise_4_set_operations()

# ============================================================================
# 进阶练习 - 综合应用
# ============================================================================

print("\n" + "=" * 60)
print("进阶练习 - 综合应用")
print("=" * 60)

def exercise_5_data_analysis():
    """练习5：销售数据分析"""
    print("\n练习5：销售数据分析")
    print("-" * 30)
    
    # 销售数据
    sales_data = [
        {"product": "手机", "category": "电子", "price": 3000, "quantity": 5},
        {"product": "笔记本", "category": "电子", "price": 5000, "quantity": 3},
        {"product": "衬衫", "category": "服装", "price": 200, "quantity": 10},
        {"product": "裤子", "category": "服装", "price": 300, "quantity": 8},
        {"product": "手机", "category": "电子", "price": 3200, "quantity": 2},
    ]
    
    print("销售数据分析:")
    
    # 1. 计算总销售额
    total_revenue = sum(item["price"] * item["quantity"] for item in sales_data)
    print(f"总销售额: {total_revenue}")
    
    # 2. 按类别统计销售额
    category_revenue = {}
    for item in sales_data:
        category = item["category"]
        revenue = item["price"] * item["quantity"]
        category_revenue[category] = category_revenue.get(category, 0) + revenue
    
    print(f"按类别销售额: {category_revenue}")
    
    # 3. 找出销售额最高的产品
    product_revenue = {}
    for item in sales_data:
        product = item["product"]
        revenue = item["price"] * item["quantity"]
        product_revenue[product] = product_revenue.get(product, 0) + revenue
    
    best_product = max(product_revenue, key=product_revenue.get)
    print(f"销售额最高产品: {best_product} ({product_revenue[best_product]}元)")
    
    # 4. 计算平均单价
    total_items = sum(item["quantity"] for item in sales_data)
    avg_price = total_revenue / total_items
    print(f"平均单价: {avg_price:.2f}元")
    
    return category_revenue, product_revenue

def exercise_6_text_processing():
    """练习6：文本处理"""
    print("\n练习6：文本处理")
    print("-" * 30)
    
    text = """
    Python是一种高级编程语言。Python简单易学，功能强大。
    Python广泛应用于Web开发、数据分析、人工智能等领域。
    学习Python可以帮助你快速入门编程。
    """
    
    print("原始文本:")
    print(text.strip())
    
    # 1. 统计单词频率
    words = text.lower().replace("，", " ").replace("。", " ").split()
    word_count = {}
    for word in words:
        if word:  # 忽略空字符串
            word_count[word] = word_count.get(word, 0) + 1
    
    print(f"\n单词频率统计:")
    for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {word}: {count}")
    
    # 2. 找出唯一单词
    unique_words = set(words)
    print(f"\n唯一单词数量: {len(unique_words)}")
    print(f"唯一单词: {sorted(unique_words)}")
    
    # 3. 找出长度大于2的单词
    long_words = [word for word in unique_words if len(word) > 2]
    print(f"\n长单词(>2字符): {sorted(long_words)}")
    
    return word_count, unique_words

def exercise_7_student_management():
    """练习7：学生管理系统"""
    print("\n练习7：学生管理系统")
    print("-" * 30)
    
    # 学生数据
    students = [
        {"id": 1001, "name": "张三", "age": 20, "courses": ["数学", "物理", "化学"]},
        {"id": 1002, "name": "李四", "age": 21, "courses": ["数学", "英语", "历史"]},
        {"id": 1003, "name": "王五", "age": 19, "courses": ["物理", "化学", "生物"]},
        {"id": 1004, "name": "赵六", "age": 22, "courses": ["数学", "物理", "英语"]},
    ]
    
    print("学生管理系统分析:")
    
    # 1. 按年龄分组
    age_groups = {}
    for student in students:
        age = student["age"]
        if age not in age_groups:
            age_groups[age] = []
        age_groups[age].append(student["name"])
    
    print(f"按年龄分组: {age_groups}")
    
    # 2. 统计课程选修人数
    course_count = {}
    for student in students:
        for course in student["courses"]:
            course_count[course] = course_count.get(course, 0) + 1
    
    print(f"课程选修统计: {course_count}")
    
    # 3. 找出选修课程最多的学生
    max_courses = max(len(student["courses"]) for student in students)
    top_students = [s["name"] for s in students if len(s["courses"]) == max_courses]
    print(f"选修课程最多的学生: {top_students} ({max_courses}门)")
    
    # 4. 找出共同课程
    all_courses = [set(student["courses"]) for student in students]
    common_courses = set.intersection(*all_courses) if all_courses else set()
    print(f"所有学生的共同课程: {common_courses}")
    
    # 5. 创建课程-学生映射
    course_students = {}
    for student in students:
        for course in student["courses"]:
            if course not in course_students:
                course_students[course] = []
            course_students[course].append(student["name"])
    
    print(f"课程-学生映射:")
    for course, names in course_students.items():
        print(f"  {course}: {names}")
    
    return age_groups, course_count, course_students

# 运行进阶练习
print("开始进阶练习...")
exercise_5_data_analysis()
exercise_6_text_processing()
exercise_7_student_management()

# ============================================================================
# 实战练习 - 真实场景应用
# ============================================================================

print("\n" + "=" * 60)
print("实战练习 - 真实场景应用")
print("=" * 60)

def exercise_8_inventory_system():
    """练习8：库存管理系统"""
    print("\n练习8：库存管理系统")
    print("-" * 30)
    
    # 初始库存
    inventory = {
        "苹果": {"quantity": 100, "price": 5.0, "category": "水果"},
        "香蕉": {"quantity": 80, "price": 3.0, "category": "水果"},
        "牛奶": {"quantity": 50, "price": 12.0, "category": "乳制品"},
        "面包": {"quantity": 30, "price": 8.0, "category": "烘焙"},
    }
    
    print("库存管理系统:")
    print(f"初始库存: {inventory}")
    
    # 销售记录
    sales = [
        ("苹果", 20),
        ("香蕉", 15),
        ("牛奶", 10),
        ("苹果", 30),
        ("面包", 5),
    ]
    
    # 处理销售
    for product, sold_qty in sales:
        if product in inventory:
            inventory[product]["quantity"] -= sold_qty
            print(f"销售 {product} {sold_qty}个")
    
    print(f"销售后库存:")
    for product, info in inventory.items():
        print(f"  {product}: {info['quantity']}个, 单价: {info['price']}元")
    
    # 库存分析
    low_stock = {p: info for p, info in inventory.items() if info["quantity"] < 50}
    total_value = sum(info["quantity"] * info["price"] for info in inventory.values())
    
    print(f"低库存商品 (<50): {list(low_stock.keys())}")
    print(f"库存总价值: {total_value:.2f}元")
    
    # 按类别统计
    category_stats = {}
    for product, info in inventory.items():
        category = info["category"]
        if category not in category_stats:
            category_stats[category] = {"count": 0, "value": 0}
        category_stats[category]["count"] += info["quantity"]
        category_stats[category]["value"] += info["quantity"] * info["price"]
    
    print(f"按类别统计:")
    for category, stats in category_stats.items():
        print(f"  {category}: {stats['count']}个, 价值: {stats['value']:.2f}元")
    
    return inventory, category_stats

def exercise_9_social_network():
    """练习9：社交网络分析"""
    print("\n练习9：社交网络分析")
    print("-" * 30)
    
    # 用户关系数据
    friendships = [
        ("Alice", "Bob"),
        ("Alice", "Charlie"),
        ("Bob", "David"),
        ("Charlie", "David"),
        ("Charlie", "Eve"),
        ("David", "Eve"),
        ("Eve", "Frank"),
    ]
    
    print("社交网络分析:")
    print(f"友谊关系: {friendships}")
    
    # 构建用户网络
    network = {}
    all_users = set()
    
    for user1, user2 in friendships:
        # 添加到网络
        if user1 not in network:
            network[user1] = set()
        if user2 not in network:
            network[user2] = set()
        
        network[user1].add(user2)
        network[user2].add(user1)  # 双向关系
        
        all_users.add(user1)
        all_users.add(user2)
    
    print(f"用户网络:")
    for user, friends in network.items():
        print(f"  {user}: {friends}")
    
    # 分析网络特征
    # 1. 找出朋友最多的用户
    most_popular = max(network, key=lambda u: len(network[u]))
    print(f"最受欢迎用户: {most_popular} ({len(network[most_popular])}个朋友)")
    
    # 2. 找出共同朋友
    def find_mutual_friends(user1, user2):
        return network.get(user1, set()) & network.get(user2, set())
    
    print(f"Alice和David的共同朋友: {find_mutual_friends('Alice', 'David')}")
    
    # 3. 推荐朋友（朋友的朋友，但不是直接朋友）
    def recommend_friends(user):
        if user not in network:
            return set()
        
        direct_friends = network[user]
        friends_of_friends = set()
        
        for friend in direct_friends:
            friends_of_friends.update(network.get(friend, set()))
        
        # 排除自己和已有朋友
        recommendations = friends_of_friends - direct_friends - {user}
        return recommendations
    
    alice_recommendations = recommend_friends("Alice")
    print(f"推荐给Alice的朋友: {alice_recommendations}")
    
    # 4. 计算网络密度
    total_possible_connections = len(all_users) * (len(all_users) - 1) // 2
    actual_connections = len(friendships)
    density = actual_connections / total_possible_connections
    print(f"网络密度: {density:.2%}")
    
    return network, all_users

def exercise_10_data_cleaning():
    """练习10：数据清洗和处理"""
    print("\n练习10：数据清洗和处理")
    print("-" * 30)
    
    # 原始数据（包含各种问题）
    raw_data = [
        {"name": "  张三  ", "age": "25", "email": "zhangsan@email.com", "city": "北京"},
        {"name": "李四", "age": "", "email": "lisi@email.com", "city": "上海"},
        {"name": "王五", "age": "30", "email": "WANGWU@EMAIL.COM", "city": ""},
        {"name": "", "age": "28", "email": "invalid-email", "city": "广州"},
        {"name": "赵六", "age": "abc", "email": "zhaoliu@email.com", "city": "深圳"},
        {"name": "钱七", "age": "35", "email": "qianqi@email.com", "city": "北京"},
        {"name": "张三", "age": "25", "email": "zhangsan@email.com", "city": "北京"},  # 重复
    ]
    
    print("数据清洗处理:")
    print(f"原始数据条数: {len(raw_data)}")
    
    cleaned_data = []
    seen_records = set()  # 用于去重
    
    for record in raw_data:
        # 1. 清理姓名（去除空白）
        name = record["name"].strip()
        if not name:  # 跳过空姓名
            continue
        
        # 2. 清理年龄（转换为整数）
        age_str = record["age"].strip()
        try:
            age = int(age_str) if age_str else None
        except ValueError:
            age = None
        
        # 3. 清理邮箱（转为小写，验证格式）
        email = record["email"].strip().lower()
        if "@" not in email or "." not in email:
            email = None
        
        # 4. 清理城市
        city = record["city"].strip() if record["city"] else None
        
        # 5. 创建清理后的记录
        clean_record = {
            "name": name,
            "age": age,
            "email": email,
            "city": city
        }
        
        # 6. 去重（基于姓名和邮箱）
        record_key = (name, email)
        if record_key not in seen_records:
            seen_records.add(record_key)
            cleaned_data.append(clean_record)
    
    print(f"清洗后数据条数: {len(cleaned_data)}")
    print("清洗后的数据:")
    for i, record in enumerate(cleaned_data, 1):
        print(f"  {i}. {record}")
    
    # 数据统计
    valid_ages = [r["age"] for r in cleaned_data if r["age"] is not None]
    valid_emails = [r["email"] for r in cleaned_data if r["email"] is not None]
    cities = [r["city"] for r in cleaned_data if r["city"] is not None]
    
    print(f"\n数据质量统计:")
    print(f"有效年龄记录: {len(valid_ages)}/{len(cleaned_data)}")
    print(f"有效邮箱记录: {len(valid_emails)}/{len(cleaned_data)}")
    print(f"有效城市记录: {len(cities)}/{len(cleaned_data)}")
    
    if valid_ages:
        print(f"平均年龄: {sum(valid_ages)/len(valid_ages):.1f}岁")
    
    # 城市分布
    city_count = {}
    for city in cities:
        city_count[city] = city_count.get(city, 0) + 1
    print(f"城市分布: {city_count}")
    
    return cleaned_data, city_count

# 运行实战练习
print("开始实战练习...")
exercise_8_inventory_system()
exercise_9_social_network()
exercise_10_data_cleaning()

# ============================================================================
# 练习总结和自测
# ============================================================================

print("\n" + "=" * 60)
print("练习总结和自测")
print("=" * 60)

def self_assessment():
    """自我评估"""
    print("\n自我评估 - 请诚实回答以下问题:")
    
    questions = [
        "1. 你能熟练创建和操作列表吗？",
        "2. 你理解元组的不可变特性吗？",
        "3. 你能有效使用字典进行数据映射吗？",
        "4. 你掌握集合的数学运算吗？",
        "5. 你能根据需求选择合适的数据结构吗？",
        "6. 你理解各种数据结构的性能特点吗？",
        "7. 你能处理复杂的嵌套数据结构吗？",
        "8. 你能使用推导式简化代码吗？",
        "9. 你能进行数据结构之间的转换吗？",
        "10. 你能解决实际的数据处理问题吗？"
    ]
    
    for question in questions:
        print(f"  {question}")
    
    print(f"\n如果你对大部分问题的答案是'是'，恭喜你已经掌握了数据结构！")
    print(f"如果还有不确定的地方，建议重新学习相关章节。")

def practice_suggestions():
    """练习建议"""
    print(f"\n进一步练习建议:")
    
    suggestions = [
        "1. 尝试用不同数据结构解决同一个问题",
        "2. 分析实际项目中的数据结构选择",
        "3. 练习更复杂的嵌套数据结构操作",
        "4. 学习collections模块的高级数据结构",
        "5. 研究数据结构的内存使用和性能优化",
        "6. 实现自己的数据处理工具函数",
        "7. 参与开源项目，观察数据结构的实际应用",
        "8. 学习算法中数据结构的应用",
    ]
    
    for suggestion in suggestions:
        print(f"  {suggestion}")

def next_steps():
    """下一步学习建议"""
    print(f"\n下一步学习建议:")
    
    steps = [
        "✓ 已完成：Python数据结构基础",
        "→ 下一步：函数和模块化编程",
        "→ 进阶：面向对象编程",
        "→ 高级：异常处理和文件操作",
        "→ 实战：综合项目开发",
    ]
    
    for step in steps:
        print(f"  {step}")

# 运行总结
self_assessment()
practice_suggestions()
next_steps()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("数据结构练习完成！")
    print("=" * 60)
    print("通过这些练习，你应该已经掌握了:")
    print("✓ 列表的各种操作和应用场景")
    print("✓ 元组的特性和使用方法")
    print("✓ 字典的键值对操作和高级用法")
    print("✓ 集合的数学运算和去重功能")
    print("✓ 数据结构的选择和性能考虑")
    print("✓ 实际问题的数据结构解决方案")
    print("\n继续加油，向下一个主题进发！")