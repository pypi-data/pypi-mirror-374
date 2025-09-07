"""
基础语法学习模块

本模块包含Python基础语法的学习内容：
- 变量和数据类型
- 运算符
- 注释规范
- 基础练习
"""

__version__ = "1.0.0"
__author__ = "Python Learning System"

# 导出主要组件
from . import variables, operators, comments

__all__ = ['variables', 'operators', 'comments']