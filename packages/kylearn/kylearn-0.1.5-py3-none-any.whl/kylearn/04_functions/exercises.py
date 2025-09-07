#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python函数练习题
===============

本文件包含函数相关的练习题，涵盖：
1. 基础函数设计和实现
2. 参数传递练习
3. 返回值处理练习
4. 高级函数特性练习
5. 递归函数练习
6. 函数优化和性能测试
7. 综合应用练习

练习说明：
- 每个练习都有详细的题目描述和要求
- 提供了参考答案和解题思路
- 包含测试用例验证答案正确性
- 标注了练习难度等级
"""

import time
import functools
from typing import List, Dict, Any, Callable, Optional, Tuple
import math


# ============================================================================
# 1. 基础函数练习
# ============================================================================

def exercise_1_basic_functions():
    """
    练习1：基础函数设计
    
    难度：★☆☆☆☆
    """
    print("=== 练习1：基础函数设计 ===")
    
    # 题目1：编写一个函数，计算圆的面积
    def calculate_circle_area(radius: float) -> float:
        """
        计算圆的面积
        
        Args:
            radius: 圆的半径
        
        Returns:
            圆的面积
        """
        if radius < 0:
            raise ValueError("半径不能为负数")
        return math.pi * radius ** 2
    
    # 题目2：编写一个函数，判断一个数是否为质数
    def is_prime(n: int) -> bool:
        """
        判断一个数是否为质数
        
        Args:
            n: 要判断的数字
        
        Returns:
            是否为质数
        """
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(n)) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    # 题目3：编写一个函数，将摄氏度转换为华氏度
    def celsius_to_fahrenheit(celsius: float) -> float:
        """
        摄氏度转华氏度
        
        Args:
            celsius: 摄氏度
        
        Returns:
            华氏度
        """
        return celsius * 9/5 + 32
    
    # 测试
    print("题目1测试：")
    print(f"半径为5的圆面积: {calculate_circle_area(5):.2f}")
    
    print("\n题目2测试：")
    test_numbers = [2, 3, 4, 17, 25, 29]
    for num in test_numbers:
        print(f"{num} 是质数: {is_prime(num)}")
    
    print("\n题目3测试：")
    celsius_temps = [0, 25, 37, 100]
    for temp in celsius_temps:
        fahrenheit = celsius_to_fahrenheit(temp)
        print(f"{temp}°C = {fahrenheit}°F")


# ============================================================================
# 2. 参数传递练习
# ============================================================================

def exercise_2_parameters():
    """
    练习2：参数传递
    
    难度：★★☆☆☆
    """
    print("\n=== 练习2：参数传递 ===")
    
    # 题目1：编写一个函数，接受任意数量的数字参数，返回它们的统计信息
    def number_statistics(*numbers, **options):
        """
        计算数字统计信息
        
        Args:
            *numbers: 任意数量的数字
            **options: 选项参数
                - precision: 小数精度，默认2
                - include_median: 是否包含中位数，默认False
        
        Returns:
            dict: 统计信息字典
        """
        if not numbers:
            return {"error": "至少需要一个数字"}
        
        precision = options.get('precision', 2)
        include_median = options.get('include_median', False)
        
        sorted_numbers = sorted(numbers)
        stats = {
            "count": len(numbers),
            "sum": round(sum(numbers), precision),
            "average": round(sum(numbers) / len(numbers), precision),
            "min": min(numbers),
            "max": max(numbers)
        }
        
        if include_median:
            n = len(sorted_numbers)
            if n % 2 == 0:
                median = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
            else:
                median = sorted_numbers[n//2]
            stats["median"] = round(median, precision)
        
        return stats
    
    # 题目2：编写一个函数，创建个人档案，支持默认参数和关键字参数
    def create_profile(name: str, age: int, city: str = "未知", 
                      email: Optional[str] = None, **additional_info):
        """
        创建个人档案
        
        Args:
            name: 姓名
            age: 年龄
            city: 城市，默认"未知"
            email: 邮箱，可选
            **additional_info: 额外信息
        
        Returns:
            dict: 个人档案
        """
        profile = {
            "name": name,
            "age": age,
            "city": city
        }
        
        if email:
            profile["email"] = email
        
        # 添加额外信息
        profile.update(additional_info)
        
        return profile
    
    # 题目3：编写一个函数，实现灵活的字符串格式化
    def flexible_format(template: str, *args, **kwargs):
        """
        灵活的字符串格式化
        
        Args:
            template: 模板字符串
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            str: 格式化后的字符串
        """
        try:
            # 先尝试使用关键字参数格式化
            if kwargs:
                return template.format(**kwargs)
            # 再尝试使用位置参数格式化
            elif args:
                return template.format(*args)
            else:
                return template
        except (KeyError, IndexError) as e:
            return f"格式化错误: {e}"
    
    # 测试
    print("题目1测试：")
    stats1 = number_statistics(1, 2, 3, 4, 5, precision=3)
    print(f"基础统计: {stats1}")
    
    stats2 = number_statistics(10, 20, 30, 40, 50, include_median=True)
    print(f"包含中位数: {stats2}")
    
    print("\n题目2测试：")
    profile1 = create_profile("张三", 25)
    print(f"基础档案: {profile1}")
    
    profile2 = create_profile("李四", 30, "北京", "li@example.com", 
                             phone="13800138000", occupation="工程师")
    print(f"完整档案: {profile2}")
    
    print("\n题目3测试：")
    result1 = flexible_format("你好，{name}！", name="世界")
    print(f"关键字格式化: {result1}")
    
    result2 = flexible_format("数字：{0}, {1}, {2}", 1, 2, 3)
    print(f"位置格式化: {result2}")


# ============================================================================
# 3. 返回值练习
# ============================================================================

def exercise_3_return_values():
    """
    练习3：返回值处理
    
    难度：★★☆☆☆
    """
    print("\n=== 练习3：返回值处理 ===")
    
    # 题目1：编写一个函数，返回多个计算结果
    def math_operations(a: float, b: float) -> Tuple[float, float, float, Optional[float]]:
        """
        执行多种数学运算
        
        Args:
            a: 第一个数
            b: 第二个数
        
        Returns:
            tuple: (加法, 减法, 乘法, 除法)
        """
        addition = a + b
        subtraction = a - b
        multiplication = a * b
        division = a / b if b != 0 else None
        
        return addition, subtraction, multiplication, division
    
    # 题目2：编写一个函数，根据条件返回不同类型的结果
    def process_data(data: Any, operation: str):
        """
        根据操作类型处理数据
        
        Args:
            data: 输入数据
            operation: 操作类型
        
        Returns:
            处理结果，类型根据操作而定
        """
        if operation == "length":
            try:
                return len(data)
            except TypeError:
                return "无法计算长度"
        
        elif operation == "type":
            return type(data).__name__
        
        elif operation == "string":
            return str(data)
        
        elif operation == "reverse":
            try:
                if isinstance(data, str):
                    return data[::-1]
                elif isinstance(data, list):
                    return data[::-1]
                else:
                    return "无法反转"
            except:
                return "反转失败"
        
        else:
            return f"未知操作: {operation}"
    
    # 题目3：编写一个函数，返回带状态的结果
    def validate_and_process(value: str) -> Dict[str, Any]:
        """
        验证并处理输入值
        
        Args:
            value: 输入字符串
        
        Returns:
            dict: 包含验证状态和处理结果的字典
        """
        result = {
            "original": value,
            "valid": False,
            "errors": [],
            "processed": None
        }
        
        # 验证非空
        if not value or not value.strip():
            result["errors"].append("输入不能为空")
            return result
        
        # 验证长度
        if len(value.strip()) < 2:
            result["errors"].append("输入长度至少为2个字符")
        
        # 验证字符类型
        cleaned_value = value.strip()
        if not cleaned_value.replace(" ", "").isalnum():
            result["errors"].append("只能包含字母、数字和空格")
        
        # 如果没有错误，标记为有效并处理
        if not result["errors"]:
            result["valid"] = True
            result["processed"] = {
                "cleaned": cleaned_value,
                "uppercase": cleaned_value.upper(),
                "lowercase": cleaned_value.lower(),
                "word_count": len(cleaned_value.split())
            }
        
        return result
    
    # 测试
    print("题目1测试：")
    add_result, sub_result, mul_result, div_result = math_operations(10, 3)
    print(f"10和3的运算结果:")
    print(f"  加法: {add_result}")
    print(f"  减法: {sub_result}")
    print(f"  乘法: {mul_result}")
    print(f"  除法: {div_result}")
    
    print("\n题目2测试：")
    test_data = ["hello", [1, 2, 3], 42, {"key": "value"}]
    operations = ["length", "type", "string", "reverse"]
    
    for data in test_data:
        print(f"数据: {data}")
        for op in operations:
            result = process_data(data, op)
            print(f"  {op}: {result}")
    
    print("\n题目3测试：")
    test_inputs = ["", "a", "hello world", "hello123", "hello@world"]
    for input_val in test_inputs:
        result = validate_and_process(input_val)
        print(f"输入: '{input_val}'")
        print(f"  有效: {result['valid']}")
        if result['errors']:
            print(f"  错误: {result['errors']}")
        if result['processed']:
            print(f"  处理结果: {result['processed']}")


# ============================================================================
# 4. 高级函数特性练习
# ============================================================================

def exercise_4_advanced_features():
    """
    练习4：高级函数特性
    
    难度：★★★☆☆
    """
    print("\n=== 练习4：高级函数特性 ===")
    
    # 题目1：实现一个缓存装饰器
    def memoize(func):
        """
        缓存装饰器
        """
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
                print(f"计算并缓存: {func.__name__}{args}")
            else:
                print(f"从缓存获取: {func.__name__}{args}")
            return cache[key]
        
        wrapper.cache = cache  # 暴露缓存以便检查
        return wrapper
    
    # 题目2：实现一个计时装饰器
    def timer(func):
        """
        计时装饰器
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{func.__name__} 执行时间: {end_time - start_time:.4f}秒")
            return result
        return wrapper
    
    # 题目3：实现一个闭包计数器工厂
    def create_counter_with_step(initial=0, step=1):
        """
        创建带步长的计数器
        
        Args:
            initial: 初始值
            step: 步长
        
        Returns:
            tuple: (计数函数, 获取当前值函数, 重置函数)
        """
        current = initial
        
        def count():
            nonlocal current
            current += step
            return current
        
        def get_current():
            return current
        
        def reset(new_initial=None):
            nonlocal current
            current = new_initial if new_initial is not None else initial
        
        return count, get_current, reset
    
    # 题目4：实现函数组合器
    def compose(*functions):
        """
        函数组合器
        
        Args:
            *functions: 要组合的函数
        
        Returns:
            function: 组合后的函数
        """
        def composed(x):
            result = x
            for func in reversed(functions):
                result = func(result)
            return result
        return composed
    
    # 使用装饰器的示例函数
    @memoize
    @timer
    def expensive_calculation(n):
        """
        模拟耗时计算
        """
        time.sleep(0.1)  # 模拟计算时间
        return sum(range(n))
    
    # 测试
    print("题目1&2测试（缓存和计时装饰器）：")
    result1 = expensive_calculation(100)
    print(f"第一次计算结果: {result1}")
    
    result2 = expensive_calculation(100)  # 应该从缓存获取
    print(f"第二次计算结果: {result2}")
    
    print("\n题目3测试（闭包计数器）：")
    counter, get_value, reset = create_counter_with_step(10, 5)
    print(f"初始值: {get_value()}")
    print(f"计数1: {counter()}")
    print(f"计数2: {counter()}")
    print(f"计数3: {counter()}")
    reset(0)
    print(f"重置后: {get_value()}")
    print(f"重置后计数: {counter()}")
    
    print("\n题目4测试（函数组合）：")
    add_one = lambda x: x + 1
    multiply_by_two = lambda x: x * 2
    square = lambda x: x ** 2
    
    # 组合函数: square(multiply_by_two(add_one(x)))
    composed_func = compose(square, multiply_by_two, add_one)
    result = composed_func(3)  # (3+1)*2 = 8, 8^2 = 64
    print(f"函数组合 compose(square, multiply_by_two, add_one)(3) = {result}")


