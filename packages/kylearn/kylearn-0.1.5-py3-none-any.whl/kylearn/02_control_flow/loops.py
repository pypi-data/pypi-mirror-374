"""
循环语句示例文件
演示Python中for循环和while循环的详细用法
包含循环嵌套、循环优化和迭代器、生成器的基础介绍
"""

def basic_for_loops():
    """基础for循环示例"""
    print("=== 基础for循环示例 ===")
    
    # 遍历数字范围
    print("1. 使用range()遍历数字：")
    for i in range(5):
        print(f"  数字：{i}")
    
    print("\n2. 指定起始和结束值：")
    for i in range(2, 8):
        print(f"  数字：{i}")
    
    print("\n3. 指定步长：")
    for i in range(0, 10, 2):
        print(f"  偶数：{i}")
    
    # 遍历列表
    print("\n4. 遍历列表：")
    fruits = ["苹果", "香蕉", "橙子", "葡萄"]
    for fruit in fruits:
        print(f"  水果：{fruit}")
    
    # 使用enumerate获取索引和值
    print("\n5. 使用enumerate获取索引：")
    for index, fruit in enumerate(fruits):
        print(f"  第{index}个水果：{fruit}")
    
    # 遍历字符串
    print("\n6. 遍历字符串：")
    word = "Python"
    for char in word:
        print(f"  字符：{char}")


def basic_while_loops():
    """基础while循环示例"""
    print("\n=== 基础while循环示例 ===")
    
    # 基本while循环
    print("1. 基本while循环：")
    count = 0
    while count < 5:
        print(f"  计数：{count}")
        count += 1
    
    # 条件控制的while循环
    print("\n2. 用户输入控制的循环（模拟）：")
    numbers = [1, 2, 3, 0, 4, 5]  # 模拟用户输入，0表示退出
    i = 0
    while i < len(numbers) and numbers[i] != 0:
        print(f"  输入的数字：{numbers[i]}")
        i += 1
    print("  遇到0，循环结束")
    
    # 无限循环的控制
    print("\n3. 使用break控制无限循环：")
    count = 0
    while True:
        if count >= 3:
            print("  达到限制，退出循环")
            break
        print(f"  无限循环中，计数：{count}")
        count += 1


def loop_control_statements():
    """循环控制语句示例"""
    print("\n=== 循环控制语句示例 ===")
    
    # break语句
    print("1. break语句 - 跳出循环：")
    for i in range(10):
        if i == 5:
            print(f"  遇到{i}，跳出循环")
            break
        print(f"  数字：{i}")
    
    # continue语句
    print("\n2. continue语句 - 跳过当前迭代：")
    for i in range(10):
        if i % 2 == 0:
            continue  # 跳过偶数
        print(f"  奇数：{i}")
    
    # else子句
    print("\n3. for-else语句：")
    numbers = [1, 3, 5, 7, 9]
    for num in numbers:
        if num % 2 == 0:
            print(f"  找到偶数：{num}")
            break
    else:
        print("  没有找到偶数")
    
    print("\n4. while-else语句：")
    count = 0
    while count < 3:
        print(f"  计数：{count}")
        count += 1
    else:
        print("  while循环正常结束")


def nested_loops():
    """嵌套循环示例"""
    print("\n=== 嵌套循环示例 ===")
    
    # 基本嵌套循环
    print("1. 九九乘法表：")
    for i in range(1, 4):  # 只显示前3行
        for j in range(1, 4):  # 只显示前3列
            result = i * j
            print(f"{i}×{j}={result:2d}", end="  ")
        print()  # 换行
    
    # 嵌套循环处理二维数据
    print("\n2. 处理二维列表：")
    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    
    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            print(f"  位置({row_index},{col_index})：{value}")
    
    # 嵌套循环中的控制语句
    print("\n3. 嵌套循环中的break和continue：")
    for i in range(3):
        print(f"  外层循环：{i}")
        for j in range(5):
            if j == 2:
                print(f"    内层跳过：{j}")
                continue
            if j == 4:
                print(f"    内层中断：{j}")
                break
            print(f"    内层循环：{j}")


def advanced_iteration():
    """高级迭代技巧"""
    print("\n=== 高级迭代技巧 ===")
    
    # zip函数
    print("1. 使用zip同时遍历多个序列：")
    names = ["张三", "李四", "王五"]
    ages = [25, 30, 35]
    cities = ["北京", "上海", "广州"]
    
    for name, age, city in zip(names, ages, cities):
        print(f"  {name}，{age}岁，来自{city}")
    
    # reversed函数
    print("\n2. 使用reversed反向遍历：")
    numbers = [1, 2, 3, 4, 5]
    for num in reversed(numbers):
        print(f"  反向数字：{num}")
    
    # sorted函数
    print("\n3. 使用sorted排序遍历：")
    words = ["python", "java", "c++", "go"]
    for word in sorted(words):
        print(f"  排序后：{word}")
    
    # 字典遍历
    print("\n4. 字典的不同遍历方式：")
    student = {"姓名": "张三", "年龄": 20, "专业": "计算机"}
    
    print("  遍历键：")
    for key in student:
        print(f"    {key}")
    
    print("  遍历值：")
    for value in student.values():
        print(f"    {value}")
    
    print("  遍历键值对：")
    for key, value in student.items():
        print(f"    {key}: {value}")


