"""
条件语句示例文件
演示Python中if、elif、else语句的使用方法
包含嵌套条件、复杂逻辑判断和条件表达式的示例
"""

def basic_if_statements():
    """基础if语句示例"""
    print("=== 基础if语句示例 ===")
    
    # 简单的if语句
    age = 18
    if age >= 18:
        print(f"年龄{age}岁，已成年")
    
    # if-else语句
    score = 85
    if score >= 60:
        print(f"分数{score}，考试通过")
    else:
        print(f"分数{score}，考试未通过")
    
    # if-elif-else语句
    temperature = 25
    if temperature > 30:
        print("天气炎热")
    elif temperature > 20:
        print("天气温暖")
    elif temperature > 10:
        print("天气凉爽")
    else:
        print("天气寒冷")


def complex_conditions():
    """复杂条件判断示例"""
    print("\n=== 复杂条件判断示例 ===")
    
    # 使用逻辑运算符
    username = "admin"
    password = "123456"
    
    if username == "admin" and password == "123456":
        print("登录成功")
    elif username == "admin" and password != "123456":
        print("密码错误")
    elif username != "admin":
        print("用户名不存在")
    
    # 使用or运算符
    day = "Saturday"
    if day == "Saturday" or day == "Sunday":
        print(f"{day}是周末")
    else:
        print(f"{day}是工作日")
    
    # 使用not运算符
    is_logged_in = False
    if not is_logged_in:
        print("请先登录")
    
    # 使用in运算符
    fruits = ["apple", "banana", "orange"]
    fruit = "apple"
    if fruit in fruits:
        print(f"{fruit}在水果列表中")


def nested_conditions():
    """嵌套条件语句示例"""
    print("\n=== 嵌套条件语句示例 ===")
    
    # 嵌套if语句
    weather = "sunny"
    temperature = 25
    
    if weather == "sunny":
        if temperature > 20:
            print("天气晴朗且温暖，适合外出")
        else:
            print("天气晴朗但较冷，注意保暖")
    elif weather == "rainy":
        if temperature > 15:
            print("下雨但不冷，带把伞")
        else:
            print("又冷又下雨，在家休息")
    else:
        print("天气一般")
    
    # 复杂嵌套示例：学生成绩评级
    score = 88
    attendance = 95
    
    if score >= 90:
        if attendance >= 90:
            print("优秀学生")
        else:
            print("成绩优秀但出勤不足")
    elif score >= 80:
        if attendance >= 90:
            print("良好学生")
        elif attendance >= 80:
            print("中等学生")
        else:
            print("成绩良好但出勤较差")
    elif score >= 60:
        if attendance >= 80:
            print("及格学生")
        else:
            print("成绩和出勤都需要改进")
    else:
        print("不及格学生")


def conditional_expressions():
    """条件表达式（三元运算符）示例"""
    print("\n=== 条件表达式示例 ===")
    
    # 基本三元运算符语法：value_if_true if condition else value_if_false
    age = 20
    status = "成年人" if age >= 18 else "未成年人"
    print(f"年龄{age}岁，身份：{status}")
    
    # 在函数中使用
    def get_grade(score):
        return "及格" if score >= 60 else "不及格"
    
    print(f"分数75：{get_grade(75)}")
    print(f"分数45：{get_grade(45)}")
    
    # 嵌套条件表达式
    score = 85
    grade = "优秀" if score >= 90 else "良好" if score >= 80 else "及格" if score >= 60 else "不及格"
    print(f"分数{score}，等级：{grade}")
    
    # 在列表推导式中使用
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    even_odd = ["偶数" if num % 2 == 0 else "奇数" for num in numbers]
    print(f"数字奇偶性：{even_odd}")
    
    # 处理None值
    name = None
    display_name = name if name is not None else "匿名用户"
    print(f"显示名称：{display_name}")


