"""
面向对象编程学习模块

本模块包含Python面向对象编程的学习内容：
- 类和对象
- 继承
- 封装
- 多态
- OOP练习
"""

__version__ = "1.0.0"
__author__ = "Python Learning System"

# 导出主要组件
from . import classes_objects, inheritance, encapsulation, polymorphism

__all__ = ['classes_objects', 'inheritance', 'encapsulation', 'polymorphism']