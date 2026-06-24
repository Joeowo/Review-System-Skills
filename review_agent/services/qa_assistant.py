"""
知识问答助手 - 改进版
使用快速查询系统
"""
import asyncio
import threading
from typing import List, Optional, Dict
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from services.knowledge_query import KnowledgeQuerySystem
from services.llm_service import SyncDeepSeekService


class QAAssistant:
    """知识问答助手"""

    def __init__(self, query_system: Optional[KnowledgeQuerySystem] = None):
        """
        初始化助手

        Args:
            query_system: 知识点查询系统
        """
        self.query_system = query_system or KnowledgeQuerySystem()
        self.llm_service = SyncDeepSeekService()
        self.console = Console()
        self.chat_history: List[Dict] = []

    def start(self):
        """启动问答界面"""
        self.console.clear()
        self.console.print()

        self.console.print("[bold cyan]═════════════════════════════════[/bold cyan]")
        self.console.print("[bold cyan]  🤖 知识问答助手[/bold cyan]")
        self.console.print("[bold cyan]═══════════════════════════════[/bold cyan]")
        self.console.print()
        self.console.print("[dim]输入你的问题，我会基于知识点库回答你。[/dim]")
        self.console.print("[dim]输入 '返回' 或 'quit' 退出[/dim]")
        self.console.print()

        while True:
            self.console.print()
            question = Prompt.ask(
                "[bold yellow]你的问题[/bold yellow]",
                console=self.console,
                default=""
            )

            if not question or question.lower() in ["返回", "quit", "exit", "q"]:
                break

            # 回答问题
            self._answer_question(question)

    def _answer_question(self, question: str):
        """回答问题"""
        self.console.print()

        # 1. 先用快速查询系统搜索
        relevant_points = self.query_system.search(question, limit=3)

        if not relevant_points:
            self.console.print("[dim]在知识点库中没有找到相关内容。[/dim]")
            return

        # 2. 如果找到高度匹配的知识点（分数>=15），直接返回
        best_match = relevant_points[0]
        if best_match["score"] >= 15:
            self._show_direct_answer(best_match, question)
            self._show_related_questions(relevant_points[1:])
            return

        # 3. 否则使用LLM生成回答
        self._show_llm_answer(question, relevant_points)

    def _show_direct_answer(self, point: Dict, question: str):
        """显示直接答案"""
        # 获取完整的知识点内容
        full_point = self.query_system.get_by_id(point["id"])
        if full_point:
            content = full_point.get("content", "")
        else:
            content = point.get("content", "")

        self.console.print(Panel(
            f"[bold]知识点:[/bold] {point['title']}\n\n"
            f"{content[:400]}{'...' if len(content) > 400 else ''}\n\n"
            f"[dim]来源: {point['session_id']} | 类型: {point['type']}[/dim]",
            title="✅ 找到匹配知识点",
            border_style="green"
        ))

    def _show_related_questions(self, related_points: List[Dict]):
        """显示相关问题建议"""
        if not related_points:
            return

        self.console.print()
        self.console.print("[dim]相关知识点:[/dim]")
        for p in related_points[:3]:
            self.console.print(f"  • {p['title']}")

    def _show_llm_answer(self, question: str, relevant_points: List[Dict]):
        """显示LLM生成的答案"""
        self.console.print("[dim]正在思考...[/dim]")

        # 构建上下文
        context_parts = []
        for i, point in enumerate(relevant_points, 1):
            full_point = self.query_system.get_by_id(point["id"])
            if full_point:
                context_parts.append(f"""
知识点{i}: {point['title']}
{full_point.get('content', '')[:300]}
                """)

        context = "\n".join(context_parts)

        # 调用LLM（使用新线程+新事件循环）
        try:
            async def get_answer():
                return await self.llm_service._async_service.chat(
                    messages=[
                        {"role": "system", "content": "你是一个专业的经济管理知识助手。请基于提供的知识点回答用户问题。"},
                        {"role": "user", "content": f"问题: {question}\n\n相关知识点:\n{context}\n\n请基于以上知识给出准确、清晰的回答。如果知识点中没有明确答案，请诚实说明。"}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )

            # 在新线程中运行
            result_holder = {"answer": None, "error": None}

            def run_in_new_loop():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(get_answer())
                    result_holder["answer"] = response
                    loop.close()
                except Exception as e:
                    result_holder["error"] = e

            thread = threading.Thread(target=run_in_new_loop)
            thread.start()
            thread.join(timeout=30)

            if result_holder["error"]:
                raise result_holder["error"]

            response = result_holder["answer"]
            answer = response["choices"][0]["message"]["content"]

            self.console.print(Panel(
                answer,
                title="🤖 AI回答",
                border_style="cyan"
            ))

            # 显示参考知识点
            self._show_reference_points(relevant_points)

        except Exception as e:
            self.console.print(f"[red]生成回答时出错: {e}[/red]")

    def _show_reference_points(self, points: List[Dict]):
        """显示参考知识点"""
        self.console.print()
        self.console.print("[dim]参考知识点:[/dim]")
        for p in points:
            self.console.print(f"  {p['title']} ({p['session_id']})")

    def ask(self, question: str) -> str:
        """
        直接提问（编程接口）

        Args:
            question: 问题

        Returns:
            答案文本
        """
        relevant_points = self.query_system.search(question, limit=3)

        if not relevant_points:
            return "抱歉，在知识点库中没有找到相关内容。"

        best_match = relevant_points[0]
        if best_match["score"] >= 15:
            full_point = self.query_system.get_by_id(best_match["id"])
            if full_point:
                return f"{best_match['title']}\n\n{full_point.get('content', '')}"

        # 使用LLM生成
        context = "\n".join([
            f"{p['title']}: {self.query_system.get_by_id(p['id']).get('content', '')[:200]}"
            for p in relevant_points
        ])

        try:
            async def get_answer():
                return await self.llm_service._async_service.chat(
                    messages=[{
                        "role": "user",
                        "content": f"问题: {question}\n\n参考知识:\n{context}\n\n请基于以上知识回答问题。"
                    }],
                    temperature=0.7,
                    max_tokens=1000
                )

            # 在新线程中运行
            result_holder = {"answer": None, "error": None}

            def run_in_new_loop():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(get_answer())
                    result_holder["answer"] = response
                    loop.close()
                except Exception as e:
                    result_holder["error"] = e

            thread = threading.Thread(target=run_in_new_loop)
            thread.start()
            thread.join(timeout=30)

            if result_holder["error"]:
                return "抱歉，生成回答时出现问题。"

            response = result_holder["answer"]
            return response["choices"][0]["message"]["content"]
        except:
            return "抱歉，生成回答时出现问题。"
