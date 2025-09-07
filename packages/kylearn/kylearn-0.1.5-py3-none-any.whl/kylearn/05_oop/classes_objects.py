"""
面向对象编程 - 类和对象示例

本模块演示Python中类和对象的基本概念，包括：
1. 类的定义和实例化
2. 构造函数(__init__)的使用
3. 实例方法和类方法
4. 类属性和实例属性的区别
5. 属性访问和修改
6. 特殊方法(魔术方法)的使用
"""


# ============================================================================
# 1. 基本类定义和实例化
# ============================================================================

class Person:
    """
    人员类 - 演示基本的类定义
    
    这是一个简单的类定义示例，展示了类的基本结构
    """
    
    def __init__(self, name, age):
        """
        构造函数 - 创建对象时自动调用
        
        Args:
            name (str): 姓名
            age (int): 年龄
        """
        self.name = name  # 实例属性
        self.age = age    # 实例属性
    
    def introduce(self):
        """
        实例方法 - 介绍自己
        
        Returns:
            str: 自我介绍的字符串
        """
        return f"你好，我是{self.name}，今年{self.age}岁。"
    
    def have_birthday(self):
        """
        实例方法 - 过生日，年龄增加1
        """
        self.age += 1
        print(f"{self.name}过生日了！现在{self.age}岁了。")


def demo_basic_class():
    """演示基本类的使用"""
    print("=== 基本类定义和实例化 ===")
    
    # 创建对象实例
    person1 = Person("张三", 25)
    person2 = Person("李四", 30)
    
    # 访问实例属性
    print(f"person1的姓名: {person1.name}")
    print(f"person1的年龄: {person1.age}")
    
    # 调用实例方法
    print(person1.introduce())
    print(person2.introduce())
    
    # 修改属性
    person1.age = 26
    print(f"修改后person1的年龄: {person1.age}")
    
    # 调用方法修改属性
    person1.have_birthday()
    
    print()


# ============================================================================
# 2. 类属性 vs 实例属性
# ============================================================================

class Student:
    """
    学生类 - 演示类属性和实例属性的区别
    """
    
    # 类属性 - 所有实例共享
    school_name = "Python学习学院"
    student_count = 0  # 记录学生总数
    
    def __init__(self, name, student_id, grade):
        """
        构造函数
        
        Args:
            name (str): 学生姓名
            student_id (str): 学号
            grade (str): 年级
        """
        # 实例属性 - 每个实例独有
        self.name = name
        self.student_id = student_id
        self.grade = grade
        self.courses = []  # 选修课程列表
        
        # 每创建一个学生，总数加1
        Student.student_count += 1
    
    def add_course(self, course):
        """
        添加课程
        
        Args:
            course (str): 课程名称
        """
        self.courses.append(course)
        print(f"{self.name}选修了课程：{course}")
    
    def get_info(self):
        """
        获取学生信息
        
        Returns:
            str: 学生详细信息
        """
        courses_str = "、".join(self.courses) if self.courses else "无"
        return (f"学校：{self.school_name}\n"
                f"姓名：{self.name}\n"
                f"学号：{self.student_id}\n"
                f"年级：{self.grade}\n"
                f"选修课程：{courses_str}")
    
    @classmethod
    def get_student_count(cls):
        """
        类方法 - 获取学生总数
        
        Returns:
            int: 学生总数
        """
        return cls.student_count
    
    @classmethod
    def change_school_name(cls, new_name):
        """
        类方法 - 修改学校名称
        
        Args:
            new_name (str): 新的学校名称
        """
        cls.school_name = new_name
        print(f"学校名称已更改为：{new_name}")
    
    @staticmethod
    def is_valid_student_id(student_id):
        """
        静态方法 - 验证学号格式
        
        Args:
            student_id (str): 学号
            
        Returns:
            bool: 学号是否有效
        """
        return len(student_id) == 8 and student_id.isdigit()


