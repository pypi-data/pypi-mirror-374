#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python基础语法练习题

本文件包含基础语法的练习题，涵盖变量、数据类型、运算符和注释等内容。
每个练习都包含题目描述、示例代码、答案和详细解释。

学习目标：
1. 通过实际练习巩固基础语法知识
2. 学会分析和解决编程问题
3. 培养良好的编程习惯和思维方式
4. 掌握自测和进度检查的方法

使用方法：
1. 阅读练习题目
2. 尝试自己编写代码
3. 查看参考答案和解释
4. 运行测试函数验证结果
"""

import sys
import traceback
from typing import Any, Callable, List, Tuple

# =============================================================================
# 练习管理系统
# =============================================================================

class ExerciseManager:
    """练习管理器，用于组织和运行练习题。"""
    
    def __init__(self):
        self.exercises = []
        self.completed_exercises = []
    
    def add_exercise(self, exercise_func: Callable, title: str, difficulty: str):
        """添加练习题。"""
        self.exercises.append({
            'function': exercise_func,
            'title': title,
            'difficulty': difficulty,
            'completed': False
        })
    
    def run_exercise(self, index: int):
        """运行指定的练习题。"""
        if 0 <= index < len(self.exercises):
            exercise = self.exercises[index]
            print(f"\n{'='*60}")
            print(f"练习 {index + 1}: {exercise['title']}")
            print(f"难度: {exercise['difficulty']}")
            print(f"{'='*60}")
            
            try:
                exercise['function']()
                exercise['completed'] = True
                if index not in self.completed_exercises:
                    self.completed_exercises.append(index)
                print(f"\n✅ 练习 {index + 1} 完成！")
            except Exception as e:
                print(f"\n❌ 练习 {index + 1} 执行出错: {e}")
                traceback.print_exc()
    
    def run_all_exercises(self):
        """运行所有练习题。"""
        for i in range(len(self.exercises)):
            self.run_exercise(i)
    
    def show_progress(self):
        """显示学习进度。"""
        total = len(self.exercises)
        completed = len(self.completed_exercises)
        percentage = (completed / total * 100) if total > 0 else 0
        
        print(f"\n📊 学习进度报告")
        print(f"{'='*40}")
        print(f"总练习数: {total}")
        print(f"已完成: {completed}")
        print(f"完成率: {percentage:.1f}%")
        print(f"进度条: {'█' * int(percentage/5)}{'░' * (20-int(percentage/5))} {percentage:.1f}%")
        
        if completed == total:
            print("🎉 恭喜！您已完成所有基础语法练习！")
        else:
            remaining = total - completed
            print(f"还有 {remaining} 个练习待完成")

# 创建全局练习管理器
exercise_manager = ExerciseManager()

# =============================================================================
# 练习1: 变量和数据类型基础
# =============================================================================

def exercise_1_variables_and_types():
    """
    练习1: 变量和数据类型基础
    
    题目：创建不同类型的变量并进行基本操作
    """
    print("\n📝 题目描述:")
    print("1. 创建一个字符串变量存储你的姓名")
    print("2. 创建一个整数变量存储你的年龄")
    print("3. 创建一个浮点数变量存储你的身高(米)")
    print("4. 创建一个布尔变量表示是否为学生")
    print("5. 打印所有变量及其类型")
    
    print("\n💡 参考答案:")
    
    # 学生答案区域
    name = "张三"                    # 字符串类型
    age = 25                        # 整数类型
    height = 1.75                   # 浮点数类型
    is_student = True               # 布尔类型
    
    # 打印变量和类型
    print(f"姓名: {name} (类型: {type(name).__name__})")
    print(f"年龄: {age} (类型: {type(age).__name__})")
    print(f"身高: {height} (类型: {type(height).__name__})")
    print(f"是否为学生: {is_student} (类型: {type(is_student).__name__})")
    
    print("\n🔍 知识点解析:")
    print("- Python是动态类型语言，变量类型在运行时确定")
    print("- 使用type()函数可以获取变量的类型")
    print("- 字符串可以用单引号或双引号定义")
    print("- 布尔值只有True和False两个值（注意大小写）")
    
    # 自测验证
    assert isinstance(name, str), "姓名应该是字符串类型"
    assert isinstance(age, int), "年龄应该是整数类型"
    assert isinstance(height, float), "身高应该是浮点数类型"
    assert isinstance(is_student, bool), "学生状态应该是布尔类型"
    print("✅ 所有类型检查通过！")

# =============================================================================
# 练习2: 类型转换
# =============================================================================

def exercise_2_type_conversion():
    """
    练习2: 类型转换
    
    题目：练习不同数据类型之间的转换
    """
    print("\n📝 题目描述:")
    print("给定字符串形式的数据，将其转换为适当的类型并进行计算")
    
    print("\n💡 参考答案:")
    
    # 原始数据（字符串形式）
    str_number1 = "123"
    str_number2 = "45.67"
    str_boolean = "True"
    str_age = "25"
    
    print(f"原始数据:")
    print(f"str_number1 = '{str_number1}' (类型: {type(str_number1).__name__})")
    print(f"str_number2 = '{str_number2}' (类型: {type(str_number2).__name__})")
    print(f"str_boolean = '{str_boolean}' (类型: {type(str_boolean).__name__})")
    print(f"str_age = '{str_age}' (类型: {type(str_age).__name__})")
    
    # 类型转换
    number1 = int(str_number1)          # 字符串转整数
    number2 = float(str_number2)        # 字符串转浮点数
    boolean_val = str_boolean == "True" # 字符串转布尔值
    age = int(str_age)                  # 字符串转整数
    
    print(f"\n转换后的数据:")
    print(f"number1 = {number1} (类型: {type(number1).__name__})")
    print(f"number2 = {number2} (类型: {type(number2).__name__})")
    print(f"boolean_val = {boolean_val} (类型: {type(boolean_val).__name__})")
    print(f"age = {age} (类型: {type(age).__name__})")
    
    # 进行计算
    sum_result = number1 + number2
    is_adult = age >= 18
    
    print(f"\n计算结果:")
    print(f"{number1} + {number2} = {sum_result}")
    print(f"年龄{age}岁，是否成年: {is_adult}")
    
    print("\n🔍 知识点解析:")
    print("- int()函数将字符串转换为整数")
    print("- float()函数将字符串转换为浮点数")
    print("- 字符串转布尔值需要比较操作，不能直接使用bool()")
    print("- 转换失败时会抛出ValueError异常")
    
    # 错误处理示例
    print("\n⚠️ 错误处理示例:")
    try:
        invalid_number = int("abc")
    except ValueError as e:
        print(f"转换错误: {e}")

# =============================================================================
# 练习3: 运算符综合应用
# =============================================================================

def exercise_3_operators():
    """
    练习3: 运算符综合应用
    
    题目：使用各种运算符解决实际问题
    """
    print("\n📝 题目描述:")
    print("编写一个简单的购物计算器，计算商品总价、折扣和最终价格")
    
    print("\n💡 参考答案:")
    
    # 商品信息
    item1_price = 99.9      # 商品1价格
    item1_quantity = 2      # 商品1数量
    
    item2_price = 149.5     # 商品2价格
    item2_quantity = 1      # 商品2数量
    
    discount_rate = 0.1     # 折扣率（10%）
    tax_rate = 0.08         # 税率（8%）
    
    print(f"商品信息:")
    print(f"商品1: 单价 ¥{item1_price}, 数量 {item1_quantity}")
    print(f"商品2: 单价 ¥{item2_price}, 数量 {item2_quantity}")
    print(f"折扣率: {discount_rate * 100}%")
    print(f"税率: {tax_rate * 100}%")
    
    # 计算小计
    subtotal1 = item1_price * item1_quantity
    subtotal2 = item2_price * item2_quantity
    total_before_discount = subtotal1 + subtotal2
    
    # 计算折扣
    discount_amount = total_before_discount * discount_rate
    total_after_discount = total_before_discount - discount_amount
    
    # 计算税费
    tax_amount = total_after_discount * tax_rate
    final_total = total_after_discount + tax_amount
    
    print(f"\n计算过程:")
    print(f"商品1小计: ¥{item1_price} × {item1_quantity} = ¥{subtotal1}")
    print(f"商品2小计: ¥{item2_price} × {item2_quantity} = ¥{subtotal2}")
    print(f"折扣前总计: ¥{total_before_discount}")
    print(f"折扣金额: ¥{total_before_discount} × {discount_rate} = ¥{discount_amount:.2f}")
    print(f"折扣后总计: ¥{total_after_discount:.2f}")
    print(f"税费: ¥{total_after_discount:.2f} × {tax_rate} = ¥{tax_amount:.2f}")
    print(f"最终总计: ¥{final_total:.2f}")
    
    # 使用比较运算符
    is_expensive = final_total > 300
    needs_approval = final_total >= 500
    
    print(f"\n条件判断:")
    print(f"总价是否超过¥300: {is_expensive}")
    print(f"是否需要审批(≥¥500): {needs_approval}")
    
    # 使用逻辑运算符
    can_use_coupon = total_before_discount > 200 and discount_rate < 0.2
    print(f"可以使用优惠券: {can_use_coupon}")
    
    print("\n🔍 知识点解析:")
    print("- 算术运算符用于数值计算")
    print("- 比较运算符用于条件判断")
    print("- 逻辑运算符用于组合多个条件")
    print("- 使用round()或格式化字符串控制小数位数")

# =============================================================================
# 练习4: 字符串操作
# =============================================================================

def exercise_4_string_operations():
    """
    练习4: 字符串操作
    
    题目：处理用户输入的姓名信息
    """
    print("\n📝 题目描述:")
    print("处理用户输入的姓名，进行格式化和验证")
    
    print("\n💡 参考答案:")
    
    # 模拟用户输入（实际中使用input()）
    user_input = "  张 三  "
    email_input = "zhangsan@example.com"
    
    print(f"原始输入: '{user_input}'")
    print(f"邮箱输入: '{email_input}'")
    
    # 字符串清理和格式化
    cleaned_name = user_input.strip()          # 去除首尾空格
    formatted_name = cleaned_name.replace(" ", "")  # 去除中间空格
    
    # 字符串信息获取
    name_length = len(formatted_name)
    first_char = formatted_name[0] if formatted_name else ""
    
    # 邮箱验证（简单版本）
    has_at = "@" in email_input
    has_dot = "." in email_input
    is_valid_email = has_at and has_dot and len(email_input) > 5
    
    print(f"\n处理结果:")
    print(f"清理后姓名: '{formatted_name}'")
    print(f"姓名长度: {name_length}")
    print(f"姓氏: '{first_char}'")
    print(f"邮箱有效性: {is_valid_email}")
    
    # 字符串格式化
    greeting = f"您好，{formatted_name}先生/女士！"
    info_message = "姓名: {}, 长度: {}, 邮箱: {}".format(
        formatted_name, name_length, email_input
    )
    
    print(f"\n格式化输出:")
    print(greeting)
    print(info_message)
    
    # 字符串方法演示
    print(f"\n字符串方法演示:")
    print(f"转大写: {formatted_name.upper()}")
    print(f"转小写: {formatted_name.lower()}")
    print(f"首字母大写: {formatted_name.capitalize()}")
    print(f"是否为字母: {formatted_name.isalpha()}")
    print(f"是否为数字: {formatted_name.isdigit()}")
    
    print("\n🔍 知识点解析:")
    print("- strip()方法去除字符串首尾空白字符")
    print("- replace()方法替换字符串中的子串")
    print("- in运算符检查子串是否存在")
    print("- f-string是推荐的字符串格式化方法")
    print("- 字符串有很多有用的内置方法")

# =============================================================================
# 练习5: 综合应用 - 个人信息管理
# =============================================================================

def exercise_5_personal_info_manager():
    """
    练习5: 综合应用 - 个人信息管理
    
    题目：创建一个简单的个人信息管理系统
    """
    print("\n📝 题目描述:")
    print("创建一个个人信息管理系统，包含信息录入、验证和显示功能")
    
    print("\n💡 参考答案:")
    
    # 个人信息数据
    personal_info = {
        "name": "李明",
        "age": "28",
        "height": "175.5",
        "weight": "70.2",
        "is_married": "False",
        "email": "liming@example.com",
        "phone": "13812345678"
    }
    
    print("原始数据（字符串格式）:")
    for key, value in personal_info.items():
        print(f"  {key}: '{value}'")
    
    # 数据类型转换和验证
    def validate_and_convert_info(info_dict):
        """验证并转换个人信息"""
        result = {}
        errors = []
        
        # 姓名验证
        name = info_dict.get("name", "").strip()
        if len(name) >= 2:
            result["name"] = name
        else:
            errors.append("姓名长度至少2个字符")
        
        # 年龄验证和转换
        try:
            age = int(info_dict.get("age", "0"))
            if 0 < age < 150:
                result["age"] = age
            else:
                errors.append("年龄必须在1-149之间")
        except ValueError:
            errors.append("年龄必须是数字")
        
        # 身高验证和转换
        try:
            height = float(info_dict.get("height", "0"))
            if 50 < height < 250:
                result["height"] = height
            else:
                errors.append("身高必须在50-250cm之间")
        except ValueError:
            errors.append("身高必须是数字")
        
        # 体重验证和转换
        try:
            weight = float(info_dict.get("weight", "0"))
            if 20 < weight < 300:
                result["weight"] = weight
            else:
                errors.append("体重必须在20-300kg之间")
        except ValueError:
            errors.append("体重必须是数字")
        
        # 婚姻状态转换
        is_married_str = info_dict.get("is_married", "False")
        result["is_married"] = is_married_str.lower() == "true"
        
        # 邮箱验证
        email = info_dict.get("email", "").strip()
        if "@" in email and "." in email and len(email) > 5:
            result["email"] = email
        else:
            errors.append("邮箱格式不正确")
        
        # 手机号验证
        phone = info_dict.get("phone", "").strip()
        if phone.isdigit() and len(phone) == 11:
            result["phone"] = phone
        else:
            errors.append("手机号必须是11位数字")
        
        return result, errors
    
    # 执行验证和转换
    validated_info, validation_errors = validate_and_convert_info(personal_info)
    
    print(f"\n验证结果:")
    if validation_errors:
        print("❌ 验证失败，错误信息:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("✅ 所有信息验证通过！")
    
    print(f"\n转换后的数据:")
    for key, value in validated_info.items():
        print(f"  {key}: {value} ({type(value).__name__})")
    
    # 计算BMI（如果身高体重都有效）
    if "height" in validated_info and "weight" in validated_info:
        height_m = validated_info["height"] / 100  # 转换为米
        weight_kg = validated_info["weight"]
        bmi = weight_kg / (height_m ** 2)
        
        # BMI分类
        if bmi < 18.5:
            bmi_category = "偏瘦"
        elif bmi < 24:
            bmi_category = "正常"
        elif bmi < 28:
            bmi_category = "偏胖"
        else:
            bmi_category = "肥胖"
        
        print(f"\n健康指标:")
        print(f"BMI: {bmi:.2f} ({bmi_category})")
    
    # 生成个人信息报告
    if "name" in validated_info and "age" in validated_info:
        name = validated_info["name"]
        age = validated_info["age"]
        marital_status = "已婚" if validated_info.get("is_married", False) else "未婚"
        
        report = f"""
