"""
题目存储库
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from models import Question
from config import QUESTION_BANK_DIR


class QuestionRepository:
    """题目存储库"""

    def __init__(self):
        """初始化存储库"""
        self._cache: Dict[str, List[Question]] = {}
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        QUESTION_BANK_DIR.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_id: str, questions: List[Question]) -> None:
        """
        保存单个会话的题目

        Args:
            session_id: 会话ID
            questions: 题目列表
        """
        output_file = QUESTION_BANK_DIR / f"{session_id}.json"
        data = [q.to_dict() for q in questions]
        output_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        self._cache[session_id] = questions

    def load_session(self, session_id: str) -> List[Question]:
        """
        加载单个会话的题目

        Args:
            session_id: 会话ID

        Returns:
            题目列表
        """
        if session_id in self._cache:
            return self._cache[session_id]

        output_file = QUESTION_BANK_DIR / f"{session_id}.json"
        if not output_file.exists():
            return []

        data = json.loads(output_file.read_text(encoding="utf-8"))
        questions = [Question.from_dict(d) for d in data]
        self._cache[session_id] = questions
        return questions

    def load_all(self) -> Dict[str, List[Question]]:
        """加载所有会话的题目"""
        results = {}
        for session_file in QUESTION_BANK_DIR.glob("*.json"):
            session_id = session_file.stem
            results[session_id] = self.load_session(session_id)
        return results

    def get_wrong_questions(self, user_id: str = "default", for_practice: bool = True) -> List[Question]:
        """
        获取错题

        Args:
            user_id: 用户ID
            for_practice: 是否用于练习（True则排除已掌握但保留的题目）

        Returns:
            错题列表

        判断标准：
        - consecutive_correct = 0 表示最近一次答错，需要进错题本
        - accuracy < 0.6 表示正确率太低，需要进错题本
        - 第一次就做对的题目不进错题本
        """
        wrong_questions = []

        for questions in self.load_all().values():
            for q in questions:
                # 判断是否为错题：最近一次答错 或 正确率低于60%
                if q.times_presented > 0:
                    accuracy = q.times_correct / q.times_presented

                    # 只有错过（consecutive_correct=0）或正确率低才是错题
                    should_include = (q.consecutive_correct == 0 or accuracy < 0.6)

                    # 如果是用于练习，排除已掌握但保留的题目
                    if for_practice and q.mastered_but_keep:
                        should_include = False

                    if should_include:
                        wrong_questions.append(q)

        # 按错误率排序（已掌握的排在后面）
        wrong_questions.sort(
            key=lambda q: (q.mastered_but_keep, 1 - q.times_correct / max(q.times_presented, 1))
        )

        return wrong_questions

    def update_question(self, question: Question) -> None:
        """
        更新题目

        Args:
            question: 题目对象
        """
        # 加载所属会话的题目
        questions = self.load_session(question.session_id)

        # 查找并更新
        for i, q in enumerate(questions):
            if q.id == question.id:
                questions[i] = question
                break

        # 保存
        self.save_session(question.session_id, questions)

    def get_due_questions(self, limit: Optional[int] = None) -> List[Question]:
        """
        获取需要复习的题目

        Args:
            limit: 最大返回数量

        Returns:
            需要复习的题目列表
        """
        now = datetime.now()
        due_questions = []

        for questions in self.load_all().values():
            for q in questions:
                if q.next_review_date and q.next_review_date <= now:
                    due_questions.append(q)

        # 按到期时间排序
        due_questions.sort(key=lambda q: q.next_review_date or now)

        if limit:
            due_questions = due_questions[:limit]

        return due_questions

    def get_statistics(self) -> Dict:
        """获取题目统计"""
        all_questions = []
        for questions in self.load_all().values():
            all_questions.extend(questions)

        total = len(all_questions)
        if total == 0:
            return {
                "total_questions": 0,
                "total_correct": 0,
                "accuracy_rate": 0,
                "due_questions": 0,
                "wrong_questions": 0,
            }

        total_correct = sum(q.times_correct for q in all_questions)
        total_presented = sum(q.times_presented for q in all_questions)

        now = datetime.now()
        due_count = sum(1 for q in all_questions if q.next_review_date and q.next_review_date <= now)

        wrong_count = len(self.get_wrong_questions())

        return {
            "total_questions": total,
            "total_correct": total_correct,
            "total_presented": total_presented,
            "accuracy_rate": total_correct / total_presented if total_presented > 0 else 0,
            "due_questions": due_count,
            "wrong_questions": wrong_count,
        }
