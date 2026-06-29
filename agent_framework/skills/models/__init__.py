"""
S1-T1: 技能系统数据模型

定义技能系统的核心数据结构：
- SkillMetadata: 技能元数据
- SkillContext: 技能执行上下文
- SkillResult: 技能执行结果
"""

from agent_framework.skills.models.metadata import SkillMetadata
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult

__all__ = [
    "SkillMetadata",
    "SkillContext",
    "SkillResult",
]
