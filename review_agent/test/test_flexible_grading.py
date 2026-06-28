"""
测试宽容性判题系统
验证AI是否能够容忍笔误、顺序差异、同义表述等
"""
import sys
sys.path.insert(0, '.')

from services.llm_service import SyncDeepSeekService
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
console.print()
console.print("[bold cyan]=== 宽容性判题测试 ===[/bold cyan]\n")

# 初始化LLM服务
llm_service = SyncDeepSeekService()

# 测试用例：涵盖各种常见的学生表述差异
test_cases = [
    {
        "name": "单位简写 (300w vs 300万)",
        "question": "某项目年利润100万元，折旧200万元，请计算年净现金流量。",
        "correct_answer": "年净现金流量 = 利润 + 折旧 = 100 + 200 = 300万元",
        "user_answer": "年净现金流量 = 利润 + 折旧 = 100 + 200 = 300w元",
        "expected_correct": True,
    },
    {
        "name": "计算步骤顺序不同",
        "question": "某项目初始投资1000万元，经营期每年净现金流量300万元，请计算静态投资回收期。",
        "correct_answer": "静态投资回收期 = 初始投资 / 年净现金流量 = 1000 / 300 ≈ 3.33年",
        "user_answer": "年净现金流量是300万元，初始投资1000万元，所以回收期 = 1000/300 = 3.33年",
        "expected_correct": True,
    },
    {
        "name": "同义表述",
        "question": "什么是机会成本？",
        "correct_answer": "机会成本是指资源用于某一用途后放弃的其他用途所能获得的最大收益。",
        "user_answer": "机会成本就是选择一个选项时，放弃的其他选项里最好的那个收益",
        "expected_correct": True,
    },
    {
        "name": "轻微笔误",
        "question": "净现值的计算公式是什么？",
        "correct_answer": "NPV = Σ(CFt / (1+r)^t)，其中CFt为第t期净现金流量，r为折现率",
        "user_answer": "NPV = Σ(CFt / (1+r)^t)，CFt是第t期净现金流，r是折现率",
        "expected_correct": True,
    },
    {
        "name": "核心概念错误（应判错）",
        "question": "什么是机会成本？",
        "correct_answer": "机会成本是指资源用于某一用途后放弃的其他用途所能获得的最大收益。",
        "user_answer": "机会成本是指投资所花费的实际货币成本。",
        "expected_correct": False,
    },
    {
        "name": "万元/万/万元混用",
        "question": "计算年净现金流量：利润100万，折旧200万",
        "correct_answer": "年净现金流量 = 100 + 200 = 300万元",
        "user_answer": "300万",
        "expected_correct": True,
    },
]

# 运行测试
results = []
console.print("[dim]正在运行测试...[/dim]\n")

for i, case in enumerate(test_cases, 1):
    console.print(f"[dim]测试 {i}/{len(test_cases)}: {case['name']}[/dim]")

    result = llm_service.evaluate_answer(
        question=case["question"],
        user_answer=case["user_answer"],
        correct_answer=case["correct_answer"]
    )

    results.append({
        "name": case["name"],
        "is_correct": result.get("is_correct", False),
        "score": result.get("score", 0),
        "feedback": result.get("feedback", ""),
        "expected": case["expected_correct"],
        "pass": result.get("is_correct", False) == case["expected_correct"],
    })

# 显示结果
console.print()
console.print("[bold]测试结果汇总[/bold]\n")

# 创建结果表格
table = Table(show_header=True, header_style="bold magenta")
table.add_column("测试用例", style="cyan")
table.add_column("预期", style="yellow")
table.add_column("实际", style="yellow")
table.add_column("得分", style="green")
table.add_column("状态", style="bold")

for r in results:
    expected_icon = "✓" if r["expected"] else "✗"
    actual_icon = "✓" if r["is_correct"] else "✗"
    status = "[green]通过[/green]" if r["pass"] else "[red]失败[/red]"

    table.add_row(
        r["name"],
        expected_icon,
        actual_icon,
        f"{r['score']:.2f}",
        status
    )

console.print(table)

# 统计
total = len(results)
passed = sum(1 for r in results if r["pass"])
console.print()
console.print(f"总计: {passed}/{total} 通过")

# 显示失败案例的详细反馈
if passed < total:
    console.print()
    console.print("[bold red]失败案例详情:[/bold red]")
    for r in results:
        if not r["pass"]:
            console.print()
            console.print(Panel(
                f"[yellow]预期: {'正确' if r['expected'] else '错误'}[/yellow]\n"
                f"[yellow]实际: {'正确' if r['is_correct'] else '错误'} (得分: {r['score']:.2f})[/yellow]\n\n"
                f"[dim]反馈: {r['feedback']}[/dim]",
                title=r["name"],
                border_style="red"
            ))
else:
    console.print()
    console.print("[green]所有测试通过！✓[/green]")

console.print()