def iterators_and_generators():
    """迭代器和生成器基础介绍"""
    print("\n=== 迭代器和生成器基础 ===")
    
    # 迭代器概念
    print("1. 迭代器概念：")
    my_list = [1, 2, 3, 4, 5]
    my_iter = iter(my_list)
    
    print("  使用next()函数：")
    try:
        print(f"    第一个元素：{next(my_iter)}")
        print(f"    第二个元素：{next(my_iter)}")
        print(f"    第三个元素：{next(my_iter)}")
    except StopIteration:
        print("    迭代器已耗尽")
    
    # 简单生成器
    print("\n2. 生成器函数：")
    def count_up_to(max_count):
        """生成从1到max_count的数字"""
        count = 1
        while count <= max_count:
            yield count
            count += 1
    
    print("  使用生成器：")
    for num in count_up_to(5):
        print(f"    生成的数字：{num}")
    
    # 生成器表达式
    print("\n3. 生成器表达式：")
    squares = (x**2 for x in range(1, 6))
    print("  平方数生成器：")
    for square in squares:
        print(f"    平方数：{square}")
    
    # 生成器的内存优势
    print("\n4. 生成器vs列表（内存效率）：")
    
    def fibonacci_generator(n):
        """斐波那契数列生成器"""
        a, b = 0, 1
        count = 0
        while count < n:
            yield a
            a, b = b, a + b
            count += 1
    
    print("  斐波那契数列（前10项）：")
    for fib in fibonacci_generator(10):
        print(f"    {fib}", end=" ")
    print()


def loop_optimization():
    """循环优化技巧"""
    print("\n=== 循环优化技巧 ===")
    
    # 避免重复计算
    print("1. 避免重复计算：")
    
    # 不好的写法
    def bad_example():
        numbers = list(range(1000))
        result = []
        for i in range(len(numbers)):
            if numbers[i] % 2 == 0:
                result.append(numbers[i] ** 2)
        return result
    
    # 好的写法
    def good_example():
        numbers = list(range(1000))
        return [num ** 2 for num in numbers if num % 2 == 0]
    
    print("  使用列表推导式更高效")
    
    # 使用内置函数
    print("\n2. 使用内置函数：")
    numbers = [1, 2, 3, 4, 5]
    
    # 计算总和
    total = sum(numbers)
    print(f"  总和：{total}")
    
    # 查找最大值
    maximum = max(numbers)
    print(f"  最大值：{maximum}")
    
    # 检查条件
    has_even = any(num % 2 == 0 for num in numbers)
    print(f"  包含偶数：{has_even}")
    
    all_positive = all(num > 0 for num in numbers)
    print(f"  全部为正数：{all_positive}")


def practical_examples():
    """实际应用示例"""
    print("\n=== 实际应用示例 ===")
    
    # 数据处理
    print("1. 学生成绩统计：")
    students = [
        {"name": "张三", "scores": [85, 90, 78]},
        {"name": "李四", "scores": [92, 88, 95]},
        {"name": "王五", "scores": [76, 82, 80]}
    ]
    
    for student in students:
        name = student["name"]
        scores = student["scores"]
        average = sum(scores) / len(scores)
        print(f"  {name}的平均分：{average:.1f}")
    
    # 文本处理
    print("\n2. 单词统计：")
    text = "python is great python is fun python is powerful"
    words = text.split()
    word_count = {}
    
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    
    for word, count in word_count.items():
        print(f"  '{word}': {count}次")
    
    # 数据验证
    print("\n3. 输入验证循环：")
    valid_inputs = ["yes", "no", "y", "n"]
    test_inputs = ["yes", "maybe", "no", "invalid", "y"]  # 模拟用户输入
    
    for user_input in test_inputs:
        if user_input.lower() in valid_inputs:
            print(f"  输入'{user_input}'有效")
            break
        else:
            print(f"  输入'{user_input}'无效，请重新输入")
    else:
        print("  没有找到有效输入")


def common_mistakes():
    """常见错误和最佳实践"""
    print("\n=== 常见错误和最佳实践 ===")
    
    # 错误1：在循环中修改列表
    print("1. 避免在循环中修改正在遍历的列表：")
    
    # 错误的做法
    numbers = [1, 2, 3, 4, 5, 6]
    print(f"  原始列表：{numbers}")
    
    # 正确的做法：使用切片创建副本
    numbers_copy = numbers[:]
    for num in numbers_copy:
        if num % 2 == 0:
            numbers.remove(num)
    print(f"  删除偶数后：{numbers}")
    
    # 错误2：无限循环
    print("\n2. 避免无限循环：")
    print("  确保循环条件会在某个时候变为False")
    print("  使用计数器或其他机制防止无限循环")
    
    # 最佳实践：使用合适的循环类型
    print("\n3. 选择合适的循环类型：")
    print("  - 已知迭代次数：使用for循环")
    print("  - 基于条件循环：使用while循环")
    print("  - 遍历序列：使用for循环")
    
    # 性能考虑
    print("\n4. 性能优化建议：")
    print("  - 避免在循环内进行重复计算")
    print("  - 使用列表推导式替代简单的for循环")
    print("  - 考虑使用生成器处理大量数据")
    print("  - 利用内置函数（sum, max, min, any, all等）")


if __name__ == "__main__":
    """运行所有示例"""
    print("Python循环语句完整示例")
    print("=" * 50)
    
    basic_for_loops()
    basic_while_loops()
    loop_control_statements()
    nested_loops()
    advanced_iteration()
    iterators_and_generators()
    loop_optimization()
    practical_examples()
    common_mistakes()
    
    print("\n" + "=" * 50)
    print("循环语句学习完成！")
    print("下一步：学习流程控制（flow_control.py）")