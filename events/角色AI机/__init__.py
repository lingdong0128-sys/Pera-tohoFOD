"""
角色AI机模块
实现Pera幻想FOD中的角色AI决策系统

功能：
- 花销计算系统
- 角色行为决策
- 时间同步行动
"""

from . import ai_core
from . import cost_calculator

__all__ = ['ai_core', 'cost_calculator']
