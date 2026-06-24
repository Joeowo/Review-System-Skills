"""
知识点数据模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid


class KnowledgeType(Enum):
    """知识点类型"""
    CONCEPT = "概念"
    FORMULA = "公式"
    CLASSIFICATION = "分类"
    PROCESS = "流程"
    RELATIONSHIP = "关系"


@dataclass
class KnowledgePoint:
    """知识点模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_file: str = ""  # 来源文件路径
    session_id: str = ""  # 所属会话ID

    # 知识点内容
    type: KnowledgeType = KnowledgeType.CONCEPT
    category: str = ""  # 大类（如"经济学"）
    subcategory: str = ""  # 子类（如"微观经济学"）
    title: str = ""  # 知识点标题
    content: str = ""  # 详细内容

    # 元数据
    keywords: List[str] = field(default_factory=list)
    related_points: List[str] = field(default_factory=list)  # 关联知识点ID
    difficulty: float = 0.5  # 难度 0.0-1.0

    # 提取信息
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    is_computational: bool = False  # 是否是计算题
    has_chart: bool = False  # 是否包含图表

    # 术语表信息（如果来自CONTEXT.md）
    is_term: bool = False
    term_definition: str = ""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "source_file": self.source_file,
            "session_id": self.session_id,
            "type": self.type.value,
            "category": self.category,
            "subcategory": self.subcategory,
            "title": self.title,
            "content": self.content,
            "keywords": self.keywords,
            "related_points": self.related_points,
            "difficulty": self.difficulty,
            "extraction_timestamp": self.extraction_timestamp.isoformat(),
            "is_computational": self.is_computational,
            "has_chart": self.has_chart,
            "is_term": self.is_term,
            "term_definition": self.term_definition,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgePoint":
        """从字典创建"""
        data = data.copy()
        if "type" in data and isinstance(data["type"], str):
            data["type"] = KnowledgeType(data["type"])
        if "extraction_timestamp" in data and isinstance(data["extraction_timestamp"], str):
            data["extraction_timestamp"] = datetime.fromisoformat(data["extraction_timestamp"])
        return cls(**data)