def demo_class_vs_instance_attributes():
    """演示类属性和实例属性的区别"""
    print("=== 类属性 vs 实例属性 ===")
    
    # 创建学生实例
    student1 = Student("王五", "20230001", "一年级")
    student2 = Student("赵六", "20230002", "二年级")
    
    # 访问类属性
    print(f"学校名称：{Student.school_name}")
    print(f"学生总数：{Student.get_student_count()}")
    
    # 实例也可以访问类属性
    print(f"student1的学校：{student1.school_name}")
    print(f"student2的学校：{student2.school_name}")
    
    # 修改类属性会影响所有实例
    Student.change_school_name("高级Python学院")
    print(f"修改后student1的学校：{student1.school_name}")
    print(f"修改后student2的学校：{student2.school_name}")
    
    # 添加课程（实例属性）
    student1.add_course("Python基础")
    student1.add_course("数据结构")
    student2.add_course("算法设计")
    
    # 显示学生信息
    print("\n学生1信息：")
    print(student1.get_info())
    print("\n学生2信息：")
    print(student2.get_info())
    
    # 使用静态方法
    print(f"\n学号验证：")
    print(f"20230001是否有效：{Student.is_valid_student_id('20230001')}")
    print(f"123是否有效：{Student.is_valid_student_id('123')}")
    
    print()


# ============================================================================
# 3. 特殊方法(魔术方法)示例
# ============================================================================

class Book:
    """
    图书类 - 演示特殊方法的使用
    """
    
    def __init__(self, title, author, pages, price):
        """
        构造函数
        
        Args:
            title (str): 书名
            author (str): 作者
            pages (int): 页数
            price (float): 价格
        """
        self.title = title
        self.author = author
        self.pages = pages
        self.price = price
    
    def __str__(self):
        """
        字符串表示 - 用于print()函数
        
        Returns:
            str: 用户友好的字符串表示
        """
        return f"《{self.title}》- {self.author}"
    
    def __repr__(self):
        """
        官方字符串表示 - 用于调试
        
        Returns:
            str: 开发者友好的字符串表示
        """
        return f"Book('{self.title}', '{self.author}', {self.pages}, {self.price})"
    
    def __len__(self):
        """
        长度方法 - 返回页数
        
        Returns:
            int: 书的页数
        """
        return self.pages
    
    def __eq__(self, other):
        """
        相等比较
        
        Args:
            other (Book): 另一本书
            
        Returns:
            bool: 是否相等
        """
        if not isinstance(other, Book):
            return False
        return (self.title == other.title and 
                self.author == other.author)
    
    def __lt__(self, other):
        """
        小于比较 - 按价格比较
        
        Args:
            other (Book): 另一本书
            
        Returns:
            bool: 是否小于
        """
        if not isinstance(other, Book):
            return NotImplemented
        return self.price < other.price
    
    def __add__(self, other):
        """
        加法运算 - 合并两本书的页数
        
        Args:
            other (Book): 另一本书
            
        Returns:
            int: 总页数
        """
        if not isinstance(other, Book):
            return NotImplemented
        return self.pages + other.pages
    
    def __getitem__(self, key):
        """
        索引访问 - 模拟访问书的属性
        
        Args:
            key (str): 属性名
            
        Returns:
            任意类型: 属性值
        """
        if key == "title":
            return self.title
        elif key == "author":
            return self.author
        elif key == "pages":
            return self.pages
        elif key == "price":
            return self.price
        else:
            raise KeyError(f"Book对象没有属性'{key}'")
    
    def __contains__(self, item):
        """
        成员测试 - 检查书名或作者中是否包含某个词
        
        Args:
            item (str): 要查找的词
            
        Returns:
            bool: 是否包含
        """
        return item in self.title or item in self.author


def demo_special_methods():
    """演示特殊方法的使用"""
    print("=== 特殊方法(魔术方法)示例 ===")
    
    # 创建图书对象
    book1 = Book("Python编程从入门到实践", "埃里克·马瑟斯", 500, 89.0)
    book2 = Book("流畅的Python", "卢西亚诺·拉马略", 600, 99.0)
    book3 = Book("Python编程从入门到实践", "埃里克·马瑟斯", 500, 89.0)
    
    # __str__ 和 __repr__
    print(f"str(book1): {str(book1)}")
    print(f"repr(book1): {repr(book1)}")
    
    # __len__
    print(f"len(book1): {len(book1)}页")
    
    # __eq__
    print(f"book1 == book2: {book1 == book2}")
    print(f"book1 == book3: {book1 == book3}")
    
    # __lt__
    print(f"book1 < book2: {book1 < book2}")
    
    # __add__
    total_pages = book1 + book2
    print(f"book1 + book2 = {total_pages}页")
    
    # __getitem__
    print(f"book1['title']: {book1['title']}")
    print(f"book1['price']: {book1['price']}")
    
    # __contains__
    print(f"'Python' in book1: {'Python' in book1}")
    print(f"'Java' in book1: {'Java' in book1}")
    
    print()


