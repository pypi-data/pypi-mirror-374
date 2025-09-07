#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python函数参数传递示例
=====================

本文件演示Python函数参数传递的各种方式，包括：
1. 位置参数
2. 关键字参数
3. 默认参数
4. 可变参数(*args)
5. 关键字可变参数(**kwargs)
6. 参数验证和类型提示
7. 参数传递的最佳实践

学习目标：
- 掌握各种参数传递方式
- 理解参数的优先级和组合使用
- 学会参数验证和错误处理
- 了解参数传递的性能考虑
"""

from typing import List, Dict, Any, Optional, Union
import functools


# ============================================================================
# 1. 位置参数 (Positional Arguments)
# ============================================================================

def greet_with_position(first_name, last_name, title):
    """
    使用位置参数的函数
    
    位置参数特点：
    - 必须按照定义的顺序传递
    - 参数个数必须匹配
    - 最基本的参数传递方式
    
    Args:
        first_name (str): 名字
        last_name (str): 姓氏
        title (str): 称谓
    
    Returns:
        str: 格式化的问候语
    """
    return f"{title} {last_name} {first_name}，您好！"


def calculate_rectangle_area(length, width):
    """
    计算矩形面积 - 位置参数示例
    
    Args:
        length (float): 长度
        width (float): 宽度
    
    Returns:
        float: 面积
    """
    return length * width


# ============================================================================
# 2. 关键字参数 (Keyword Arguments)
# ============================================================================

def create_user_profile(name, age, city, email):
    """
    创建用户档案 - 演示关键字参数的使用
    
    关键字参数特点：
    - 可以不按顺序传递
    - 提高代码可读性
    - 减少参数传递错误
    
    Args:
        name (str): 姓名
        age (int): 年龄
        city (str): 城市
        email (str): 邮箱
    
    Returns:
        dict: 用户档案字典
    """
    return {
        "name": name,
        "age": age,
        "city": city,
        "email": email,
        "created_at": "2024-01-01"
    }


def keyword_only_function(*, name, age, city="北京"):
    """
    仅关键字参数函数 (Python 3+)
    
    使用*强制后面的参数只能通过关键字传递
    
    Args:
        name (str): 姓名（仅关键字）
        age (int): 年龄（仅关键字）
        city (str): 城市（仅关键字，有默认值）
    
    Returns:
        str: 格式化信息
    """
    return f"{name}，{age}岁，来自{city}"


# ============================================================================
# 3. 默认参数 (Default Arguments)
# ============================================================================

def greet_with_default(name, greeting="你好", punctuation="！"):
    """
    带默认参数的函数
    
    默认参数特点：
    - 调用时可以省略
    - 必须放在位置参数之后
    - 默认值在函数定义时确定
    
    Args:
        name (str): 姓名
        greeting (str): 问候语，默认"你好"
        punctuation (str): 标点符号，默认"！"
    
    Returns:
        str: 问候语
    """
    return f"{greeting}，{name}{punctuation}"


def calculate_power(base, exponent=2):
    """
    计算幂次方 - 默认参数示例
    
    Args:
        base (float): 底数
        exponent (float): 指数，默认为2（平方）
    
    Returns:
        float: 幂次方结果
    """
    return base ** exponent


def create_list_with_default(items=None):
    """
    正确使用可变对象作为默认参数
    
    注意：不要直接使用[]作为默认参数！
    
    Args:
        items (list, optional): 初始项目列表
    
    Returns:
        list: 新的列表
    """
    if items is None:
        items = []  # 每次调用都创建新列表
    
    items.append("新项目")
    return items


def wrong_default_example(items=[]):
    """
    错误的默认参数使用示例 - 仅用于演示，不要这样做！
    
    这个函数展示了为什么不应该使用可变对象作为默认参数
    """
    items.append("新项目")
    return items


# ============================================================================
# 4. 可变参数 (*args)
# ============================================================================

def sum_all_numbers(*args):
    """
    计算所有传入数字的和
    
    *args特点：
    - 接收任意数量的位置参数
    - 在函数内部是一个元组
    - 通常命名为args，但可以是任何名称
    
    Args:
        *args: 任意数量的数字
    
    Returns:
        float: 所有数字的和
    """
    if not args:
        return 0
    
    total = 0
    for num in args:
        if isinstance(num, (int, float)):
            total += num
        else:
            raise TypeError(f"期望数字类型，得到 {type(num)}")
    
    return total


def find_maximum(*numbers):
    """
    找出所有数字中的最大值
    
    Args:
        *numbers: 任意数量的数字
    
    Returns:
        float: 最大值
    
    Raises:
        ValueError: 当没有传入参数时
    """
    if not numbers:
        raise ValueError("至少需要传入一个数字")
    
    return max(numbers)


def print_info(title, *details):
    """
    打印信息 - 混合使用位置参数和*args
    
    Args:
        title (str): 标题
        *details: 详细信息列表
    """
    print(f"=== {title} ===")
    for i, detail in enumerate(details, 1):
        print(f"{i}. {detail}")


# ============================================================================
# 5. 关键字可变参数 (**kwargs)
# ============================================================================

def create_config(**kwargs):
    """
    创建配置字典
    
    **kwargs特点：
    - 接收任意数量的关键字参数
    - 在函数内部是一个字典
    - 通常命名为kwargs，但可以是任何名称
    
    Args:
        **kwargs: 任意关键字参数
    
    Returns:
        dict: 配置字典
    """
    default_config = {
        "debug": False,
        "timeout": 30,
        "retries": 3
    }
    
    # 更新默认配置
    default_config.update(kwargs)
    return default_config


def log_message(level, message, **context):
    """
    记录日志消息 - 混合使用普通参数和**kwargs
    
    Args:
        level (str): 日志级别
        message (str): 日志消息
        **context: 额外的上下文信息
    """
    print(f"[{level.upper()}] {message}")
    
    if context:
        print("上下文信息:")
        for key, value in context.items():
            print(f"  {key}: {value}")


def flexible_function(*args, **kwargs):
    """
    最灵活的函数 - 同时使用*args和**kwargs
    
    Args:
        *args: 任意位置参数
        **kwargs: 任意关键字参数
    """
    print("位置参数:")
    for i, arg in enumerate(args):
        print(f"  args[{i}]: {arg}")
    
    print("关键字参数:")
    for key, value in kwargs.items():
        print(f"  {key}: {value}")


# ============================================================================
# 6. 参数验证和类型提示
# ============================================================================

def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        bool: 是否为有效邮箱
    """
    if not isinstance(email, str):
        return False
    
    return "@" in email and "." in email.split("@")[-1]


