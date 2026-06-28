"""
AutoResearch 主程序 (V2)
强化置信度和学术规范性
"""
import argparse
import sys
from pathlib import Path

from .config import Config, RESEARCH_TEMPLATES
from .researcher_v2 import DeepSeekResearcher, SearchQuery, Source
from .reporter_v2 import ReportGenerator
from .planner import TaskPlanner, ResearchPlan


def print_banner():
    """打印欢迎横幅"""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║          AutoResearch V2  智能自动化研究工具               ║
    ║                                                            ║
    ║       基于 DeepSeek V4-Pro + WebSearch + 置信度强化        ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_research_types():
    """打印研究类型列表"""
    print("\n📚 可用的研究类型:")
    print("-" * 50)
    for key, template in RESEARCH_TEMPLATES.items():
        print(f"  [{key}] {template['description']}")
        print(f"       重点关注: {', '.join(template['focus_areas'])}")
        print()


def validate_config():
    """验证配置"""
    try:
        Config.validate()
        Config.display()
        return True
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print(f"\n请检查 .env 文件配置")
        return False


def execute_research_plan(plan: ResearchPlan):
    """执行研究计划"""
    researcher = DeepSeekResearcher()
    reporter = ReportGenerator()

    # 根据计划模式执行研究
    if plan.mode == "single":
        result = researcher.search(SearchQuery(query=plan.topic, depth=plan.depth))
        filepath = reporter.generate_single_report(result, plan.research_type)
        print_report_summary(filepath)

    elif plan.mode == "deep":
        results = researcher.research_deep(plan.topic, plan.aspects, plan.depth)
        filepath = reporter.generate_comprehensive_report(
            topic=plan.topic,
            results=results,
            research_type=plan.research_type,
            aspects=plan.aspects
        )
        print_report_summary(filepath)

    elif plan.mode == "interactive":
        results = []
        for result in researcher.research_iterative(plan.topic, plan.aspects):
            results.append(result)
        filepath = reporter.generate_comprehensive_report(
            topic=plan.topic,
            results=results,
            research_type=plan.research_type,
            aspects=plan.aspects
        )
        print_report_summary(filepath)


def research_single(topic: str, research_type: str = "通用", depth: str = "comprehensive"):
    """单次研究模式"""
    print(f"\n🎯 研究主题: {topic}")
    print(f"📝 研究类型: {research_type}")
    print(f"🔍 研究深度: {depth}")

    researcher = DeepSeekResearcher()
    reporter = ReportGenerator()

    query = SearchQuery(
        query=topic,
        depth=depth,
        require_sources=True
    )

    result = researcher.search(query)
    filepath = reporter.generate_single_report(result, research_type)

    print_report_summary(filepath)


def research_deep(topic: str, research_type: str = "通用"):
    """深度研究模式"""
    print(f"\n🎯 研究主题: {topic}")
    print(f"📝 研究类型: {research_type}")
    print(f"🔬 模式: 深度研究")

    researcher = DeepSeekResearcher()
    reporter = ReportGenerator()

    template = RESEARCH_TEMPLATES.get(research_type, RESEARCH_TEMPLATES["通用"])

    # 使用模板的关注领域作为研究维度
    aspects = template["focus_areas"]

    results = researcher.research_deep(topic, aspects)

    filepath = reporter.generate_comprehensive_report(
        topic=topic,
        results=results,
        research_type=research_type,
        aspects=aspects
    )

    print_report_summary(filepath)


def research_interactive(topic: str, research_type: str = "通用"):
    """交互式研究模式"""
    print(f"\n🎯 研究主题: {topic}")
    print(f"📝 研究类型: {research_type}")
    print(f"💬 模式: 交互式研究")

    researcher = DeepSeekResearcher()
    reporter = ReportGenerator()

    # 生成研究问题
    questions = researcher.generate_research_questions(topic, research_type)

    print(f"\n📋 生成的研究问题 ({len(questions)} 个):")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")

    # 执行迭代研究
    results = []
    for result in researcher.research_iterative(topic, questions):
        results.append(result)

    # 生成报告
    filepath = reporter.generate_comprehensive_report(
        topic=topic,
        results=results,
        research_type=research_type,
        aspects=questions
    )

    print_report_summary(filepath)


