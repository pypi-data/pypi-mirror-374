
"""
Python学习系统 (KyLearn - Python Learning)

一个系统化的Python学习资源包，提供从基础到高级的完整学习路径。

主要模块:
- 01_basics: 基础语法
- 02_control_flow: 控制流程  
- 03_data_structures: 数据结构
- 04_functions: 函数
- 05_oop: 面向对象编程
- generators: 生成器和yield
- 06_advanced: 高级特性
- 07_projects: 综合项目

使用方法:
    from kylearn import LearningGuide
    from kylearn.generators import GeneratorGuide
    
    guide = LearningGuide()
    print(guide.get_learning_path())
    
    gen_guide = GeneratorGuide()
    gen_guide.start_section('yield_basics')
"""

import fire
from .learning_guide import LearningGuide

__version__ = "1.0.0"
__author__ = "Python Learning System"

# 导出主要组件
__all__ = ['LearningGuide', 'ENTRY', 'main']


class ENTRY(object):
    """命令行入口类"""
    
    def __init__(self):
        self.guide = LearningGuide()
    
    def hello(self):
        """问候信息"""
        print("欢迎使用Python学习系统!")
        print("使用 'path' 命令查看学习路径")
        print("使用 'module <模块名>' 命令查看模块详情")
    
    def path(self):
        """显示完整学习路径"""
        print("=== Python学习路径 ===")
        for i, module in enumerate(self.guide.get_learning_path(), 1):
            module_info = self.guide._modules[module]
            print(f"{i}. {module_info.name} ({module}) - {module_info.estimated_time}分钟")
    
    def module(self, module_name: str):
        """显示指定模块的详细信息"""
        try:
            print(f"=== {module_name} 模块详情 ===")
            print(self.guide.get_module_description(module_name))
        except KeyError as e:
            print(f"错误: {e}")
            print("可用模块:", ", ".join(self.guide.get_all_modules().keys()))
    
    def progress(self, *completed_modules):
        """显示学习进度 (传入已完成的模块名)"""
        completed = list(completed_modules)
        print(self.guide.get_learning_progress_summary(completed))
    
    def next_step(self, current_module: str):
        """获取下一步学习建议"""
        suggestion = self.guide.suggest_next_step(current_module)
        print(f"学习建议: {suggestion}")
    
    def generators(self, action: str = "info"):
        """生成器学习模块"""
        from .generators import GeneratorGuide
        
        gen_guide = GeneratorGuide()
        
        if action == "info":
            print("=== 生成器学习模块 ===")
            sections = gen_guide.get_learning_sections()
            for i, section in enumerate(sections, 1):
                info = gen_guide.get_section_info(section)
                print(f"{i}. {info['name']} ({section}) - {info['estimated_time']}分钟")
                print(f"   {info['description']}")
        elif action == "start":
            print("开始生成器学习！使用 'generators section <章节名>' 来学习特定章节")
            print("可用章节:", ", ".join(gen_guide.get_learning_sections()))
        else:
            print(f"未知操作: {action}")
            print("可用操作: info, start")
    
    def generator_section(self, section_name: str):
        """学习特定的生成器章节"""
        from .generators import GeneratorGuide
        
        gen_guide = GeneratorGuide()
        try:
            gen_guide.start_section(section_name)
        except KeyError as e:
            print(f"错误: {e}")
            print("可用章节:", ", ".join(gen_guide.get_learning_sections()))


def main() -> None:
    """主入口函数"""
    fire.Fire(ENTRY)








