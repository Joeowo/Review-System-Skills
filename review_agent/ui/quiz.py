"""
刷题界面
实现终端刷题交互
"""
import time
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.syntax import Syntax
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text

from models import Question, UserAnswer, AnswerEvaluation
from core.sm2_scheduler import SM2Scheduler
from core.answer_evaluator import AnswerEvaluator
from config import QUESTIONS_PER_ROUND


class QuizInterface:
    """刷题界面"""

    def __init__(self, evaluator: AnswerEvaluator, scheduler: SM2Scheduler):
        """
        初始化界面

        Args:
            evaluator: 答案评估器
            scheduler: SM-2调度器
        """
        self.console = Console()
        self.evaluator = evaluator
        self.scheduler = scheduler
        self.current_round: List[Question] = []
        self.user_answers: List[tuple[Question, str]] = []
        self.start_time: Optional[datetime] = None

    def start_round(self, questions: List[Question], round_num: int = 1) -> List[UserAnswer]:
        """
        开始一轮刷题

        Args:
            questions: 题目列表
            round_num: 轮次编号

        Returns:
            用户答题记录列表
        """
        self.current_round = questions[:QUESTIONS_PER_ROUND]
        self.user_answers = []
        self.start_time = datetime.now()
        self.round_num = round_num
        self._should_continue = False  # 是否继续下一轮

        # 显示欢迎信息
        self._show_round_intro()

        # 逐题作答
        for idx, question in enumerate(self.current_round, 1):
            self._show_question(idx, question)
            answer = self._get_user_answer()
            self.user_answers.append((question, answer))

        # 显示结果
        return self._show_results()

    def _show_round_intro(self):
        """显示轮次介绍"""
        self.console.clear()
        self.console.print()

        intro = f"""
[bold cyan]═══════════════════════════════════════════════════════
  📝 开始刷题 - 第 {self.round_num} 轮 ({len(self.current_round)} 题)
═══════════════════════════════════════════════════════[/bold cyan]

[dim]答题提示:[/dim]
• 输入你的答案后按 Enter 提交
• 按 Ctrl+C 可随时退出
• 答题结束后会显示答案对比和AI评估

        """

        self.console.print(intro)
        time.sleep(0.5)

    def _show_question(self, index: int, question: Question):
        """显示单个题目"""
        self.console.clear()
        self.console.print()

        # 题目信息
        question_type = question.type.value
        difficulty = self._get_difficulty_label(question.difficulty)

        self.console.print(f"[bold]第 {index}/{len(self.current_round)} 题[/bold]")
        self.console.print(f"[dim]类型: {question_type} | 难度: {difficulty}[/dim]")

        # 复习信息（如果不是新题）
        if question.repetition > 0:
            days_since = (datetime.now() - question.last_review_date).days if question.last_review_date else 0
            self.console.print(f"[dim]上次复习: {days_since}天前 | 复习次数: {question.repetition}[/dim]")

        self.console.print()
        self.console.print(Panel(
            question.content,
            title="[bold yellow]题目[/bold yellow]",
            border_style="yellow",
            padding=(0, 1)
        ))

    def _get_difficulty_label(self, difficulty: float) -> str:
        """获取难度标签"""
        if difficulty < 0.3:
            return "[green]简单[/green]"
        elif difficulty < 0.7:
            return "[yellow]中等[/yellow]"
        else:
            return "[red]困难[/red]"

    def _get_user_answer(self) -> str:
        """获取用户答案"""
        self.console.print()

        answer = Prompt.ask(
            "[bold cyan]你的答案[/bold cyan]",
            console=self.console,
            show_default=False
        )

        return answer.strip()

    def _show_results(self) -> List[UserAnswer]:
        """显示答题结果"""
        self.console.clear()
        self.console.print()

        # 显示评估提示
        self.console.print("[bold yellow]🤖 AI正在评估你的答案（并发处理中）...[/bold yellow]")
        self.console.print()

        # 并发评估所有答案
        questions = [q for q, _ in self.user_answers]
        answers = [a for _, a in self.user_answers]

        evaluations = self.evaluator.evaluate_batch(questions, answers)

        # 统计结果
        correct_count = sum(1 for e in evaluations if e.is_correct)

        self.console.print(Panel.fit(
            f"[bold]答题完成![/bold]\n\n"
            f"正确: [green]{correct_count}[/green] | "
            f"错误: [red]{len(evaluations) - correct_count}[/red] | "
            f"正确率: [cyan]{correct_count/len(evaluations)*100:.1f}%[/cyan]",
            title="统计",
            border_style="cyan"
        ))

        # 逐个显示答案对比
        for idx, ((question, user_answer), evaluation) in enumerate(zip(self.user_answers, evaluations), 1):
            self._show_answer_comparison(idx, question, user_answer, evaluation)

        # 请求质量评分并更新SM-2参数
        user_records = self._collect_quality_ratings(evaluations)

        # 显示结束选项并询问是否继续
        self._should_continue = self._show_end_options()

        return user_records

    def should_continue(self) -> bool:
        """
        检查是否应该继续下一轮

        Returns:
            True表示继续，False表示返回主菜单
        """
        return getattr(self, '_should_continue', False)

    def _show_answer_comparison(
        self,
        index: int,
        question: Question,
        user_answer: str,
        evaluation: AnswerEvaluation
    ):
        """显示答案对比"""
        self.console.print()
        self.console.print(f"[bold cyan]═══ 第 {index} 题答案对比 ═══[/bold cyan]")
        self.console.print()

        # 用户答案
        self.console.print(Panel(
            user_answer or "[dim](未回答)[/dim]",
            title="[bold]你的答案[/bold]",
            border_style="blue" if evaluation.is_correct else "red",
        ))

        # 正确答案
        self.console.print()
        self.console.print(Panel(
            question.correct_answer,
            title="[bold]参考答案[/bold]",
            border_style="green",
        ))

        # AI评估
        self.console.print()
        feedback_text = self.evaluator.generate_feedback(evaluation, question)
        self.console.print(Panel.fit(
            feedback_text,
            title="AI评估",
            border_style="yellow",
        ))

    def _collect_quality_ratings(self, evaluations: List[AnswerEvaluation]) -> List[UserAnswer]:
        """自动根据评估结果生成质量评分（跳过用户自评）"""
        user_records = []

        for (question, answer_text), evaluation in zip(self.user_answers, evaluations):
            # 根据评估结果自动计算质量评分
            score = evaluation.score
            if score >= 0.9:
                quality = 5  # 完美记忆
            elif score >= 0.7:
                quality = 4  # 正确但有犹豫
            elif score >= 0.4:
                quality = 3  # 困难但正确
            elif score >= 0.2:
                quality = 2  # 容易但有错
            else:
                quality = 1  # 困难

            # 更新题目统计字段
            question.times_presented += 1
            if evaluation.is_correct:
                question.times_correct += 1
                question.consecutive_correct += 1
                # 连续2次答对后标记为已掌握但保留
                if question.consecutive_correct >= 2:
                    question.mastered_but_keep = True
            else:
                question.consecutive_correct = 0
                question.mastered_but_keep = False

            # 更新SM-2参数
            self.scheduler.update_question(question, quality)

            # 创建用户记录
            record = UserAnswer(
                question_id=question.id,
                answer_text=answer_text,
                is_correct=evaluation.is_correct,
                score=evaluation.score,
                feedback=evaluation.feedback,
                quality_rating=quality,
            )
            user_records.append(record)

        return user_records

    def _show_end_options(self) -> bool:
        """
        显示结束选项

        Returns:
            True表示继续下一轮，False表示返回主菜单
        """
        self.console.print()
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")

        from rich.prompt import Prompt

        choice = Prompt.ask(
            "[bold cyan]是否继续下一轮？[/bold cyan]",
            choices=["y", "n"],
            default="y",
            console=self.console
        )

        return choice.lower() == "y"

    def show_progress(self, stats: Dict):
        """显示学习进度"""
        self.console.print()
        self.console.print(Panel.fit(
            f"[bold]学习统计[/bold]\n\n"
            f"总答题数: {stats.get('total_questions', 0)}\n"
            f"正确率: [cyan]{stats.get('accuracy_rate', 0):.1f}%[/cyan]\n"
            f"待复习: [yellow]{stats.get('due_questions', 0)}[/yellow]\n"
            f"新题数: [green]{stats.get('new_questions', 0)}[/green]\n"
            f"平均易记因子: {stats.get('average_ease_factor', 0):.2f}",
            title="进度",
            border_style="cyan"
        ))


