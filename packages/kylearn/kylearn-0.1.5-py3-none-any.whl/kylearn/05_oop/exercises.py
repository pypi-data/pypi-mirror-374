"""
面向对象编程 - 练习题

本模块包含面向对象编程的练习题，涵盖：
1. 类设计和OOP原则练习
2. 继承和多态练习
3. 封装和属性管理练习
4. 实际项目中的类设计练习
5. 设计模式的基础介绍和练习

每个练习都包含题目描述、参考答案和详细解释
"""

from abc import ABC, abstractmethod
import math
from datetime import datetime, timedelta


# ============================================================================
# 练习1：基础类设计 - 学生管理系统
# ============================================================================

def exercise_1():
    """
    练习1：设计一个学生管理系统
    
    要求：
    1. 创建Student类，包含姓名、学号、年龄、成绩列表等属性
    2. 实现添加成绩、计算平均分、获取学生信息等方法
    3. 实现适当的特殊方法(__str__, __repr__, __eq__等)
    4. 创建StudentManager类来管理多个学生
    """
    print("=== 练习1：学生管理系统 ===")
    
    class Student:
        """学生类"""
        
        def __init__(self, name, student_id, age):
            """
            构造函数
            
            Args:
                name (str): 姓名
                student_id (str): 学号
                age (int): 年龄
            """
            self.name = name
            self.student_id = student_id
            self.age = age
            self.grades = []  # 成绩列表
        
        def add_grade(self, subject, score):
            """
            添加成绩
            
            Args:
                subject (str): 科目
                score (float): 分数
            """
            if 0 <= score <= 100:
                self.grades.append({"subject": subject, "score": score})
                print(f"为{self.name}添加{subject}成绩：{score}分")
            else:
                print("成绩必须在0-100之间")
        
        def get_average_score(self):
            """
            计算平均分
            
            Returns:
                float: 平均分，如果没有成绩返回0
            """
            if not self.grades:
                return 0
            total = sum(grade["score"] for grade in self.grades)
            return total / len(self.grades)
        
        def get_info(self):
            """
            获取学生详细信息
            
            Returns:
                str: 学生信息
            """
            avg_score = self.get_average_score()
            grade_info = ", ".join([f"{g['subject']}:{g['score']}" for g in self.grades])
            return (f"姓名：{self.name}，学号：{self.student_id}，年龄：{self.age}，"
                   f"平均分：{avg_score:.2f}，成绩：{grade_info}")
        
        def __str__(self):
            """字符串表示"""
            return f"Student({self.name}, {self.student_id})"
        
        def __eq__(self, other):
            """相等比较 - 基于学号"""
            if isinstance(other, Student):
                return self.student_id == other.student_id
            return False
    
    # 测试代码
    print("创建学生...")
    student1 = Student("张三", "2023001", 20)
    student2 = Student("李四", "2023002", 19)
    
    # 添加成绩
    student1.add_grade("数学", 85)
    student1.add_grade("英语", 92)
    student2.add_grade("数学", 90)
    
    # 显示学生信息
    print(f"学生1：{student1.get_info()}")
    print(f"学生2：{student2.get_info()}")
    
    print()


# ============================================================================
# 练习2：继承和多态 - 图形计算系统
# ============================================================================

def exercise_2():
    """
    练习2：设计一个图形计算系统
    
    要求：
    1. 创建Shape抽象基类，定义计算面积和周长的抽象方法
    2. 实现Rectangle、Circle、Triangle等具体图形类
    3. 使用多态处理不同类型的图形
    """
    print("=== 练习2：图形计算系统 ===")
    
    class Shape(ABC):
        """图形抽象基类"""
        
        def __init__(self, name):
            self.name = name
        
        @abstractmethod
        def area(self):
            """计算面积 - 抽象方法"""
            pass
        
        @abstractmethod
        def perimeter(self):
            """计算周长 - 抽象方法"""
            pass
        
        def describe(self):
            """描述图形"""
            return f"{self.name}：面积={self.area():.2f}，周长={self.perimeter():.2f}"
    
    class Rectangle(Shape):
        """矩形类"""
        
        def __init__(self, width, height):
            super().__init__("矩形")
            self.width = width
            self.height = height
        
        def area(self):
            return self.width * self.height
        
        def perimeter(self):
            return 2 * (self.width + self.height)
    
    class Circle(Shape):
        """圆形类"""
        
        def __init__(self, radius):
            super().__init__("圆形")
            self.radius = radius
        
        def area(self):
            return math.pi * self.radius ** 2
        
        def perimeter(self):
            return 2 * math.pi * self.radius
    
    # 测试代码
    shapes = [
        Rectangle(5, 3),
        Circle(4),
        Rectangle(6, 6)  # 正方形
    ]
    
    print("图形信息：")
    for i, shape in enumerate(shapes, 1):
        print(f"  {i}. {shape.describe()}")
    
    # 计算总面积 - 多态应用
    total_area = sum(shape.area() for shape in shapes)
    print(f"总面积：{total_area:.2f}")
    
    print()


