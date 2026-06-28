"""
错题本服务
管理错题收集、分析和练习
"""
from typing import List, Dict, Tuple
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from models import Question
from repositories.question_repo import QuestionRepository
from ui.quiz import QuizInterface, AnswerComparisonView, QuestionBrowser
from core.sm2_scheduler import SM2Scheduler
from core.answer_evaluator import AnswerEvaluator


class WrongQuestionBook:
    """错题本"""

    def __init__(
        self,
        question_repo: QuestionRepository,
        quiz_interface: QuizInterface,
        scheduler: SM2Scheduler
    ):
        """
        初始化错题本

        Args:
            question_repo: 题目存储库
            quiz_interface: 刷题界面
            scheduler: SM-2调度器
        """
        self.repo = question_repo
        self.quiz = quiz_interface
        self.scheduler = scheduler
        self.console = Console()

    def get_wrong_questions(self, limit: int = None, for_practice: bool = False) -> List[Question]:
        """
        获取错题列表

        Args:
            limit: 最大返回数量（None 表示不限制）
            for_practice: 是否用于练习（True则排除已掌握但保留的题目）

        Returns:
            错题列表
        """
        questions = self.repo.get_wrong_questions(for_practice=for_practice)
        return questions[:limit] if limit is not None else questions

    def show_wrong_questions(self):
        """显示错题本"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")
        self.console.print("[bold cyan]  📕 错题本[/bold cyan]")
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")
        self.console.print()

        wrong_questions = self.get_wrong_questions()

        if not wrong_questions:
            self.console.print("[green]🎉 太棒了！当前没有错题！[/green]")
            self.console.print()
            input("按 Enter 返回...")
            return

        # 创建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)
        table.add_column("题目", style="yellow")
        table.add_column("正确率", style="white")
        table.add_column("连续正确", style="white")
        table.add_column("类型", style="dim")

        for idx, q in enumerate(wrong_questions, 1):
            accuracy = q.times_correct / max(q.times_presented, 1) if q.times_presented > 0 else 0

            # 根据正确率着色
            accuracy_color = "red" if accuracy < 0.4 else "yellow" if accuracy < 0.6 else "green"

            table.add_row(
                str(idx),
                q.content[:30] + "..." if len(q.content) > 30 else q.content,
                f"[{accuracy_color}]{accuracy:.0%}[/{accuracy_color}]",
                f"{'✓' * q.consecutive_correct}{'✗' * (3 - q.consecutive_correct)}",
                q.type.value,
            )

        self.console.print(table)

        # 显示弱项分析
        self._show_weak_analysis(wrong_questions)

        # 显示选项
        self._show_options(wrong_questions)

    def _show_weak_analysis(self, wrong_questions: List[Question]):
        """显示弱项分析"""
        # 统计按类别的错误
        category_errors = {}
        for q in wrong_questions:
            for tag in q.tags:
                category_errors[tag] = category_errors.get(tag, 0) + 1

        if category_errors:
            # 找出错误最多的类别
            top_weak = sorted(category_errors.items(), key=lambda x: x[1], reverse=True)[:5]

            self.console.print()
            self.console.print(Panel.fit(
                "[bold]📊 弱项分析[/bold]\n\n" +
                "\n".join(f"  {tag}: {count}题" for tag, count in top_weak),
                title="需要加强的知识点",
                border_style="yellow"
            ))

    def _show_options(self, wrong_questions: List[Question]):
        """显示操作选项"""
        self.console.print()
        choice = Prompt.ask(
            "[bold cyan]选择操作[/bold cyan]",
            choices=["练习", "详情", "返回"],
            default="返回",
            console=self.console
        )

        if choice == "练习":
            # 获取用于练习的错题（排除已掌握但保留的）
            # 不限制数量，让用户可以连续练习所有错题
            practice_questions = self.get_wrong_questions(limit=None, for_practice=True)
            self._practice_wrong(practice_questions)
        elif choice == "详情":
            self._show_details(wrong_questions)

    def _practice_wrong(self, questions: List[Question]):
        """练习错题（支持连续练习）"""
        if not questions:
            return

        round_num = 1
        per_round = min(5, len(questions))  # 每轮最多5题

        while True:
            # 获取本轮练习的题目
            start_idx = (round_num - 1) * per_round
            if start_idx >= len(questions):
                # 所有题目都练完了，重新获取错题列表
                questions = self.get_wrong_questions(for_practice=True)
                if not questions:
                    self.console.print()
                    self.console.print("[green]🎉 恭喜！错题本已清空！[/green]")
                    self.console.print()
                    input("按 Enter 返回...")
                    return
                round_num = 1
                start_idx = 0

            end_idx = min(start_idx + per_round, len(questions))
            round_questions = questions[start_idx:end_idx]

            self.console.print()
            self.console.print(f"[bold yellow]开始错题练习（第 {round_num} 轮，共 {len(round_questions)} 题）[/bold yellow]")
            self.console.print()

            # 使用刷题界面
            user_records = self.quiz.start_round(round_questions, round_num=round_num)

            # 保存更新后的题目统计信息
            # 注意：round_questions 中的对象已在 start_round 中被修改
            all_questions = self.repo.load_all()
            for practiced_q in round_questions:
                # 找到该题目所属的会话并保存
                for session_id, session_questions in all_questions.items():
                    for i, q in enumerate(session_questions):
                        if q.id == practiced_q.id:
                            # 使用更新后的题目对象
                            session_questions[i] = practiced_q
                            self.repo.save_session(session_id, session_questions)
                            break
                    else:
                        continue
                    break

            # 检查是否继续下一轮
            if not self.quiz.should_continue():
                break

            round_num += 1

    def _show_details(self, wrong_questions: List[Question]):
        """显示错题详情"""
        if not wrong_questions:
            self.console.print("[dim]暂无错题[/dim]")
            return

        self.console.print()

        # 提示快速浏览模式
        self.console.print("[dim]提示：进入详情后可按 Enter 连续浏览下一题，按 'q' 返回[/dim]")
        self.console.print()

        # 选择题目
        try:
            idx = int(Prompt.ask(
                "输入题目编号（或直接按 Enter 进入快速浏览模式）",
                default="1",
                console=self.console
            ))
        except (ValueError, KeyboardInterrupt):
            return

        if 1 <= idx <= len(wrong_questions):
            # 进入快速浏览模式，从选中的题目开始
            self._quick_browse_details(wrong_questions, idx - 1)

    def _quick_browse_details(self, questions: List[Question], start_idx: int = 0):
        """
        快速浏览模式：按 Enter 连续查看题目详情

        Args:
            questions: 题目列表
            start_idx: 起始索引
        """
        browser = QuestionBrowser()
        browser.browse_questions(questions, start_idx)

    def mark_mastered(self, question_id: str) -> bool:
        """
        标记题目为已掌握

        Args:
            question_id: 题目ID

        Returns:
            是否成功标记
        """
        # 从所有会话中查找题目
        all_questions = self.repo.load_all()

        for session_id, questions in all_questions.items():
            for q in questions:
                if q.id == question_id:
                    # 检查是否满足掌握条件（连续正确3次）
                    if q.consecutive_correct >= 3:
                        # 增加间隔，降低复习频率
                        q.interval *= 2
                        q.ease_factor = min(q.ease_factor + 0.1, 3.0)
                        self.repo.update_question(q)
                        return True
        return False

    def get_mastered_questions(self) -> List[Question]:
        """获取已掌握的题目"""
        mastered = []

        for questions in self.repo.load_all().values():
            for q in questions:
                if q.consecutive_correct >= 3:
                    mastered.append(q)

        return mastered

    def show_mastered(self):
        """显示已掌握的题目"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold green]═══════════════════════════════[/bold green]")
        self.console.print("[bold green]  ✓ 已掌握的题目[/bold green]")
        self.console.print("[bold green]═══════════════════════════════[/bold green]")
        self.console.print()

        mastered = self.get_mastered_questions()

        if not mastered:
            self.console.print("[dim]还没有已掌握的题目。连续答对3题后即可标记为已掌握。[/dim]")
            self.console.print()
            input("按 Enter 返回...")
            return

        # 创建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)
        table.add_column("题目", style="yellow")
        table.add_column("复习次数", style="white")
        table.add_column("间隔", style="white")

        for idx, q in enumerate(mastered, 1):
            table.add_row(
                str(idx),
                q.content[:30] + "..." if len(q.content) > 30 else q.content,
                str(q.repetition),
                f"{q.interval}天",
            )

        self.console.print(table)
        self.console.print()
        input("按 Enter 返回...")
