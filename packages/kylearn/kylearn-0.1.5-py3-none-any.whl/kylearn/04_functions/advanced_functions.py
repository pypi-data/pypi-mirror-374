#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python高级函数特性示例
=====================

本文件演示Python的高级函数特性，包括：
1. Lambda函数（匿名函数）
2. 装饰器（Decorators）
3. 闭包（Closures）
4. 高阶函数
5. 函数式编程概念
6. 生成器函数
7. 协程函数

学习目标：
- 掌握lambda函数的使用场景
- 理解装饰器的工作原理和应用
- 学会创建和使用闭包
- 了解函数式编程的基本概念
- 掌握高阶函数的设计模式
"""

import functools
import time
from typing import Callable, Any, List, Iterator, Generator
import asyncio


# ============================================================================
# 1. Lambda函数（匿名函数）
# ============================================================================

def lambda_examples():
    """
    Lambda函数示例和应用场景
    
    Lambda函数特点：
    - 匿名函数，不需要def关键字
    - 只能包含表达式，不能包含语句
    - 通常用于简单的、一次性的函数
    - 常与map、filter、sort等函数配合使用
    """
    print("=== Lambda函数示例 ===")
    
    # 基础lambda函数
    square = lambda x: x ** 2
    print(f"Lambda平方函数: square(5) = {square(5)}")
    
    # 多参数lambda
    add = lambda x, y: x + y
    print(f"Lambda加法函数: add(3, 4) = {add(3, 4)}")
    
    # 条件表达式lambda
    max_value = lambda x, y: x if x > y else y
    print(f"Lambda最大值函数: max_value(10, 7) = {max_value(10, 7)}")
    
    # 与内置函数配合使用
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # map函数 - 对每个元素应用函数
    squares = list(map(lambda x: x ** 2, numbers))
    print(f"使用map计算平方: {squares}")
    
    # filter函数 - 过滤元素
    evens = list(filter(lambda x: x % 2 == 0, numbers))
    print(f"使用filter过滤偶数: {evens}")
    
    # sorted函数 - 自定义排序
    students = [
        {"name": "张三", "score": 85},
        {"name": "李四", "score": 92},
        {"name": "王五", "score": 78}
    ]
    sorted_students = sorted(students, key=lambda s: s["score"], reverse=True)
    print(f"按分数排序: {sorted_students}")
    
    # reduce函数 - 累积计算
    from functools import reduce
    product = reduce(lambda x, y: x * y, [1, 2, 3, 4, 5])
    print(f"使用reduce计算阶乘: {product}")


# ============================================================================
# 2. 装饰器（Decorators）
# ============================================================================

def simple_decorator(func):
    """
    简单装饰器示例
    
    装饰器是一个接受函数作为参数并返回新函数的函数
    """
    @functools.wraps(func)  # 保持原函数的元数据
    def wrapper(*args, **kwargs):
        print(f"调用函数 {func.__name__} 之前")
        result = func(*args, **kwargs)
        print(f"调用函数 {func.__name__} 之后")
        return result
    return wrapper


def timing_decorator(func):
    """
    计时装饰器 - 测量函数执行时间
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"函数 {func.__name__} 执行时间: {end_time - start_time:.4f} 秒")
        return result
    return wrapper


def retry_decorator(max_retries=3):
    """
    重试装饰器 - 带参数的装饰器
    
    Args:
        max_retries (int): 最大重试次数
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        print(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败")
                        raise e
                    print(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}")
            return None
        return wrapper
    return decorator


def cache_decorator(func):
    """
    缓存装饰器 - 缓存函数结果
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 创建缓存键
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in cache:
            print(f"从缓存获取 {func.__name__} 的结果")
            return cache[key]
        
        print(f"计算 {func.__name__} 的结果")
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    return wrapper


class CountCalls:
    """
    类装饰器 - 统计函数调用次数
    """
    def __init__(self, func):
        self.func = func
        self.count = 0
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"函数 {self.func.__name__} 被调用了 {self.count} 次")
        return self.func(*args, **kwargs)


# 装饰器使用示例
@simple_decorator
def greet(name):
    """被装饰的问候函数"""
    return f"你好, {name}!"