# ============================================================================
# 4. 综合示例：银行账户类
# ============================================================================

class BankAccount:
    """
    银行账户类 - 综合演示面向对象编程概念
    """
    
    # 类属性
    bank_name = "Python银行"
    interest_rate = 0.03  # 年利率3%
    account_count = 0
    
    def __init__(self, account_holder, initial_balance=0):
        """
        构造函数
        
        Args:
            account_holder (str): 账户持有人
            initial_balance (float): 初始余额，默认为0
        """
        self.account_holder = account_holder
        self._balance = initial_balance  # 使用下划线表示"私有"属性
        self._transaction_history = []   # 交易历史
        
        # 生成账户号码
        BankAccount.account_count += 1
        self.account_number = f"ACC{BankAccount.account_count:06d}"
        
        # 记录开户交易
        self._add_transaction("开户", initial_balance)
    
    def deposit(self, amount):
        """
        存款
        
        Args:
            amount (float): 存款金额
            
        Returns:
            bool: 操作是否成功
        """
        if amount <= 0:
            print("存款金额必须大于0")
            return False
        
        self._balance += amount
        self._add_transaction("存款", amount)
        print(f"成功存款 {amount:.2f} 元，当前余额：{self._balance:.2f} 元")
        return True
    
    def withdraw(self, amount):
        """
        取款
        
        Args:
            amount (float): 取款金额
            
        Returns:
            bool: 操作是否成功
        """
        if amount <= 0:
            print("取款金额必须大于0")
            return False
        
        if amount > self._balance:
            print(f"余额不足！当前余额：{self._balance:.2f} 元")
            return False
        
        self._balance -= amount
        self._add_transaction("取款", -amount)
        print(f"成功取款 {amount:.2f} 元，当前余额：{self._balance:.2f} 元")
        return True
    
    def get_balance(self):
        """
        获取余额
        
        Returns:
            float: 当前余额
        """
        return self._balance
    
    def _add_transaction(self, transaction_type, amount):
        """
        添加交易记录（私有方法）
        
        Args:
            transaction_type (str): 交易类型
            amount (float): 交易金额
        """
        from datetime import datetime
        transaction = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "类型": transaction_type,
            "金额": amount,
            "余额": self._balance
        }
        self._transaction_history.append(transaction)
    
    def get_transaction_history(self):
        """
        获取交易历史
        
        Returns:
            list: 交易历史列表
        """
        return self._transaction_history.copy()  # 返回副本，保护原数据
    
    def calculate_interest(self, months):
        """
        计算利息
        
        Args:
            months (int): 存款月数
            
        Returns:
            float: 利息金额
        """
        monthly_rate = self.interest_rate / 12
        interest = self._balance * monthly_rate * months
        return interest
    
    def __str__(self):
        """字符串表示"""
        return f"账户号：{self.account_number}，持有人：{self.account_holder}，余额：{self._balance:.2f}元"
    
    def __repr__(self):
        """官方字符串表示"""
        return f"BankAccount('{self.account_holder}', {self._balance})"
    
    @classmethod
    def get_bank_info(cls):
        """
        获取银行信息
        
        Returns:
            str: 银行信息
        """
        return f"银行：{cls.bank_name}，年利率：{cls.interest_rate*100}%，总账户数：{cls.account_count}"


def demo_bank_account():
    """演示银行账户类的使用"""
    print("=== 综合示例：银行账户类 ===")
    
    # 创建账户
    account1 = BankAccount("张三", 1000)
    account2 = BankAccount("李四", 500)
    
    print(account1)
    print(account2)
    print(BankAccount.get_bank_info())
    print()
    
    # 进行交易
    account1.deposit(500)
    account1.withdraw(200)
    account1.withdraw(2000)  # 余额不足的情况
    
    print(f"张三的余额：{account1.get_balance():.2f} 元")
    
    # 计算利息
    interest = account1.calculate_interest(12)
    print(f"存款12个月的利息：{interest:.2f} 元")
    
    # 查看交易历史
    print("\n交易历史：")
    for transaction in account1.get_transaction_history():
        print(f"{transaction['时间']} - {transaction['类型']}: {transaction['金额']:.2f}元, 余额: {transaction['余额']:.2f}元")
    
    print()


