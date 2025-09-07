"""
面向对象编程 - 封装示例

本模块演示Python中封装的概念和实现，包括：
1. 私有属性和方法的约定
2. 属性装饰器(@property)的使用
3. getter、setter、deleter方法
4. 数据隐藏和访问控制
5. 接口设计原则
6. 封装的最佳实践
"""


# ============================================================================
# 1. 基本封装概念 - 私有属性和方法
# ============================================================================

class BankAccount:
    """
    银行账户类 - 演示基本封装概念
    
    使用下划线约定来表示私有属性和方法
    """
    
    def __init__(self, account_number, initial_balance=0):
        """
        构造函数
        
        Args:
            account_number (str): 账户号码
            initial_balance (float): 初始余额
        """
        self.account_number = account_number  # 公开属性
        self._balance = initial_balance       # 受保护属性(单下划线)
        self.__pin = "1234"                  # 私有属性(双下划线)
        self.__transaction_count = 0         # 私有属性
    
    def deposit(self, amount):
        """
        存款 - 公开方法
        
        Args:
            amount (float): 存款金额
            
        Returns:
            bool: 操作是否成功
        """
        if self.__validate_amount(amount):
            self._balance += amount
            self.__record_transaction("存款", amount)
            print(f"存款成功：{amount:.2f}元，余额：{self._balance:.2f}元")
            return True
        return False
    
    def withdraw(self, amount, pin):
        """
        取款 - 需要验证PIN码
        
        Args:
            amount (float): 取款金额
            pin (str): PIN码
            
        Returns:
            bool: 操作是否成功
        """
        if not self.__verify_pin(pin):
            print("PIN码错误")
            return False
        
        if not self.__validate_amount(amount):
            return False
        
        if amount > self._balance:
            print("余额不足")
            return False
        
        self._balance -= amount
        self.__record_transaction("取款", -amount)
        print(f"取款成功：{amount:.2f}元，余额：{self._balance:.2f}元")
        return True
    
    def get_balance(self, pin):
        """
        查询余额 - 需要验证PIN码
        
        Args:
            pin (str): PIN码
            
        Returns:
            float or None: 余额或None(验证失败)
        """
        if self.__verify_pin(pin):
            return self._balance
        else:
            print("PIN码错误")
            return None
    
    def change_pin(self, old_pin, new_pin):
        """
        修改PIN码
        
        Args:
            old_pin (str): 旧PIN码
            new_pin (str): 新PIN码
            
        Returns:
            bool: 操作是否成功
        """
        if not self.__verify_pin(old_pin):
            print("旧PIN码错误")
            return False
        
        if len(new_pin) != 4 or not new_pin.isdigit():
            print("新PIN码必须是4位数字")
            return False
        
        self.__pin = new_pin
        print("PIN码修改成功")
        return True
    
    def __validate_amount(self, amount):
        """
        验证金额 - 私有方法
        
        Args:
            amount (float): 金额
            
        Returns:
            bool: 金额是否有效
        """
        if amount <= 0:
            print("金额必须大于0")
            return False
        return True
    
    def __verify_pin(self, pin):
        """
        验证PIN码 - 私有方法
        
        Args:
            pin (str): PIN码
            
        Returns:
            bool: PIN码是否正确
        """
        return pin == self.__pin
    
    def __record_transaction(self, transaction_type, amount):
        """
        记录交易 - 私有方法
        
        Args:
            transaction_type (str): 交易类型
            amount (float): 交易金额
        """
        self.__transaction_count += 1
        print(f"交易记录：{transaction_type} {amount:.2f}元 (第{self.__transaction_count}笔)")
    
    def get_transaction_count(self):
        """
        获取交易次数 - 公开方法访问私有数据
        
        Returns:
            int: 交易次数
        """
        return self.__transaction_count