# ============================================================================
# 5. 递归函数练习
# ============================================================================

def exercise_5_recursion():
    """
    练习5：递归函数
    
    难度：★★★☆☆
    """
    print("\n=== 练习5：递归函数 ===")
    
    # 题目1：实现阶乘函数
    def factorial(n: int) -> int:
        """
        计算阶乘（递归实现）
        
        Args:
            n: 非负整数
        
        Returns:
            n的阶乘
        """
        if n < 0:
            raise ValueError("阶乘只能计算非负整数")
        if n == 0 or n == 1:
            return 1
        return n * factorial(n - 1)
    
    # 题目2：实现斐波那契数列（带记忆化）
    def fibonacci_memo(n: int, memo: Dict[int, int] = None) -> int:
        """
        计算斐波那契数列（记忆化递归）
        
        Args:
            n: 位置索引
            memo: 记忆化字典
        
        Returns:
            第n个斐波那契数
        """
        if memo is None:
            memo = {}
        
        if n in memo:
            return memo[n]
        
        if n <= 1:
            return n
        
        memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
        return memo[n]
    
    # 题目3：实现二叉树遍历
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right
    
    def tree_traversal(root: Optional[TreeNode], order: str = "inorder") -> List[int]:
        """
        二叉树遍历
        
        Args:
            root: 树根节点
            order: 遍历顺序 ("preorder", "inorder", "postorder")
        
        Returns:
            遍历结果列表
        """
        if not root:
            return []
        
        if order == "preorder":
            return [root.val] + tree_traversal(root.left, order) + tree_traversal(root.right, order)
        elif order == "inorder":
            return tree_traversal(root.left, order) + [root.val] + tree_traversal(root.right, order)
        elif order == "postorder":
            return tree_traversal(root.left, order) + tree_traversal(root.right, order) + [root.val]
        else:
            raise ValueError("不支持的遍历顺序")
    
    # 题目4：实现汉诺塔问题
    def hanoi_tower(n: int, source: str, target: str, auxiliary: str) -> List[str]:
        """
        汉诺塔问题求解
        
        Args:
            n: 盘子数量
            source: 源柱子
            target: 目标柱子
            auxiliary: 辅助柱子
        
        Returns:
            移动步骤列表
        """
        if n == 1:
            return [f"移动盘子从 {source} 到 {target}"]
        
        steps = []
        # 将前n-1个盘子从源柱移到辅助柱
        steps.extend(hanoi_tower(n - 1, source, auxiliary, target))
        # 将最大的盘子从源柱移到目标柱
        steps.append(f"移动盘子从 {source} 到 {target}")
        # 将n-1个盘子从辅助柱移到目标柱
        steps.extend(hanoi_tower(n - 1, auxiliary, target, source))
        
        return steps
    
    # 测试
    print("题目1测试（阶乘）：")
    for i in range(6):
        print(f"{i}! = {factorial(i)}")
    
    print("\n题目2测试（斐波那契）：")
    for i in range(10):
        print(f"fib({i}) = {fibonacci_memo(i)}")
    
    print("\n题目3测试（二叉树遍历）：")
    # 构建测试树:     1
    #              /   \
    #             2     3
    #            / \
    #           4   5
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    
    print(f"前序遍历: {tree_traversal(root, 'preorder')}")
    print(f"中序遍历: {tree_traversal(root, 'inorder')}")
    print(f"后序遍历: {tree_traversal(root, 'postorder')}")
    
    print("\n题目4测试（汉诺塔）：")
    steps = hanoi_tower(3, "A", "C", "B")
    print("3个盘子的汉诺塔解法：")
    for i, step in enumerate(steps, 1):
        print(f"步骤{i}: {step}")


