"""
Python学习系统 - 学习指南

本模块提供完整的Python学习路径指导，包括：
- 推荐的学习顺序
- 各模块的详细描述
- 前置条件检查
- 学习进度跟踪
- 下一步学习建议
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class LearningModule:
    """学习模块数据模型"""
    name: str                    # 模块名称
    description: str             # 模块描述
    prerequisites: List[str]     # 前置要求
    learning_objectives: List[str] # 学习目标
    examples: List[str]          # 示例文件路径
    exercises: List[str]         # 练习文件路径
    estimated_time: int          # 预估学习时间(分钟)


class LearningGuide:
    """Python学习指南类
    
    提供系统化的Python学习路径和进度管理功能
    """
    
    def __init__(self):
        """初始化学习指南"""
        self._modules = self._initialize_modules()
        self._learning_path = self._create_learning_path()
    
    def _initialize_modules(self) -> Dict[str, LearningModule]:
        """初始化所有学习模块"""
        return {
            "01_basics": LearningModule(
                name="基础语法",
                description="Python基础语法学习，包括变量、数据类型、运算符和注释规范",
                prerequisites=[],
                learning_objectives=[
                    "掌握Python变量定义和命名规范",
                    "理解基本数据类型：字符串、整数、浮点数、布尔值",
                    "熟练使用各种运算符",
                    "学会正确的注释写法"
                ],
                examples=["variables.py", "operators.py", "comments.py"],
                exercises=["exercises.py"],
                estimated_time=120
            ),
            
            "02_control_flow": LearningModule(
                name="控制流程",
                description="程序控制流程学习，包括条件语句、循环和流程控制",
                prerequisites=["01_basics"],
                learning_objectives=[
                    "掌握if、elif、else条件语句",
                    "熟练使用for和while循环",
                    "理解break、continue、pass的使用场景",
                    "能够编写嵌套的控制结构"
                ],
                examples=["conditions.py", "loops.py", "flow_control.py"],
                exercises=["exercises.py"],
                estimated_time=150
            ),
            
            "03_data_structures": LearningModule(
                name="数据结构",
                description="Python内置数据结构学习，包括列表、元组、字典和集合",
                prerequisites=["01_basics", "02_control_flow"],
                learning_objectives=[
                    "掌握列表的创建、访问和修改方法",
                    "理解元组的不可变特性和使用场景",
                    "熟练操作字典的键值对",
                    "掌握集合的去重和运算功能",
                    "能够选择合适的数据结构解决问题"
                ],
                examples=["lists.py", "tuples.py", "dictionaries.py", "sets.py"],
                exercises=["exercises.py"],
                estimated_time=180
            ),
            
            "04_functions": LearningModule(
                name="函数",
                description="函数定义和使用，包括参数传递、返回值和高级函数特性",
                prerequisites=["01_basics", "02_control_flow", "03_data_structures"],
                learning_objectives=[
                    "掌握函数的定义和调用",
                    "理解各种参数传递方式",
                    "熟练使用返回值",
                    "了解lambda函数、装饰器等高级特性",
                    "理解函数作用域和变量生命周期"
                ],
                examples=["basic_functions.py", "parameters.py", "advanced_functions.py"],
                exercises=["exercises.py"],
                estimated_time=200
            ),
            
            "05_oop": LearningModule(
                name="面向对象编程",
                description="面向对象编程概念，包括类、对象、继承、封装和多态",
                prerequisites=["01_basics", "02_control_flow", "03_data_structures", "04_functions"],
                learning_objectives=[
                    "掌握类和对象的定义与使用",
                    "理解继承的概念和实现方法",
                    "掌握封装和数据隐藏",
                    "理解多态和方法重写",
                    "熟练使用特殊方法(魔术方法)"
                ],
                examples=["classes_objects.py", "inheritance.py", "encapsulation.py", "polymorphism.py"],
                exercises=["exercises.py"],
                estimated_time=240
            ),
            
            "generators": LearningModule(
                name="生成器和yield",
                description="Python生成器学习，包括yield关键字、生成器概念和实际应用",
                prerequisites=["01_basics", "02_control_flow", "03_data_structures", "04_functions"],
                learning_objectives=[
                    "理解yield关键字的作用和用法",
                    "掌握生成器的概念和优势",
                    "学会创建和使用生成器函数",
                    "理解惰性求值和内存效率",
                    "能够在实际项目中应用生成器"
                ],
                examples=["basic_yield.py", "generator_vs_list.py", "real_world_cases.py"],
                exercises=["beginner.py", "intermediate.py", "advanced.py"],
                estimated_time=195
            ),
            
            "06_advanced": LearningModule(
                name="高级特性",
                description="Python高级特性，包括异常处理、模块化和文件操作",
                prerequisites=["01_basics", "02_control_flow", "03_data_structures", "04_functions", "05_oop", "generators"],
                learning_objectives=[
                    "掌握异常处理的完整流程",
                    "理解模块和包的概念",
                    "熟练进行文件操作",
                    "能够组织和管理代码结构"
                ],
                examples=["exceptions.py", "modules.py", "file_handling.py"],
                exercises=["exercises.py"],
                estimated_time=180
            ),
            
            "07_projects": LearningModule(
                name="综合项目",
                description="综合运用所学知识完成实际项目",
                prerequisites=["01_basics", "02_control_flow", "03_data_structures", "04_functions", "05_oop", "generators", "06_advanced"],
                learning_objectives=[
                    "综合运用所有学过的Python概念",
                    "完成具有实际意义的项目",
                    "掌项目组织和代码结构设计",
                    "培养解决实际问题的能力"
                ],
                examples=["calculator.py", "todo_list.py", "student_manager.py"],
                exercises=[],
                estimated_time=300
            )
        }
    
    def _create_learning_path(self) -> List[str]:
        """创建推荐的学习路径"""
        return [
            "01_basics",
            "02_control_flow", 
            "03_data_structures",
            "04_functions",
            "05_oop",
            "generators",
            "06_advanced",
            "07_projects"
        ]
    
    def get_learning_path(self) -> List[str]:
        """获取完整的学习路径
        
        Returns:
            List[str]: 按顺序排列的模块名称列表
        """
        return self._learning_path.copy()
    
    def get_module_description(self, module_name: str) -> str:
        """获取指定模块的详细描述
        
        Args:
            module_name (str): 模块名称
            
        Returns:
            str: 模块的详细描述
            
        Raises:
            KeyError: 当模块不存在时
        """
        if module_name not in self._modules:
            raise KeyError(f"模块 '{module_name}' 不存在")
        
        module = self._modules[module_name]
        description = f"""
