"""
Agent Framework 主菜单界面

提供 Workflow 选择、会话管理、运行控制等功能
"""
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.prompt import Prompt
from rich import box

from config.settings import config
from core.state import AgentState, load_session_state, sync_to_persistence
from core.checkpoint import CheckpointManager
from workflows.f1_learning_research import create_f1_workflow
from workflows.f2_qa_enhanced import create_f2_workflow
from workflows.f3_academic_writing import create_f3_workflow
from workflows.f4_review_planning import create_f4_workflow
from langgraph.checkpoint.memory import MemorySaver


class MainMenu:
    """主菜单"""

    def __init__(self):
        """初始化菜单"""
        self.console = Console()
        self.running = True

        # Workflow 注册
        self.workflows = {
            "f1": {
                "name": "F1 学习研究一体化",
                "description": "从研究到掌握的完整学习流程",
                "creator": create_f1_workflow
            },
            "f2": {
                "name": "F2 知识问答增强",
                "description": "基于知识库的智能问答",
                "creator": create_f2_workflow
            },
            "f3": {
                "name": "F3 学术写作全流程",
                "description": "从澄清到完成的学术写作",
                "creator": create_f3_workflow
            },
            "f4": {
                "name": "F4 复习计划生成",
                "description": "基于 SM2 算法的复习计划",
                "creator": create_f4_workflow
            }
        }

        # 会话管理
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def show(self):
        """显示主菜单"""
        while self.running:
            self.console.clear()
            self._show_header()

            # 显示会话统计
            self._show_session_stats()

            # 显示菜单选项
            choice = self._show_menu_options()

            # 处理选择
            self._handle_choice(choice)

    def _show_header(self):
        """显示标题"""
        header = """
[bold cyan]╔═════════════════════════════════════════════════════════════╗
║                  🚀 ^^Agent Framework^^                    ║
║              ComindFlow 核心编排引擎 v0.1.0                  ║
╚═════════════════════════════════════════════════════════════╝[/bold cyan]
        """
        self.console.print(header)

    def _show_session_stats(self):
        """显示会话统计"""
        # 统计会话目录
        sessions = list(self.sessions_dir.iterdir()) if self.sessions_dir.exists() else []
        session_count = len([s for s in sessions if s.is_dir()])

        self.console.print()
        self.console.print(Panel.fit(
            f"[dim]会话目录:[/dim] [cyan]{self.sessions_dir}[/cyan]    "
            f"[dim]会话数:[/dim] [cyan]{session_count}[/cyan]",
            border_style="dim"
        ))
        self.console.print()

    def _show_menu_options(self) -> str:
        """显示菜单选项并获取用户选择"""
        menu = """
[bold cyan]1.[/bold cyan] [white]选择 Workflow[/white]          [dim]选择并运行工作流 (F1/F2/F3/F4)[/dim]
[bold cyan]2.[/bold cyan] [white]会话管理[/white]            [dim]创建新会话 / 恢复已有会话[/dim]
[bold cyan]3.[/bold cyan] [white]查看状态[/white]            [dim]显示配置和系统状态[/dim]
[bold cyan]4.[/bold cyan] [white]快速启动[/white]            [dim]快速启动最近使用的会话[/dim]
[bold cyan]0.[/bold cyan] [white]退出[/white]                [dim]退出系统[/dim]
        """

        self.console.print(menu)
        self.console.print()

        choice = Prompt.ask(
            "[bold cyan]请选择操作[/bold cyan]",
            choices=["0", "1", "2", "3", "4"],
            default="1",
            console=self.console
        )

        return choice

    def _handle_choice(self, choice: str):
        """处理用户选择"""
        if choice == "0":
            self._exit()
        elif choice == "1":
            self._select_workflow()
        elif choice == "2":
            self._manage_sessions()
        elif choice == "3":
            self._show_status()
        elif choice == "4":
            self._quick_start()

    # ==============================================================================
    # Workflow 选择
    # ==============================================================================

    def _select_workflow(self):
        """选择并运行 Workflow"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold cyan]═════════════════════════════════════════[/bold cyan]")
        self.console.print("[bold cyan]  📋 选择 Workflow[/bold cyan]")
        self.console.print("[bold cyan]═════════════════════════════════════════[/bold cyan]")
        self.console.print()

        # 显示 Workflow 列表
        table = Table(box=box.ROUNDED)
        table.add_column("编号", style="cyan", width=6)
        table.add_column("Workflow", style="white")
        table.add_column("描述", style="dim")

        for key, info in self.workflows.items():
            table.add_row(key, info["name"], info["description"])

        self.console.print(table)
        self.console.print()

        # 选择 Workflow
        wf_choice = Prompt.ask(
            "[bold cyan]选择 Workflow[/bold cyan]",
            choices=list(self.workflows.keys()) + ["返回"],
            default="返回",
            console=self.console
        )

        if wf_choice == "返回":
            return

        # 选择会话或创建新会话
        self._run_workflow(wf_choice)

    def _run_workflow(self, workflow_key: str):
        """运行指定的 Workflow"""
        workflow_info = self.workflows[workflow_key]

        self.console.clear()
        self.console.print()
        self.console.print(f"[bold cyan]正在启动: {workflow_info['name']}[/bold cyan]")
        self.console.print()

        # 获取或创建会话
        session_path = self._get_or_create_session(workflow_key)

        if not session_path:
            self.console.print("[yellow]操作取消[/yellow]")
            self.console.print()
            input("按 Enter 返回...")
            return

        # 根据不同的 workflow 准备参数
        initial_state = self._prepare_workflow_state(workflow_key, session_path)

        if not initial_state:
            self.console.print("[yellow]状态准备失败[/yellow]")
            self.console.print()
            input("按 Enter 返回...")
            return

        # 编译并运行 workflow
        try:
            self.console.print("[dim]编译 Workflow...[/dim]")
            workflow = workflow_info["creator"]()
            app = workflow.compile(checkpointer=MemorySaver())

            self.console.print("[green]✓ Workflow 编译成功[/green]")
            self.console.print()
            self.console.print("[bold yellow]开始执行 Workflow...[/bold yellow]")
            self.console.print("[dim](按 Ctrl+C 可中断执行)[/dim]")
            self.console.print()

            # 执行 workflow
            config = {"configurable": {"thread_id": f"{workflow_key}_{datetime.now().strftime('%Y%m%d%H%M')}"}}

            result = app.invoke(initial_state, config=config)

            # 显示结果
            self._show_workflow_result(workflow_key, result)

        except KeyboardInterrupt:
            self.console.print()
            self.console.print("[yellow]Workflow 执行被中断[/yellow]")
        except Exception as e:
            self.console.print()
            self.console.print(f"[red]✗ Workflow 执行失败: {e}[/red]")
            import traceback
            self.console.print(traceback.format_exc())

        self.console.print()
        input("按 Enter 返回...")

    def _get_or_create_session(self, workflow_key: str) -> Optional[Path]:
        """获取或创建会话"""
        # 列出现有会话
        existing_sessions = [s for s in self.sessions_dir.iterdir() if s.is_dir()]

        self.console.print(f"[dim]会话目录: {self.sessions_dir}[/dim]")

        if existing_sessions:
            self.console.print()
            self.console.print("[bold]现有会话:[/bold]")
            for i, s in enumerate(existing_sessions, 1):
                self.console.print(f"  {i}. {s.name}")
            self.console.print()

        # 询问是否使用现有会话或创建新会话
        action = Prompt.ask(
            "[bold cyan]选择操作[/bold cyan]",
            choices=["新会话", "现有会话", "取消"],
            default="新会话",
            console=self.console
        )

        if action == "取消":
            return None

        if action == "新会话":
            session_name = Prompt.ask(
                "[bold cyan]输入会话名称[/bold cyan]",
                default=f"{workflow_key}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                console=self.console
            )
            session_path = self.sessions_dir / session_name
            session_path.mkdir(parents=True, exist_ok=True)

            # 初始化会话文件
            (session_path / "CONTEXT.md").write_text(
                f"# {session_name}\n\n## 术语定义\n\n",
                encoding="utf-8"
            )
            (session_path / "Task.md").write_text(
                f"# {session_name} - 学习任务\n\n初始化时间: {datetime.now().isoformat()}\nWorkflow: {workflow_key}\n\n",
                encoding="utf-8"
            )

            self.console.print(f"[green]✓ 会话已创建: {session_path}[/green]")
            return session_path

        else:  # 现有会话
            if not existing_sessions:
                self.console.print("[yellow]没有现有会话[/yellow]")
                return None

            session_num = Prompt.ask(
                "[bold cyan]选择会话编号[/bold cyan]",
                choices=[str(i) for i in range(1, len(existing_sessions) + 1)],
                console=self.console
            )
            return existing_sessions[int(session_num) - 1]

    def _prepare_workflow_state(self, workflow_key: str, session_path: Path) -> Optional[dict]:
        """准备 Workflow 初始状态"""
        try:
            state = load_session_state(session_path)

            # 设置通用字段
            state["workflow_name"] = workflow_key
            state["start_time"] = datetime.now().isoformat()

            # 根据不同 workflow 设置特定字段
            if workflow_key == "f1":
                # F1 需要主题
                topic = Prompt.ask(
                    "[bold cyan]输入学习主题[/bold cyan]",
                    console=self.console
                )
                state["topic"] = topic

            elif workflow_key == "f2":
                # F2 自动加载知识库
                pass

            elif workflow_key == "f3":
                # F3 需要写作主题
                topic = Prompt.ask(
                    "[bold cyan]输入写作主题[/bold cyan]",
                    console=self.console
                )
                state["topic"] = topic

            elif workflow_key == "f4":
                # F4 需要源文件路径
                source_path = Prompt.ask(
                    "[bold cyan]输入学习资料路径[/bold cyan]",
                    console=self.console
                )
                state["source_paths"] = [source_path]

            return state

        except Exception as e:
            self.console.print(f"[red]状态准备失败: {e}[/red]")
            return None

    def _show_workflow_result(self, workflow_key: str, result: dict):
        """显示 Workflow 执行结果"""
        self.console.print()
        self.console.print("[bold green]═════════════════════════════════════════[/bold green]")
        self.console.print("[bold green]  ✓ Workflow 执行完成[/bold green]")
        self.console.print("[bold green]═════════════════════════════════════════[/bold green]")
        self.console.print()

        # 显示关键结果
        if workflow_key == "f1":
            report_path = result.get("report_path")
            if report_path:
                self.console.print(f"[bold]研究报告:[/bold] {report_path}")

            concepts = result.get("key_concepts", [])
            if concepts:
                self.console.print(f"[bold]提取概念:[/bold] {len(concepts)} 个")

            mastery = result.get("mastery_level", "")
            if mastery:
                self.console.print(f"[bold]掌握程度:[/bold] {mastery}")

        elif workflow_key == "f2":
            answer = result.get("generated_answer")
            if answer:
                self.console.print(f"[bold]回答:[/bold]")
                self.console.print(answer)

        elif workflow_key == "f3":
            review_score = result.get("review_score", 0)
            self.console.print(f"[bold]审查分数:[/bold] {review_score:.2f}")

            draft_paths = result.get("draft_paths", [])
            if draft_paths:
                self.console.print(f"[bold]草稿文件:[/bold] {len(draft_paths)} 个")

        elif workflow_key == "f4":
            plan_path = result.get("review_plan_path")
            if plan_path:
                self.console.print(f"[bold]复习计划:[/bold] {plan_path}")

            knowledge_points = result.get("knowledge_points", [])
            if knowledge_points:
                self.console.print(f"[bold]知识点:[/bold] {len(knowledge_points)} 个")

        self.console.print()

    # ==============================================================================
    # 会话管理
    # ==============================================================================

    def _manage_sessions(self):
        """会话管理"""
        while True:
            self.console.clear()
            self.console.print()
            self.console.print("[bold cyan]═════════════════════════════════════════[/bold cyan]")
            self.console.print("[bold cyan]  📁 会话管理[/bold cyan]")
            self.console.print("[bold cyan]═════════════════════════════════════════[/bold cyan]")
            self.console.print()

            # 列出现有会话
            sessions = [s for s in self.sessions_dir.iterdir() if s.is_dir()]

            if not sessions:
                self.console.print("[dim]暂无会话[/dim]")
                self.console.print()
                input("按 Enter 返回...")
                return

            # 显示会话列表
            table = Table(box=box.ROUNDED)
            table.add_column("编号", style="cyan", width=6)
            table.add_column("会话名称", style="white")
            table.add_column("修改时间", style="dim")

            for i, s in enumerate(sessions, 1):
                mtime = datetime.fromtimestamp(s.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                table.add_row(str(i), s.name, mtime)

            self.console.print(table)
            self.console.print()

            # 操作选项
            action = Prompt.ask(
                "[bold cyan]选择操作[/bold cyan]",
                choices=["删除", "重命名", "返回"],
                default="返回",
                console=self.console
            )

            if action == "返回":
                return
            elif action == "删除":
                self._delete_session(sessions)
            elif action == "重命名":
                self._rename_session(sessions)

    def _delete_session(self, sessions: list):
        """删除会话"""
        session_num = Prompt.ask(
            "[bold cyan]选择要删除的会话编号[/bold cyan]",
            choices=[str(i) for i in range(1, len(sessions) + 1)],
            console=self.console
        )

        session = sessions[int(session_num) - 1]

        confirm = Prompt.ask(
            f"[bold yellow]确认删除 '{session.name}'?[/bold yellow]",
            choices=["y", "n"],
            default="n",
            console=self.console
        )

        if confirm == "y":
            import shutil
            shutil.rmtree(session)
            self.console.print(f"[green]✓ 会话已删除[/green]")
            self.console.print()
            input("按 Enter 返回...")

    def _rename_session(self, sessions: list):
        """重命名会话"""
        session_num = Prompt.ask(
            "[bold cyan]选择要重命名的会话编号[/bold cyan]",
            choices=[str(i) for i in range(1, len(sessions) + 1)],
            console=self.console
        )

        session = sessions[int(session_num) - 1]

        new_name = Prompt.ask(
            "[bold cyan]输入新名称[/bold cyan]",
            default=session.name,
            console=self.console
        )

        if new_name and new_name != session.name:
            new_path = session.parent / new_name
            session.rename(new_path)
            self.console.print(f"[green]✓ 会话已重命名[/green]")
            self.console.print()
            input("按 Enter 返回...")

    # ==============================================================================
    # 状态查看
    # ==============================================================================

    def _show_status(self):
        """显示系统状态"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold cyan]═════════════════════════════════════════[/bold cyan]")
        self.console.print("[bold cyan]  📊 系统状态[/bold cyan]")
        self.console.print("[bold cyan]═════════════════════════════════════════[/bold cyan]")
        self.console.print()

        # 配置信息
        self.console.print("[bold]LLM 配置:[/bold]")
        self.console.print(f"  Model: {config.llm.model}")
        self.console.print(f"  Base URL: {config.llm.base_url}")
        self.console.print(f"  Temperature: {config.llm.temperature}")
        self.console.print()

        self.console.print("[bold]Checkpoint 配置:[/bold]")
        self.console.print(f"  路径: {config.checkpoint.db_path}")
        self.console.print(f"  清理周期: {config.checkpoint.cleanup_days} 天")
        self.console.print()

        self.console.print("[bold]Agent 配置:[/bold]")
        self.console.print(f"  确认级别: {config.confirmation_level}")
        self.console.print(f"  最大重试: {config.max_retries}")
        self.console.print(f"  超时: {config.timeout_seconds} 秒")
        self.console.print()

        # Workflow 信息
        self.console.print("[bold]可用 Workflow:[/bold]")
        for key, info in self.workflows.items():
            self.console.print(f"  {key}: {info['name']}")

        self.console.print()
        input("按 Enter 返回...")

    # ==============================================================================
    # 快速启动
    # ==============================================================================

    def _quick_start(self):
        """快速启动最近使用的会话"""
        self.console.clear()
        self.console.print()

        # 获取最近修改的会话
        sessions = sorted(
            [s for s in self.sessions_dir.iterdir() if s.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if not sessions:
            self.console.print("[yellow]暂无会话，请先创建会话[/yellow]")
            self.console.print()
            input("按 Enter 返回...")
            return

        recent_session = sessions[0]

        self.console.print(f"[bold cyan]最近会话:[/bold cyan] {recent_session.name}")
        self.console.print()

        # 询问要运行的 workflow
        wf_choice = Prompt.ask(
            "[bold cyan]选择 Workflow[/bold cyan]",
            choices=list(self.workflows.keys()) + ["取消"],
            default="f1",
            console=self.console
        )

        if wf_choice == "取消":
            return

        # 直接运行
        workflow_info = self.workflows[wf_choice]
        state = load_session_state(recent_session)
        state["workflow_name"] = wf_choice
        state["start_time"] = datetime.now().isoformat()

        try:
            workflow = workflow_info["creator"]()
            app = workflow.compile(checkpointer=MemorySaver())

            config = {"configurable": {"thread_id": f"{wf_choice}_quick"}}

            self.console.print()
            self.console.print(f"[bold yellow]执行 {workflow_info['name']}...[/bold yellow]")
            self.console.print()

            result = app.invoke(state, config=config)
            self._show_workflow_result(wf_choice, result)

        except Exception as e:
            self.console.print(f"[red]✗ 执行失败: {e}[/red]")

        self.console.print()
        input("按 Enter 返回...")

    # ==============================================================================
    # 退出
    # ==============================================================================

    def _exit(self):
        """退出系统"""
        self.console.clear()
        self.console.print()
        self.console.print("[bold green]感谢使用 Agent Framework！再见！👋[/bold green]")
        self.console.print()
        self.running = False
        time.sleep(1)


# 测试代码
if __name__ == "__main__":
    menu = MainMenu()
    menu.show()