# ============================================================================
# 5. 更多特殊方法示例
# ============================================================================

class MagicNumber:
    """
    魔术数字类 - 演示更多特殊方法的使用
    """
    
    def __init__(self, value):
        """
        构造函数
        
        Args:
            value (int/float): 数值
        """
        self.value = value
    
    def __str__(self):
        """用户友好的字符串表示"""
        return f"MagicNumber({self.value})"
    
    def __repr__(self):
        """开发者友好的字符串表示"""
        return f"MagicNumber({self.value!r})"
    
    def __int__(self):
        """转换为整数"""
        return int(self.value)
    
    def __float__(self):
        """转换为浮点数"""
        return float(self.value)
    
    def __bool__(self):
        """转换为布尔值"""
        return self.value != 0
    
    def __abs__(self):
        """绝对值"""
        return MagicNumber(abs(self.value))
    
    def __neg__(self):
        """负号"""
        return MagicNumber(-self.value)
    
    def __pos__(self):
        """正号"""
        return MagicNumber(+self.value)
    
    def __round__(self, n=0):
        """四舍五入"""
        return MagicNumber(round(self.value, n))
    
    def __add__(self, other):
        """加法"""
        if isinstance(other, MagicNumber):
            return MagicNumber(self.value + other.value)
        elif isinstance(other, (int, float)):
            return MagicNumber(self.value + other)
        return NotImplemented
    
    def __radd__(self, other):
        """右加法(当左操作数不支持加法时)"""
        return self.__add__(other)
    
    def __sub__(self, other):
        """减法"""
        if isinstance(other, MagicNumber):
            return MagicNumber(self.value - other.value)
        elif isinstance(other, (int, float)):
            return MagicNumber(self.value - other)
        return NotImplemented
    
    def __mul__(self, other):
        """乘法"""
        if isinstance(other, MagicNumber):
            return MagicNumber(self.value * other.value)
        elif isinstance(other, (int, float)):
            return MagicNumber(self.value * other)
        return NotImplemented
    
    def __rmul__(self, other):
        """右乘法"""
        return self.__mul__(other)
    
    def __truediv__(self, other):
        """除法"""
        if isinstance(other, MagicNumber):
            if other.value == 0:
                raise ZeroDivisionError("除数不能为零")
            return MagicNumber(self.value / other.value)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("除数不能为零")
            return MagicNumber(self.value / other)
        return NotImplemented
    
    def __pow__(self, other):
        """幂运算"""
        if isinstance(other, MagicNumber):
            return MagicNumber(self.value ** other.value)
        elif isinstance(other, (int, float)):
            return MagicNumber(self.value ** other)
        return NotImplemented
    
    def __eq__(self, other):
        """相等比较"""
        if isinstance(other, MagicNumber):
            return self.value == other.value
        elif isinstance(other, (int, float)):
            return self.value == other
        return False
    
    def __lt__(self, other):
        """小于比较"""
        if isinstance(other, MagicNumber):
            return self.value < other.value
        elif isinstance(other, (int, float)):
            return self.value < other
        return NotImplemented
    
    def __le__(self, other):
        """小于等于比较"""
        return self == other or self < other
    
    def __gt__(self, other):
        """大于比较"""
        if isinstance(other, MagicNumber):
            return self.value > other.value
        elif isinstance(other, (int, float)):
            return self.value > other
        return NotImplemented
    
    def __ge__(self, other):
        """大于等于比较"""
        return self == other or self > other
    
    def __hash__(self):
        """哈希值(使对象可以作为字典键或集合元素)"""
        return hash(self.value)