# ============================================================================
# 练习3：封装和属性管理 - 银行账户
# ============================================================================

def exercise_3():
    """
    练习3：设计一个银行账户类
    
    要求：
    1. 使用属性装饰器管理账户余额
    2. 实现存款、取款等方法
    3. 使用封装保护敏感信息
    """
    print("=== 练习3：银行账户系统 ===")
    
    class BankAccount:
        """银行账户类"""
        
        def __init__(self, account_number, account_holder, initial_balance=0):
            self.account_number = account_number
            self.account_holder = account_holder
            self._balance = initial_balance  # 私有属性
        
        @property
        def balance(self):
            """余额属性 - 只读"""
            return self._balance
        
        def deposit(self, amount):
            """存款"""
            if amount > 0:
                self._balance += amount
                print(f"存款成功：{amount:.2f}元，当前余额：{self._balance:.2f}元")
                return True
            else:
                print("存款金额必须大于0")
                return False
        
        def withdraw(self, amount):
            """取款"""
            if amount <= 0:
                print("取款金额必须大于0")
                return False
            
            if amount > self._balance:
                print(f"余额不足！当前余额：{self._balance:.2f}元")
                return False
            
            self._balance -= amount
            print(f"取款成功：{amount:.2f}元，当前余额：{self._balance:.2f}元")
            return True
        
        def __str__(self):
            return f"账户{self.account_number}({self.account_holder}) - 余额:{self._balance:.2f}元"
    
    # 测试代码
    account = BankAccount("ACC001", "张三", 1000)
    print(f"创建账户：{account}")
    
    account.deposit(500)
    account.withdraw(200)
    account.withdraw(2000)  # 余额不足
    
    print(f"最终状态：{account}")
    print()


# ============================================================================
# 练习4：综合应用 - 简化的图书管理系统
# ============================================================================

def exercise_4():
    """
    练习4：设计一个简化的图书管理系统
    
    要求：
    1. 综合运用所有OOP概念
    2. 实现图书、用户、借阅等功能
    """
    print("=== 练习4：图书管理系统 ===")
    
    class Book:
        """图书类"""
        
        def __init__(self, title, author, isbn):
            self.title = title
            self.author = author
            self.isbn = isbn
            self.is_borrowed = False
        
        def borrow(self):
            """借出图书"""
            if not self.is_borrowed:
                self.is_borrowed = True
                return True
            return False
        
        def return_book(self):
            """归还图书"""
            if self.is_borrowed:
                self.is_borrowed = False
                return True
            return False
        
        def __str__(self):
            status = "已借出" if self.is_borrowed else "可借"
            return f"《{self.title}》- {self.author} ({status})"
    
    class Library:
        """图书馆类"""
        
        def __init__(self):
            self.books = {}  # ISBN -> Book
            self.borrowed_books = {}  # user -> [books]
        
        def add_book(self, book):
            """添加图书"""
            self.books[book.isbn] = book
            print(f"添加图书：{book}")
        
        def borrow_book(self, user, isbn):
            """借书"""
            if isbn not in self.books:
                print("图书不存在")
                return False
            
            book = self.books[isbn]
            if book.borrow():
                if user not in self.borrowed_books:
                    self.borrowed_books[user] = []
                self.borrowed_books[user].append(book)
                print(f"{user}成功借阅《{book.title}》")
                return True
            else:
                print(f"《{book.title}》已被借出")
                return False
        
        def return_book(self, user, isbn):
            """还书"""
            if user in self.borrowed_books:
                for book in self.borrowed_books[user]:
                    if book.isbn == isbn:
                        book.return_book()
                        self.borrowed_books[user].remove(book)
                        print(f"{user}成功归还《{book.title}》")
                        return True
            
            print("未找到借阅记录")
            return False
        
        def list_books(self):
            """列出所有图书"""
            print("图书列表：")
            for book in self.books.values():
                print(f"  {book}")
    
    # 测试代码
    library = Library()
    
    # 添加图书
    books = [
        Book("Python编程", "作者A", "001"),
        Book("数据结构", "作者B", "002"),
        Book("算法导论", "作者C", "003")
    ]
    
    for book in books:
        library.add_book(book)
    
    print()
    library.list_books()
    
    # 借书还书操作
    print(f"\n=== 借书操作 ===")
    library.borrow_book("张三", "001")
    library.borrow_book("李四", "002")
    library.borrow_book("王五", "001")  # 已被借出
    
    print()
    library.list_books()
    
    print(f"\n=== 还书操作 ===")
    library.return_book("张三", "001")
    
    print()
    library.list_books()
    
    print()


def main():
    """运行所有练习"""
    print("Python面向对象编程 - 练习题")
    print("=" * 60)
    
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    
    print("所有练习完成！")
    print("\n练习总结：")
    print("1. 学生管理系统 - 基础类设计和特殊方法")
    print("2. 图形计算系统 - 继承、多态和抽象基类")
    print("3. 银行账户系统 - 封装和属性管理")
    print("4. 图书管理系统 - 综合OOP概念应用")


if __name__ == "__main__":
    main()