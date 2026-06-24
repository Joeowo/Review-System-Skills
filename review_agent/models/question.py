"""
题目数据模型
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
import uuid


class QuestionType(Enum):
    """题目类型"""
    DEFINITION = "定义题"
    FORMULA = "公式题"
    CLASSIFICATION = "分类题"
    RELATIONSHIP = "关系题"
    APPLICATION = "应用题"


@dataclass
class AnswerEvaluation:
    """答案评估结果"""
    is_correct: bool
    score: float  # 0.0-1.0
    feedback: str = ""
    missing_points: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    evaluation_time: datetime = field(default_factory=datetime.now)


@dataclass
class Question:
    """题目模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    knowledge_point_id: str = ""  # 关联的知识点ID
    session_id: str = ""  # 来源会话

    # 题目内容
    type: QuestionType = QuestionType.DEFINITION
    content: str = ""  # 题目文本
    correct_answer: str = ""  # 正确答案
    explanation: str = ""  # 详细解析

    # 元数据
    difficulty: float = 0.5  # 0.0-1.0
    tags: List[str] = field(default_factory=list)  # 分类标签
    source: str = ""  # 题目来源（文件名）
    source_priority: int = 0  # 来源优先级：2=历年试题, 1=复习资料, 0=自动生成
    created_at: datetime = field(default_factory=datetime.now)

    # SuperMemo-2 算法字段
    ease_factor: float = 2.5  # 易记因子 EF
    interval: int = 1  # 复习间隔（天）
    repetition: int = 0  # 复习次数
    next_review_date: datetime = field(default_factory=datetime.now)
    last_review_date: Optional[datetime] = None
    last_quality: Optional[int] = None  # 上次评分 0-5

    # 统计
    times_presented: int = 0  # 出现次数
    times_correct: int = 0  # 正确次数
    consecutive_correct: int = 0  # 连续正确次数（用于错题本）
    mastered_but_keep: bool = False  # 是否已掌握但保留在错题本（连续答对2次后设为true）

    def is_due(self) -> bool:
        """是否需要复习"""
        return datetime.now() >= self.next_review_date

    def update_sm2(self, quality: int) -> None:
        """
        根据SuperMemo-2算法更新参数

        Args:
            quality: 用户评分 0-5
                5: 完美记忆
                4: 正确但有犹豫
                3: 困难但正确
                2: 错误但感觉容易
                1: 错误且困难
                0: 完全忘记
        """
        self.last_quality = quality
        self.repetition += 1
        self.last_review_date = datetime.now()
        self.times_presented += 1

        if quality >= 3:
            # 答对了，更新间隔
            if self.repetition == 1:
                self.interval = 1
            elif self.repetition == 2:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)

            # 更新易记因子
            # EF' = EF + (0.1 - (3-q) * (0.08 + (3-q) * 0.02))
            self.ease_factor = max(
                1.3,
                self.ease_factor + (0.1 - (3 - quality) * (0.08 + (3 - quality) * 0.02))
            )
        else:
            # 答错了，重置
            self.repetition = 0
            self.interval = 1
            # 易记因子不重置

        # 计算下次复习日期
        self.next_review_date = datetime.now() + timedelta(days=self.interval)

        # 更新正确统计
        if quality >= 3:
            self.times_correct += 1
            self.consecutive_correct += 1
        else:
            self.consecutive_correct = 0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "knowledge_point_id": self.knowledge_point_id,
            "session_id": self.session_id,
            "type": self.type.value,
            "content": self.content,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "source": self.source,
            "source_priority": self.source_priority,
            "created_at": self.created_at.isoformat(),
            "ease_factor": self.ease_factor,
            "interval": self.interval,
            "repetition": self.repetition,
            "next_review_date": self.next_review_date.isoformat(),
            "last_review_date": self.last_review_date.isoformat() if self.last_review_date else None,
            "last_quality": self.last_quality,
            "times_presented": self.times_presented,
            "times_correct": self.times_correct,
            "consecutive_correct": self.consecutive_correct,
            "mastered_but_keep": self.mastered_but_keep,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """从字典创建"""
        data = data.copy()
        if "type" in data and isinstance(data["type"], str):
            data["type"] = QuestionType(data["type"])
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "next_review_date" in data and isinstance(data["next_review_date"], str):
            data["next_review_date"] = datetime.fromisoformat(data["next_review_date"])
        if "last_review_date" in data and data["last_review_date"]:
            if isinstance(data["last_review_date"], str):
                data["last_review_date"] = datetime.fromisoformat(data["last_review_date"])
        return cls(**data)