# ============================================================================
# 6. 函数优化和性能测试
# ============================================================================

def exercise_6_optimization():
    """
    练习6：函数优化和性能测试
    
    难度：★★★★☆
    """
    print("\n=== 练习6：函数优化和性能测试 ===")
    
    # 题目1：比较不同实现的性能
    def performance_comparison():
        """
        性能比较示例
        """
        # 方法1：普通循环求和
        def sum_loop(n):
            total = 0
            for i in range(1, n + 1):
                total += i
            return total
        
        # 方法2：使用内置sum函数
        def sum_builtin(n):
            return sum(range(1, n + 1))
        
        # 方法3：数学公式
        def sum_formula(n):
            return n * (n + 1) // 2
        
        # 性能测试
        n = 100000
        functions = [
            ("循环求和", sum_loop),
            ("内置sum", sum_builtin),
            ("数学公式", sum_formula)
        ]
        
        print("性能比较（计算1到100000的和）：")
        for name, func in functions:
            start_time = time.time()
            result = func(n)
            end_time = time.time()
            print(f"{name}: 结果={result}, 时间={end_time - start_time:.6f}秒")
    
    # 题目2：实现一个性能分析装饰器
    def profile(func):
        """
        性能分析装饰器
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import sys
            
            # 记录调用信息
            start_time = time.time()
            start_memory = sys.getsizeof(args) + sys.getsizeof(kwargs)
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = sys.getsizeof(result)
            
            print(f"函数 {func.__name__} 性能分析:")
            print(f"  执行时间: {end_time - start_time:.6f}秒")
            print(f"  输入内存: {start_memory}字节")
            print(f"  输出内存: {end_memory}字节")
            
            return result
        return wrapper
    
    # 题目3：实现缓存大小限制的装饰器
    def lru_cache(maxsize=128):
        """
        LRU缓存装饰器
        
        Args:
            maxsize: 最大缓存大小
        """
        def decorator(func):
            cache = {}
            access_order = []
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = str(args) + str(sorted(kwargs.items()))
                
                if key in cache:
                    # 更新访问顺序
                    access_order.remove(key)
                    access_order.append(key)
                    return cache[key]
                
                # 计算新值
                result = func(*args, **kwargs)
                
                # 如果缓存已满，删除最久未使用的项
                if len(cache) >= maxsize:
                    oldest_key = access_order.pop(0)
                    del cache[oldest_key]
                
                # 添加新项
                cache[key] = result
                access_order.append(key)
                
                return result
            
            wrapper.cache_info = lambda: {
                "cache_size": len(cache),
                "max_size": maxsize,
                "keys": list(cache.keys())
            }
            
            return wrapper
        return decorator
    
    # 使用装饰器的测试函数
    @profile
    def generate_primes(limit):
        """
        生成质数列表
        """
        primes = []
        for num in range(2, limit):
            is_prime = True
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
        return primes
    
    @lru_cache(maxsize=5)
    def expensive_fibonacci(n):
        """
        耗时的斐波那契计算（用于测试LRU缓存）
        """
        if n <= 1:
            return n
        return expensive_fibonacci(n - 1) + expensive_fibonacci(n - 2)
    
    # 测试
    print("题目1测试（性能比较）：")
    performance_comparison()
    
    print("\n题目2测试（性能分析装饰器）：")
    primes = generate_primes(1000)
    print(f"生成了 {len(primes)} 个质数")
    
    print("\n题目3测试（LRU缓存）：")
    # 测试LRU缓存
    for i in [5, 3, 7, 5, 8, 3, 9, 10, 5]:
        result = expensive_fibonacci(i)
        print(f"fibonacci({i}) = {result}")
    
    print(f"缓存信息: {expensive_fibonacci.cache_info()}")
    
    performance_comparison()


# ============================================================================
# 7. 综合应用练习
# ============================================================================

def exercise_7_comprehensive():
    """
    练习7：综合应用
    
    难度：★★★★★
    """
    print("\n=== 练习7：综合应用 ===")
    
    # 题目：实现一个简单的函数式编程库
    class FunctionalProgramming:
        """
        函数式编程工具类
        """
        
        @staticmethod
        def map_reduce(data: List[Any], map_func: Callable, reduce_func: Callable, initial=None):
            """
            MapReduce实现
            
            Args:
                data: 输入数据
                map_func: 映射函数
                reduce_func: 归约函数
                initial: 初始值
            
            Returns:
                归约结果
            """
            # Map阶段
            mapped_data = [map_func(item) for item in data]
            
            # Reduce阶段
            if initial is None:
                if not mapped_data:
                    return None
                result = mapped_data[0]
                start_index = 1
            else:
                result = initial
                start_index = 0
            
            for item in mapped_data[start_index:]:
                result = reduce_func(result, item)
            
            return result
        
        @staticmethod
        def pipeline(*functions):
            """
            创建函数管道
            
            Args:
                *functions: 管道中的函数
            
            Returns:
                function: 管道函数
            """
            def pipe(data):
                result = data
                for func in functions:
                    result = func(result)
                return result
            return pipe
        
        @staticmethod
        def curry(func):
            """
            柯里化函数
            
            Args:
                func: 要柯里化的函数
            
            Returns:
                function: 柯里化后的函数
            """
            def curried(*args, **kwargs):
                if len(args) + len(kwargs) >= func.__code__.co_argcount:
                    return func(*args, **kwargs)
                return lambda *more_args, **more_kwargs: curried(
                    *(args + more_args), **{**kwargs, **more_kwargs}
                )
            return curried
        
        @staticmethod
        def partial(func, *partial_args, **partial_kwargs):
            """
            偏函数应用
            
            Args:
                func: 原函数
                *partial_args: 部分参数
                **partial_kwargs: 部分关键字参数
            
            Returns:
                function: 偏应用函数
            """
            def partial_func(*args, **kwargs):
                return func(*(partial_args + args), **{**partial_kwargs, **kwargs})
            return partial_func
    
    # 测试综合应用
    print("综合应用测试：")
    
    # 测试MapReduce
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # 计算所有数字平方的和
    square_sum = FunctionalProgramming.map_reduce(
        numbers,
        lambda x: x ** 2,  # map: 计算平方
        lambda x, y: x + y,  # reduce: 求和
        0  # 初始值
    )
    print(f"数字平方和: {square_sum}")
    
    # 测试函数管道
    # 创建一个管道：加1 -> 乘2 -> 平方
    pipeline = FunctionalProgramming.pipeline(
        lambda x: x + 1,
        lambda x: x * 2,
        lambda x: x ** 2
    )
    
    pipeline_results = [pipeline(x) for x in range(1, 6)]
    print(f"管道处理结果: {pipeline_results}")
    
    # 测试柯里化
    @FunctionalProgramming.curry
    def add_three_numbers(a, b, c):
        return a + b + c
    
    add_5_and_3 = add_three_numbers(5)(3)
    curry_result = add_5_and_3(2)
    print(f"柯里化结果: {curry_result}")
    
    # 测试偏函数
    multiply = lambda x, y: x * y
    double = FunctionalProgramming.partial(multiply, 2)
    triple = FunctionalProgramming.partial(multiply, 3)
    
    print(f"偏函数 double(5): {double(5)}")
    print(f"偏函数 triple(5): {triple(5)}")


# ============================================================================
# 8. 自测系统
# ============================================================================

def self_test_system():
    """
    自测系统 - 运行所有练习并检查结果
    """
    print("=" * 60)
    print("Python函数练习自测系统")
    print("=" * 60)
    
    exercises = [
        ("基础函数设计", exercise_1_basic_functions),
        ("参数传递", exercise_2_parameters),
        ("返回值处理", exercise_3_return_values),
        ("高级函数特性", exercise_4_advanced_features),
        ("递归函数", exercise_5_recursion),
        ("函数优化和性能测试", exercise_6_optimization),
        ("综合应用", exercise_7_comprehensive)
    ]
    
    for name, exercise_func in exercises:
        try:
            print(f"\n{'='*20} {name} {'='*20}")
            exercise_func()
            print(f"✓ {name} 练习完成")
        except Exception as e:
            print(f"✗ {name} 练习出错: {e}")
    
    print("\n" + "=" * 60)
    print("所有练习完成！")
    print("=" * 60)


if __name__ == "__main__":
    self_test_system()