def membership_and_identity():
    """成员关系和身份判断示例"""
    print("\n=== 成员关系和身份判断示例 ===")
    
    # 使用in和not in
    colors = ["red", "green", "blue"]
    color = "red"
    
    if color in colors:
        print(f"{color}是基本颜色")
    
    if "purple" not in colors:
        print("purple不是基本颜色")
    
    # 字符串包含判断
    text = "Python编程很有趣"
    if "Python" in text:
        print("文本包含Python")
    
    # 字典键值判断
    student = {"name": "张三", "age": 20, "grade": 85}
    if "name" in student:
        print(f"学生姓名：{student['name']}")
    
    # 使用is和is not（身份判断）
    a = None
    if a is None:
        print("a是None")
    
    b = []
    c = []
    if b is not c:
        print("b和c是不同的对象")
    
    # 布尔值判断
    empty_list = []
    if not empty_list:  # 空列表为False
        print("列表为空")
    
    non_empty_list = [1, 2, 3]
    if non_empty_list:  # 非空列表为True
        print("列表不为空")


def practical_examples():
    """实际应用示例"""
    print("\n=== 实际应用示例 ===")
    
    # 用户输入验证
    def validate_email(email):
        """简单的邮箱验证"""
        if not email:
            return False, "邮箱不能为空"
        elif "@" not in email:
            return False, "邮箱格式不正确：缺少@符号"
        elif "." not in email.split("@")[1]:
            return False, "邮箱格式不正确：域名格式错误"
        else:
            return True, "邮箱格式正确"
    
    # 测试邮箱验证
    test_emails = ["", "test", "test@", "test@example", "test@example.com"]
    for email in test_emails:
        is_valid, message = validate_email(email)
        print(f"邮箱'{email}': {message}")
    
    print()
    
    # 成绩等级判定系统
    def get_letter_grade(score):
        """根据分数返回字母等级"""
        if score < 0 or score > 100:
            return "无效分数"
        elif score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    # 测试成绩等级
    test_scores = [95, 85, 75, 65, 55, 105, -10]
    for score in test_scores:
        grade = get_letter_grade(score)
        print(f"分数{score}: 等级{grade}")


def common_mistakes():
    """常见错误和最佳实践"""
    print("\n=== 常见错误和最佳实践 ===")
    
    # 错误1：使用=而不是==
    print("错误示例：使用=而不是==进行比较")
    x = 5
    # if x = 5:  # 这会导致语法错误
    #     print("错误的比较方式")
    
    if x == 5:  # 正确的比较方式
        print("正确的比较方式")
    
    # 错误2：浮点数比较
    print("\n浮点数比较的注意事项：")
    a = 0.1 + 0.2
    b = 0.3
    print(f"0.1 + 0.2 = {a}")
    print(f"0.3 = {b}")
    print(f"0.1 + 0.2 == 0.3: {a == b}")  # 可能为False
    
    # 正确的浮点数比较方式
    tolerance = 1e-9
    if abs(a - b) < tolerance:
        print("浮点数相等（使用容差比较）")
    
    # 最佳实践：避免过深的嵌套
    print("\n最佳实践示例：")
    
    # 不好的写法（过深嵌套）
    def process_user_bad(user):
        if user is not None:
            if "name" in user:
                if user["name"]:
                    if len(user["name"]) > 0:
                        return f"用户：{user['name']}"
        return "无效用户"
    
    # 好的写法（早期返回）
    def process_user_good(user):
        if user is None:
            return "无效用户"
        if "name" not in user:
            return "无效用户"
        if not user["name"]:
            return "无效用户"
        return f"用户：{user['name']}"
    
    # 测试两种写法
    test_user = {"name": "张三"}
    print(f"不好的写法结果：{process_user_bad(test_user)}")
    print(f"好的写法结果：{process_user_good(test_user)}")


if __name__ == "__main__":
    """运行所有示例"""
    print("Python条件语句完整示例")
    print("=" * 50)
    
    basic_if_statements()
    complex_conditions()
    nested_conditions()
    conditional_expressions()
    membership_and_identity()
    practical_examples()
    common_mistakes()
    
    print("\n" + "=" * 50)
    print("条件语句学习完成！")
    print("下一步：学习循环语句（loops.py）")