class AnswerComparisonView:
    """答案对比视图"""

    def __init__(self):
        self.console = Console()

    def show_comparison(
        self,
        question: Question,
        user_answer: str,
        evaluation: AnswerEvaluation
    ):
        """显示答案对比"""
        self.console.print()

        # 创建对比表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("", style="cyan")
        table.add_column("内容")

        table.add_row(
            "[yellow]你的答案[/yellow]",
            user_answer or "[dim](未回答)[/dim]"
        )
        table.add_row(
            "[green]参考答案[/green]",
            question.correct_answer
        )

        self.console.print(table)

        # 显示评估
        self.console.print()
        if evaluation.is_correct:
            self.console.print(f"✅ [green]正确[/green] (得分: {evaluation.score:.0%})")
        else:
            self.console.print(f"❌ [red]错误[/red] (得分: {evaluation.score:.0%})")

        # 显示反馈
        if evaluation.feedback:
            self.console.print(f"\n[dim]{evaluation.feedback}[/dim]")

        # 显示缺失点
        if evaluation.missing_points:
            self.console.print("\n[bold yellow]遗漏要点:[/bold yellow]")
            for point in evaluation.missing_points:
                self.console.print(f"  • {point}")

        # 显示优点
        if evaluation.strengths:
            self.console.print("\n[bold green]回答亮点:[/bold green]")
            for strength in evaluation.strengths:
                self.console.print(f"  • {strength}")
