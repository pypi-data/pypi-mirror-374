"""
控制流程练习文件
包含条件语句、循环语句和流程控制的渐进式练习题
提供实际问题解决的综合练习和答案解析
"""

def exercise_1_basic_conditions():
    """练习1：基础条件判断"""
    print("=== 练习1：基础条件判断 ===")
    print("题目：编写函数判断一个数字的性质")
    
    def analyze_number(num):
        """
        分析数字的性质
        要求：判断数字是正数、负数还是零，以及是否为偶数
        """
        # 学生练习区域 - 请完成以下代码
        result = []
        
        # 判断正负性
        if num > 0:
            result.append("正数")
        elif num < 0:
            result.append("负数")
        else:
            result.append("零")
        
        # 判断奇偶性（零被认为是偶数）
        if num % 2 == 0:
            result.append("偶数")
        else:
            result.append("奇数")
        
        return result
    
    # 测试用例
    test_numbers = [5, -3, 0, 8, -2]
    print("测试结果：")
    for num in test_numbers:
        properties = analyze_number(num)
        print(f"  数字 {num}: {', '.join(properties)}")
    
    print("\n解题思路：")
    print("1. 使用if-elif-else判断正负性")
    print("2. 使用模运算符%判断奇偶性")
    print("3. 注意零的特殊情况处理")


def exercise_2_grade_system():
    """练习2：成绩等级系统"""
    print("\n=== 练习2：成绩等级系统 ===")
    print("题目：实现一个完整的成绩评级系统")
    
    def get_grade_info(score):
        """
        根据分数返回等级和评语
        等级标准：A(90-100), B(80-89), C(70-79), D(60-69), F(0-59)
        """
        # 输入验证
        if not isinstance(score, (int, float)):
            return "错误", "分数必须是数字"
        
        if score < 0 or score > 100:
            return "错误", "分数必须在0-100之间"
        
        # 等级判定
        if score >= 90:
            grade = "A"
            comment = "优秀"
        elif score >= 80:
            grade = "B"
            comment = "良好"
        elif score >= 70:
            grade = "C"
            comment = "中等"
        elif score >= 60:
            grade = "D"
            comment = "及格"
        else:
            grade = "F"
            comment = "不及格"
        
        return grade, comment
    
    # 测试用例
    test_scores = [95, 85, 75, 65, 45, 105, -10, "abc"]
    print("测试结果：")
    for score in test_scores:
        grade, comment = get_grade_info(score)
        print(f"  分数 {score}: 等级 {grade}, 评语 {comment}")
    
    print("\n解题思路：")
    print("1. 首先进行输入验证")
    print("2. 使用if-elif链进行等级判定")
    print("3. 返回等级和对应评语")


def exercise_3_basic_loops():
    """练习3：基础循环练习"""
    print("\n=== 练习3：基础循环练习 ===")
    print("题目：使用循环解决数学问题")
    
    def calculate_factorial(n):
        """计算n的阶乘"""
        if n < 0:
            return None
        
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    
    def sum_even_numbers(start, end):
        """计算指定范围内偶数的和"""
        total = 0
        for num in range(start, end + 1):
            if num % 2 == 0:
                total += num
        return total
    
    def fibonacci_sequence(n):
        """生成斐波那契数列的前n项"""
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        elif n == 2:
            return [0, 1]
        
        sequence = [0, 1]
        for i in range(2, n):
            next_num = sequence[i-1] + sequence[i-2]
            sequence.append(next_num)
        
        return sequence
    
    # 测试阶乘
    print("阶乘计算：")
    for n in [0, 1, 5, 7]:
        result = calculate_factorial(n)
        print(f"  {n}! = {result}")
    
    # 测试偶数和
    print("\n偶数和计算：")
    result = sum_even_numbers(1, 10)
    print(f"  1到10之间偶数的和: {result}")
    
    # 测试斐波那契数列
    print("\n斐波那契数列：")
    fib_seq = fibonacci_sequence(10)
    print(f"  前10项: {fib_seq}")
    
    print("\n解题思路：")
    print("1. 阶乘：使用for循环累乘")
    print("2. 偶数和：循环中使用条件判断")
    print("3. 斐波那契：维护前两项，循环计算后续项")


