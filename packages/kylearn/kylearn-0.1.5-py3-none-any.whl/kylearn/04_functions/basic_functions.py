#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python函数基础示例
==================

本文件演示Python函数的基础概念，包括：
1. 函数定义和调用
2. 函数命名规范
3. 文档字符串最佳实践
4. 函数作用域和变量生命周期
5. 函数返回值

学习目标：
- 掌握函数的基本语法
- 理解函数作用域
- 学会编写规范的函数文档
- 了解函数返回值的使用
"""

# ============================================================================
# 1. 基础函数定义和调用
# ============================================================================

def greet():
    """
    最简单的函数示例 - 无参数，无返回值
    
    这是一个最基本的函数，演示了函数的基本结构：
    - def 关键字
    - 函数名
    - 括号()
    - 冒号:
    - 函数体（缩进）
    """
    print("你好，欢迎学习Python函数！")


def greet_person(name):
    """
    带参数的函数示例
    
    Args:
        name (str): 要问候的人的姓名
    
    这个函数演示了如何接收参数并在函数内使用
    """
    print(f"你好，{name}！欢迎学习Python！")


def add_numbers(a, b):
    """
    带返回值的函数示例
    
    Args:
        a (int/float): 第一个数字
        b (int/float): 第二个数字
    
    Returns:
        int/float: 两个数字的和
    
    这个函数演示了如何使用return语句返回计算结果
    """
    result = a + b
    return result


# ============================================================================
# 2. 函数命名规范和最佳实践
# ============================================================================

# 好的函数命名示例（遵循PEP 8规范）
def calculate_area(length, width):
    """
    计算矩形面积
    
    函数命名规范：
    - 使用小写字母
    - 单词之间用下划线分隔
    - 名称要有描述性，能清楚表达函数功能
    
    Args:
        length (float): 矩形长度
        width (float): 矩形宽度
    
    Returns:
        float: 矩形面积
    """
    return length * width


def is_even_number(number):
    """
    判断数字是否为偶数
    
    布尔函数命名规范：
    - 通常以is_、has_、can_等开头
    - 返回True或False
    
    Args:
        number (int): 要判断的数字
    
    Returns:
        bool: 如果是偶数返回True，否则返回False
    """
    return number % 2 == 0


def get_user_info():
    """
    获取用户信息
    
    获取类函数命名规范：
    - 通常以get_开头
    - 表示从某处获取或计算数据
    
    Returns:
        dict: 包含用户信息的字典
    """
    return {
        "name": "张三",
        "age": 25,
        "city": "北京"
    }


# ============================================================================
# 3. 文档字符串最佳实践
# ============================================================================

def calculate_bmi(weight, height):
    """
    计算身体质量指数(BMI)
    
    这是一个完整的文档字符串示例，包含了所有推荐的部分：
    - 简短的功能描述
    - 详细的参数说明
    - 返回值说明
    - 使用示例
    - 注意事项
    
    BMI计算公式：BMI = 体重(kg) / 身高(m)²
    
    Args:
        weight (float): 体重，单位为千克(kg)
        height (float): 身高，单位为米(m)
    
    Returns:
        float: BMI值，保留两位小数
    
    Raises:
        ValueError: 当体重或身高为负数或零时抛出异常
    
    Example:
        >>> bmi = calculate_bmi(70, 1.75)
        >>> print(f"BMI: {bmi}")
        BMI: 22.86
    
    Note:
        - BMI正常范围：18.5-24.9
        - 此函数不进行BMI分类，仅计算数值
    """
    if weight <= 0 or height <= 0:
        raise ValueError("体重和身高必须为正数")
    
    bmi = weight / (height ** 2)
    return round(bmi, 2)


# ============================================================================
# 4. 函数作用域和变量生命周期
# ============================================================================

# 全局变量
global_counter = 0
global_message = "这是全局变量"


def demonstrate_scope():
    """
    演示函数作用域和变量生命周期
    
    作用域类型：
    1. 全局作用域：在函数外定义的变量
    2. 局部作用域：在函数内定义的变量
    3. 内置作用域：Python内置的变量和函数
    """
    # 局部变量
    local_message = "这是局部变量"
    local_counter = 10
    
    print("=== 作用域演示 ===")
    print(f"局部变量: {local_message}")
    print(f"局部计数器: {local_counter}")
    print(f"全局变量: {global_message}")
    print(f"全局计数器: {global_counter}")


def modify_global_variable():
    """
    演示如何在函数内修改全局变量
    
    使用global关键字可以在函数内修改全局变量
    """
    global global_counter
    global_counter += 1
    print(f"全局计数器已增加到: {global_counter}")


def variable_lifetime_demo():
    """
    演示变量的生命周期
    
    变量生命周期：
    - 局部变量：函数调用时创建，函数结束时销毁
    - 全局变量：程序开始时创建，程序结束时销毁
    """
    temp_var = "临时变量"
    print(f"函数内创建的变量: {temp_var}")
    
    # 函数结束后，temp_var将被销毁
    # 在函数外无法访问temp_var


def nested_scope_demo():
    """
    演示嵌套作用域（闭包的基础）
    """
    outer_var = "外层变量"
    
    def inner_function():
        inner_var = "内层变量"
        print(f"内层函数可以访问: {outer_var}")
        print(f"内层变量: {inner_var}")
    
    inner_function()
    # print(inner_var)  # 这行会报错，因为inner_var在外层不可见


# ============================================================================
# 5. 函数返回值详解
# ============================================================================

def no_return_function():
    """
    没有显式返回值的函数
    
    Returns:
        None: Python函数默认返回None
    """
    print("这个函数没有return语句")
    # 隐式返回None


def single_return_function(x):
    """
    返回单个值的函数
    
    Args:
        x (int): 输入数字
    
    Returns:
        int: 输入数字的平方
    """
    return x ** 2


def multiple_return_function(a, b):
    """
    返回多个值的函数
    
    Python可以同时返回多个值，实际上是返回一个元组
    
    Args:
        a (int): 第一个数字
        b (int): 第二个数字
    
    Returns:
        tuple: (和, 差, 积, 商)
    """
    sum_result = a + b
    diff_result = a - b
    product_result = a * b
    quotient_result = a / b if b != 0 else None
    
    return sum_result, diff_result, product_result, quotient_result


def conditional_return_function(number):
    """
    根据条件返回不同值的函数
    
    Args:
        number (int): 输入数字
    
    Returns:
        str: 数字的分类描述
    """
    if number > 0:
        return "正数"
    elif number < 0:
        return "负数"
    else:
        return "零"


def early_return_function(items):
    """
    演示提前返回的用法
    
    提前返回可以减少嵌套，使代码更清晰
    
    Args:
        items (list): 项目列表
    
    Returns:
        int: 列表长度，如果列表为空则返回-1
    """
    # 提前返回，避免深层嵌套
    if not items:
        return -1
    
    if not isinstance(items, list):
        return -1
    
    return len(items)


# ============================================================================
# 6. 高级返回值示例
# ============================================================================

def return_multiple_types(data_type: str):
    """
    根据类型返回不同类型的值
    
    Args:
        data_type (str): 数据类型 ("list", "dict", "tuple", "set")
    
    Returns:
        Union[list, dict, tuple, set]: 不同类型的数据结构
    """
    if data_type == "list":
        return [1, 2, 3, 4, 5]
    elif data_type == "dict":
        return {"name": "张三", "age": 25}
    elif data_type == "tuple":
        return (10, 20, 30)
    elif data_type == "set":
        return {1, 2, 3, 4, 5}
    else:
        return None


def return_with_unpacking():
    """
    演示返回值解包的各种方式
    
    Returns:
        tuple: (姓名, 年龄, 城市, 邮箱)
    """
    return "李四", 28, "深圳", "lisi@example.com"


def return_named_tuple():
    """
    使用命名元组作为返回值
    
    Returns:
        Person: 包含个人信息的命名元组
    """
    from collections import namedtuple
    
    Person = namedtuple('Person', ['name', 'age', 'city'])
    return Person("王五", 30, "广州")


def return_generator():
    """
    返回生成器对象
    
    Yields:
        int: 斐波那契数列的下一个数字
    """
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def return_function():
    """
    返回函数对象（高阶函数）
    
    Returns:
        function: 一个计算平方的函数
    """
    def square(x):
        return x ** 2
    
    return square


def return_with_context_manager():
    """
    返回上下文管理器
    
    Returns:
        _io.TextIOWrapper: 文件对象（上下文管理器）
    """
    import tempfile
    import os
    
    # 创建临时文件
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
    temp_file.write("这是一个临时文件的内容\n")
    temp_file.write("用于演示返回上下文管理器\n")
    temp_file.close()
    
    # 返回文件路径，调用者需要自己管理文件
    return temp_file.name


def return_class_instance():
    """
    返回类实例
    
    Returns:
        Calculator: 计算器类的实例
    """
    class Calculator:
        def __init__(self):
            self.result = 0
        
        def add(self, value):
            self.result += value
            return self
        
        def multiply(self, value):
            self.result *= value
            return self
        
        def get_result(self):
            return self.result
    
    return Calculator()


def return_with_error_handling(operation: str, a: float, b: float):
    """
    带错误处理的返回值示例
    
    Args:
        operation (str): 操作类型
        a (float): 第一个操作数
        b (float): 第二个操作数
    
    Returns:
        tuple: (是否成功, 结果或错误信息)
    """
    try:
        if operation == "add":
            return True, a + b
        elif operation == "subtract":
            return True, a - b
        elif operation == "multiply":
            return True, a * b
        elif operation == "divide":
            if b == 0:
                return False, "除数不能为零"
            return True, a / b
        else:
            return False, f"不支持的操作: {operation}"
    except Exception as e:
        return False, f"计算错误: {str(e)}"


def return_optional_value(include_optional: bool = False):
    """
    返回可选值的示例
    
    Args:
        include_optional (bool): 是否包含可选值
    
    Returns:
        dict: 包含必需和可选字段的字典
    """
    result = {
        "required_field": "这是必需字段",
        "timestamp": "2024-01-01 12:00:00"
    }
    
    if include_optional:
        result["optional_field"] = "这是可选字段"
        result["extra_data"] = [1, 2, 3, 4, 5]
    
    return result


def return_chained_operations():
    """
    返回支持链式调用的对象
    
    Returns:
        ChainableCalculator: 支持链式调用的计算器
    """
    class ChainableCalculator:
        def __init__(self, initial_value=0):
            self.value = initial_value
        
        def add(self, x):
            self.value += x
            return self  # 返回自身支持链式调用
        
        def multiply(self, x):
            self.value *= x
            return self
        
        def subtract(self, x):
            self.value -= x
            return self
        
        def divide(self, x):
            if x != 0:
                self.value /= x
            return self
        
        def get_value(self):
            return self.value
        
        def __str__(self):
            return f"ChainableCalculator(value={self.value})"
    
    return ChainableCalculator()


# ============================================================================
# 8. 返回值类型注解最佳实践
# ============================================================================

def typed_function(name: str, age: int, height: float = 1.70) -> str:
    """
    使用类型注解的函数示例
    
    类型注解的好处：
    1. 提高代码可读性
    2. 帮助IDE提供更好的代码提示
    3. 便于静态类型检查工具分析
    
    Args:
        name: 姓名
        age: 年龄
        height: 身高（默认1.70米）
    
    Returns:
        格式化的个人信息字符串
    """
    return f"姓名: {name}, 年龄: {age}, 身高: {height}m"


from typing import List, Dict, Optional, Union


def advanced_typed_function(
    numbers: List[int], 
    config: Dict[str, Union[str, int]], 
    optional_param: Optional[str] = None
) -> List[int]:
    """
    高级类型注解示例
    
    Args:
        numbers: 整数列表
        config: 配置字典，值可以是字符串或整数
        optional_param: 可选的字符串参数
    
    Returns:
        处理后的整数列表
    """
    multiplier = config.get('multiplier', 1)
    if isinstance(multiplier, int):
        result = [num * multiplier for num in numbers]
    else:
        result = numbers.copy()
    
    return result


# ============================================================================
# 9. 示例运行和测试
# ============================================================================

def main():
    """
    主函数，演示所有函数的使用
    """
    print("=" * 60)
    print("Python函数基础示例")
    print("=" * 60)
    
    # 1. 基础函数调用
    print("\n1. 基础函数调用:")
    greet()
    greet_person("小明")
    result = add_numbers(10, 20)
    print(f"10 + 20 = {result}")
    
    # 2. 函数命名规范示例
    print("\n2. 函数命名规范示例:")
    area = calculate_area(5, 3)
    print(f"矩形面积: {area}")
    print(f"8是偶数吗? {is_even_number(8)}")
    print(f"7是偶数吗? {is_even_number(7)}")
    user = get_user_info()
    print(f"用户信息: {user}")
    
    # 3. 文档字符串示例
    print("\n3. 文档字符串示例:")
    try:
        bmi = calculate_bmi(70, 1.75)
        print(f"BMI计算结果: {bmi}")
    except ValueError as e:
        print(f"错误: {e}")
    
    # 4. 作用域演示
    print("\n4. 作用域演示:")
    demonstrate_scope()
    modify_global_variable()
    modify_global_variable()
    variable_lifetime_demo()
    nested_scope_demo()
    
    # 5. 返回值演示
    print("\n5. 返回值演示:")
    print(f"无返回值函数结果: {no_return_function()}")
    print(f"5的平方: {single_return_function(5)}")
    
    # 多返回值解包
    sum_val, diff_val, prod_val, quot_val = multiple_return_function(10, 3)
    print(f"10和3的运算结果: 和={sum_val}, 差={diff_val}, 积={prod_val}, 商={quot_val}")
    
    print(f"数字分类: 5是{conditional_return_function(5)}")
    print(f"数字分类: -3是{conditional_return_function(-3)}")
    print(f"数字分类: 0是{conditional_return_function(0)}")
    
    print(f"列表长度: {early_return_function([1, 2, 3, 4])}")
    print(f"空列表长度: {early_return_function([])}")
    
    # 6. 高级返回值示例
    print("\n6. 高级返回值示例:")
    
    # 返回不同类型
    list_result = return_multiple_types("list")
    dict_result = return_multiple_types("dict")
    print(f"返回列表: {list_result}")
    print(f"返回字典: {dict_result}")
    
    # 返回值解包
    name, age, city, email = return_with_unpacking()
    print(f"解包结果: {name}, {age}岁, 来自{city}, 邮箱{email}")
    
    # 命名元组
    person = return_named_tuple()
    print(f"命名元组: {person.name}, {person.age}岁, 来自{person.city}")
    
    # 生成器
    fib_gen = return_generator()
    fib_numbers = [next(fib_gen) for _ in range(10)]
    print(f"斐波那契数列前10项: {fib_numbers}")
    
    # 返回函数
    square_func = return_function()
    print(f"返回的函数计算5的平方: {square_func(5)}")
    
    # 返回类实例
    calc = return_class_instance()
    result = calc.add(10).multiply(2).add(5).get_result()
    print(f"链式计算结果: {result}")
    
    # 错误处理返回值
    success, result = return_with_error_handling("divide", 10, 2)
    print(f"除法操作: 成功={success}, 结果={result}")
    
    success, error = return_with_error_handling("divide", 10, 0)
    print(f"除零操作: 成功={success}, 错误={error}")
    
    # 可选值返回
    basic_result = return_optional_value(False)
    full_result = return_optional_value(True)
    print(f"基础结果: {basic_result}")
    print(f"完整结果: {full_result}")
    
    # 链式操作
    chain_calc = return_chained_operations()
    final_value = chain_calc.add(10).multiply(3).subtract(5).divide(5).get_value()
    print(f"链式计算: {final_value}")
    
    # 7. 类型注解示例
    print("\n7. 类型注解示例:")
    info = typed_function("李四", 28, 1.80)
    print(info)
    
    numbers = [1, 2, 3, 4, 5]
    config = {"multiplier": 2}
    result = advanced_typed_function(numbers, config)
    print(f"处理后的数字: {result}")


if __name__ == "__main__":
    main()