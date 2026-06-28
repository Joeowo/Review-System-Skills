"""
学习进度统计模型
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List
import uuid


@dataclass
class SessionStats:
    """会话统计数据"""
    session_id: str = ""
    total_questions: int = 0
    correct_count: int = 0
    total_time_seconds: int = 0
    last_review_date: datetime = field(default_factory=datetime.now)
    knowledge_coverage: Dict[str, int] = field(default_factory=dict)  # 类别 -> 已复习数量

    @property
    def accuracy_rate(self) -> float:
        """正确率"""
        if self.total_questions == 0:
            return 0.0
        return self.correct_count / self.total_questions


@dataclass
class Progress:
    """用户学习进度"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"

    # 统计数据
    total_answers: int = 0
    correct_answers: int = 0
    total_study_time: int = 0  # 总学习时间（秒）
    streak_days: int = 0  # 连续学习天数
    last_study_date: datetime = field(default_factory=datetime.now)

    # 会话统计
    session_stats: Dict[str, SessionStats] = field(default_factory=dict)

    # 弱项分析
    weak_areas: Dict[str, int] = field(default_factory=dict)  # 类别 -> 错误次数

    @property
    def accuracy_rate(self) -> float:
        """总体正确率"""
        if self.total_answers == 0:
            return 0.0
        return self.correct_answers / self.total_answers

    def add_answer(self, is_correct: bool, category: str, time_seconds: int) -> None:
        """添加答题记录"""
        self.total_answers += 1
        self.total_study_time += time_seconds
        if is_correct:
            self.correct_answers += 1
        else:
            self.weak_areas[category] = self.weak_areas.get(category, 0) + 1

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total_answers": self.total_answers,
            "correct_answers": self.correct_answers,
            "total_study_time": self.total_study_time,
            "streak_days": self.streak_days,
            "last_study_date": self.last_study_date.isoformat(),
            "session_stats": {
                k: {
                    "session_id": v.session_id,
                    "total_questions": v.total_questions,
                    "correct_count": v.correct_count,
                    "total_time_seconds": v.total_time_seconds,
                    "last_review_date": v.last_review_date.isoformat(),
                    "knowledge_coverage": v.knowledge_coverage,
                }
                for k, v in self.session_stats.items()
            },
            "weak_areas": self.weak_areas,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Progress":
        """从字典创建"""
        data = data.copy()
        if "last_study_date" in data and isinstance(data["last_study_date"], str):
            data["last_study_date"] = datetime.fromisoformat(data["last_study_date"])
        if "session_stats" in data:
            session_stats = {}
            for k, v in data["session_stats"].items():
                v["last_review_date"] = datetime.fromisoformat(v["last_review_date"])
                session_stats[k] = SessionStats(**v)
            data["session_stats"] = session_stats
        return cls(**data)
