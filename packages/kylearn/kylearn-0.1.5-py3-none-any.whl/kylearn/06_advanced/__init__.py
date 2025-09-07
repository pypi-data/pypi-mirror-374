"""
高级特性学习模块

本模块包含Python高级特性的学习内容：
- 异常处理
- 模块化
- 文件操作
- 高级特性练习
"""

__version__ = "1.0.0"
__author__ = "Python Learning System"

# 导出主要组件
from . import exceptions, modules, file_handling

__all__ = ['exceptions', 'modules', 'file_handling']