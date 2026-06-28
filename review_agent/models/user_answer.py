"""
用户答题记录模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class UserAnswer:
    """用户答题记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str = ""
    user_id: str = "default"  # 用户标识

    # 答题内容
    answer_text: str = ""
    time_spent_seconds: int = 0  # 答题用时
    timestamp: datetime = field(default_factory=datetime.now)

    # 评估结果
    is_correct: bool = False
    score: float = 0.0  # 0.0-1.0
    feedback: str = ""
    quality_rating: Optional[int] = None  # 用户自评 0-5

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "user_id": self.user_id,
            "answer_text": self.answer_text,
            "time_spent_seconds": self.time_spent_seconds,
            "timestamp": self.timestamp.isoformat(),
            "is_correct": self.is_correct,
            "score": self.score,
            "feedback": self.feedback,
            "quality_rating": self.quality_rating,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserAnswer":
        """从字典创建"""
        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
