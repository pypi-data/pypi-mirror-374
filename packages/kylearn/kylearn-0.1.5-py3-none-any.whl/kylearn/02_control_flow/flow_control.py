"""
流程控制示例文件
演示Python中break、continue、pass的使用场景
包含异常流程控制的基础示例和程序结构设计的最佳实践
"""

def break_statement_examples():
    """break语句使用示例"""
    print("=== break语句使用示例 ===")
    
    # 1. 在for循环中使用break
    print("1. 在for循环中查找特定值：")
    numbers = [1, 3, 5, 8, 9, 11, 13]
    target = 8
    
    for i, num in enumerate(numbers):
        if num == target:
            print(f"  在索引{i}处找到目标值{target}")
            break
        print(f"  检查索引{i}：{num}")
    else:
        print(f"  未找到目标值{target}")
    
    # 2. 在while循环中使用break
    print("\n2. 在while循环中处理用户输入：")
    commands = ["help", "list", "quit", "status"]  # 模拟用户输入
    i = 0
    
    while i < len(commands):
        command = commands[i]
        print(f"  用户输入：{command}")
        
        if command == "quit":
            print("  程序退出")
            break
        elif command == "help":
            print("  显示帮助信息")
        elif command == "list":
            print("  显示列表")
        else:
            print("  未知命令")
        
        i += 1
    
    # 3. 嵌套循环中的break
    print("\n3. 嵌套循环中的break（只跳出内层循环）：")
    for i in range(3):
        print(f"  外层循环：{i}")
        for j in range(5):
            if j == 3:
                print(f"    内层循环在j={j}时break")
                break
            print(f"    内层循环：{j}")
        print(f"  外层循环{i}继续")


def continue_statement_examples():
    """continue语句使用示例"""
    print("\n=== continue语句使用示例 ===")
    
    # 1. 跳过特定条件
    print("1. 跳过偶数，只处理奇数：")
    for i in range(10):
        if i % 2 == 0:
            continue  # 跳过偶数
        print(f"  处理奇数：{i}")
    
    # 2. 数据过滤
    print("\n2. 过滤无效数据：")
    data = [1, -2, 3, 0, -5, 7, 8, -1]
    
    print("  处理正数：")
    for num in data:
        if num <= 0:
            continue  # 跳过非正数
        print(f"    正数：{num}")
    
    # 3. 字符串处理
    print("\n3. 跳过空白字符：")
    text = "P y t h o n"
    result = ""
    
    for char in text:
        if char == " ":
            continue  # 跳过空格
        result += char
    
    print(f"  原文本：'{text}'")
    print(f"  处理后：'{result}'")
    
    # 4. 嵌套循环中的continue
    print("\n4. 嵌套循环中的continue：")
    matrix = [[1, 2, 0], [4, 0, 6], [7, 8, 9]]
    
    for i, row in enumerate(matrix):
        print(f"  处理第{i}行：")
        for j, value in enumerate(row):
            if value == 0:
                print(f"    跳过位置({i},{j})的零值")
                continue
            print(f"    处理位置({i},{j})：{value}")


def pass_statement_examples():
    """pass语句使用示例"""
    print("\n=== pass语句使用示例 ===")
    
    # 1. 占位符函数
    print("1. 使用pass作为占位符：")
    
    def future_function():
        """这个函数将来会实现"""
        pass  # 暂时什么都不做
    
    print("  定义了一个空函数（使用pass占位）")
    
    # 2. 空的类定义
    class EmptyClass:
        """空类定义"""
        pass
    
    print("  定义了一个空类（使用pass占位）")
    
    # 3. 异常处理中的pass
    print("\n2. 在异常处理中使用pass：")
    
    def safe_divide(a, b):
        """安全除法，忽略除零错误"""
        try:
            result = a / b
            return result
        except ZeroDivisionError:
            pass  # 忽略除零错误，不做任何处理
        return None
    
    print(f"  10 / 2 = {safe_divide(10, 2)}")
    print(f"  10 / 0 = {safe_divide(10, 0)}")
    
    # 4. 条件语句中的pass
    print("\n3. 在条件语句中使用pass：")
    
    def process_grade(score):
        """处理成绩，某些情况下暂不处理"""
        if score >= 90:
            print(f"    优秀成绩：{score}")
        elif score >= 80:
            print(f"    良好成绩：{score}")
        elif score >= 60:
            print(f"    及格成绩：{score}")
        else:
            # 不及格的情况暂时不处理
            pass
    
    test_scores = [95, 85, 65, 45]
    for score in test_scores:
        process_grade(score)