@timing_decorator
@cache_decorator
def fibonacci(n):
    """计算斐波那契数列（带缓存和计时）"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@retry_decorator(max_retries=2)
def unreliable_function():
    """不可靠的函数（用于演示重试装饰器）"""
    import random
    if random.random() < 0.7:  # 70%的概率失败
        raise Exception("随机失败")
    return "成功执行"


@CountCalls
def counted_function(x):
    """被计数的函数"""
    return x * 2


# ============================================================================
# 3. 闭包（Closures）
# ============================================================================

def create_multiplier(factor):
    """
    创建乘法器闭包
    
    闭包特点：
    - 内部函数引用外部函数的变量
    - 外部函数返回内部函数
    - 内部函数"记住"外部函数的环境
    
    Args:
        factor (int): 乘法因子
    
    Returns:
        function: 乘法器函数
    """
    def multiplier(number):
        return number * factor  # 引用外部变量factor
    
    return multiplier


def create_counter(initial_value=0):
    """
    创建计数器闭包
    
    Args:
        initial_value (int): 初始值
    
    Returns:
        function: 计数器函数
    """
    count = initial_value
    
    def counter():
        nonlocal count  # 修改外部变量
        count += 1
        return count
    
    return counter


def create_accumulator():
    """
    创建累加器闭包
    
    Returns:
        tuple: (累加函数, 获取总和函数, 重置函数)
    """
    total = 0
    
    def add(value):
        nonlocal total
        total += value
        return total
    
    def get_total():
        return total
    
    def reset():
        nonlocal total
        total = 0
    
    return add, get_total, reset


def create_validator(min_value, max_value):
    """
    创建验证器闭包
    
    Args:
        min_value: 最小值
        max_value: 最大值
    
    Returns:
        function: 验证函数
    """
    def validate(value):
        if min_value <= value <= max_value:
            return True, f"值 {value} 在有效范围内"
        else:
            return False, f"值 {value} 超出范围 [{min_value}, {max_value}]"
    
    return validate


# ============================================================================
# 4. 高阶函数
# ============================================================================

def apply_operation(numbers: List[float], operation: Callable[[float], float]) -> List[float]:
    """
    对数字列表应用操作函数
    
    Args:
        numbers: 数字列表
        operation: 操作函数
    
    Returns:
        处理后的数字列表
    """
    return [operation(num) for num in numbers]


def compose_functions(*functions):
    """
    函数组合 - 将多个函数组合成一个函数
    
    Args:
        *functions: 要组合的函数列表
    
    Returns:
        function: 组合后的函数
    """
    def composed_function(x):
        result = x
        for func in reversed(functions):  # 从右到左应用函数
            result = func(result)
        return result
    
    return composed_function


def create_pipeline(*functions):
    """
    创建函数管道 - 从左到右应用函数
    
    Args:
        *functions: 管道中的函数
    
    Returns:
        function: 管道函数
    """
    def pipeline(x):
        result = x
        for func in functions:
            result = func(result)
        return result
    
    return pipeline


def partial_application(func, *partial_args, **partial_kwargs):
    """
    偏函数应用 - 固定函数的部分参数
    
    Args:
        func: 原函数
        *partial_args: 部分位置参数
        **partial_kwargs: 部分关键字参数
    
    Returns:
        function: 偏应用函数
    """
    def partial_func(*args, **kwargs):
        # 合并参数
        all_args = partial_args + args
        all_kwargs = {**partial_kwargs, **kwargs}
        return func(*all_args, **all_kwargs)
    
    return partial_func


def curry_function(func):
    """
    柯里化函数 - 将多参数函数转换为单参数函数链
    
    Args:
        func: 要柯里化的函数
    
    Returns:
        function: 柯里化后的函数
    """
    def curried(*args, **kwargs):
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        else:
            return lambda *more_args, **more_kwargs: curried(
                *(args + more_args), **{**kwargs, **more_kwargs}
            )
    
    return curried


# ============================================================================
# 5. 函数式编程概念
# ============================================================================

def functional_programming_examples():
    """
    函数式编程概念示例
    """
    print("=== 函数式编程示例 ===")
    
    # 不可变数据处理
    original_list = [1, 2, 3, 4, 5]
    
    # 使用map进行转换（不修改原列表）
    doubled = list(map(lambda x: x * 2, original_list))
    print(f"原列表: {original_list}")
    print(f"翻倍后: {doubled}")
    
    # 使用filter进行过滤
    evens = list(filter(lambda x: x % 2 == 0, original_list))
    print(f"偶数: {evens}")
    
    # 使用reduce进行聚合
    from functools import reduce
    sum_result = reduce(lambda x, y: x + y, original_list)
    print(f"求和: {sum_result}")
    
    # 函数组合示例
    add_one = lambda x: x + 1
    multiply_by_two = lambda x: x * 2
    square = lambda x: x ** 2
    
    # 组合函数: square(multiply_by_two(add_one(x)))
    composed = compose_functions(square, multiply_by_two, add_one)
    result = composed(3)  # (3+1)*2 = 8, 8^2 = 64
    print(f"函数组合结果: {result}")
    
    # 管道示例
    pipeline = create_pipeline(add_one, multiply_by_two, square)
    pipeline_result = pipeline(3)  # 同样的结果
    print(f"管道结果: {pipeline_result}")


# ============================================================================
# 6. 生成器函数
# ============================================================================

def simple_generator():
    """
    简单生成器函数
    
    Yields:
        int: 0到4的数字
    """
    for i in range(5):
        print(f"生成 {i}")
        yield i


def fibonacci_generator(limit=None):
    """
    斐波那契数列生成器
    
    Args:
        limit (int, optional): 生成数字的上限
    
    Yields:
        int: 斐波那契数列的下一个数字
    """
    a, b = 0, 1
    count = 0
    
    while limit is None or count < limit:
        yield a
        a, b = b, a + b
        count += 1


def file_reader_generator(filename):
    """
    文件读取生成器
    
    Args:
        filename (str): 文件名
    
    Yields:
        str: 文件的每一行
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                yield line_number, line.strip()
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")


