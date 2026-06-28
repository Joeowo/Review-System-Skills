"""
主菜单界面
"""
import time
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align

from config import ensure_data_dirs
from repositories.knowledge_repo import KnowledgeRepository
from repositories.question_repo import QuestionRepository
from repositories.stats_repo import StatsRepository
from core.knowledge_extractor import AgentKnowledgeExtractor
from core.question_generator import QuestionGenerator
from core.sm2_scheduler import SM2Scheduler
from core.answer_evaluator import AnswerEvaluator
from services.llm_service import SyncDeepSeekService
from services.qa_assistant import QAAssistant
from services.wrong_question_service import WrongQuestionBook
from services.knowledge_query import KnowledgeQuerySystem
from services.question_extraction_service import QuestionExtractionService
from ui.quiz import QuizInterface, QuestionBrowser


class MainMenu:
    """主菜单"""

    def __init__(self):
        """初始化菜单"""
        self.console = Console()
        ensure_data_dirs()

        # 初始化组件
        self.knowledge_repo = KnowledgeRepository()
        self.question_repo = QuestionRepository()
        self.stats_repo = StatsRepository()
        self.llm_service = SyncDeepSeekService()
        self.scheduler = SM2Scheduler()
        self.evaluator = AnswerEvaluator(self.llm_service)
        self.generator = QuestionGenerator()
        self.extractor = AgentKnowledgeExtractor()
        self.query_system = KnowledgeQuerySystem()  # 添加查询系统

        # 初始化界面
        self.quiz_interface = QuizInterface(self.evaluator, self.scheduler)

        # 初始化服务
        self.qa_assistant = QAAssistant(self.query_system)
        self.wrong_book = WrongQuestionBook(
            self.question_repo,
            self.quiz_interface,
            self.scheduler
        )
        self.question_extraction = QuestionExtractionService()

        self.running = True

    def show(self):
        """显示主菜单"""
        while self.running:
            self.console.clear()
            self._show_header()

            # 获取统计数据
            stats = self._get_main_stats()
            self._show_stats(stats)

            # 显示菜单选项
            choice = self._show_menu_options()

            # 处理选择
            self._handle_choice(choice)

    def _show_header(self):
        """显示标题"""
        header = """
[bold cyan]╔═══════════════════════════════════════════════════════╗
║               📚 ^^经济管理复习系统^^                 ║
║                 Review Agent v1.0                     ║
╚═══════════════════════════════════════════════════════╝[/bold cyan]
        """
        self.console.print(header)

    def _get_main_stats(self) -> dict:
        """获取主要统计"""
        # 知识点统计
        knowledge_stats = self.knowledge_repo.get_stats()

        # 题目统计
        question_stats = self.question_repo.get_statistics()

        # 用户统计
        user_stats = self.stats_repo.load_progress()

        return {
            "knowledge_points": knowledge_stats.get("total_points", 0),
            "total_questions": question_stats.get("total_questions", 0),
            "due_questions": question_stats.get("due_questions", 0),
            "wrong_questions": question_stats.get("wrong_questions", 0),
            "accuracy_rate": question_stats.get("accuracy_rate", 0),
            "total_answers": user_stats.total_answers,
        }

    def _show_stats(self, stats: dict):
        """显示统计信息"""
        self.console.print()
        self.console.print(Panel.fit(
            f"[dim]知识点:[/dim] [cyan]{stats['knowledge_points']}[/cyan]    "
            f"[dim]题库:[/dim] [cyan]{stats['total_questions']}[/cyan]    "
            f"[dim]待复习:[/dim] [yellow]{stats['due_questions']}[/yellow]    "
            f"[dim]错题:[/dim] [red]{stats['wrong_questions']}[/red]    "
            f"[dim]正确率:[/dim] [cyan]{stats['accuracy_rate']:.1%}[/cyan]",
            border_style="dim"
        ))
        self.console.print()

    def _show_menu_options(self) -> str:
        """显示菜单选项并获取用户选择"""
        menu = """
[bold cyan]1.[/bold cyan] [white]开始刷题[/white]          [dim]基于SuperMemo-2智能调度[/dim]
[bold cyan]2.[/bold cyan] [white]错题本[/white]            [dim]查看和练习错题[/dim]
[bold cyan]3.[/bold cyan] [white]学习统计[/white]          [dim]查看详细学习数据[/dim]
[bold cyan]4.[/bold cyan] [white]问答助手[/white]          [dim]知识问答[/dim]
[bold cyan]5.[/bold cyan] [white]提取题目[/white]          [dim]从历年试题和复习资料提取[/dim]
[bold cyan]6.[/bold cyan] [white]重新提取知识点[/white]    [dim]从源文件提取知识点[/dim]
[bold cyan]7.[/bold cyan] [white]生成题目[/white]          [dim]从知识点生成题目[/dim]
[bold cyan]0.[/bold cyan] [white]退出[/white]              [dim]退出系统[/dim]
        """

        self.console.print(menu)
        self.console.print()

        from rich.prompt import Prompt

        choice = Prompt.ask(
            "[bold cyan]请选择操作[/bold cyan]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7"],
            default="1",
            console=self.console
        )

        return choice

    def _handle_choice(self, choice: str):
        """处理用户选择"""
        if choice == "0":
            self._exit()
        elif choice == "1":
            self._start_quiz()
        elif choice == "2":
            self._wrong_book()
        elif choice == "3":
            self._show_stats_detail()
        elif choice == "4":
            self._qa_assistant()
        elif choice == "5":
            self._extract_questions()
        elif choice == "6":
            self._extract_knowledge()
        elif choice == "7":
            self._generate_questions()

    def _start_quiz(self):
        """开始刷题（支持答题和浏览模式）"""
        self.console.clear()

        # 获取需要复习的题目
        all_questions = []
        for questions in self.question_repo.load_all().values():
            all_questions.extend(questions)

        if not all_questions:
            self.console.print("[yellow]题库为空，请先生成题目。[/yellow]")
            self.console.print()
            input("按 Enter 返回...")
            return

        # 使用SM-2调度获取题目
        due_questions = self.scheduler.get_due_questions(all_questions, limit=None)

        if not due_questions:
            # 没有到期题目，获取新题
            new_questions = self.scheduler.get_new_questions(all_questions, limit=None)
            if not new_questions:
                self.console.print("[green]🎉 所有题目都已复习完毕！[/green]")
                self.console.print()
                input("按 Enter 返回...")
                return
            due_questions = new_questions

        # 显示题目统计
        self.console.print(f"[bold cyan]═══ 题目统计 ═══[/bold cyan]")
        self.console.print(f"待复习: [yellow]{len([q for q in due_questions if q.repetition > 0])}[/yellow] 题")
        self.console.print(f"新题目: [green]{len([q for q in due_questions if q.repetition == 0])}[/green] 题")
        self.console.print(f"总计: [cyan]{len(due_questions)}[/cyan] 题")
        self.console.print()

        # 询问模式选择
        from rich.prompt import Prompt
        mode = Prompt.ask(
            "[bold cyan]选择模式[/bold cyan]",
            choices=["答题", "浏览"],
            default="答题",
            console=self.console
        )

        if mode == "浏览":
            # 浏览模式
            self.console.print()
            self.console.print("[dim]提示：按 Enter 连续浏览下一题，按 'q' 返回[/dim]")
            self.console.print()

            browser = QuestionBrowser()
            browser.browse_questions(due_questions)

            self.console.print()
            self.console.print("[green]✓ 浏览结束[/green]")
            self.console.print()
            input("按 Enter 返回...")
        else:
            # 答题模式（连续多轮）
            round_num = 1
            per_round = min(5, len(due_questions))

            while True:
                # 获取本轮题目
                start_idx = (round_num - 1) * per_round
                if start_idx >= len(due_questions):
                    self.console.print()
                    self.console.print("[green]🎉 所有题目已练习完毕！[/green]")
                    self.console.print()
                    input("按 Enter 返回...")
                    break

                end_idx = min(start_idx + per_round, len(due_questions))
                round_questions = due_questions[start_idx:end_idx]

                # 开始一轮刷题
                self.console.print()
                self.console.print(f"[bold cyan]═══ 第 {round_num} 轮 ({len(round_questions)} 题) ═══[/bold cyan]")
                user_records = self.quiz_interface.start_round(round_questions, round_num)

                # 保存答题记录和更新题目统计
                for record in user_records:
                    self.stats_repo.save_answer(record)

                # 保存更新后的题目
                all_questions_dict = self.question_repo.load_all()
                session_updates = {}  # session_id -> {question_id: updated_question}

                for answered_q in round_questions:
                    # 找到该题目所属的会话
                    for session_id, session_questions in all_questions_dict.items():
                        for i, q in enumerate(session_questions):
                            if q.id == answered_q.id:
                                if session_id not in session_updates:
                                    session_updates[session_id] = {}
                                session_updates[session_id][answered_q.id] = (i, answered_q)
                                break
                        else:
                            continue
                        break

                # 批量保存更新的会话
                for session_id, updates in session_updates.items():
                    session_questions = list(all_questions_dict[session_id])
                    for idx, updated_q in updates.values():
                        session_questions[idx] = updated_q
                    self.question_repo.save_session(session_id, session_questions)

                # 检查是否继续
                continue_quiz = self.quiz_interface.should_continue()
                if not continue_quiz:
                    break

                round_num += 1

            self.console.print()
            self.console.print("[green]✓ 刷题结束，感谢学习！[/green]")
            self.console.print()
            input("按 Enter 返回...")

    def _wrong_book(self):
        """错题本"""
        self.wrong_book.show_wrong_questions()

    def _show_stats_detail(self):
        """显示详细统计"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")
        self.console.print("[bold cyan]  📊 学习统计[/bold cyan]")
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")
        self.console.print()

        # 知识点统计
        knowledge_stats = self.knowledge_repo.get_stats()
        self.console.print(f"[bold]知识点统计[/bold]")
        self.console.print(f"  总知识点数: {knowledge_stats.get('total_points', 0)}")
        self.console.print(f"  会话数量: {knowledge_stats.get('total_sessions', 0)}")

        by_type = knowledge_stats.get('by_type', {})
        if by_type:
            self.console.print(f"  按类型分布:")
            for type_name, count in by_type.items():
                self.console.print(f"    {type_name}: {count}")

        self.console.print()

        # 题目统计
        question_stats = self.question_repo.get_statistics()
        self.console.print(f"[bold]题目统计[/bold]")
        self.console.print(f"  总题目数: {question_stats.get('total_questions', 0)}")
        self.console.print(f"  答题总数: {question_stats.get('total_presented', 0)}")
        self.console.print(f"  正确率: {question_stats.get('accuracy_rate', 0):.1%}")
        self.console.print(f"  待复习: {question_stats.get('due_questions', 0)}")
        self.console.print(f"  错题数: {question_stats.get('wrong_questions', 0)}")

        self.console.print()

        # 用户统计
        user_stats = self.stats_repo.load_progress()
        self.console.print(f"[bold]个人统计[/bold]")
        self.console.print(f"  总答题数: {user_stats.total_answers}")
        self.console.print(f"  总学习时间: {user_stats.total_study_time // 60} 分钟")
        self.console.print(f"  连续学习: {user_stats.streak_days} 天")

        weak_areas = user_stats.weak_areas
        if weak_areas:
            self.console.print(f"  弱项:")
            for area, count in list(weak_areas.items())[:5]:
                self.console.print(f"    {area + ':':>12} {count:>4}题")

        self.console.print()
        input("按 Enter 返回...")

    def _qa_assistant(self):
        """问答助手"""
        self.qa_assistant.start()

    def _extract_questions(self):
        """提取题目"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")
        self.console.print("[bold cyan]  📝 题目提取[/bold cyan]")
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")
        self.console.print()

        # 显示当前题库统计
        stats = self.question_extraction.get_statistics()
        self.console.print(f"[dim]当前题库统计:[/dim]")
        self.console.print(f"  总题数: {stats['total_questions']}")
        self.console.print(f"  文件数: {stats['files']}")
        self.console.print()

        # 选择提取源
        from rich.prompt import Prompt
        source_type = Prompt.ask(
            "[bold cyan]选择提取源[/bold cyan]",
            choices=["all", "exams", "materials"],
            default="all",
            console=self.console
        )

        source_names = {
            "all": "全部源（历年试题+复习资料）",
            "exams": "仅历年试题",
            "materials": "仅复习资料"
        }
        self.console.print()
        self.console.print(f"[bold yellow]正在从 {source_names[source_type]} 提取题目...[/bold yellow]")
        self.console.print()

        try:
            report = self.question_extraction.process_and_save(source_type)

            self.console.print()
            self.console.print("[bold green]═══════════════════════════════[/bold green]")
            self.console.print("[bold green]  ✓ 提取完成[/bold green]")
            self.console.print("[bold green]═══════════════════════════════[/bold green]")
            self.console.print()
            self.console.print(f"[bold]原始提取:[/bold] {report['raw_count']} 道题目")
            self.console.print(f"[bold]去重后:[/bold] {report['unique_count']} 道题目")
            self.console.print(f"[bold]去重率:[/bold] {report['duplicate_rate']:.1%}")
            self.console.print()

            if report.get('by_source'):
                self.console.print("[bold]按来源统计:[/bold]")
                for source, count in report['by_source'].items():
                    self.console.print(f"  {source}: {count} 道题目")

            if 'saved_to' in report:
                self.console.print()
                self.console.print(f"[dim]已保存到: {report['saved_to']}[/dim]")

        except Exception as e:
            self.console.print()
            self.console.print(f"[red]✗ 提取失败: {e}[/red]")

        self.console.print()
        input("按 Enter 返回...")

    def _extract_knowledge(self):
        """提取知识点"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold yellow]正在提取知识点...[/bold yellow]")

        try:
            results = self.extractor.extract_all()

            # 保存结果
            for session_id, points in results.items():
                self.knowledge_repo.save_session(session_id, points)

            self.console.print()
            total = sum(len(points) for points in results.values())
            self.console.print(f"[green]✓ 成功提取 {total} 个知识点[/green]")

            for session_id, points in results.items():
                self.console.print(f"  - {session_id}: {len(points)} 个")

        except Exception as e:
            self.console.print(f"[red]✗ 提取失败: {e}[/red]")

        self.console.print()
        input("按 Enter 返回...")

    def _generate_questions(self):
        """生成题目"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold yellow]正在生成题目...[/bold yellow]")

        try:
            all_knowledge = self.knowledge_repo.load_all()
            all_questions = []

            for session_id, knowledge_points in all_knowledge.items():
                # 为该会话生成题目
                questions = self.generator.generate_batch(knowledge_points)
                all_questions.extend(questions)

                # 保存题目
                self.question_repo.save_session(session_id, questions)

            self.console.print()
            self.console.print(f"[green]✓ 成功生成 {len(all_questions)} 道题目[/green]")

        except Exception as e:
            self.console.print(f"[red]✗ 生成失败: {e}[/red]")

        self.console.print()
        input("按 Enter 返回...")

    def _exit(self):
        """退出系统"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold green]感谢使用！再见！👋[/bold green]")
        self.console.print()
        self.running = False
        time.sleep(1)


# 测试代码
if __name__ == "__main__":
    menu = MainMenu()
    menu.show()