def exercise_4_nested_loops():
    """练习4：嵌套循环练习"""
    print("\n=== 练习4：嵌套循环练习 ===")
    print("题目：使用嵌套循环处理二维问题")
    
    def print_multiplication_table(size):
        """打印乘法表"""
        print(f"  {size}x{size}乘法表：")
        for i in range(1, size + 1):
            for j in range(1, size + 1):
                product = i * j
                print(f"{product:4d}", end="")
            print()  # 换行
    
    def find_prime_numbers(limit):
        """使用埃拉托斯特尼筛法找质数"""
        if limit < 2:
            return []
        
        # 初始化筛子
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        
        # 筛选过程
        for i in range(2, int(limit**0.5) + 1):
            if is_prime[i]:
                # 标记i的倍数为非质数
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        
        # 收集质数
        primes = []
        for i in range(2, limit + 1):
            if is_prime[i]:
                primes.append(i)
        
        return primes
    
    def matrix_transpose(matrix):
        """矩阵转置"""
        if not matrix or not matrix[0]:
            return []
        
        rows = len(matrix)
        cols = len(matrix[0])
        
        # 创建转置矩阵
        transposed = []
        for j in range(cols):
            new_row = []
            for i in range(rows):
                new_row.append(matrix[i][j])
            transposed.append(new_row)
        
        return transposed
    
    # 测试乘法表
    print_multiplication_table(5)
    
    # 测试质数查找
    print("\n质数查找：")
    primes = find_prime_numbers(30)
    print(f"  30以内的质数: {primes}")
    
    # 测试矩阵转置
    print("\n矩阵转置：")
    original_matrix = [[1, 2, 3], [4, 5, 6]]
    transposed_matrix = matrix_transpose(original_matrix)
    print(f"  原矩阵: {original_matrix}")
    print(f"  转置后: {transposed_matrix}")
    
    print("\n解题思路：")
    print("1. 乘法表：双重循环，外层控制行，内层控制列")
    print("2. 质数筛选：外层遍历候选数，内层标记倍数")
    print("3. 矩阵转置：交换行列索引")


def exercise_5_loop_control():
    """练习5：循环控制练习"""
    print("\n=== 练习5：循环控制练习 ===")
    print("题目：使用break、continue优化循环")
    
    def find_first_duplicate(numbers):
        """找到列表中第一个重复的数字"""
        seen = set()
        
        for num in numbers:
            if num in seen:
                return num  # 找到第一个重复数字，直接返回
            seen.add(num)
        
        return None  # 没有重复数字
    
    def process_valid_numbers(numbers):
        """处理有效数字，跳过无效值"""
        valid_numbers = []
        
        for item in numbers:
            # 跳过非数字类型
            if not isinstance(item, (int, float)):
                continue
            
            # 跳过负数
            if item < 0:
                continue
            
            # 如果遇到0，停止处理
            if item == 0:
                break
            
            valid_numbers.append(item)
        
        return valid_numbers
    
    def search_in_matrix(matrix, target):
        """在二维矩阵中搜索目标值"""
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if value == target:
                    return (i, j)  # 找到目标，返回位置
        
        return None  # 未找到
    
    # 测试重复数字查找
    print("查找重复数字：")
    test_lists = [
        [1, 2, 3, 4, 2, 5],
        [1, 2, 3, 4, 5],
        [5, 5, 1, 2, 3]
    ]
    
    for test_list in test_lists:
        duplicate = find_first_duplicate(test_list)
        print(f"  列表 {test_list}: 第一个重复数字 {duplicate}")
    
    # 测试有效数字处理
    print("\n处理有效数字：")
    mixed_data = [1, -2, 3.5, "abc", 4, 0, 5, 6]
    valid_nums = process_valid_numbers(mixed_data)
    print(f"  原数据: {mixed_data}")
    print(f"  有效数字: {valid_nums}")
    
    # 测试矩阵搜索
    print("\n矩阵搜索：")
    test_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    targets = [5, 10]
    
    for target in targets:
        position = search_in_matrix(test_matrix, target)
        if position:
            print(f"  数字 {target} 在位置 {position}")
        else:
            print(f"  数字 {target} 未找到")
    
    print("\n解题思路：")
    print("1. 使用break在找到结果时立即退出")
    print("2. 使用continue跳过不符合条件的项")
    print("3. 合理使用控制语句提高效率")