def research_questions(topic: str, questions: list, research_type: str = "通用"):
    """自定义问题研究模式"""
    print(f"\n🎯 研究主题: {topic}")
    print(f"📝 研究类型: {research_type}")
    print(f"❓ 模式: 自定义问题 ({len(questions)} 个)")

    researcher = DeepSeekResearcher()
    reporter = ReportGenerator()

    results = []
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"问题 {i}/{len(questions)}: {question}")
        print(f"{'='*60}")

        result = researcher.search(SearchQuery(
            query=f"{topic}: {question}",
            require_sources=True
        ))
        results.append(result)

    filepath = reporter.generate_comprehensive_report(
        topic=topic,
        results=results,
        research_type=research_type,
        aspects=questions
    )

    print_report_summary(filepath)


def print_report_summary(filepath: str):
    """打印报告摘要"""
    import os

    print("\n" + "=" * 60)
    print("📄 研究报告已生成")
    print("=" * 60)
    print(f"文件路径: {filepath}")
    print(f"文件大小: {os.path.getsize(filepath) / 1024:.1f} KB")
    print("=" * 60)
    print("\n💡 提示: 可以使用以下命令查看报告")
    print(f"   cat {filepath}" if sys.platform != "win32" else f"   type {filepath}")
    print()


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="AutoResearch V2 - 强化置信度的自动化研究工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自然语言模式 (自动分析，强化来源追踪)
  python -m autoresearch "帮我调研 RAG 技术的最新进展"

  # 深度研究
  python -m autoresearch "大模型微调" --mode deep --type 技术

  # 交互式研究
  python -m autoresearch "AI Agent 架构" --mode interactive

  # 自定义问题
  python -m autoresearch "MySQL 优化" -q "索引优化" "查询优化" "配置优化"

  # 列出研究类型
  python -m autoresearch --list-types

  # 使用 V2 版本 (强化置信度)
  python -m autoresearch_v2 "研究主题"
        """
    )

    parser.add_argument("topic", nargs="?", help="研究主题或自然语言描述")
    parser.add_argument("--mode", "-m", choices=["auto", "single", "deep", "interactive"],
                        default="auto", help="研究模式 (默认: auto，自动分析)")
    parser.add_argument("--type", "-t", choices=list(RESEARCH_TEMPLATES.keys()),
                        help="研究类型 (auto 模式下自动推断)")
    parser.add_argument("--questions", "-q", nargs="+", help="自定义研究问题")
    parser.add_argument("--depth", "-d", choices=["basic", "standard", "comprehensive"],
                        help="研究深度 (auto 模式下自动推断)")
    parser.add_argument("--list-types", action="store_true", help="列出所有研究类型")
    parser.add_argument("--config", action="store_true", help="显示当前配置")
    parser.add_argument("--no-confirm", action="store_true", help="跳过确认直接执行")
    parser.add_argument("--v2", action="store_true", help="使用 V2 版本 (强化置信度)")

    args = parser.parse_args()

    print_banner()

    # 处理特殊命令
    if args.list_types:
        print_research_types()
        return

    if args.config:
        if validate_config():
            return
        else:
            sys.exit(1)

    # 验证配置
    if not validate_config():
        sys.exit(1)

    # 验证主题
    if not args.topic:
        print("❌ 请提供研究主题")
        print("\n使用 --help 查看帮助信息")
        sys.exit(1)

    # 判断是否使用智能规划
    use_auto_plan = (
        args.mode == "auto" or
        (args.mode != "auto" and not args.type and not args.depth)
    )

    # 根据模式执行研究
    try:
        if use_auto_plan:
            # 使用智能规划模式
            print("\n🤖 智能规划模式")
            print("正在分析你的研究需求...")

            planner = TaskPlanner()
            plan = planner.plan(args.topic)
            TaskPlanner.display_plan(plan)

            if not args.no_confirm:
                if not TaskPlanner.confirm_plan():
                    print("\n⚠️ 研究已取消")
                    return

            execute_research_plan(plan)

        elif args.questions:
            research_questions(args.topic, args.questions, args.type or "通用")

        elif args.mode == "single":
            research_single(args.topic, args.type or "通用", args.depth or "comprehensive")

        elif args.mode == "deep":
            research_deep(args.topic, args.type or "通用")

        elif args.mode == "interactive":
            research_interactive(args.topic, args.type or "通用")

    except KeyboardInterrupt:
        print("\n\n⚠️ 研究被用户中断")
    except Exception as e:
        print(f"\n❌ 研究过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
