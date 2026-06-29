"""
S1-T1: SkillContext 数据模型

定义技能执行的上下文结构。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any


@dataclass(frozen=True)
class SkillContext:
    """技能执行上下文

    包含技能执行所需的所有上下文信息。

    Attributes:
        session_path: 会话目录路径，指向 CONTEXT.md 和 Task.md 所在目录
        state: 执行状态字典，包含当前执行的运行时数据
    """

    session_path: Path
    state: Dict[str, Any] = field(default_factory=dict)
