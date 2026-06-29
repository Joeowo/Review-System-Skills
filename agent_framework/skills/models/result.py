"""
S1-T1: SkillResult 数据模型

定义技能执行的结果结构。
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class SkillResult:
    """技能执行结果

    包含技能执行后的返回信息。

    Attributes:
        success: 执行是否成功
        output: 执行成功时的输出内容
        error: 执行失败时的错误信息
        metadata: 额外的元数据信息，如轮次、掌握程度等
    """

    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
