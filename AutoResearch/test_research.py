"""
AutoResearch 实际研究测试
使用 agent skills/workflow 优化主题
"""
import sys
sys.path.insert(0, 'D:/CODE/review_system_skills')

from autoresearch.researcher import DeepSeekResearcher, SearchQuery
from autoresearch.reporter import ReportGenerator
from autoresearch.planner import TaskPlanner, ResearchPlan
from autoresearch.config import Config

# 验证配置
try:
    Config.validate()
    print("✅ 配置验证成功\n")
except Exception as e:
    print(f"❌ 配置错误: {e}")
    sys.exit(1)

# 用户 prompt
user_prompt = """我觉得对于模型来说 讲清楚软工设计原则， 分析仓库，根据仓库情况应用合适的软工设计原则进行设计，编码开发都是不同的任务。经常给模型一个问题，它就只思考如何快速解决问题了，而不会考虑架构兼容，设计模式等问题。所以agent架构，workflow，任务上下文设计等工作就很重要。帮我调研目前用agent skills/workflow 优化agent框架/workflow本身的研究/benchmark 等等"""

print("=" * 60)
print("🚀 AutoResearch V2 实际研究测试")
print("=" * 60)

# 使用智能规划
print("\n🤖 智能规划模式")
print("正在分析你的研究需求...\n")

planner = TaskPlanner()
plan = planner.plan(user_prompt)

# 显示计划
TaskPlanner.display_plan(plan)

# 执行研究
print("\n" + "=" * 60)
print("开始执行研究...")
print("=" * 60)

researcher = DeepSeekResearcher()
reporter = ReportGenerator()

# 使用深度研究模式
results = researcher.research_deep(
    topic=plan.topic,
    aspects=plan.aspects,
    depth=plan.depth
)

# 生成报告
print("\n" + "=" * 60)
print("生成综合报告...")
print("=" * 60)

filepath = reporter.generate_comprehensive_report(
    topic=plan.topic,
    results=results,
    research_type=plan.research_type,
    aspects=plan.aspects
)

# 显示报告摘要
import os
print("\n" + "=" * 60)
print("📄 研究报告已生成")
print("=" * 60)
print(f"文件路径: {filepath}")
print(f"文件大小: {os.path.getsize(filepath) / 1024:.1f} KB")

# 统计来源信息
all_sources = set()
for result in results:
    for source in result.sources:
        all_sources.add(source.type)

print(f"\n📊 来源统计:")
print(f"  - 研究维度: {len(results)}")
print(f"  - 收集来源: {sum(len(r.sources) for r in results)} 个")
print(f"  - 来源类型: {', '.join(all_sources)}")

# 显示置信度分布
confidence_count = {"high": 0, "medium": 0, "low": 0}
for result in results:
    for source in result.sources:
        confidence_count[source.confidence] = confidence_count.get(source.confidence, 0) + 1

print(f"\n🎯 置信度分布:")
print(f"  - 高置信度: {confidence_count['high']} 个")
print(f"  - 中置信度: {confidence_count['medium']} 个")
print(f"  - 低置信度: {confidence_count['low']} 个")

print("\n" + "=" * 60)
print("✅ 研究完成")
print("=" * 60)