def exception_flow_control():
    """异常流程控制基础示例"""
    print("\n=== 异常流程控制基础示例 ===")
    
    # 1. 基本异常处理
    print("1. 基本try-except结构：")
    
    def safe_input_number():
        """安全的数字输入（模拟）"""
        test_inputs = ["123", "abc", "45.6", ""]
        
        for input_str in test_inputs:
            print(f"  尝试转换：'{input_str}'")
            try:
                number = int(input_str)
                print(f"    成功转换为整数：{number}")
                return number
            except ValueError:
                print(f"    转换失败：'{input_str}'不是有效整数")
                continue
        
        print("    所有输入都无效")
        return None
    
    result = safe_input_number()
    
    # 2. 多种异常类型处理
    print("\n2. 处理多种异常类型：")
    
    def process_data(data_list, index):
        """处理列表数据，可能出现多种异常"""
        try:
            value = data_list[index]
            result = 100 / value
            return result
        except IndexError:
            print(f"    索引错误：索引{index}超出范围")
        except ZeroDivisionError:
            print(f"    除零错误：不能除以零")
        except TypeError:
            print(f"    类型错误：数据类型不正确")
        except Exception as e:
            print(f"    其他错误：{e}")
        
        return None
    
    # 测试不同的异常情况
    test_data = [1, 2, 0, 4, 5]
    test_cases = [
        (test_data, 1),   # 正常情况
        (test_data, 10),  # 索引错误
        (test_data, 2),   # 除零错误
    ]
    
    for data, idx in test_cases:
        print(f"  测试数据{data}，索引{idx}：")
        result = process_data(data, idx)
        if result is not None:
            print(f"    结果：{result}")
    
    # 3. try-except-else-finally结构
    print("\n3. 完整的异常处理结构：")
    
    def file_operation_simulation():
        """模拟文件操作的异常处理"""
        filename = "test.txt"
        
        try:
            print(f"    尝试打开文件：{filename}")
            # 模拟文件操作
            file_exists = False  # 模拟文件不存在
            if not file_exists:
                raise FileNotFoundError(f"文件{filename}不存在")
            
            print(f"    成功打开文件：{filename}")
            
        except FileNotFoundError as e:
            print(f"    文件错误：{e}")
            return False
        
        except PermissionError:
            print(f"    权限错误：无法访问文件{filename}")
            return False
        
        else:
            print(f"    文件操作成功完成")
            return True
        
        finally:
            print(f"    清理资源（无论是否出现异常）")
    
    file_operation_simulation()


def program_structure_best_practices():
    """程序结构设计最佳实践"""
    print("\n=== 程序结构设计最佳实践 ===")
    
    # 1. 早期返回模式
    print("1. 使用早期返回避免深层嵌套：")
    
    def validate_user_bad(user_data):
        """不好的写法：深层嵌套"""
        if user_data is not None:
            if "name" in user_data:
                if user_data["name"]:
                    if len(user_data["name"]) >= 2:
                        if "age" in user_data:
                            if isinstance(user_data["age"], int):
                                if user_data["age"] >= 0:
                                    return True, "用户数据有效"
        return False, "用户数据无效"
    
    def validate_user_good(user_data):
        """好的写法：早期返回"""
        if user_data is None:
            return False, "用户数据为空"
        
        if "name" not in user_data:
            return False, "缺少姓名字段"
        
        if not user_data["name"]:
            return False, "姓名不能为空"
        
        if len(user_data["name"]) < 2:
            return False, "姓名长度不足"
        
        if "age" not in user_data:
            return False, "缺少年龄字段"
        
        if not isinstance(user_data["age"], int):
            return False, "年龄必须是整数"
        
        if user_data["age"] < 0:
            return False, "年龄不能为负数"
        
        return True, "用户数据有效"
    
    # 测试两种写法
    test_user = {"name": "张三", "age": 25}
    
    is_valid_bad, msg_bad = validate_user_bad(test_user)
    is_valid_good, msg_good = validate_user_good(test_user)
    
    print(f"  嵌套写法结果：{is_valid_bad}, {msg_bad}")
    print(f"  早期返回结果：{is_valid_good}, {msg_good}")
    
    # 2. 状态机模式
    print("\n2. 使用状态机处理复杂流程：")
    
    class SimpleStateMachine:
        """简单状态机示例"""
        
        def __init__(self):
            self.state = "idle"
            self.states = {
                "idle": self.handle_idle,
                "processing": self.handle_processing,
                "completed": self.handle_completed,
                "error": self.handle_error
            }
        
        def handle_idle(self, event):
            if event == "start":
                self.state = "processing"
                return "开始处理"
            return "等待开始信号"
        
        def handle_processing(self, event):
            if event == "success":
                self.state = "completed"
                return "处理成功"
            elif event == "error":
                self.state = "error"
                return "处理出错"
            return "正在处理中"
        
        def handle_completed(self, event):
            if event == "reset":
                self.state = "idle"
                return "重置为空闲状态"
            return "已完成"
        
        def handle_error(self, event):
            if event == "retry":
                self.state = "processing"
                return "重试处理"
            elif event == "reset":
                self.state = "idle"
                return "重置为空闲状态"
            return "错误状态"
        
        def process_event(self, event):
            handler = self.states.get(self.state)
            if handler:
                result = handler(event)
                print(f"    状态：{self.state}，事件：{event}，结果：{result}")
                return result
            return "未知状态"
    
    # 测试状态机
    sm = SimpleStateMachine()
    events = ["start", "success", "reset", "start", "error", "retry", "success"]
    
    for event in events:
        sm.process_event(event)
    
    # 3. 责任链模式
    print("\n3. 责任链模式处理请求：")
    
    class RequestHandler:
        """请求处理器基类"""
        
        def __init__(self):
            self.next_handler = None
        
        def set_next(self, handler):
            self.next_handler = handler
            return handler
        
        def handle(self, request):
            if self.can_handle(request):
                return self.process(request)
            elif self.next_handler:
                return self.next_handler.handle(request)
            else:
                return f"无法处理请求：{request}"
        
        def can_handle(self, request):
            return False
        
        def process(self, request):
            return f"处理请求：{request}"
    
    class AuthHandler(RequestHandler):
        """认证处理器"""
        
        def can_handle(self, request):
            return request.get("type") == "auth"
        
        def process(self, request):
            return f"认证处理：用户{request.get('user', '未知')}"
    
    class DataHandler(RequestHandler):
        """数据处理器"""
        
        def can_handle(self, request):
            return request.get("type") == "data"
        
        def process(self, request):
            return f"数据处理：{request.get('data', '无数据')}"
    
    # 构建责任链
    auth_handler = AuthHandler()
    data_handler = DataHandler()
    auth_handler.set_next(data_handler)
    
    # 测试请求
    requests = [
        {"type": "auth", "user": "张三"},
        {"type": "data", "data": "用户信息"},
        {"type": "unknown", "content": "未知请求"}
    ]
    
    for req in requests:
        result = auth_handler.handle(req)
        print(f"    请求：{req} -> 结果：{result}")


