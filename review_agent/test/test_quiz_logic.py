"""测试刷题逻辑（非交互式）"""
import sys
sys.path.insert(0, '.')

from repositories.question_repo import QuestionRepository
from core.sm2_scheduler import SM2Scheduler
from core.answer_evaluator import AnswerEvaluator
from services.llm_service import SyncDeepSeekService

print('=== 刷题逻辑测试 ===\n')

# 初始化
repo = QuestionRepository()
scheduler = SM2Scheduler()
evaluator = AnswerEvaluator(SyncDeepSeekService())

# 加载题目
all_questions = []
for session_data in repo.load_all().values():
    all_questions.extend(session_data)

print(f'题库总数: {len(all_questions)} 题')

# 获取新题
due_questions = scheduler.get_new_questions(all_questions, limit=5)
print(f'获取到 {len(due_questions)} 道题目\n')

# 模拟答题
print('--- 模拟答题 ---\n')
user_records = []
sample_answers = [
    "组织一切生产、分配、流通和消费活动与关系的系统",
    "人类不必花费任何代价就可获得的资源",
    "人类必须花费一定的代价才能获得的资源",
    "人们想要或者希望得到的对各种物品的要求",
    "土地、资本、劳动力、企业家才能",
]

for i, (question, answer) in enumerate(zip(due_questions, sample_answers), 1):
    print(f'第 {i}/5 题')
    print(f'问题: {question.content}')
    print(f'你的答案: {answer}')

    # 评估答案
    evaluation = evaluator.evaluate(question, answer)

    print(f'AI评估: {"正确" if evaluation.is_correct else "错误"} (得分: {evaluation.score:.1%})')
    print(f'反馈: {evaluation.feedback[:60]}...' if len(evaluation.feedback) > 60 else f'反馈: {evaluation.feedback}')

    # 更新SM-2参数
    quality = 4 if evaluation.is_correct else 2
    scheduler.update_question(question, quality)

    user_record = {
        'question_id': question.id,
        'answer': answer,
        'is_correct': evaluation.is_correct,
        'score': evaluation.score,
    }
    user_records.append(user_record)
    print()

# 统计
correct_count = sum(1 for r in user_records if r['is_correct'])
print(f'=== 答题完成 ===')
print(f'总题数: {len(user_records)}')
print(f'正确: {correct_count}')
print(f'错误: {len(user_records) - correct_count}')
print(f'正确率: {correct_count/len(user_records)*100:.1f}%')

# 查看更新后的SM-2参数
print('\n=== SuperMemo-2 参数更新 ===')
for i, q in enumerate(due_questions, 1):
    print(f'题目 {i}: {q.content[:30]}...')
    print(f'  间隔: {q.interval} 天, 易记因子: {q.ease_factor:.2f}, 下次复习: {q.next_review_date.strftime("%Y-%m-%d")}')