class SmartList:
    """
    智能列表类 - 演示容器相关的特殊方法
    """
    
    def __init__(self, items=None):
        """
        构造函数
        
        Args:
            items (list): 初始项目列表
        """
        self._items = list(items) if items else []
    
    def __len__(self):
        """返回列表长度"""
        return len(self._items)
    
    def __getitem__(self, index):
        """
        获取项目 - 支持索引和切片
        
        Args:
            index (int/slice): 索引或切片
            
        Returns:
            任意类型: 项目或SmartList(切片时)
        """
        if isinstance(index, slice):
            return SmartList(self._items[index])
        return self._items[index]
    
    def __setitem__(self, index, value):
        """
        设置项目
        
        Args:
            index (int): 索引
            value: 新值
        """
        self._items[index] = value
    
    def __delitem__(self, index):
        """
        删除项目
        
        Args:
            index (int): 索引
        """
        del self._items[index]
    
    def __contains__(self, item):
        """
        成员测试
        
        Args:
            item: 要查找的项目
            
        Returns:
            bool: 是否包含
        """
        return item in self._items
    
    def __iter__(self):
        """
        返回迭代器
        
        Returns:
            iterator: 迭代器对象
        """
        return iter(self._items)
    
    def __reversed__(self):
        """
        返回反向迭代器
        
        Returns:
            iterator: 反向迭代器
        """
        return reversed(self._items)
    
    def __add__(self, other):
        """
        列表连接
        
        Args:
            other (SmartList/list): 另一个列表
            
        Returns:
            SmartList: 连接后的新列表
        """
        if isinstance(other, SmartList):
            return SmartList(self._items + other._items)
        elif isinstance(other, list):
            return SmartList(self._items + other)
        return NotImplemented
    
    def __mul__(self, count):
        """
        列表重复
        
        Args:
            count (int): 重复次数
            
        Returns:
            SmartList: 重复后的新列表
        """
        if isinstance(count, int):
            return SmartList(self._items * count)
        return NotImplemented
    
    def __rmul__(self, count):
        """右乘法"""
        return self.__mul__(count)
    
    def __str__(self):
        """字符串表示"""
        return f"SmartList({self._items})"
    
    def __repr__(self):
        """官方字符串表示"""
        return f"SmartList({self._items!r})"
    
    def __eq__(self, other):
        """相等比较"""
        if isinstance(other, SmartList):
            return self._items == other._items
        elif isinstance(other, list):
            return self._items == other
        return False
    
    def append(self, item):
        """添加项目"""
        self._items.append(item)
    
    def extend(self, items):
        """扩展列表"""
        self._items.extend(items)
    
    def remove(self, item):
        """移除项目"""
        self._items.remove(item)
    
    def pop(self, index=-1):
        """弹出项目"""
        return self._items.pop(index)
    
    def clear(self):
        """清空列表"""
        self._items.clear()


class CallableClass:
    """
    可调用类 - 演示__call__方法
    """
    
    def __init__(self, name, operation="add"):
        """
        构造函数
        
        Args:
            name (str): 计算器名称
            operation (str): 默认操作
        """
        self.name = name
        self.operation = operation
        self.history = []
    
    def __call__(self, a, b=None, operation=None):
        """
        使对象可以像函数一样调用
        
        Args:
            a (float): 第一个操作数
            b (float): 第二个操作数(可选)
            operation (str): 操作类型(可选)
            
        Returns:
            float: 计算结果
        """
        op = operation or self.operation
        
        if b is None:
            # 一元操作
            if op == "abs":
                result = abs(a)
            elif op == "neg":
                result = -a
            elif op == "square":
                result = a ** 2
            else:
                raise ValueError(f"不支持的一元操作：{op}")
        else:
            # 二元操作
            if op == "add":
                result = a + b
            elif op == "sub":
                result = a - b
            elif op == "mul":
                result = a * b
            elif op == "div":
                if b == 0:
                    raise ZeroDivisionError("除数不能为零")
                result = a / b
            elif op == "pow":
                result = a ** b
            else:
                raise ValueError(f"不支持的二元操作：{op}")
        
        # 记录历史
        if b is None:
            operation_str = f"{op}({a}) = {result}"
        else:
            operation_str = f"{a} {op} {b} = {result}"
        
        self.history.append(operation_str)
        
        return result
    
    def get_history(self):
        """获取计算历史"""
        return self.history.copy()
    
    def clear_history(self):
        """清空历史"""
        self.history.clear()
    
    def __str__(self):
        """字符串表示"""
        return f"{self.name}计算器(默认操作:{self.operation})"


