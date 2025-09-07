#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python模块化编程示例
===================

本文件演示Python中模块的导入、使用和管理方法。
包含import和from import的不同用法，模块搜索路径，以及动态导入等高级特性。

学习目标：
- 理解模块的概念和作用
- 掌握不同的导入方式
- 了解模块搜索机制
- 学会使用动态导入和模块重载
"""

import sys
import os
import importlib
import math
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json as json_module  # 使用别名导入


def demonstrate_basic_imports():
    """演示基本的导入方式"""
    print("=== 基本导入方式演示 ===")
    
    # 1. 完整模块导入
    print("\n1. 完整模块导入 (import module)")
    print(f"使用math模块计算: math.pi = {math.pi}")
    print(f"使用math模块计算: math.sqrt(16) = {math.sqrt(16)}")
    
    # 2. 从模块导入特定函数/类
    print("\n2. 从模块导入特定内容 (from module import item)")
    from math import sin, cos, pi
    print(f"直接使用导入的函数: sin(pi/2) = {sin(pi/2)}")
    print(f"直接使用导入的常量: pi = {pi}")
    
    # 3. 导入所有内容（不推荐）
    print("\n3. 导入所有内容 (from module import *)")
    print("注意：from module import * 不推荐使用，可能造成命名冲突")
    
    # 4. 使用别名导入
    print("\n4. 使用别名导入 (import module as alias)")
    try:
        import numpy as np  # 这是一个常见的别名用法示例
        print("成功导入: import numpy as np")
    except ImportError:
        print("numpy未安装，这里演示别名导入概念")
    print("常见别名: import numpy as np, import pandas as pd")
    
    # 5. 从模块导入并使用别名
    print("\n5. 从模块导入特定内容并使用别名")
    from datetime import datetime as dt
    print(f"使用别名: dt.now() = {dt.now()}")


def demonstrate_module_search_path():
    """演示模块搜索路径"""
    print("\n=== 模块搜索路径演示 ===")
    
    print("Python模块搜索顺序：")
    print("1. 当前工作目录")
    print("2. PYTHONPATH环境变量指定的目录")
    print("3. Python标准库目录")
    print("4. site-packages目录（第三方包）")
    
    print(f"\n当前工作目录: {os.getcwd()}")
    print(f"Python可执行文件路径: {sys.executable}")
    
    print("\n当前模块搜索路径 (sys.path):")
    for i, path in enumerate(sys.path, 1):
        print(f"{i:2d}. {path}")
    
    # 动态添加搜索路径
    print("\n动态添加搜索路径:")
    new_path = "/tmp/my_modules"  # 示例路径
    if new_path not in sys.path:
        sys.path.append(new_path)
        print(f"已添加路径: {new_path}")
    else:
        print(f"路径已存在: {new_path}")


def demonstrate_package_structure():
    """演示包结构和__init__.py的作用"""
    print("\n=== 包结构演示 ===")
    
    print("Python包的基本结构:")
    print("""
    mypackage/
    ├── __init__.py          # 包初始化文件
    ├── module1.py           # 模块1
    ├── module2.py           # 模块2
    └── subpackage/          # 子包
        ├── __init__.py      # 子包初始化文件
        └── submodule.py     # 子模块
    """)
    
    print("__init__.py文件的作用:")
    print("1. 标识目录为Python包")
    print("2. 控制包的导入行为")
    print("3. 可以包含包级别的初始化代码")
    print("4. 定义__all__变量控制from package import *的行为")
    
    # 演示当前包的结构
    print(f"\n当前模块所在包: {__package__}")
    print(f"当前模块名称: {__name__}")
    print(f"当前文件路径: {__file__}")


def demonstrate_dynamic_import():
    """演示动态导入"""
    print("\n=== 动态导入演示 ===")
    
    # 1. 使用importlib.import_module()
    print("1. 使用importlib.import_module()动态导入:")
    
    module_names = ['json', 'random', 'string']
    imported_modules = {}
    
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            imported_modules[module_name] = module
            print(f"   成功导入模块: {module_name}")
        except ImportError as e:
            print(f"   导入失败: {module_name} - {e}")
    
    # 使用动态导入的模块
    if 'json' in imported_modules:
        json_mod = imported_modules['json']
        data = {"name": "Python", "version": "3.9"}
        json_str = json_mod.dumps(data)
        print(f"   使用动态导入的json模块: {json_str}")
    
    # 2. 使用__import__()函数（不推荐）
    print("\n2. 使用__import__()函数（不推荐，仅作演示）:")
    math_module = __import__('math')
    print(f"   使用__import__导入math: {math_module.factorial(5)}")


def demonstrate_module_reload():
    """演示模块重载"""
    print("\n=== 模块重载演示 ===")
    
    print("模块重载的使用场景:")
    print("1. 开发调试时修改模块代码")
    print("2. 动态更新配置模块")
    print("3. 热更新功能实现")
    
    # 重载示例（需要已导入的模块）
    print(f"\n重载前json模块的id: {id(json_module)}")
    
    try:
        # 重载模块
        reloaded_json = importlib.reload(json_module)
        print(f"重载后json模块的id: {id(reloaded_json)}")
        print("注意: 重载后模块对象的id可能会改变")
    except Exception as e:
        print(f"重载失败: {e}")
    
    print("\n重载注意事项:")
    print("1. 只能重载已经导入的模块")
    print("2. 重载不会影响已经创建的对象")
    print("3. 重载可能导致内存泄漏")
    print("4. 生产环境中谨慎使用")


def demonstrate_module_attributes():
    """演示模块属性和内省"""
    print("\n=== 模块属性和内省演示 ===")
    
    # 模块的特殊属性
    print("模块的特殊属性:")
    print(f"__name__: {__name__}")
    print(f"__file__: {__file__}")
    print(f"__package__: {__package__}")
    print(f"__doc__: {__doc__[:50]}..." if __doc__ else "None")
    
    # 查看模块的所有属性
    print(f"\n当前模块的所有属性数量: {len(dir())}")
    print("部分属性列表:")
    module_attrs = [attr for attr in dir() if not attr.startswith('_')]
    for attr in module_attrs[:10]:  # 只显示前10个
        print(f"  - {attr}")
    
    # 检查模块是否有特定属性
    print(f"\n检查模块属性:")
    print(f"hasattr(math, 'pi'): {hasattr(math, 'pi')}")
    print(f"hasattr(math, 'nonexistent'): {hasattr(math, 'nonexistent')}")
    
    # 获取模块属性
    if hasattr(math, 'pi'):
        pi_value = getattr(math, 'pi')
        print(f"getattr(math, 'pi'): {pi_value}")


def demonstrate_conditional_import():
    """演示条件导入"""
    print("\n=== 条件导入演示 ===")
    
    print("条件导入的常见场景:")
    
    # 1. 可选依赖
    print("\n1. 可选依赖处理:")
    try:
        import numpy as np
        HAS_NUMPY = True
        print("   numpy可用，启用高级数值计算功能")
    except ImportError:
        HAS_NUMPY = False
        print("   numpy不可用，使用基础数学功能")
    
    # 2. 版本兼容性
    print("\n2. Python版本兼容性:")
    if sys.version_info >= (3, 8):
        from functools import cached_property
        print("   Python 3.8+: 使用cached_property")
    else:
        print("   Python < 3.8: 使用自定义缓存属性实现")
    
    # 3. 平台特定导入
    print("\n3. 平台特定导入:")
    if sys.platform.startswith('win'):
        print("   Windows平台: 可导入winsound等Windows特定模块")
    elif sys.platform.startswith('linux'):
        print("   Linux平台: 可导入Linux特定模块")
    else:
        print(f"   其他平台 ({sys.platform}): 使用通用模块")


def demonstrate_best_practices():
    """演示模块导入的最佳实践"""
    print("\n=== 模块导入最佳实践 ===")
    
    print("1. 导入顺序规范 (PEP 8):")
    print("   a) 标准库导入")
    print("   b) 相关第三方库导入")
    print("   c) 本地应用/库导入")
    print("   d) 每组之间用空行分隔")
    
    print("\n2. 导入语句规范:")
    print("   ✓ 推荐: import os")
    print("   ✓ 推荐: from os import path")
    print("   ✗ 避免: from os import *")
    print("   ✗ 避免: import os, sys  # 应该分行")
    
    print("\n3. 别名使用规范:")
    print("   ✓ 推荐: import numpy as np")
    print("   ✓ 推荐: import pandas as pd")
    print("   ✗ 避免: import numpy as n  # 别名太短")
    
    print("\n4. 循环导入避免:")
    print("   - 重新设计模块结构")
    print("   - 使用延迟导入")
    print("   - 将共同依赖提取到单独模块")
    
    print("\n5. 性能考虑:")
    print("   - 避免在函数内重复导入")
    print("   - 大型模块考虑延迟导入")
    print("   - 使用from import减少属性查找")


def create_example_module():
    """创建一个示例模块文件"""
    print("\n=== 创建示例模块 ===")
    
    example_module_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例模块 - example_module.py
这是一个演示模块结构的示例文件
"""