def exercise_6_while_loops():
    """练习6：while循环练习"""
    print("\n=== 练习6：while循环练习 ===")
    print("题目：使用while循环解决问题")
    
    def guess_number_game():
        """猜数字游戏（模拟版）"""
        import random
        
        target = random.randint(1, 100)
        guesses = [50, 75, 88, 92, 90, 91]  # 模拟用户猜测
        attempts = 0
        max_attempts = len(guesses)
        
        print(f"  猜数字游戏开始！数字在1-100之间")
        print(f"  （目标数字是 {target}，这里显示是为了演示）")
        
        while attempts < max_attempts:
            guess = guesses[attempts]
            attempts += 1
            
            print(f"  第{attempts}次猜测: {guess}")
            
            if guess == target:
                print(f"  恭喜！你在第{attempts}次猜中了！")
                break
            elif guess < target:
                print(f"  太小了！")
            else:
                print(f"  太大了！")
        else:
            print(f"  游戏结束！正确答案是 {target}")
    
    def calculate_gcd(a, b):
        """使用欧几里得算法计算最大公约数"""
        print(f"  计算 {a} 和 {b} 的最大公约数：")
        
        original_a, original_b = a, b
        
        while b != 0:
            print(f"    {a} = {a//b} × {b} + {a%b}")
            a, b = b, a % b
        
        print(f"  最大公约数是: {a}")
        return a
    
    def collatz_sequence(n):
        """计算考拉兹猜想序列"""
        print(f"  考拉兹序列（起始数字 {n}）：")
        
        sequence = [n]
        steps = 0
        
        while n != 1:
            if n % 2 == 0:
                n = n // 2
            else:
                n = 3 * n + 1
            
            sequence.append(n)
            steps += 1
            
            # 防止序列过长，限制显示
            if steps > 20:
                sequence.append("...")
                break
        
        print(f"    序列: {sequence}")
        print(f"    步数: {steps}")
        return sequence
    
    # 测试猜数字游戏
    guess_number_game()
    
    # 测试最大公约数
    print("\n最大公约数计算：")
    calculate_gcd(48, 18)
    
    # 测试考拉兹序列
    print("\n考拉兹序列：")
    collatz_sequence(7)
    
    print("\n解题思路：")
    print("1. 猜数字：使用while循环直到猜中或达到最大次数")
    print("2. 最大公约数：欧几里得算法的while实现")
    print("3. 考拉兹序列：按规则迭代直到达到1")


def exercise_7_comprehensive():
    """练习7：综合应用练习"""
    print("\n=== 练习7：综合应用练习 ===")
    print("题目：文本处理和数据分析")
    
    def analyze_text(text):
        """文本分析：统计字符、单词、行数等"""
        if not text:
            return {"chars": 0, "words": 0, "lines": 0, "sentences": 0}
        
        # 字符统计
        char_count = len(text)
        
        # 单词统计
        words = text.split()
        word_count = len(words)
        
        # 行数统计
        lines = text.split('\n')
        line_count = len(lines)
        
        # 句子统计（简单版本，以句号、问号、感叹号结尾）
        sentence_count = 0
        for char in text:
            if char in '.!?':
                sentence_count += 1
        
        return {
            "chars": char_count,
            "words": word_count,
            "lines": line_count,
            "sentences": sentence_count
        }
    
    def find_common_elements(list1, list2):
        """找到两个列表的公共元素"""
        common = []
        
        for item in list1:
            if item in list2 and item not in common:
                common.append(item)
        
        return common
    
    def validate_password(password):
        """密码强度验证"""
        if len(password) < 8:
            return False, "密码长度至少8位"
        
        has_upper = False
        has_lower = False
        has_digit = False
        has_special = False
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        for char in password:
            if char.isupper():
                has_upper = True
            elif char.islower():
                has_lower = True
            elif char.isdigit():
                has_digit = True
            elif char in special_chars:
                has_special = True
        
        missing = []
        if not has_upper:
            missing.append("大写字母")
        if not has_lower:
            missing.append("小写字母")
        if not has_digit:
            missing.append("数字")
        if not has_special:
            missing.append("特殊字符")
        
        if missing:
            return False, f"缺少: {', '.join(missing)}"
        
        return True, "密码强度良好"
    
    # 测试文本分析
    print("文本分析：")
    sample_text = """Python是一种高级编程语言。
它简单易学，功能强大！
你喜欢Python吗？"""
    
    stats = analyze_text(sample_text)
    print(f"  文本: {repr(sample_text)}")
    print(f"  统计: {stats}")
    
    # 测试公共元素查找
    print("\n公共元素查找：")
    list_a = [1, 2, 3, 4, 5]
    list_b = [3, 4, 5, 6, 7]
    common = find_common_elements(list_a, list_b)
    print(f"  列表A: {list_a}")
    print(f"  列表B: {list_b}")
    print(f"  公共元素: {common}")
    
    # 测试密码验证
    print("\n密码强度验证：")
    test_passwords = [
        "123456",
        "password",
        "Password123",
        "P@ssw0rd123"
    ]
    
    for pwd in test_passwords:
        is_valid, message = validate_password(pwd)
        status = "有效" if is_valid else "无效"
        print(f"  密码 '{pwd}': {status} - {message}")
    
    print("\n解题思路：")
    print("1. 文本分析：遍历字符串，统计不同类型的内容")
    print("2. 公共元素：嵌套循环查找，注意去重")
    print("3. 密码验证：逐字符检查，使用布尔标志记录状态")