def create_user_with_validation(
    name: str,
    age: int,
    email: str,
    phone: Optional[str] = None,
    interests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    创建用户信息（带参数验证）
    
    Args:
        name: 用户姓名
        age: 用户年龄
        email: 邮箱地址
        phone: 电话号码（可选）
        interests: 兴趣爱好列表（可选）
    
    Returns:
        用户信息字典
    
    Raises:
        ValueError: 参数验证失败时
        TypeError: 参数类型错误时
    """
    # 参数类型验证
    if not isinstance(name, str):
        raise TypeError("姓名必须是字符串")
    
    if not isinstance(age, int):
        raise TypeError("年龄必须是整数")
    
    if not isinstance(email, str):
        raise TypeError("邮箱必须是字符串")
    
    # 参数值验证
    if not name.strip():
        raise ValueError("姓名不能为空")
    
    if age < 0 or age > 150:
        raise ValueError("年龄必须在0-150之间")
    
    if not validate_email(email):
        raise ValueError("邮箱格式不正确")
    
    if phone is not None and not isinstance(phone, str):
        raise TypeError("电话号码必须是字符串")
    
    if interests is not None and not isinstance(interests, list):
        raise TypeError("兴趣爱好必须是列表")
    
    # 创建用户信息
    user_info = {
        "name": name.strip(),
        "age": age,
        "email": email.lower(),
    }
    
    if phone:
        user_info["phone"] = phone
    
    if interests:
        user_info["interests"] = interests
    
    return user_info


def type_checked_function(
    numbers: List[Union[int, float]],
    operation: str = "sum",
    precision: int = 2
) -> Union[int, float]:
    """
    类型检查函数示例
    
    Args:
        numbers: 数字列表
        operation: 操作类型 ("sum", "avg", "max", "min")
        precision: 小数精度
    
    Returns:
        计算结果
    """
    if not isinstance(numbers, list):
        raise TypeError("numbers必须是列表")
    
    if not all(isinstance(n, (int, float)) for n in numbers):
        raise TypeError("列表中所有元素必须是数字")
    
    if not isinstance(operation, str):
        raise TypeError("operation必须是字符串")
    
    if not isinstance(precision, int) or precision < 0:
        raise TypeError("precision必须是非负整数")
    
    if not numbers:
        return 0
    
    if operation == "sum":
        result = sum(numbers)
    elif operation == "avg":
        result = sum(numbers) / len(numbers)
    elif operation == "max":
        result = max(numbers)
    elif operation == "min":
        result = min(numbers)
    else:
        raise ValueError(f"不支持的操作: {operation}")
    
    return round(result, precision)


# ============================================================================
# 7. 参数传递最佳实践
# ============================================================================

def good_parameter_design(
    required_param: str,
    optional_param: str = "default",
    *args: Any,
    flag: bool = False,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    良好的参数设计示例
    
    参数顺序规则：
    1. 必需的位置参数
    2. 有默认值的位置参数
    3. *args
    4. 仅关键字参数
    5. **kwargs
    
    Args:
        required_param: 必需参数
        optional_param: 可选参数
        *args: 可变位置参数
        flag: 仅关键字参数
        **kwargs: 可变关键字参数
    
    Returns:
        参数信息字典
    """
    return {
        "required": required_param,
        "optional": optional_param,
        "args": args,
        "flag": flag,
        "kwargs": kwargs
    }


def parameter_unpacking_demo():
    """
    演示参数解包的使用
    """
    # 列表解包
    numbers = [1, 2, 3, 4, 5]
    total = sum_all_numbers(*numbers)
    print(f"列表解包求和: {total}")
    
    # 字典解包
    user_data = {
        "name": "张三",
        "age": 25,
        "city": "上海",
        "email": "zhangsan@example.com"
    }
    profile = create_user_profile(**user_data)
    print(f"字典解包创建档案: {profile}")


# ============================================================================
# 8. 装饰器中的参数处理
# ============================================================================

def parameter_logger(func):
    """
    记录函数参数的装饰器
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用函数 {func.__name__}")
        print(f"位置参数: {args}")
        print(f"关键字参数: {kwargs}")
        result = func(*args, **kwargs)
        print(f"返回值: {result}")
        return result
    return wrapper


@parameter_logger
def decorated_function(a, b, c=10, *args, **kwargs):
    """
    被装饰的函数示例
    """
    return a + b + c + sum(args) + sum(kwargs.values())


# ============================================================================
# 9. 示例运行和测试
# ============================================================================

def main():
    """
    主函数，演示所有参数传递方式
    """
    print("=" * 60)
    print("Python函数参数传递示例")
    print("=" * 60)
    
    # 1. 位置参数
    print("\n1. 位置参数:")
    greeting = greet_with_position("小明", "李", "先生")
    print(greeting)
    area = calculate_rectangle_area(5, 3)
    print(f"矩形面积: {area}")
    
    # 2. 关键字参数
    print("\n2. 关键字参数:")
    # 按顺序传递
    profile1 = create_user_profile("张三", 25, "北京", "zhang@example.com")
    print(f"按顺序: {profile1}")
    
    # 使用关键字参数，不按顺序
    profile2 = create_user_profile(
        email="li@example.com",
        name="李四", 
        city="上海",
        age=30
    )
    print(f"关键字参数: {profile2}")
    
    # 仅关键字参数
    info = keyword_only_function(name="王五", age=28)
    print(f"仅关键字参数: {info}")
    
    # 3. 默认参数
    print("\n3. 默认参数:")
    print(greet_with_default("小红"))
    print(greet_with_default("小蓝", "晚上好"))
    print(greet_with_default("小绿", "早上好", "。"))
    
    print(f"2的平方: {calculate_power(2)}")
    print(f"2的三次方: {calculate_power(2, 3)}")
    
    # 正确的默认参数使用
    list1 = create_list_with_default()
    list2 = create_list_with_default()
    print(f"正确的默认参数: list1={list1}, list2={list2}")
    
    # 错误的默认参数使用（演示）
    wrong1 = wrong_default_example()
    wrong2 = wrong_default_example()
    print(f"错误的默认参数: wrong1={wrong1}, wrong2={wrong2}")
    
    # 4. 可变参数 (*args)
    print("\n4. 可变参数 (*args):")
    print(f"求和: {sum_all_numbers(1, 2, 3, 4, 5)}")
    print(f"求和: {sum_all_numbers(10, 20)}")
    print(f"空参数求和: {sum_all_numbers()}")
    
    print(f"最大值: {find_maximum(3, 7, 2, 9, 1)}")
    
    print_info("购物清单", "苹果", "香蕉", "橙子", "葡萄")
    
    # 5. 关键字可变参数 (**kwargs)
    print("\n5. 关键字可变参数 (**kwargs):")
    config = create_config(debug=True, timeout=60, host="localhost", port=8080)
    print(f"配置: {config}")
    
    log_message("error", "数据库连接失败", 
                host="localhost", port=5432, retry_count=3)
    
    print("\n灵活函数调用:")
    flexible_function(1, 2, 3, name="测试", version="1.0", debug=True)
    
    # 6. 参数验证
    print("\n6. 参数验证:")
    try:
        user = create_user_with_validation(
            name="测试用户",
            age=25,
            email="test@example.com",
            phone="13800138000",
            interests=["编程", "阅读"]
        )
        print(f"创建用户成功: {user}")
    except (ValueError, TypeError) as e:
        print(f"创建用户失败: {e}")
    
    # 类型检查函数
    numbers = [1, 2, 3, 4, 5]
    print(f"数字列表求和: {type_checked_function(numbers, 'sum')}")
    print(f"数字列表平均值: {type_checked_function(numbers, 'avg')}")
    
    # 7. 参数解包
    print("\n7. 参数解包:")
    parameter_unpacking_demo()
    
    # 8. 装饰器参数处理
    print("\n8. 装饰器参数处理:")
    result = decorated_function(1, 2, d=4, e=5)
    print(f"最终结果: {result}")


if __name__ == "__main__":
    main()