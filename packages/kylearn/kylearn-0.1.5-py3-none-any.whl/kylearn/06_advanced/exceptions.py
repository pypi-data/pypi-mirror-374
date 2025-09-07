"""
异常处理示例文件
=================

本文件演示Python中异常处理的各种用法，包括：
- 基本的try、except、finally、raise语句
- 自定义异常类
- 异常链和上下文管理器
- 异常处理最佳实践

学习目标：
1. 掌握异常处理的基本语法
2. 学会创建和使用自定义异常
3. 理解异常链的概念和用法
4. 掌握上下文管理器的使用
"""

import logging
import traceback
from typing import Optional, Any
from contextlib import contextmanager

# ============================================================================
# 1. 基本异常处理语法
# ============================================================================

def basic_exception_handling():
    """演示基本的异常处理语法"""
    print("=== 基本异常处理 ===")
    
    # 1.1 基本的try-except结构
    try:
        result = 10 / 0  # 这会引发ZeroDivisionError
    except ZeroDivisionError:
        print("捕获到除零错误")
    
    # 1.2 捕获多种异常类型
    try:
        numbers = [1, 2, 3]
        print(numbers[10])  # IndexError
    except (IndexError, ValueError) as e:
        print(f"捕获到异常: {type(e).__name__}: {e}")
    
    # 1.3 使用else子句（当没有异常时执行）
    try:
        result = 10 / 2
    except ZeroDivisionError:
        print("除零错误")
    else:
        print(f"计算成功，结果是: {result}")
    
    # 1.4 使用finally子句（无论是否有异常都会执行）
    try:
        file = open("nonexistent.txt", "r")
    except FileNotFoundError:
        print("文件未找到")
    finally:
        print("清理资源（finally块总是执行）")


def exception_hierarchy_demo():
    """演示异常层次结构和捕获顺序"""
    print("\n=== 异常层次结构 ===")
    
    # 异常捕获应该从具体到一般
    try:
        # 这里可能抛出不同类型的异常
        raise ValueError("这是一个值错误")
    except ValueError as e:
        print(f"捕获到ValueError: {e}")
    except Exception as e:
        print(f"捕获到其他异常: {e}")
    
    # 错误的做法：先捕获基类会导致子类异常永远不会被捕获
    # except Exception as e:  # 这应该放在最后
    #     print(f"捕获到异常: {e}")
    # except ValueError as e:  # 这行代码永远不会执行
    #     print(f"捕获到ValueError: {e}")


# ============================================================================
# 2. 自定义异常类
# ============================================================================

class CustomError(Exception):
    """基础自定义异常类"""
    pass


class ValidationError(CustomError):
    """数据验证异常"""
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field
        self.message = message
    
    def __str__(self):
        if self.field:
            return f"验证错误 [{self.field}]: {self.message}"
        return f"验证错误: {self.message}"


