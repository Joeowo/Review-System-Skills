"""
SuperMemo-2 间隔重复调度算法
实现SM-2算法的核心逻辑
"""
import random
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass

from models import Question
from config import SM2_INITIAL_EF, SM2_INITIAL_INTERVAL, SM2_MINIMUM_EF, QUESTIONS_PER_ROUND


@dataclass
class SM2Config:
    """SM-2算法配置"""
    initial_ease_factor: float = SM2_INITIAL_EF  # 初始易记因子
    initial_interval: int = SM2_INITIAL_INTERVAL  # 初始间隔（天）
    minimum_ease_factor: float = SM2_MINIMUM_EF  # 最小易记因子
    questions_per_round: int = QUESTIONS_PER_ROUND  # 每轮题目数


class SM2Scheduler:
    """
    SuperMemo-2 调度器

    SM-2 算法简介：
    - EF (Ease Factor): 易记因子，表示记忆难易程度
    - I (Interval): 复习间隔（天）
    - q (Quality): 用户评分 0-5
      - 5: 完美记忆，毫不费力
      - 4: 正确回答，稍有犹豫
      - 3: 正确回答，但很困难
      - 2: 错误，但感觉容易
      - 1: 错误，且困难
      - 0: 完全忘记

    核心公式：
    - EF' = EF + (0.1 - (3-q) * (0.08 + (3-q) * 0.02))
    - I(n) = 1 (第1次复习)
    - I(n) = 6 (第2次复习)
    - I(n) = I(n-1) * EF (第3次及以后，当q>=3时)
    """

    def __init__(self, config: Optional[SM2Config] = None):
        """
        初始化调度器

        Args:
            config: SM-2配置
        """
        self.config = config or SM2Config()

    def calculate_next_review(
        self,
        current_ef: float,
        current_interval: int,
        repetition: int,
        quality: int
    ) -> tuple[float, int, int, datetime]:
        """
        计算下次复习时间

        Args:
            current_ef: 当前易记因子
            current_interval: 当前间隔
            repetition: 当前复习次数
            quality: 用户评分 (0-5)

        Returns:
            (new_ease_factor, new_interval, new_repetition, next_review_date)
        """
        new_repetition = repetition + 1
        next_review_date = datetime.now()

        if quality >= 3:
            # 答对了
            if new_repetition == 1:
                new_interval = 1
            elif new_repetition == 2:
                new_interval = 6
            else:
                new_interval = int(current_interval * current_ef)

            # 更新易记因子
            # EF' = EF + (0.1 - (3-q) * (0.08 + (3-q) * 0.02))
            new_ef = current_ef + (0.1 - (3 - quality) * (0.08 + (3 - quality) * 0.02))
            new_ef = max(new_ef, self.config.minimum_ease_factor)

            next_review_date = datetime.now() + timedelta(days=new_interval)

        else:
            # 答错了，重置
            new_interval = 1
            new_repetition = 0
            new_ef = current_ef  # 易记因子不重置
            next_review_date = datetime.now() + timedelta(days=new_interval)

        return new_ef, new_interval, new_repetition, next_review_date

    def update_question(self, question: Question, quality: int) -> Question:
        """
        更新题目的SM-2参数

        Args:
            question: 题目对象
            quality: 用户评分 (0-5)

        Returns:
            更新后的题目对象
        """
        ef, interval, rep, next_date = self.calculate_next_review(
            question.ease_factor,
            question.interval,
            question.repetition,
            quality
        )

        question.ease_factor = ef
        question.interval = interval
        question.repetition = rep
        question.next_review_date = next_date
        question.last_review_date = datetime.now()
        question.last_quality = quality

        return question

    def _shuffle_by_priority(
        self,
        questions: List[Question],
        key,
        group_size: int = 10
    ) -> List[Question]:
        """
        按优先级分组后随机打乱

        在保持整体优先级顺序的同时，在每组内部随机打乱。
        这样既有秩序感，又不会每次都出相同的题目顺序。

        Args:
            questions: 题目列表
            key: 分组键函数
            group_size: 每组大小

        Returns:
            打乱后的题目列表
        """
        if not questions:
            return questions

        # 按优先级排序
        sorted_questions = sorted(questions, key=key)

        # 分组并随机打乱
        result = []
        for i in range(0, len(sorted_questions), group_size):
            group = sorted_questions[i:i + group_size]
            random.shuffle(group)
            result.extend(group)

        return result

    def get_due_questions(
        self,
        questions: List[Question],
        limit: Optional[int] = None,
        shuffle: bool = True
    ) -> List[Question]:
        """
        获取需要复习的题目

        选择策略：
        1. 优先选择到期的题目（next_review_date <= now）
        2. 按优先级分组后随机打乱（间隔越短优先级越高）
        3. 限制数量

        Args:
            questions: 所有题目列表
            limit: 最大返回数量
            shuffle: 是否打乱顺序（引入随机性）

        Returns:
            需要复习的题目列表
        """
        now = datetime.now()

        # 筛选到期的题目
        due_questions = [q for q in questions if q.next_review_date <= now]

        if shuffle:
            # 分组随机：按间隔分组，组内随机
            due_questions = self._shuffle_by_priority(due_questions, key=lambda q: q.interval)
        else:
            # 按间隔和难度排序
            due_questions.sort(key=lambda q: (
                q.interval,  # 间隔越短越优先
                q.difficulty  # 难度越低越优先
            ))

        if limit:
            due_questions = due_questions[:limit]

        return due_questions

    def get_new_questions(
        self,
        questions: List[Question],
        limit: Optional[int] = None,
        shuffle: bool = True
    ) -> List[Question]:
        """
        获取新题目（从未复习过的）

        Args:
            questions: 所有题目列表
            limit: 最大返回数量
            shuffle: 是否打乱顺序（引入随机性）

        Returns:
            新题目列表
        """
        new_questions = [q for q in questions if q.repetition == 0 and q.times_presented == 0]

        if shuffle:
            # 分组随机：按难度分组，组内随机
            new_questions = self._shuffle_by_priority(new_questions, key=lambda q: q.difficulty)
        else:
            # 按难度排序，先从简单的开始
            new_questions.sort(key=lambda q: q.difficulty)

        if limit:
            new_questions = new_questions[:limit]

        return new_questions

    def get_mixed_questions(
        self,
        questions: List[Question],
        limit: Optional[int] = None,
        new_ratio: float = 0.3,
        shuffle: bool = True
    ) -> List[Question]:
        """
        获取混合题目（新题 + 复习题）

        Args:
            questions: 所有题目列表
            limit: 最大返回数量
            new_ratio: 新题比例 (0.0-1.0)
            shuffle: 是否打乱顺序（引入随机性）

        Returns:
            混合题目列表
        """
        limit = limit or self.config.questions_per_round
        new_count = int(limit * new_ratio)
        review_count = limit - new_count

        # 获取新题
        new_questions = self.get_new_questions(questions, limit=new_count, shuffle=shuffle)

        # 获取复习题
        review_questions = self.get_due_questions(
            [q for q in questions if q not in new_questions],
            limit=review_count,
            shuffle=shuffle
        )

        # 合并
        mixed = new_questions + review_questions

        if not shuffle:
            # 不打乱时，新题优先
            mixed.sort(key=lambda q: (
                0 if q.repetition == 0 else 1,  # 新题优先
                q.next_review_date if q.next_review_date else datetime.now()
            ))
        else:
            # 打乱新题和复习题的混合顺序
            random.shuffle(mixed)

        return mixed[:limit]

    def quality_to_score(self, quality: int) -> float:
        """
        将质量评分转换为分数

        Args:
            quality: 质量评分 (0-5)

        Returns:
            分数 (0.0-1.0)
        """
        if quality >= 5:
            return 1.0
        elif quality >= 4:
            return 0.9
        elif quality >= 3:
            return 0.7
        elif quality >= 2:
            return 0.4
        elif quality >= 1:
            return 0.2
        else:
            return 0.0

    def get_statistics(self, questions: List[Question]) -> dict:
        """
        获取题目统计信息

        Args:
            questions: 题目列表

        Returns:
            统计信息字典
        """
        now = datetime.now()
        total = len(questions)
        due = len([q for q in questions if q.next_review_date <= now])
        new = len([q for q in questions if q.repetition == 0])

        # 计算平均易记因子
        avg_ef = sum(q.ease_factor for q in questions) / total if total > 0 else 0

        # 计算正确率
        correct_count = sum(q.times_correct for q in questions)
        total_attempts = sum(q.times_presented for q in questions)
        accuracy = correct_count / total_attempts if total_attempts > 0 else 0

        return {
            "total_questions": total,
            "due_questions": due,
            "new_questions": new,
            "average_ease_factor": round(avg_ef, 2),
            "accuracy_rate": round(accuracy * 100, 1),
        }


# 测试代码
if __name__ == "__main__":
    from models import Question, QuestionType

    # 创建测试题目
    test_questions = [
        Question(
            id="q1",
            content="什么是机会成本？",
            correct_answer="资源用于某一用途后放弃的最大收益",
            type=QuestionType.DEFINITION,
            ease_factor=2.5,
            interval=1,
            repetition=0,
        ),
        Question(
            id="q2",
            content="什么是需求定律？",
            correct_answer="价格上升，需求量下降",
            type=QuestionType.DEFINITION,
            ease_factor=2.5,
            interval=1,
            repetition=0,
        ),
    ]

    # 测试调度器
    scheduler = SM2Scheduler()

    # 获取新题
    new_questions = scheduler.get_new_questions(test_questions)
    print(f"新题数量: {len(new_questions)}")

    # 更新题目（假设用户评分为4）
    if new_questions:
        updated = scheduler.update_question(new_questions[0], quality=4)
        print(f"更新后间隔: {updated.interval} 天")
        print(f"更新后易记因子: {updated.ease_factor}")

    # 获取统计
    stats = scheduler.get_statistics(test_questions)
    print(f"统计信息: {stats}")
