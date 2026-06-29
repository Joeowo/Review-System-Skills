"""
S1-T1: SkillMetadata 数据模型

定义技能的元数据结构，从 SKILL.md 的 frontmatter 解析得到。
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SkillMetadata:
    """技能元数据

    从 SKILL.md 的 YAML frontmatter 解析得到的技能信息。
    使用 frozen=True 确保不可变性，避免意外修改。

    Attributes:
        name: 技能名称，对应 SKILL.md 的 name 字段
        description: 技能描述，对应 SKILL.md 的 description 字段
        path: SKILL.md 文件的完整路径
        version: 技能版本，默认 "1.0"
        category: 技能分类，默认 "general"
        tags: 技能标签列表，默认为空列表
    """

    name: str
    description: str
    path: Path
    version: str = "1.0"
    category: str = "general"
    tags: list[str] = field(default_factory=list)
