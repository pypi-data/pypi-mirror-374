#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python注释规范和最佳实践

本文件演示Python中各种注释的正确使用方法，包括单行注释、多行注释、
文档字符串(docstring)的规范写法，以及注释的最佳实践。

学习目标：
1. 掌握Python中不同类型注释的语法
2. 学会编写规范的文档字符串
3. 理解注释的最佳实践和使用场景
4. 避免常见的注释错误和反模式

作者: Python学习系统
版本: 1.0
日期: 2024
"""

# =============================================================================
# 1. 单行注释 (Single-line Comments)
# =============================================================================

# 这是一个单行注释，使用井号(#)开头
# 单行注释通常用于解释下面一行或几行代码的作用

print("Hello, World!")  # 这是行尾注释，解释这行代码的作用

# 好的单行注释示例：
age = 25        # 用户年龄（年）
pi = 3.14159    # 圆周率的近似值

# 计算圆的面积
radius = 5
area = pi * radius ** 2

# 不好的注释示例（避免这样写）：
# x = 10          # 设置x为10（这种注释没有提供额外信息）
# print(x)        # 打印x（显而易见的操作不需要注释）

# =============================================================================
# 2. 多行注释 (Multi-line Comments)
# =============================================================================

# 方法1：使用多个单行注释
# 这是一个多行注释的示例
# 每一行都以井号开头
# 通常用于较长的解释说明

# 方法2：使用三引号（实际上是字符串，但可以用作注释）
"""
这是使用三引号的多行注释
可以跨越多行
通常用于模块、类或函数的文档说明
"""

'''
也可以使用单引号的三引号
效果是一样的
但建议统一使用双引号
'''

# =============================================================================
# 3. 文档字符串 (Docstrings)
# =============================================================================

def calculate_rectangle_area(length, width):
    """
    计算矩形的面积。
    
    这个函数接受矩形的长和宽作为参数，返回矩形的面积。
    
    Args:
        length (float): 矩形的长度，必须为正数
        width (float): 矩形的宽度，必须为正数
    
    Returns:
        float: 矩形的面积
    
    Raises:
        ValueError: 当长度或宽度不是正数时抛出异常
    
    Examples:
        >>> calculate_rectangle_area(5, 3)
        15.0
        >>> calculate_rectangle_area(2.5, 4.0)
        10.0
    """
    if length <= 0 or width <= 0:
        raise ValueError("长度和宽度必须为正数")
    
    return length * width


class Person:
    """
    表示一个人的类。
    
    这个类用于存储和管理个人信息，包括姓名、年龄等基本属性。
    
    Attributes:
        name (str): 人的姓名
        age (int): 人的年龄
        email (str): 人的电子邮件地址（可选）
    
    Examples:
        >>> person = Person("张三", 25)
        >>> person.name
        '张三'
        >>> person.get_info()
        '姓名: 张三, 年龄: 25'
    """
    
    def __init__(self, name, age, email=None):
        """
        初始化Person对象。
        
        Args:
            name (str): 人的姓名
            age (int): 人的年龄，必须为非负整数
            email (str, optional): 电子邮件地址。默认为None。
        
        Raises:
            ValueError: 当年龄为负数时抛出异常
            TypeError: 当姓名不是字符串时抛出异常
        """
        if not isinstance(name, str):
            raise TypeError("姓名必须是字符串")
        if age < 0:
            raise ValueError("年龄不能为负数")
        
        self.name = name
        self.age = age
        self.email = email
    
    def get_info(self):
        """
        获取人的基本信息。
        
        Returns:
            str: 包含姓名和年龄的格式化字符串
        """
        return f"姓名: {self.name}, 年龄: {self.age}"
    
    def celebrate_birthday(self):
        """
        庆祝生日，年龄增加1。
        
        这个方法会将当前年龄增加1，模拟过生日的过程。
        """
        self.age += 1
        print(f"{self.name} 过生日了！现在 {self.age} 岁。")


# =============================================================================
# 4. 不同风格的文档字符串
# =============================================================================

def google_style_docstring(param1, param2):
    """Google风格的文档字符串示例。
    
    这是Google推荐的文档字符串格式，结构清晰，易于阅读。
    
    Args:
        param1 (int): 第一个参数的描述
        param2 (str): 第二个参数的描述
    
    Returns:
        bool: 返回值的描述
    
    Raises:
        ValueError: 异常情况的描述
    """
    pass


def numpy_style_docstring(param1, param2):
    """NumPy风格的文档字符串示例。
    
    这是NumPy项目使用的文档字符串格式，适合科学计算项目。
    
    Parameters
    ----------
    param1 : int
        第一个参数的描述
    param2 : str
        第二个参数的描述
    
    Returns
    -------
    bool
        返回值的描述
    
    Raises
    ------
    ValueError
        异常情况的描述
    """
    pass


def sphinx_style_docstring(param1, param2):
    """Sphinx风格的文档字符串示例。
    
    这是Sphinx文档生成工具使用的格式，广泛用于Python项目。
    
    :param param1: 第一个参数的描述
    :type param1: int
    :param param2: 第二个参数的描述
    :type param2: str
    :returns: 返回值的描述
    :rtype: bool
    :raises ValueError: 异常情况的描述
    """
    pass


# =============================================================================
# 5. 注释的最佳实践
# =============================================================================

# 最佳实践1：解释"为什么"而不是"是什么"
def process_data(data):
    """处理输入数据并返回结果。"""
    
    # 好的注释：解释为什么这样做
    # 使用深拷贝避免修改原始数据，防止副作用
    import copy
    processed_data = copy.deepcopy(data)
    
    # 坏的注释：只是重复代码
    # processed_data = copy.deepcopy(data)  # 深拷贝数据
    
    return processed_data


# 最佳实践2：使用TODO、FIXME、NOTE等标记
def example_function():
    """示例函数，展示注释标记的使用。"""
    
    # TODO: 添加输入验证
    # FIXME: 修复边界条件的bug
    # NOTE: 这个算法的时间复杂度是O(n^2)
    # HACK: 临时解决方案，需要重构
    # WARNING: 这个函数在多线程环境下不安全
    
    pass


# 最佳实践3：保持注释与代码同步
def calculate_discount(price, discount_rate):
    """
    计算折扣后的价格。
    
    Args:
        price (float): 原价
        discount_rate (float): 折扣率（0.0-1.0）
    
    Returns:
        float: 折扣后的价格
    """
    # 确保折扣率在有效范围内
    if not 0 <= discount_rate <= 1:
        raise ValueError("折扣率必须在0到1之间")
    
    # 计算折扣后的价格
    discounted_price = price * (1 - discount_rate)
    return discounted_price


# 最佳实践4：使用类型提示配合注释
from typing import List, Dict, Optional, Union

def process_user_data(
    users: List[Dict[str, Union[str, int]]], 
    filter_active: bool = True
) -> List[Dict[str, Union[str, int]]]:
    """
    处理用户数据列表。
    
    Args:
        users: 用户数据列表，每个用户是包含姓名、年龄等信息的字典
        filter_active: 是否只返回活跃用户，默认为True
    
    Returns:
        处理后的用户数据列表
    """
    # 实现细节...
    return users


# =============================================================================
# 6. 注释的常见错误和反模式
# =============================================================================

def bad_commenting_examples():
    """展示不好的注释习惯（避免这样做）。"""
    
    # 错误1：显而易见的注释
    x = 5           # 设置x为5
    y = x + 1       # 将x加1赋值给y
    
    # 错误2：过时的注释
    # 计算税率（注意：这个注释可能已经过时了）
    tax_rate = 0.08  # 实际上税率可能已经改变
    
    # 错误3：误导性的注释
    # 计算平均值
    total = sum([1, 2, 3, 4, 5])  # 实际上这是计算总和
    
    # 错误4：注释掉的代码（应该删除而不是注释）
    # old_calculation = x * 2
    # print("Old result:", old_calculation)
    
    # 错误5：过长的行内注释
    result = complex_calculation()  # 这是一个非常复杂的计算，涉及多个步骤，包括数据预处理、算法执行、结果后处理等等...


def good_commenting_examples():
    """展示好的注释习惯。"""
    
    # 好的注释：解释业务逻辑
    # 根据公司政策，VIP客户享受15%的折扣
    vip_discount = 0.15
    
    # 好的注释：解释复杂的算法
    # 使用快速排序算法，平均时间复杂度O(n log n)
    def quicksort(arr):
        if len(arr) <= 1:
            return arr
        # 选择中间元素作为基准点，避免最坏情况
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quicksort(left) + middle + quicksort(right)
    
    # 好的注释：解释特殊情况的处理
    def safe_divide(a, b):
        # 处理除零错误，返回None而不是抛出异常
        if b == 0:
            return None
        return a / b


# =============================================================================
# 7. 文档生成工具的使用
# =============================================================================

def documented_function(x: int, y: int = 10) -> int:
    """
    一个完整文档化的函数示例。
    
    这个函数演示了如何编写完整的文档字符串，
    包括参数说明、返回值、异常处理和使用示例。
    
    Args:
        x: 第一个整数参数
        y: 第二个整数参数，默认值为10
    
    Returns:
        两个参数的和
    
    Raises:
        TypeError: 当参数不是整数时
    
    Examples:
        >>> documented_function(5)
        15
        >>> documented_function(3, 7)
        10
        >>> documented_function(1, 2)
        3
    
    Note:
        这个函数可以用于演示文档生成工具如何解析docstring。
    
    See Also:
        - math.add(): 标准库中的加法函数
        - operator.add(): 运算符模块中的加法函数
    """
    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("参数必须是整数")
    
    return x + y


# =============================================================================
# 8. 实际项目中的注释示例
# =============================================================================

class BankAccount:
    """
    银行账户类。
    
    这个类模拟了一个简单的银行账户，支持存款、取款和查询余额等操作。
    所有的金额操作都会记录到交易历史中。
    
    Attributes:
        account_number (str): 账户号码
        balance (float): 当前余额
        transaction_history (List[Dict]): 交易历史记录
    """
    
    def __init__(self, account_number: str, initial_balance: float = 0.0):
        """
        初始化银行账户。
        
        Args:
            account_number: 账户号码，必须是唯一的
            initial_balance: 初始余额，默认为0.0
        
        Raises:
            ValueError: 当初始余额为负数时
        """
        if initial_balance < 0:
            raise ValueError("初始余额不能为负数")
        
        self.account_number = account_number
        self.balance = initial_balance
        self.transaction_history = []
        
        # 记录账户创建的交易
        if initial_balance > 0:
            self._add_transaction("开户存款", initial_balance)
    
    def deposit(self, amount: float) -> None:
        """
        存款操作。
        
        Args:
            amount: 存款金额，必须为正数
        
        Raises:
            ValueError: 当存款金额不是正数时
        """
        if amount <= 0:
            raise ValueError("存款金额必须为正数")
        
        self.balance += amount
        self._add_transaction("存款", amount)
    
    def withdraw(self, amount: float) -> bool:
        """
        取款操作。
        
        Args:
            amount: 取款金额，必须为正数
        
        Returns:
            取款是否成功
        
        Raises:
            ValueError: 当取款金额不是正数时
        """
        if amount <= 0:
            raise ValueError("取款金额必须为正数")
        
        # 检查余额是否充足
        if amount > self.balance:
            return False
        
        self.balance -= amount
        self._add_transaction("取款", -amount)
        return True
    
    def _add_transaction(self, transaction_type: str, amount: float) -> None:
        """
        添加交易记录（私有方法）。
        
        Args:
            transaction_type: 交易类型
            amount: 交易金额（正数表示收入，负数表示支出）
        """
        import datetime
        
        transaction = {
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.balance,
            "timestamp": datetime.datetime.now()
        }
        self.transaction_history.append(transaction)


# =============================================================================
# 9. 注释的维护和更新
# =============================================================================

def version_controlled_function():
    """
    版本控制的函数示例。
    
    Version History:
        v1.0 (2024-01-01): 初始版本
        v1.1 (2024-01-15): 添加了错误处理
        v1.2 (2024-02-01): 优化了性能
    
    TODO:
        - 添加更多的输入验证
        - 支持异步操作
        - 添加缓存机制
    
    CHANGELOG:
        - 2024-02-01: 修复了边界条件的bug
        - 2024-01-15: 改进了错误消息的可读性
    """
    pass


# =============================================================================
# 测试和演示
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Python注释规范演示")
    print("=" * 60)
    
    # 演示函数文档字符串的访问
    print("函数文档字符串:")
    print(calculate_rectangle_area.__doc__)
    
    print("\n" + "-" * 40)
    
    # 演示类文档字符串的访问
    print("类文档字符串:")
    print(Person.__doc__)
    
    print("\n" + "-" * 40)
    
    # 创建Person实例并测试
    person = Person("李四", 30)
    print(f"创建的人员信息: {person.get_info()}")
    
    # 演示银行账户类
    print("\n" + "-" * 40)
    print("银行账户演示:")
    
    account = BankAccount("123456789", 1000.0)
    print(f"初始余额: {account.balance}")
    
    account.deposit(500.0)
    print(f"存款后余额: {account.balance}")
    
    success = account.withdraw(200.0)
    print(f"取款成功: {success}, 余额: {account.balance}")
    
    print(f"交易历史记录数: {len(account.transaction_history)}")
    
    print("\n" + "=" * 60)
    print("注释规范学习完成！")
    print("=" * 60)
    
    print("\n重要提示:")
    print("1. 好的注释解释'为什么'，而不是'是什么'")
    print("2. 保持注释与代码同步")
    print("3. 使用标准的文档字符串格式")
    print("4. 避免显而易见的注释")
    print("5. 定期更新和维护注释")