模块名称: {module.name}
描述: {module.description}
预估学习时间: {module.estimated_time} 分钟

学习目标:
"""
        for i, objective in enumerate(module.learning_objectives, 1):
            description += f"{i}. {objective}\n"
        
        description += f"\n示例文件: {', '.join(module.examples)}"
        if module.exercises:
            description += f"\n练习文件: {', '.join(module.exercises)}"
        
        return description.strip()
    
    def get_prerequisites(self, module_name: str) -> List[str]:
        """获取指定模块的前置条件
        
        Args:
            module_name (str): 模块名称
            
        Returns:
            List[str]: 前置模块列表
            
        Raises:
            KeyError: 当模块不存在时
        """
        if module_name not in self._modules:
            raise KeyError(f"模块 '{module_name}' 不存在")
        
        return self._modules[module_name].prerequisites.copy()
    
    def suggest_next_step(self, current_module: str) -> str:
        """根据当前模块建议下一步学习内容
        
        Args:
            current_module (str): 当前学习的模块名称
            
        Returns:
            str: 下一步学习建议
        """
        if current_module not in self._modules:
            return "建议从 '01_basics' 开始学习Python基础语法"
        
        try:
            current_index = self._learning_path.index(current_module)
            if current_index < len(self._learning_path) - 1:
                next_module = self._learning_path[current_index + 1]
                next_module_info = self._modules[next_module]
                return f"建议继续学习: {next_module_info.name} ({next_module})"
            else:
                return "恭喜！您已完成所有基础学习模块，可以开始更深入的Python学习或实际项目开发"
        except ValueError:
            return "建议按照推荐的学习路径进行学习"
    
    def check_prerequisites(self, module_name: str, completed_modules: List[str]) -> tuple[bool, List[str]]:
        """检查是否满足学习指定模块的前置条件
        
        Args:
            module_name (str): 要学习的模块名称
            completed_modules (List[str]): 已完成的模块列表
            
        Returns:
            tuple[bool, List[str]]: (是否满足条件, 缺少的前置模块列表)
        """
        if module_name not in self._modules:
            return False, [f"模块 '{module_name}' 不存在"]
        
        prerequisites = self.get_prerequisites(module_name)
        missing = [prereq for prereq in prerequisites if prereq not in completed_modules]
        
        return len(missing) == 0, missing
    
    def get_learning_progress_summary(self, completed_modules: List[str]) -> str:
        """获取学习进度摘要
        
        Args:
            completed_modules (List[str]): 已完成的模块列表
            
        Returns:
            str: 学习进度摘要
        """
        total_modules = len(self._learning_path)
        completed_count = len([m for m in completed_modules if m in self._learning_path])
        progress_percentage = (completed_count / total_modules) * 100
        
        summary = f"""
学习进度摘要:
总模块数: {total_modules}
已完成: {completed_count}
完成率: {progress_percentage:.1f}%

已完成的模块:
"""
        for module in completed_modules:
            if module in self._modules:
                summary += f"✓ {self._modules[module].name} ({module})\n"
        
        # 建议下一步
        if completed_count < total_modules:
            for module in self._learning_path:
                if module not in completed_modules:
                    can_start, missing = self.check_prerequisites(module, completed_modules)
                    if can_start:
                        summary += f"\n建议下一步学习: {self._modules[module].name} ({module})"
                        break
                    else:
                        summary += f"\n需要先完成前置模块: {', '.join(missing)}"
                        break
        else:
            summary += "\n🎉 恭喜完成所有基础学习模块！"
        
        return summary.strip()
    
    def get_all_modules(self) -> Dict[str, str]:
        """获取所有模块的名称和描述
        
        Returns:
            Dict[str, str]: 模块ID到模块名称的映射
        """
        return {module_id: module.name for module_id, module in self._modules.items()}


def main():
    """演示学习指南的使用方法"""
    guide = LearningGuide()
    
    print("=== Python学习系统指南 ===\n")
    
    # 显示学习路径
    print("推荐学习路径:")
    for i, module in enumerate(guide.get_learning_path(), 1):
        module_info = guide._modules[module]
        print(f"{i}. {module_info.name} ({module}) - {module_info.estimated_time}分钟")
    
    print("\n" + "="*50 + "\n")
    
    # 显示第一个模块的详细信息
    first_module = guide.get_learning_path()[0]
    print("第一个模块详细信息:")
    print(guide.get_module_description(first_module))
    
    print("\n" + "="*50 + "\n")
    
    # 演示学习进度跟踪
    completed = ["01_basics", "02_control_flow"]
    print("学习进度示例:")
    print(guide.get_learning_progress_summary(completed))


if __name__ == "__main__":
    main()