# 模块级别的变量
MODULE_VERSION = "1.0.0"
MODULE_AUTHOR = "Python学习者"

# 控制from module import *的行为
__all__ = ['greet', 'calculate', 'CONSTANT_VALUE']

# 模块常量
CONSTANT_VALUE = 42

def greet(name):
    """问候函数"""
    return f"你好, {name}!"

def calculate(x, y):
    """简单计算函数"""
    return x * y + CONSTANT_VALUE

class ExampleClass:
    """示例类"""
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

# 模块初始化代码
print(f"模块 {__name__} 已加载")
'''
    
    # 将示例模块内容写入临时文件（仅作演示）
    temp_file = "temp_example_module.py"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(example_module_content)
        print(f"示例模块已创建: {temp_file}")
        
        # 演示如何导入和使用
        print("\n导入和使用示例:")
        print("import temp_example_module as em")
        print("print(em.greet('张三'))")
        print("print(em.calculate(5, 3))")
        
    except Exception as e:
        print(f"创建示例模块失败: {e}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"已清理临时文件: {temp_file}")


def main():
    """主函数 - 运行所有演示"""
    print("Python模块化编程完整演示")
    print("=" * 50)
    
    try:
        demonstrate_basic_imports()
        demonstrate_module_search_path()
        demonstrate_package_structure()
        demonstrate_dynamic_import()
        demonstrate_module_reload()
        demonstrate_module_attributes()
        demonstrate_conditional_import()
        demonstrate_best_practices()
        create_example_module()
        
        print("\n" + "=" * 50)
        print("模块化编程演示完成！")
        print("\n学习要点总结:")
        print("1. 掌握不同的导入方式和使用场景")
        print("2. 理解模块搜索路径和包结构")
        print("3. 学会使用动态导入和模块重载")
        print("4. 遵循导入的最佳实践和规范")
        print("5. 避免常见的导入陷阱和问题")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()