def infinite_sequence():
    """
    无限序列生成器
    
    Yields:
        int: 无限递增的数字
    """
    num = 0
    while True:
        yield num
        num += 1


# ============================================================================
# 7. 协程函数（异步函数）
# ============================================================================

async def async_function_example():
    """
    异步函数示例
    """
    print("异步函数开始执行")
    await asyncio.sleep(1)  # 模拟异步操作
    print("异步函数执行完成")
    return "异步结果"


async def async_generator_example():
    """
    异步生成器示例
    
    Yields:
        str: 异步生成的消息
    """
    for i in range(3):
        await asyncio.sleep(0.5)  # 模拟异步操作
        yield f"异步消息 {i + 1}"


# ============================================================================
# 8. 示例运行和测试
# ============================================================================

def main():
    """
    主函数，演示所有高级函数特性
    """
    print("=" * 60)
    print("Python高级函数特性示例")
    print("=" * 60)
    
    # 1. Lambda函数示例
    lambda_examples()
    
    # 2. 装饰器示例
    print("\n=== 装饰器示例 ===")
    result = greet("世界")
    print(f"装饰器结果: {result}")
    
    print("\n计算斐波那契数列:")
    print(f"fibonacci(10) = {fibonacci(10)}")
    print(f"fibonacci(10) = {fibonacci(10)}")  # 第二次调用会使用缓存
    
    print("\n重试装饰器测试:")
    try:
        result = unreliable_function()
        print(f"重试成功: {result}")
    except Exception as e:
        print(f"重试失败: {e}")
    
    print("\n计数装饰器测试:")
    print(f"counted_function(5) = {counted_function(5)}")
    print(f"counted_function(10) = {counted_function(10)}")
    
    # 3. 闭包示例
    print("\n=== 闭包示例 ===")
    
    # 乘法器闭包
    double = create_multiplier(2)
    triple = create_multiplier(3)
    print(f"double(5) = {double(5)}")
    print(f"triple(5) = {triple(5)}")
    
    # 计数器闭包
    counter1 = create_counter()
    counter2 = create_counter(10)
    print(f"counter1: {counter1()}, {counter1()}, {counter1()}")
    print(f"counter2: {counter2()}, {counter2()}")
    
    # 累加器闭包
    add, get_total, reset = create_accumulator()
    print(f"累加器: {add(5)}, {add(3)}, {add(2)}")
    print(f"总和: {get_total()}")
    reset()
    print(f"重置后: {get_total()}")
    
    # 验证器闭包
    age_validator = create_validator(0, 120)
    valid, msg = age_validator(25)
    print(f"年龄验证: {msg}")
    valid, msg = age_validator(150)
    print(f"年龄验证: {msg}")
    
    # 4. 高阶函数示例
    print("\n=== 高阶函数示例 ===")
    
    numbers = [1, 2, 3, 4, 5]
    
    # 应用操作
    squared = apply_operation(numbers, lambda x: x ** 2)
    print(f"平方操作: {squared}")
    
    # 偏函数应用
    multiply = lambda x, y: x * y
    double_func = partial_application(multiply, 2)
    print(f"偏函数应用: double_func(5) = {double_func(5)}")
    
    # 柯里化
    @curry_function
    def add_three_numbers(a, b, c):
        return a + b + c
    
    add_5_and_3 = add_three_numbers(5)(3)
    result = add_5_and_3(2)
    print(f"柯里化结果: {result}")
    
    # 5. 函数式编程
    functional_programming_examples()
    
    # 6. 生成器示例
    print("\n=== 生成器示例 ===")
    
    print("简单生成器:")
    gen = simple_generator()
    for value in gen:
        print(f"接收到: {value}")
    
    print("\n斐波那契生成器:")
    fib_gen = fibonacci_generator(8)
    fib_list = list(fib_gen)
    print(f"前8个斐波那契数: {fib_list}")
    
    print("\n无限序列生成器（前5个）:")
    infinite_gen = infinite_sequence()
    for i, value in enumerate(infinite_gen):
        if i >= 5:
            break
        print(f"无限序列[{i}]: {value}")


async def async_main():
    """
    异步主函数，演示协程
    """
    print("\n=== 协程示例 ===")
    
    # 异步函数
    result = await async_function_example()
    print(f"异步函数结果: {result}")
    
    # 异步生成器
    print("异步生成器:")
    async for message in async_generator_example():
        print(f"接收到: {message}")


if __name__ == "__main__":
    # 运行同步示例
    main()
    
    # 运行异步示例
    print("\n" + "=" * 60)
    asyncio.run(async_main())