def demo_basic_encapsulation():
    """演示基本封装概念"""
    print("=== 基本封装概念 ===")
    
    account = BankAccount("ACC001", 1000)
    
    # 正常操作
    print("=== 正常操作 ===")
    account.deposit(500)
    account.withdraw(200, "1234")
    balance = account.get_balance("1234")
    print(f"当前余额：{balance:.2f}元")
    
    # 错误操作
    print("\n=== 错误操作 ===")
    account.withdraw(100, "0000")  # 错误PIN
    account.get_balance("0000")    # 错误PIN
    
    # 修改PIN码
    print("\n=== 修改PIN码 ===")
    account.change_pin("1234", "5678")
    account.withdraw(100, "5678")  # 使用新PIN
    
    # 访问属性
    print("\n=== 属性访问 ===")
    print(f"账户号码(公开)：{account.account_number}")
    print(f"余额(受保护)：{account._balance}")  # 可以访问但不推荐
    print(f"交易次数：{account.get_transaction_count()}")
    
    # 尝试访问私有属性
    print("\n=== 尝试访问私有属性 ===")
    try:
        print(account.__pin)  # 这会失败
    except AttributeError as e:
        print(f"无法直接访问私有属性：{e}")
    
    # 通过名称修饰访问私有属性(不推荐)
    print(f"通过名称修饰访问PIN(不推荐)：{account._BankAccount__pin}")
    
    print()


# ============================================================================
# 2. 属性装饰器(@property)的使用
# ============================================================================