def demo_advanced_special_methods():
    """演示更多特殊方法"""
    print("=== 更多特殊方法示例 ===")
    
    # MagicNumber示例
    print("=== MagicNumber类 ===")
    num1 = MagicNumber(10)
    num2 = MagicNumber(3)
    
    print(f"num1 = {num1}")
    print(f"num2 = {num2}")
    
    # 算术运算
    print(f"\n算术运算：")
    print(f"num1 + num2 = {num1 + num2}")
    print(f"num1 - num2 = {num1 - num2}")
    print(f"num1 * num2 = {num1 * num2}")
    print(f"num1 / num2 = {num1 / num2}")
    print(f"num1 ** num2 = {num1 ** num2}")
    
    # 与普通数字运算
    print(f"\n与普通数字运算：")
    print(f"num1 + 5 = {num1 + 5}")
    print(f"2 * num1 = {2 * num1}")
    
    # 一元运算
    print(f"\n一元运算：")
    print(f"-num1 = {-num1}")
    print(f"abs(MagicNumber(-7)) = {abs(MagicNumber(-7))}")
    print(f"round(MagicNumber(3.7)) = {round(MagicNumber(3.7))}")
    
    # 比较运算
    print(f"\n比较运算：")
    print(f"num1 == 10: {num1 == 10}")
    print(f"num1 > num2: {num1 > num2}")
    print(f"num1 <= 15: {num1 <= 15}")
    
    # 类型转换
    print(f"\n类型转换：")
    print(f"int(num1) = {int(num1)}")
    print(f"float(num1) = {float(num1)}")
    print(f"bool(MagicNumber(0)) = {bool(MagicNumber(0))}")
    print(f"bool(num1) = {bool(num1)}")
    
    # 哈希和集合
    print(f"\n哈希和集合：")
    num_set = {num1, MagicNumber(10), MagicNumber(20)}
    print(f"集合：{num_set}")
    print(f"集合长度：{len(num_set)}")  # 应该是2，因为两个10相等
    
    # SmartList示例
    print(f"\n=== SmartList类 ===")
    smart_list = SmartList([1, 2, 3, 4, 5])
    print(f"smart_list = {smart_list}")
    print(f"长度：{len(smart_list)}")
    
    # 索引和切片
    print(f"\n索引和切片：")
    print(f"smart_list[0] = {smart_list[0]}")
    print(f"smart_list[1:3] = {smart_list[1:3]}")
    print(f"smart_list[-1] = {smart_list[-1]}")
    
    # 修改操作
    smart_list[0] = 10
    print(f"修改后：{smart_list}")
    
    # 成员测试
    print(f"\n成员测试：")
    print(f"10 in smart_list: {10 in smart_list}")
    print(f"99 in smart_list: {99 in smart_list}")
    
    # 迭代
    print(f"\n正向迭代：")
    for item in smart_list:
        print(f"  {item}")
    
    print(f"反向迭代：")
    for item in reversed(smart_list):
        print(f"  {item}")
    
    # 列表操作
    print(f"\n列表操作：")
    list2 = SmartList([6, 7, 8])
    combined = smart_list + list2
    print(f"连接：{combined}")
    
    repeated = smart_list * 2
    print(f"重复：{repeated}")
    
    # CallableClass示例
    print(f"\n=== CallableClass类 ===")
    calculator = CallableClass("我的", "add")
    print(f"计算器：{calculator}")
    
    # 像函数一样调用
    print(f"\n计算示例：")
    result1 = calculator(10, 5)  # 默认加法
    print(f"10 + 5 = {result1}")
    
    result2 = calculator(10, 3, "mul")  # 乘法
    print(f"10 * 3 = {result2}")
    
    result3 = calculator(25, operation="square")  # 平方
    print(f"25的平方 = {result3}")
    
    result4 = calculator(-7, operation="abs")  # 绝对值
    print(f"|-7| = {result4}")
    
    # 查看历史
    print(f"\n计算历史：")
    for record in calculator.get_history():
        print(f"  {record}")
    
    print()


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

def main():
    """运行所有示例"""
    print("Python面向对象编程 - 类和对象示例")
    print("=" * 50)
    
    demo_basic_class()
    demo_class_vs_instance_attributes()
    demo_special_methods()
    demo_bank_account()
    demo_advanced_special_methods()
    
    print("所有示例运行完成！")


if __name__ == "__main__":
    main()