def control_flow_patterns():
    """常用控制流程模式"""
    print("\n=== 常用控制流程模式 ===")
    
    # 1. 重试模式
    print("1. 重试模式：")
    
    def retry_operation(operation, max_retries=3):
        """重试操作模式"""
        for attempt in range(max_retries):
            try:
                print(f"    第{attempt + 1}次尝试")
                result = operation()
                print(f"    操作成功：{result}")
                return result
            except Exception as e:
                print(f"    第{attempt + 1}次尝试失败：{e}")
                if attempt == max_retries - 1:
                    print(f"    达到最大重试次数，操作失败")
                    raise
                continue
    
    def unreliable_operation():
        """模拟不稳定的操作"""
        import random
        if random.random() < 0.7:  # 70%的失败率
            raise Exception("操作失败")
        return "操作成功"
    
    try:
        retry_operation(unreliable_operation)
    except Exception:
        print("    最终操作失败")
    
    # 2. 批处理模式
    print("\n2. 批处理模式：")
    
    def batch_process(items, batch_size=3):
        """批处理模式"""
        total_items = len(items)
        processed = 0
        
        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]
            print(f"    处理批次 {i//batch_size + 1}：{batch}")
            
            # 模拟批处理
            for item in batch:
                try:
                    # 模拟处理可能失败
                    if item == "error":
                        raise ValueError(f"处理项目{item}时出错")
                    processed += 1
                except ValueError as e:
                    print(f"      跳过错误项目：{e}")
                    continue
            
            print(f"    批次处理完成，已处理{processed}/{total_items}项")
    
    test_items = ["item1", "item2", "error", "item4", "item5", "item6", "item7"]
    batch_process(test_items)
    
    # 3. 管道模式
    print("\n3. 管道模式：")
    
    def pipeline_process(data, *processors):
        """管道处理模式"""
        result = data
        
        for i, processor in enumerate(processors):
            try:
                print(f"    阶段{i + 1}：{processor.__name__}")
                result = processor(result)
                print(f"      结果：{result}")
            except Exception as e:
                print(f"      阶段{i + 1}处理失败：{e}")
                break
        
        return result
    
    def validate_data(data):
        """验证数据"""
        if not isinstance(data, list):
            raise TypeError("数据必须是列表")
        return data
    
    def filter_positive(data):
        """过滤正数"""
        return [x for x in data if x > 0]
    
    def calculate_sum(data):
        """计算总和"""
        return sum(data)
    
    test_data = [1, -2, 3, 4, -5, 6]
    final_result = pipeline_process(
        test_data,
        validate_data,
        filter_positive,
        calculate_sum
    )
    print(f"    最终结果：{final_result}")


if __name__ == "__main__":
    """运行所有示例"""
    print("Python流程控制完整示例")
    print("=" * 50)
    
    break_statement_examples()
    continue_statement_examples()
    pass_statement_examples()
    exception_flow_control()
    program_structure_best_practices()
    control_flow_patterns()
    
    print("\n" + "=" * 50)
    print("流程控制学习完成！")
    print("下一步：完成控制流程练习（exercises.py）")