个人信息报告
{'='*30}
姓名: {name}
年龄: {age}岁
婚姻状况: {marital_status}
联系方式: {validated_info.get('email', '未提供')}
        """
        print(report)
    
    print("\n🔍 知识点解析:")
    print("- 数据验证是程序健壮性的重要保证")
    print("- 异常处理用于捕获转换错误")
    print("- 字典是存储结构化数据的好选择")
    print("- 条件判断用于数据分类和决策")
    print("- 字符串格式化用于生成报告")

# =============================================================================
# 练习6: 注释和文档编写
# =============================================================================

def exercise_6_documentation():
    """
    练习6: 注释和文档编写
    
    题目：为函数编写完整的文档字符串和注释
    """
    print("\n📝 题目描述:")
    print("为一个计算函数编写完整的文档字符串和注释")
    
    print("\n💡 参考答案:")
    
    def calculate_loan_payment(principal, annual_rate, years):
        """
        计算等额本息贷款的月还款额。
        
        使用等额本息还款公式计算每月应还款金额。
        公式: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        其中: M=月还款额, P=本金, r=月利率, n=还款月数
        
        Args:
            principal (float): 贷款本金，必须为正数
            annual_rate (float): 年利率，以小数形式表示（如0.05表示5%）
            years (int): 贷款年限，必须为正整数
        
        Returns:
            float: 每月还款金额
        
        Raises:
            ValueError: 当参数不在有效范围内时
        
        Examples:
            >>> calculate_loan_payment(100000, 0.05, 20)
            659.96
            >>> calculate_loan_payment(200000, 0.04, 30)
            954.83
        
        Note:
            计算结果保留两位小数，适用于等额本息还款方式。
        """
        # 参数验证
        if principal <= 0:
            raise ValueError("贷款本金必须为正数")
        if annual_rate < 0:
            raise ValueError("年利率不能为负数")
        if years <= 0:
            raise ValueError("贷款年限必须为正整数")
        
        # 特殊情况：无利息贷款
        if annual_rate == 0:
            return principal / (years * 12)
        
        # 计算月利率和总月数
        monthly_rate = annual_rate / 12  # 月利率 = 年利率 / 12
        total_months = years * 12        # 总月数 = 年数 * 12
        
        # 使用等额本息公式计算月还款额
        # 分子: 本金 * 月利率 * (1 + 月利率)^总月数
        numerator = principal * monthly_rate * ((1 + monthly_rate) ** total_months)
        
        # 分母: (1 + 月利率)^总月数 - 1
        denominator = ((1 + monthly_rate) ** total_months) - 1
        
        # 月还款额
        monthly_payment = numerator / denominator
        
        return round(monthly_payment, 2)  # 保留两位小数
    
    # 测试函数
    print("函数测试:")
    
    # 测试用例1: 普通贷款
    principal1 = 300000    # 30万本金
    rate1 = 0.045         # 4.5%年利率
    years1 = 25           # 25年
    
    payment1 = calculate_loan_payment(principal1, rate1, years1)
    print(f"贷款 ¥{principal1:,}, 年利率 {rate1*100}%, {years1}年")
    print(f"月还款额: ¥{payment1:,}")
    
    # 测试用例2: 无息贷款
    payment2 = calculate_loan_payment(120000, 0, 10)
    print(f"\n无息贷款 ¥120,000, 10年")
    print(f"月还款额: ¥{payment2:,}")
    
    # 测试错误处理
    print(f"\n错误处理测试:")
    try:
        calculate_loan_payment(-100000, 0.05, 20)
    except ValueError as e:
        print(f"捕获到预期错误: {e}")
    
    print(f"\n函数文档字符串:")
    print(calculate_loan_payment.__doc__)
    
    print("\n🔍 知识点解析:")
    print("- 文档字符串应该描述函数的功能、参数、返回值和异常")
    print("- 注释应该解释复杂的算法和业务逻辑")
    print("- 参数验证提高函数的健壮性")
    print("- 示例代码帮助用户理解函数用法")
    print("- 使用标准的文档字符串格式便于工具解析")

# =============================================================================
# 注册所有练习
# =============================================================================

# 注册练习题
exercise_manager.add_exercise(exercise_1_variables_and_types, "变量和数据类型基础", "初级")
exercise_manager.add_exercise(exercise_2_type_conversion, "类型转换", "初级")
exercise_manager.add_exercise(exercise_3_operators, "运算符综合应用", "中级")
exercise_manager.add_exercise(exercise_4_string_operations, "字符串操作", "中级")
exercise_manager.add_exercise(exercise_5_personal_info_manager, "综合应用-个人信息管理", "高级")
exercise_manager.add_exercise(exercise_6_documentation, "注释和文档编写", "中级")

# =============================================================================
# 主程序和菜单系统
# =============================================================================

def show_menu():
    """显示练习菜单。"""
    print("\n" + "="*60)
    print("🎯 Python基础语法练习系统")
    print("="*60)
    print("请选择要进行的练习:")
    
    for i, exercise in enumerate(exercise_manager.exercises):
        status = "✅" if exercise['completed'] else "⭕"
        print(f"{status} {i+1}. {exercise['title']} ({exercise['difficulty']})")
    
    print(f"\n0. 运行所有练习")
    print(f"p. 查看学习进度")
    print(f"q. 退出")
    print("-" * 60)

def main():
    """主程序入口。"""
    print("欢迎使用Python基础语法练习系统！")
    print("本系统包含6个练习，涵盖变量、类型、运算符、字符串和注释等内容。")
    
    while True:
        show_menu()
        choice = input("请输入选择 (1-6, 0, p, q): ").strip().lower()
        
        if choice == 'q':
            print("感谢使用！祝您学习愉快！")
            break
        elif choice == 'p':
            exercise_manager.show_progress()
        elif choice == '0':
            print("\n🚀 开始运行所有练习...")
            exercise_manager.run_all_exercises()
            exercise_manager.show_progress()
        elif choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(exercise_manager.exercises):
                exercise_manager.run_exercise(index)
            else:
                print("❌ 无效的选择，请重新输入")
        else:
            print("❌ 无效的选择，请重新输入")

# =============================================================================
# 自动测试函数
# =============================================================================

def run_all_tests():
    """运行所有练习的自动测试。"""
    print("🧪 运行自动测试...")
    exercise_manager.run_all_exercises()
    exercise_manager.show_progress()

# =============================================================================
# 程序入口
# =============================================================================

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 自动测试模式
        run_all_tests()
    else:
        # 交互模式
        main()