"""
答案评估模块
使用AI评估用户答案
支持异步并行评估
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

from models import Question, UserAnswer, AnswerEvaluation
from services.llm_service import SyncDeepSeekService, AsyncDeepSeekService
from utils.task_manager import get_global_manager


class AnswerEvaluator:
    """答案评估器"""

    def __init__(self, llm_service: SyncDeepSeekService = None):
        """
        初始化评估器

        Args:
            llm_service: LLM服务实例
        """
        self.llm_service = llm_service or SyncDeepSeekService()
        self.async_service: Optional[AsyncDeepSeekService] = None
        self.task_manager = get_global_manager()

    def _get_async_service(self) -> AsyncDeepSeekService:
        """获取或创建异步服务"""
        if self.async_service is None:
            self.async_service = AsyncDeepSeekService()
        return self.async_service

    def evaluate(
        self,
        question: Question,
        user_answer: str
    ) -> AnswerEvaluation:
        """
        评估单个答案

        Args:
            question: 题目对象
            user_answer: 用户答案

        Returns:
            评估结果
        """
        result = self.llm_service.evaluate_answer(
            question=question.content,
            user_answer=user_answer,
            correct_answer=question.correct_answer
        )

        return AnswerEvaluation(
            is_correct=result.get("is_correct", False),
            score=result.get("score", 0.0),
            feedback=result.get("feedback", ""),
            missing_points=result.get("missing_points", []),
            strengths=result.get("strengths", []),
        )

    def evaluate_batch(
        self,
        questions: List[Question],
        user_answers: List[str]
    ) -> List[AnswerEvaluation]:
        """
        批量评估答案（异步并行处理）

        Args:
            questions: 题目列表
            user_answers: 用户答案列表

        Returns:
            评估结果列表
        """
        if len(questions) != len(user_answers):
            raise ValueError("题目和答案数量不匹配")

        # 使用异步服务进行并发评估
        async_service = self._get_async_service()

        questions_str = [q.content for q in questions]
        correct_answers = [q.correct_answer for q in questions]

        # 在新的事件循环中运行异步评估
        import threading
        result_holder = {"results": None, "exception": None}

        def run_in_new_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                async def evaluate():
                    results = await async_service.evaluate_answers_batch(
                        questions_str,
                        user_answers,
                        correct_answers
                    )
                    # 转换为AnswerEvaluation对象
                    evaluations = []
                    for i, result in enumerate(results):
                        evaluations.append(AnswerEvaluation(
                            is_correct=result.get("is_correct", False),
                            score=result.get("score", 0.0),
                            feedback=result.get("feedback", ""),
                            missing_points=result.get("missing_points", []),
                            strengths=result.get("strengths", []),
                        ))
                    return evaluations

                result = loop.run_until_complete(evaluate())
                result_holder["results"] = result
                loop.close()
            except Exception as e:
                result_holder["exception"] = e

        # 在新线程中运行
        thread = threading.Thread(target=run_in_new_loop)
        thread.start()
        thread.join()

        # 检查是否有异常
        if result_holder["exception"] is not None:
            raise result_holder["exception"]

        return result_holder["results"]

    async def evaluate_batch_async(
        self,
        questions: List[Question],
        user_answers: List[str]
    ) -> List[AnswerEvaluation]:
        """
        批量评估答案（异步并行）

        Args:
            questions: 题目列表
            user_answers: 用户答案列表

        Returns:
            评估结果列表
        """
        if len(questions) != len(user_answers):
            raise ValueError("题目和答案数量不匹配")

        # 使用异步服务进行并发评估
        async_service = self._get_async_service()

        questions_str = [q.content for q in questions]
        correct_answers = [q.correct_answer for q in questions]

        results = await async_service.evaluate_answers_batch(
            questions_str,
            user_answers,
            correct_answers
        )

        # 转换为AnswerEvaluation对象
        evaluations = []
        for i, result in enumerate(results):
            evaluations.append(AnswerEvaluation(
                is_correct=result.get("is_correct", False),
                score=result.get("score", 0.0),
                feedback=result.get("feedback", ""),
                missing_points=result.get("missing_points", []),
                strengths=result.get("strengths", []),
            ))

        return evaluations

    def submit_evaluation_task(
        self,
        questions: List[Question],
        user_answers: List[str]
    ) -> str:
        """
        提交后台评估任务

        Args:
            questions: 题目列表
            user_answers: 用户答案列表

        Returns:
            任务ID
        """
        if len(questions) != len(user_answers):
            raise ValueError("题目和答案数量不匹配")

        # 创建异步评估协程
        async def evaluate_task():
            return await self.evaluate_batch_async(questions, user_answers)

        # 在新的事件循环中执行任务
        import threading

        result_holder = {"task_id": None}
        exception_holder = {"exception": None}

        def run_in_new_loop():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                task_id = loop.run_until_complete(
                    self.task_manager.submit_task(
                        evaluate_task(),
                        total_steps=len(questions)
                    )
                )
                result_holder["task_id"] = task_id
                loop.close()
            except Exception as e:
                exception_holder["exception"] = e

        # 在新线程中运行
        thread = threading.Thread(target=run_in_new_loop)
        thread.daemon = True
        thread.start()

        # 等待任务ID生成
        while result_holder["task_id"] is None and exception_holder["exception"] is None:
            import time
            time.sleep(0.01)

        if exception_holder["exception"] is not None:
            raise exception_holder["exception"]

        return result_holder["task_id"]

    async def get_task_result_async(self, task_id: str, timeout: Optional[float] = None) -> List[AnswerEvaluation]:
        """
        获取任务结果（异步）

        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）

        Returns:
            评估结果列表
        """
        return await self.task_manager.get_task_result(task_id, timeout)

    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> List[AnswerEvaluation]:
        """
        获取任务结果（同步）

        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）

        Returns:
            评估结果列表
        """
        return asyncio.run(self.get_task_result_async(task_id, timeout))

    def get_task_progress(self, task_id: str) -> Optional[float]:
        """获取任务进度"""
        return self.task_manager.get_task_progress(task_id)

    def is_task_complete(self, task_id: str) -> bool:
        """检查任务是否完成"""
        from utils.task_manager import TaskStatus
        status = self.task_manager.get_task_status(task_id)
        return status == TaskStatus.COMPLETED if status else False

    def generate_feedback(self, evaluation: AnswerEvaluation, question: Question) -> str:
        """
        生成详细的反馈文本

        Args:
            evaluation: 评估结果
            question: 题目对象

        Returns:
            反馈文本
        """
        lines = []

        # 判断结果
        if evaluation.is_correct:
            lines.append(f"✅ 回答正确 (得分: {evaluation.score:.1%})")
        else:
            lines.append(f"❌ 回答有误 (得分: {evaluation.score:.1%})")

        # 优点
        if evaluation.strengths:
            lines.append("\n👍 回答亮点:")
            for strength in evaluation.strengths:
                lines.append(f"  - {strength}")

        # 缺失点
        if evaluation.missing_points:
            lines.append("\n📝 遗漏要点:")
            for point in evaluation.missing_points:
                lines.append(f"  - {point}")

        # AI反馈
        if evaluation.feedback:
            lines.append(f"\n💡 详细反馈:\n{evaluation.feedback}")

        # 正确答案
        lines.append(f"\n📖 参考答案:\n{question.correct_answer}")

        return "\n".join(lines)

    def get_quality_rating(self, evaluation: AnswerEvaluation, user_confidence: int) -> int:
        """
        根据评估结果和用户自信度获取SM-2质量评分

        Args:
            evaluation: 评估结果
            user_confidence: 用户自信度 (1-5)

        Returns:
            质量评分 (0-5)
        """
        if evaluation.is_correct:
            if user_confidence >= 4:
                return 5  # 完美
            elif user_confidence >= 3:
                return 4  # 正确但有犹豫
            else:
                return 3  # 困难但正确
        else:
            if user_confidence >= 3:
                return 2  # 错误但感觉容易
            elif user_confidence >= 2:
                return 1  # 错误且困难
            else:
                return 0  # 完全忘记


# 测试代码
if __name__ == "__main__":
    from models import Question, QuestionType
    from dotenv import load_dotenv
    import os

    load_dotenv()

    # 创建测试题目
    test_question = Question(
        id="test_q1",
        content="什么是机会成本？",
        correct_answer="机会成本是指资源用于某一用途后放弃的其他用途所能获得的最大收益。",
        type=QuestionType.DEFINITION,
        explanation="机会成本是经济学中的核心概念",
    )

    # 创建评估器
    evaluator = AnswerEvaluator()

    # 测试评估
    user_answer = "机会成本是指选择一个选项后放弃的其他选项的最大收益。"
    evaluation = evaluator.evaluate(test_question, user_answer)

    print("评估结果:")
    print(f"正确: {evaluation.is_correct}")
    print(f"得分: {evaluation.score:.2f}")
    print(f"反馈: {evaluation.feedback}")

    # 测试反馈生成
    feedback = evaluator.generate_feedback(evaluation, test_question)
    print("\n详细反馈:")
    print(feedback)