class BusinessLogicError(CustomError):
    """业务逻辑异常"""
    def __init__(self, message: str, error_code: int = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
    
    def __str__(self):
        if self.error_code:
            return f"业务错误 [{self.error_code}]: {self.message}"
        return f"业务错误: {self.message}"


def custom_exception_demo():
    """演示自定义异常的使用"""
    print("\n=== 自定义异常 ===")
    
    def validate_age(age: int):
        """验证年龄的函数"""
        if not isinstance(age, int):
            raise ValidationError("年龄必须是整数", "age")
        if age < 0:
            raise ValidationError("年龄不能为负数", "age")
        if age > 150:
            raise ValidationError("年龄不能超过150岁", "age")
        return True
    
    def process_user_registration(name: str, age: int):
        """用户注册处理函数"""
        if not name.strip():
            raise ValidationError("姓名不能为空", "name")
        
        validate_age(age)
        
        # 模拟业务逻辑检查
        if name.lower() == "admin":
            raise BusinessLogicError("不能使用保留用户名", 1001)
        
        return f"用户 {name}（{age}岁）注册成功"
    
    # 测试自定义异常
    test_cases = [
        ("张三", 25),      # 正常情况
        ("", 30),          # 姓名为空
        ("李四", -5),      # 年龄为负
        ("admin", 25),     # 保留用户名
        ("王五", "abc"),   # 年龄类型错误
    ]
    
    for name, age in test_cases:
        try:
            result = process_user_registration(name, age)
            print(f"✓ {result}")
        except ValidationError as e:
            print(f"✗ 验证失败: {e}")
        except BusinessLogicError as e:
            print(f"✗ 业务错误: {e}")
        except Exception as e:
            print(f"✗ 未预期的错误: {e}")


# ============================================================================
# 3. 异常链和异常传播
# ============================================================================

def exception_chaining_demo():
    """演示异常链的使用"""
    print("\n=== 异常链 ===")
    
    def parse_config_file(filename: str):
        """解析配置文件"""
        try:
            with open(filename, 'r') as f:
                content = f.read()
                # 模拟JSON解析错误
                if "invalid" in content:
                    raise ValueError("无效的JSON格式")
                return {"config": "loaded"}
        except FileNotFoundError as e:
            # 使用 raise ... from e 创建异常链
            raise BusinessLogicError(f"配置文件加载失败: {filename}") from e
        except ValueError as e:
            # 使用 raise ... from e 保留原始异常信息
            raise BusinessLogicError("配置文件格式错误") from e
    
    def initialize_application():
        """初始化应用程序"""
        try:
            config = parse_config_file("config.json")
            return config
        except BusinessLogicError as e:
            # 再次包装异常，形成异常链
            raise RuntimeError("应用程序初始化失败") from e
    
    # 测试异常链
    try:
        initialize_application()
    except RuntimeError as e:
        print(f"最终异常: {e}")
        print(f"原因: {e.__cause__}")
        if e.__cause__ and e.__cause__.__cause__:
            print(f"根本原因: {e.__cause__.__cause__}")
        
        # 打印完整的异常链
        print("\n完整异常链:")
        traceback.print_exc()


def exception_suppression_demo():
    """演示异常抑制"""
    print("\n=== 异常抑制 ===")
    
    def risky_operation():
        """可能出错的操作"""
        raise ValueError("操作失败")
    
    def cleanup_operation():
        """清理操作也可能出错"""
        raise RuntimeError("清理失败")
    
    # 不使用异常抑制（cleanup异常会掩盖原始异常）
    try:
        try:
            risky_operation()
        finally:
            cleanup_operation()  # 这个异常会掩盖risky_operation的异常
    except Exception as e:
        print(f"捕获到异常: {e}")  # 只会看到cleanup的异常
    
    # 使用异常抑制
    try:
        try:
            risky_operation()
        finally:
            try:
                cleanup_operation()
            except Exception:
                pass  # 抑制cleanup异常，保留原始异常
    except Exception as e:
        print(f"捕获到原始异常: {e}")


# ============================================================================
# 4. 上下文管理器
# ============================================================================

class DatabaseConnection:
    """模拟数据库连接的上下文管理器"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connected = False
    
    def __enter__(self):
        """进入上下文时调用"""
        print(f"连接到数据库: {self.connection_string}")
        self.connected = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时调用"""
        if self.connected:
            print("关闭数据库连接")
            self.connected = False
        
        # 如果有异常发生
        if exc_type is not None:
            print(f"处理异常: {exc_type.__name__}: {exc_val}")
            # 返回False表示不抑制异常，True表示抑制异常
            return False
    
    def execute_query(self, query: str):
        """执行查询"""
        if not self.connected:
            raise RuntimeError("数据库未连接")
        
        if "DROP" in query.upper():
            raise ValueError("危险操作被禁止")
        
        return f"执行查询: {query}"


@contextmanager
def temporary_file(filename: str):
    """使用生成器创建上下文管理器"""
    print(f"创建临时文件: {filename}")
    try:
        # 模拟创建文件
        file_handle = open(filename, 'w')
        yield file_handle
    except Exception as e:
        print(f"文件操作出错: {e}")
        raise
    finally:
        # 清理资源
        if 'file_handle' in locals():
            file_handle.close()
        print(f"清理临时文件: {filename}")


def context_manager_demo():
    """演示上下文管理器的使用"""
    print("\n=== 上下文管理器 ===")
    
    # 1. 使用自定义上下文管理器
    print("1. 数据库连接上下文管理器:")
    try:
        with DatabaseConnection("mysql://localhost:3306/test") as db:
            result = db.execute_query("SELECT * FROM users")
            print(f"查询结果: {result}")
            # 模拟异常
            db.execute_query("DROP TABLE users")
    except Exception as e:
        print(f"操作失败: {e}")
    
    print("\n2. 生成器上下文管理器:")
    try:
        with temporary_file("temp.txt") as f:
            f.write("临时数据")
            print("文件写入成功")
    except Exception as e:
        print(f"文件操作失败: {e}")
    
    # 3. 多个上下文管理器
    print("\n3. 多个上下文管理器:")
    try:
        with DatabaseConnection("db1") as db1, \
             DatabaseConnection("db2") as db2:
            print("同时使用两个数据库连接")
            db1.execute_query("SELECT 1")
            db2.execute_query("SELECT 2")
    except Exception as e:
        print(f"多连接操作失败: {e}")


# ============================================================================
# 5. 异常处理最佳实践
# ============================================================================

def logging_exceptions_demo():
    """演示异常日志记录的最佳实践"""
    print("\n=== 异常日志记录 ===")
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    def process_data(data: Any):
        """处理数据的函数"""
        try:
            if data is None:
                raise ValueError("数据不能为空")
            
            if isinstance(data, str) and len(data) == 0:
                raise ValueError("字符串数据不能为空")
            
            # 模拟处理过程
            result = str(data).upper()
            logger.info(f"数据处理成功: {data} -> {result}")
            return result
            
        except ValueError as e:
            # 记录业务异常
            logger.warning(f"数据验证失败: {e}")
            raise
        except Exception as e:
            # 记录未预期的异常
            logger.error(f"数据处理出现未预期错误: {e}", exc_info=True)
            raise
    
    # 测试异常日志记录
    test_data = ["hello", "", None, 123]
    
    for data in test_data:
        try:
            result = process_data(data)
            print(f"✓ 处理成功: {data} -> {result}")
        except Exception as e:
            print(f"✗ 处理失败: {data} -> {e}")


def exception_handling_patterns():
    """演示异常处理的常见模式"""
    print("\n=== 异常处理模式 ===")
    
    # 1. 重试模式
    def retry_operation(max_attempts: int = 3):
        """重试操作模式"""
        import random
        
        for attempt in range(max_attempts):
            try:
                # 模拟可能失败的操作
                if random.random() < 0.7:  # 70%的失败率
                    raise ConnectionError("网络连接失败")
                
                print(f"操作成功（第{attempt + 1}次尝试）")
                return "操作成功"
                
            except ConnectionError as e:
                if attempt == max_attempts - 1:
                    print(f"重试{max_attempts}次后仍然失败: {e}")
                    raise
                else:
                    print(f"第{attempt + 1}次尝试失败，准备重试: {e}")
    
    # 2. 回退模式
    def fallback_operation():
        """回退操作模式"""
        try:
            # 尝试主要操作
            raise ConnectionError("主服务器不可用")
        except ConnectionError:
            print("主操作失败，使用备用方案")
            return "使用缓存数据"
    
    # 3. 电路熔断模式（简化版）
    class CircuitBreaker:
        def __init__(self, failure_threshold: int = 3):
            self.failure_count = 0
            self.failure_threshold = failure_threshold
            self.is_open = False
        
        def call(self, func, *args, **kwargs):
            if self.is_open:
                raise RuntimeError("电路熔断器已打开")
            
            try:
                result = func(*args, **kwargs)
                self.failure_count = 0  # 重置失败计数
                return result
            except Exception as e:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.is_open = True
                    print("电路熔断器打开")
                raise
    
    # 测试各种模式
    print("1. 重试模式:")
    try:
        retry_operation()
    except Exception as e:
        print(f"最终失败: {e}")
    
    print("\n2. 回退模式:")
    result = fallback_operation()
    print(f"结果: {result}")
    
    print("\n3. 电路熔断模式:")
    breaker = CircuitBreaker(failure_threshold=2)
    
    def failing_service():
        raise ConnectionError("服务不可用")
    
    for i in range(4):
        try:
            breaker.call(failing_service)
        except Exception as e:
            print(f"调用{i+1}失败: {e}")


# ============================================================================
# 6. 性能考虑和调试技巧
# ============================================================================

def performance_considerations():
    """异常处理的性能考虑"""
    print("\n=== 性能考虑 ===")
    
    import time
    
    # 1. 异常处理的性能开销
    def test_exception_performance():
        """测试异常处理的性能开销"""
        
        # 正常流程
        start_time = time.time()
        for i in range(10000):
            try:
                result = i * 2
            except:
                pass
        normal_time = time.time() - start_time
        
        # 异常流程
        start_time = time.time()
        for i in range(1000):  # 减少次数，因为异常很慢
            try:
                raise ValueError("测试异常")
            except ValueError:
                pass
        exception_time = time.time() - start_time
        
        print(f"正常流程时间: {normal_time:.4f}秒")
        print(f"异常流程时间: {exception_time:.4f}秒")
        print("结论: 异常处理比正常流程慢很多，不应该用于控制程序流程")
    
    test_exception_performance()
    
    # 2. 使用EAFP vs LBYL
    def eafp_vs_lbyl_demo():
        """演示EAFP vs LBYL的区别"""
        data = {"key1": "value1", "key2": "value2"}
        
        # LBYL (Look Before You Leap) - 先检查再操作
        def lbyl_approach(key):
            if key in data:
                return data[key]
            else:
                return None
        
        # EAFP (Easier to Ask for Forgiveness than Permission) - 先操作再处理异常
        def eafp_approach(key):
            try:
                return data[key]
            except KeyError:
                return None
        
        print("\nEAFP vs LBYL:")
        print(f"LBYL结果: {lbyl_approach('key1')}")
        print(f"EAFP结果: {eafp_approach('key1')}")
        print("Python推荐使用EAFP风格")
    
    eafp_vs_lbyl_demo()


def debugging_techniques():
    """异常调试技巧"""
    print("\n=== 调试技巧 ===")
    
    # 1. 获取详细的异常信息
    def detailed_exception_info():
        """获取详细的异常信息"""
        try:
            # 创建一个复杂的调用栈
            def level1():
                def level2():
                    def level3():
                        raise ValueError("深层异常")
                    level3()
                level2()
            level1()
        except Exception as e:
            print("异常类型:", type(e).__name__)
            print("异常消息:", str(e))
            print("异常参数:", e.args)
            
            # 获取异常的traceback信息
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            print("\n调用栈信息:")
            traceback.print_tb(exc_traceback)
            
            print("\n格式化的异常信息:")
            traceback.print_exc()
    
    detailed_exception_info()
    
    # 2. 自定义异常钩子
    def custom_exception_hook(exc_type, exc_value, exc_traceback):
        """自定义异常钩子"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 对于键盘中断，只显示简单消息
            print("程序被用户中断")
        else:
            # 对于其他异常，显示详细信息
            print(f"未处理的异常: {exc_type.__name__}: {exc_value}")
            traceback.print_tb(exc_traceback)
    
    # 注意：在实际应用中可以设置异常钩子
    # sys.excepthook = custom_exception_hook


# ============================================================================
# 7. 主函数和测试
# ============================================================================

def main():
    """主函数，演示所有异常处理概念"""
    print("Python异常处理完整示例")
    print("=" * 50)
    
    # 运行所有示例
    basic_exception_handling()
    exception_hierarchy_demo()
    custom_exception_demo()
    exception_chaining_demo()
    exception_suppression_demo()
    context_manager_demo()
    logging_exceptions_demo()
    exception_handling_patterns()
    performance_considerations()
    debugging_techniques()
    
    print("\n" + "=" * 50)
    print("异常处理学习完成！")
    print("\n关键要点总结:")
    print("1. 使用具体的异常类型，避免捕获所有异常")
    print("2. 异常处理不应该用于控制程序流程")
    print("3. 使用自定义异常类提供更好的错误信息")
    print("4. 利用异常链保留完整的错误上下文")
    print("5. 使用上下文管理器确保资源正确释放")
    print("6. 记录异常日志帮助调试和监控")
    print("7. 遵循EAFP原则，先尝试操作再处理异常")


if __name__ == "__main__":
    main()