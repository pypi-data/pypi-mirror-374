"""
Python学习系统命令行入口

使用方法:
    python -m src.kylearn hello          # 显示欢迎信息
    python -m src.kylearn path           # 显示学习路径
    python -m src.kylearn module 01_basics  # 显示模块详情
    python -m src.kylearn progress 01_basics 02_control_flow  # 显示学习进度
    python -m src.kylearn next_step 01_basics  # 获取下一步建议
"""

from . import main

if __name__ == "__main__":
    main()