def exercise_8_advanced():
    """练习8：高级练习"""
    print("\n=== 练习8：高级练习 ===")
    print("题目：算法实现和优化")
    
    def bubble_sort(arr):
        """冒泡排序实现"""
        n = len(arr)
        arr = arr.copy()  # 不修改原数组
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            
            # 如果没有交换，说明已经排序完成
            if not swapped:
                break
        
        return arr
    
    def binary_search(arr, target):
        """二分查找实现"""
        left, right = 0, len(arr) - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return -1  # 未找到
    
    def generate_pascal_triangle(n):
        """生成帕斯卡三角形"""
        triangle = []
        
        for i in range(n):
            row = [1]  # 每行第一个数字是1
            
            if i > 0:
                # 中间的数字是上一行相邻两数之和
                for j in range(1, i):
                    value = triangle[i-1][j-1] + triangle[i-1][j]
                    row.append(value)
                
                row.append(1)  # 每行最后一个数字是1
            
            triangle.append(row)
        
        return triangle
    
    # 测试冒泡排序
    print("冒泡排序：")
    test_array = [64, 34, 25, 12, 22, 11, 90]
    sorted_array = bubble_sort(test_array)
    print(f"  原数组: {test_array}")
    print(f"  排序后: {sorted_array}")
    
    # 测试二分查找
    print("\n二分查找：")
    sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15]
    targets = [7, 4, 15]
    
    for target in targets:
        index = binary_search(sorted_arr, target)
        if index != -1:
            print(f"  数字 {target} 在索引 {index}")
        else:
            print(f"  数字 {target} 未找到")
    
    # 测试帕斯卡三角形
    print("\n帕斯卡三角形（前6行）：")
    triangle = generate_pascal_triangle(6)
    for i, row in enumerate(triangle):
        spaces = " " * (6 - i)
        row_str = " ".join(f"{num:2d}" for num in row)
        print(f"  {spaces}{row_str}")
    
    print("\n解题思路：")
    print("1. 冒泡排序：双重循环，内层进行相邻比较和交换")
    print("2. 二分查找：在有序数组中，每次排除一半元素")
    print("3. 帕斯卡三角形：每个数字是上方两个数字之和")


def run_all_exercises():
    """运行所有练习"""
    print("Python控制流程练习集")
    print("=" * 60)
    
    exercise_1_basic_conditions()
    exercise_2_grade_system()
    exercise_3_basic_loops()
    exercise_4_nested_loops()
    exercise_5_loop_control()
    exercise_6_while_loops()
    exercise_7_comprehensive()
    exercise_8_advanced()
    
    print("\n" + "=" * 60)
    print("所有练习完成！")
    print("\n学习建议：")
    print("1. 理解每种控制结构的适用场景")
    print("2. 练习编写清晰、高效的控制流程")
    print("3. 学会选择合适的循环类型和控制语句")
    print("4. 注意边界条件和异常情况的处理")
    print("\n下一步：学习数据结构（03_data_structures）")


if __name__ == "__main__":
    run_all_exercises()