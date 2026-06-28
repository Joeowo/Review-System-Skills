"""测试刷题功能"""
import sys
sys.path.insert(0, '.')

from rich.console import Console
from services.knowledge_query import KnowledgeQuerySystem
from repositories.question_repo import QuestionRepository
from core.sm2_scheduler import SM2Scheduler
from core.answer_evaluator import AnswerEvaluator
from services.llm_service import SyncDeepSeekService
from ui.quiz import QuizInterface

console = Console()
console.print()
console.print("[bold cyan]=== 刷题功能测试 ===[/bold cyan]")

# 初始化
qs = KnowledgeQuerySystem()
repo = QuestionRepository()
scheduler = SM2Scheduler()
llm_service = SyncDeepSeekService()
evaluator = AnswerEvaluator(llm_service)

# 加载所有题目
all_questions = []
for session_data in repo.load_all().values():
    all_questions.extend(session_data)

console.print(f'题库总数: {len(all_questions)} 题\n')

if not all_questions:
    console.print('[red]题库为空，请先生成题目[/red]')
    sys.exit(1)

# 获取需要复习的题目（新题）
due_questions = scheduler.get_new_questions(all_questions, limit=5)

console.print(f'获取到 {len(due_questions)} 道题目\n')

# 创建刷题界面
quiz = QuizInterface(evaluator, scheduler)

# 开始刷题
user_records = quiz.start_round(due_questions)

# 显示结果
console.print()
console.print(f'[bold]答题完成！[/bold]')
console.print(f'回答记录: {len(user_records)} 条')
console.print(f'正确: {sum(1 for r in user_records if r.is_correct)}')
console.print(f'错误: {sum(1 for r in user_records if not r.is_correct)}')