class Temperature:
    """
    温度类 - 演示@property装饰器的使用
    """
    
    def __init__(self, celsius=0):
        """
        构造函数
        
        Args:
            celsius (float): 摄氏温度
        """
        self._celsius = celsius
    
    @property
    def celsius(self):
        """
        摄氏温度的getter
        
        Returns:
            float: 摄氏温度
        """
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """
        摄氏温度的setter
        
        Args:
            value (float): 摄氏温度值
            
        Raises:
            ValueError: 温度低于绝对零度
        """
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度(-273.15°C)")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """
        华氏温度的getter - 只读属性
        
        Returns:
            float: 华氏温度
        """
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """
        华氏温度的setter
        
        Args:
            value (float): 华氏温度值
        """
        self.celsius = (value - 32) * 5/9
    
    @property
    def kelvin(self):
        """
        开尔文温度的getter - 只读属性
        
        Returns:
            float: 开尔文温度
        """
        return self._celsius + 273.15
    
    @kelvin.setter
    def kelvin(self, value):
        """
        开尔文温度的setter
        
        Args:
            value (float): 开尔文温度值
        """
        self.celsius = value - 273.15
    
    def __str__(self):
        """字符串表示"""
        return f"{self._celsius:.2f}°C ({self.fahrenheit:.2f}°F, {self.kelvin:.2f}K)"


class Circle:
    """
    圆形类 - 演示计算属性和验证
    """
    
    def __init__(self, radius):
        """
        构造函数
        
        Args:
            radius (float): 半径
        """
        self._radius = None
        self.radius = radius  # 使用setter进行验证
    
    @property
    def radius(self):
        """
        半径的getter
        
        Returns:
            float: 半径
        """
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """
        半径的setter - 包含验证
        
        Args:
            value (float): 半径值
            
        Raises:
            ValueError: 半径必须为正数
        """
        if value <= 0:
            raise ValueError("半径必须为正数")
        self._radius = value
    
    @property
    def diameter(self):
        """
        直径 - 计算属性
        
        Returns:
            float: 直径
        """
        return self._radius * 2
    
    @diameter.setter
    def diameter(self, value):
        """
        通过直径设置半径
        
        Args:
            value (float): 直径值
        """
        self.radius = value / 2
    
    @property
    def area(self):
        """
        面积 - 只读计算属性
        
        Returns:
            float: 面积
        """
        import math
        return math.pi * self._radius ** 2
    
    @property
    def circumference(self):
        """
        周长 - 只读计算属性
        
        Returns:
            float: 周长
        """
        import math
        return 2 * math.pi * self._radius
    
    def __str__(self):
        """字符串表示"""
        return f"圆形(半径:{self._radius:.2f}, 面积:{self.area:.2f}, 周长:{self.circumference:.2f})"


def demo_property_decorator():
    """演示@property装饰器的使用"""
    print("=== @property装饰器使用示例 ===")
    
    # 温度转换示例
    print("=== 温度转换 ===")
    temp = Temperature(25)
    print(f"初始温度：{temp}")
    
    # 修改摄氏温度
    temp.celsius = 100
    print(f"设置为100°C：{temp}")
    
    # 通过华氏温度设置
    temp.fahrenheit = 32
    print(f"设置为32°F：{temp}")
    
    # 通过开尔文温度设置
    temp.kelvin = 373.15
    print(f"设置为373.15K：{temp}")
    
    # 验证错误处理
    try:
        temp.celsius = -300
    except ValueError as e:
        print(f"温度验证错误：{e}")
    
    # 圆形示例
    print("\n=== 圆形属性 ===")
    circle = Circle(5)
    print(f"初始圆形：{circle}")
    
    # 修改半径
    circle.radius = 10
    print(f"修改半径为10：{circle}")
    
    # 通过直径修改
    circle.diameter = 30
    print(f"设置直径为30：{circle}")
    
    # 尝试设置只读属性
    try:
        circle.area = 100  # 这会失败
    except AttributeError as e:
        print(f"无法设置只读属性：{e}")
    
    # 验证错误处理
    try:
        circle.radius = -5
    except ValueError as e:
        print(f"半径验证错误：{e}")
    
    print()


# ============================================================================
# 3. 高级封装示例 - 用户管理系统
# ============================================================================

class User:
    """
    用户类 - 演示完整的封装设计
    """
    
    def __init__(self, username, email, password):
        """
        构造函数
        
        Args:
            username (str): 用户名
            email (str): 邮箱
            password (str): 密码
        """
        self._username = None
        self._email = None
        self._password_hash = None
        self._is_active = True
        self._login_attempts = 0
        self._max_login_attempts = 3
        
        # 使用setter进行验证
        self.username = username
        self.email = email
        self.password = password
    
    @property
    def username(self):
        """
        用户名getter
        
        Returns:
            str: 用户名
        """
        return self._username
    
    @username.setter
    def username(self, value):
        """
        用户名setter - 包含验证
        
        Args:
            value (str): 用户名
            
        Raises:
            ValueError: 用户名格式错误
        """
        if not isinstance(value, str) or len(value) < 3:
            raise ValueError("用户名必须是至少3个字符的字符串")
        
        if not value.isalnum():
            raise ValueError("用户名只能包含字母和数字")
        
        self._username = value
    
    @property
    def email(self):
        """
        邮箱getter
        
        Returns:
            str: 邮箱
        """
        return self._email
    
    @email.setter
    def email(self, value):
        """
        邮箱setter - 包含验证
        
        Args:
            value (str): 邮箱地址
            
        Raises:
            ValueError: 邮箱格式错误
        """
        if not isinstance(value, str) or "@" not in value:
            raise ValueError("邮箱格式不正确")
        
        self._email = value
    
    @property
    def password(self):
        """
        密码getter - 不返回实际密码
        
        Returns:
            str: 密码掩码
        """
        return "*" * 8
    
    @password.setter
    def password(self, value):
        """
        密码setter - 进行哈希处理
        
        Args:
            value (str): 明文密码
            
        Raises:
            ValueError: 密码强度不够
        """
        if not self._validate_password(value):
            raise ValueError("密码必须至少8个字符，包含字母和数字")
        
        self._password_hash = self._hash_password(value)
    
    @property
    def is_active(self):
        """
        账户状态getter
        
        Returns:
            bool: 账户是否激活
        """
        return self._is_active
    
    @property
    def login_attempts(self):
        """
        登录尝试次数getter
        
        Returns:
            int: 登录尝试次数
        """
        return self._login_attempts
    
    def _validate_password(self, password):
        """
        验证密码强度 - 私有方法
        
        Args:
            password (str): 密码
            
        Returns:
            bool: 密码是否符合要求
        """
        if len(password) < 8:
            return False
        
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_letter and has_digit
    
    def _hash_password(self, password):
        """
        密码哈希 - 私有方法(简化实现)
        
        Args:
            password (str): 明文密码
            
        Returns:
            str: 哈希后的密码
        """
        # 实际应用中应使用bcrypt等安全的哈希算法
        return str(hash(password))
    
    def verify_password(self, password):
        """
        验证密码
        
        Args:
            password (str): 待验证的密码
            
        Returns:
            bool: 密码是否正确
        """
        if not self._is_active:
            print("账户已被锁定")
            return False
        
        if self._login_attempts >= self._max_login_attempts:
            self._is_active = False
            print("登录尝试次数过多，账户已被锁定")
            return False
        
        password_hash = self._hash_password(password)
        if password_hash == self._password_hash:
            self._login_attempts = 0  # 重置登录尝试次数
            return True
        else:
            self._login_attempts += 1
            remaining = self._max_login_attempts - self._login_attempts
            print(f"密码错误，剩余尝试次数：{remaining}")
            return False
    
    def reset_password(self, old_password, new_password):
        """
        重置密码
        
        Args:
            old_password (str): 旧密码
            new_password (str): 新密码
            
        Returns:
            bool: 操作是否成功
        """
        if not self.verify_password(old_password):
            return False
        
        try:
            self.password = new_password
            print("密码重置成功")
            return True
        except ValueError as e:
            print(f"密码重置失败：{e}")
            return False
    
    def activate_account(self):
        """激活账户"""
        self._is_active = True
        self._login_attempts = 0
        print("账户已激活")
    
    def deactivate_account(self):
        """停用账户"""
        self._is_active = False
        print("账户已停用")
    
    def get_info(self):
        """
        获取用户信息
        
        Returns:
            dict: 用户信息
        """
        return {
            "username": self._username,
            "email": self._email,
            "is_active": self._is_active,
            "login_attempts": self._login_attempts
        }
    
    def __str__(self):
        """字符串表示"""
        status = "激活" if self._is_active else "停用"
        return f"用户：{self._username} ({self._email}) - 状态：{status}"


def demo_advanced_encapsulation():
    """演示高级封装示例"""
    print("=== 高级封装示例 - 用户管理系统 ===")
    
    # 创建用户
    try:
        user = User("alice123", "alice@example.com", "password123")
        print(f"用户创建成功：{user}")
    except ValueError as e:
        print(f"用户创建失败：{e}")
    
    # 测试属性访问
    print(f"\n=== 属性访问 ===")
    print(f"用户名：{user.username}")
    print(f"邮箱：{user.email}")
    print(f"密码：{user.password}")  # 显示掩码
    print(f"账户状态：{user.is_active}")
    
    # 测试密码验证
    print(f"\n=== 密码验证 ===")
    print(f"正确密码：{user.verify_password('password123')}")
    print(f"错误密码：{user.verify_password('wrongpassword')}")
    print(f"错误密码：{user.verify_password('wrongpassword')}")
    print(f"错误密码：{user.verify_password('wrongpassword')}")  # 第三次，账户被锁定
    
    # 尝试再次登录
    print(f"账户锁定后登录：{user.verify_password('password123')}")
    
    # 激活账户
    user.activate_account()
    print(f"激活后登录：{user.verify_password('password123')}")
    
    # 重置密码
    print(f"\n=== 重置密码 ===")
    user.reset_password("password123", "newpassword456")
    print(f"使用新密码登录：{user.verify_password('newpassword456')}")
    
    # 测试属性验证
    print(f"\n=== 属性验证 ===")
    try:
        user.username = "ab"  # 太短
    except ValueError as e:
        print(f"用户名验证错误：{e}")
    
    try:
        user.email = "invalid-email"  # 格式错误
    except ValueError as e:
        print(f"邮箱验证错误：{e}")
    
    try:
        user.password = "123"  # 密码太弱
    except ValueError as e:
        print(f"密码验证错误：{e}")
    
    # 显示用户信息
    print(f"\n=== 用户信息 ===")
    info = user.get_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print()


# ============================================================================
# 4. 封装设计原则和最佳实践
# ============================================================================

class DataProcessor:
    """
    数据处理器 - 演示封装设计原则
    """
    
    def __init__(self):
        """构造函数"""
        self._data = []
        self._processed = False
        self._result = None
        self._processing_steps = []
    
    def add_data(self, item):
        """
        添加数据
        
        Args:
            item: 数据项
        """
        if self._processed:
            raise RuntimeError("数据已处理，无法添加新数据")
        
        self._data.append(item)
        print(f"添加数据：{item}")
    
    def clear_data(self):
        """清空数据"""
        self._data.clear()
        self._processed = False
        self._result = None
        self._processing_steps.clear()
        print("数据已清空")
    
    def process(self):
        """
        处理数据 - 公开接口
        
        Returns:
            任意类型: 处理结果
        """
        if not self._data:
            raise ValueError("没有数据可处理")
        
        if self._processed:
            print("数据已处理，返回缓存结果")
            return self._result
        
        print("开始处理数据...")
        
        # 执行处理步骤
        self._validate_data()
        self._clean_data()
        self._transform_data()
        self._calculate_result()
        
        self._processed = True
        print("数据处理完成")
        return self._result
    
    def _validate_data(self):
        """
        验证数据 - 私有方法
        """
        print("验证数据...")
        for item in self._data:
            if item is not None and not isinstance(item, (int, float)):
                raise TypeError(f"数据项必须是数字，得到：{type(item)}")
        
        self._processing_steps.append("数据验证")
    
    def _clean_data(self):
        """
        清理数据 - 私有方法
        """
        print("清理数据...")
        # 移除None值和重复项
        original_count = len(self._data)
        self._data = list(set(item for item in self._data if item is not None))
        cleaned_count = len(self._data)
        
        if cleaned_count != original_count:
            print(f"清理了{original_count - cleaned_count}个无效数据项")
        
        self._processing_steps.append("数据清理")
    
    def _transform_data(self):
        """
        转换数据 - 私有方法
        """
        print("转换数据...")
        # 将所有数据转换为浮点数
        self._data = [float(item) for item in self._data]
        self._processing_steps.append("数据转换")
    
    def _calculate_result(self):
        """
        计算结果 - 私有方法
        """
        print("计算结果...")
        if not self._data:
            self._result = {"error": "没有有效数据"}
            return
        
        self._result = {
            "count": len(self._data),
            "sum": sum(self._data),
            "average": sum(self._data) / len(self._data),
            "min": min(self._data),
            "max": max(self._data)
        }
        self._processing_steps.append("结果计算")
    
    @property
    def is_processed(self):
        """
        检查是否已处理
        
        Returns:
            bool: 是否已处理
        """
        return self._processed
    
    @property
    def data_count(self):
        """
        获取数据数量
        
        Returns:
            int: 数据数量
        """
        return len(self._data)
    
    def get_processing_steps(self):
        """
        获取处理步骤
        
        Returns:
            list: 处理步骤列表
        """
        return self._processing_steps.copy()
    
    def get_summary(self):
        """
        获取处理摘要
        
        Returns:
            dict: 处理摘要
        """
        return {
            "data_count": self.data_count,
            "is_processed": self.is_processed,
            "processing_steps": self.get_processing_steps(),
            "result": self._result
        }


def demo_encapsulation_principles():
    """演示封装设计原则"""
    print("=== 封装设计原则和最佳实践 ===")
    
    processor = DataProcessor()
    
    # 添加数据
    print("=== 添加数据 ===")
    data_items = [1, 2, 3, 2, 4.5, 6, None, 7, 8, 9]
    for item in data_items:
        try:
            processor.add_data(item)
        except Exception as e:
            print(f"添加数据失败：{e}")
    
    # 检查状态
    print(f"\n数据数量：{processor.data_count}")
    print(f"是否已处理：{processor.is_processed}")
    
    # 处理数据
    print(f"\n=== 处理数据 ===")
    try:
        result = processor.process()
        print(f"处理结果：{result}")
    except Exception as e:
        print(f"处理失败：{e}")
    
    # 再次处理(应该返回缓存结果)
    print(f"\n=== 再次处理 ===")
    result2 = processor.process()
    
    # 获取摘要
    print(f"\n=== 处理摘要 ===")
    summary = processor.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # 尝试在处理后添加数据
    print(f"\n=== 尝试在处理后添加数据 ===")
    try:
        processor.add_data(10)
    except RuntimeError as e:
        print(f"操作被拒绝：{e}")
    
    # 清空数据重新开始
    print(f"\n=== 清空数据重新开始 ===")
    processor.clear_data()
    processor.add_data(100)
    processor.add_data(200)
    result3 = processor.process()
    print(f"新的处理结果：{result3}")
    
    print()


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

def main():
    """运行所有示例"""
    print("Python面向对象编程 - 封装示例")
    print("=" * 50)
    
    demo_basic_encapsulation()
    demo_property_decorator()
    demo_advanced_encapsulation()
    demo_encapsulation_principles()
    
    print("所有示例运行完成！")


if __name__ == "__main__":
    main()