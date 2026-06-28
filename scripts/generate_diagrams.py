"""
架构图生成脚本

使用 Graphviz 生成 workflow 架构图
"""

import sys
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Any

# 添加 agent_framework 到路径
framework_root = Path(__file__).parent.parent / "agent_framework"
if str(framework_root) not in sys.path:
    sys.path.insert(0, str(framework_root))


def validate_graphviz() -> bool:
    """验证 graphviz 是否可用

    Returns:
        graphviz 是否可用
    """
    return shutil.which("dot") is not None


def create_node_label(node_id: str) -> str:
    """创建节点标签

    Args:
        node_id: 节点ID

    Returns:
        格式化的标签
    """
    # 移除 _node 后缀
    label = node_id.replace("_node", "")
    # 转换为可读格式
    label = label.replace("_", " ").title()
    return label


def extract_workflow_structure(workflow: Any) -> Tuple[List[Dict], List[Dict]]:
    """提取 workflow 结构

    Args:
        workflow: LangGraph workflow 对象

    Returns:
        (节点列表, 边列表)
    """
    nodes = []
    edges = []

    try:
        # LangGraph StateGraph 使用 builder
        if hasattr(workflow, "builder"):
            graph = workflow.builder
        else:
            graph = workflow

        # 提取节点
        if hasattr(graph, "nodes"):
            for node_id in graph.nodes.keys():
                nodes.append({
                    "id": node_id,
                    "label": create_node_label(node_id)
                })

        # 提取边
        if hasattr(graph, "edges"):
            for edge in graph.edges:
                edges.append({
                    "from": edge[0] if isinstance(edge, tuple) else str(edge),
                    "to": edge[1] if len(edge) > 1 else ""
                })

        # 如果没有提取到节点，尝试使用 add_node 的记录
        if not nodes:
            # 默认节点列表
            nodes = [
                {"id": "start", "label": "Start"},
                {"id": "end", "label": "End"}
            ]

    except Exception as e:
        print(f"Warning: Could not extract workflow structure: {e}")

    return nodes, edges


def generate_workflow_diagram(
    workflow_name: str,
    nodes: List[Dict],
    edges: List[Dict],
    output_path: str,
    format: str = "png"
) -> bool:
    """生成 workflow 架构图

    Args:
        workflow_name: workflow 名称
        nodes: 节点列表 [{"id": "...", "label": "..."}]
        edges: 边列表 [{"from": "...", "to": "...", "label": "..."}]
        output_path: 输出路径（不含扩展名）
        format: 输出格式

    Returns:
        是否成功生成
    """
    if not nodes:
        return False

    try:
        # 检查 graphviz 是否可用
        if not validate_graphviz():
            print("Warning: Graphviz not found. Skipping diagram generation.")
            print("Install Graphviz from: https://graphviz.org/download/")
            return False

        import graphviz

        dot = graphviz.Digraph(comment=workflow_name)

        # 设置图表属性
        dot.attr(rankdir="LR")
        dot.attr("node", shape="box", style="rounded")

        # 添加节点
        for node in nodes:
            node_id = node.get("id", "")
            label = node.get("label", node_id)
            dot.node(node_id, label)

        # 添加边
        for edge in edges:
            from_node = edge.get("from", "")
            to_node = edge.get("to", "")
            label = edge.get("label", "")

            if from_node and to_node:
                if label:
                    dot.edge(from_node, to_node, label=label)
                else:
                    dot.edge(from_node, to_node)

        # 渲染图表
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        dot.render(
            str(output_file),
            format=format,
            cleanup=True
        )

        return True

    except ImportError:
        print("Warning: graphviz Python package not installed.")
        print("Install with: pip install graphviz")
        return False
    except Exception as e:
        print(f"Error generating diagram: {e}")
        return False


def generate_all_diagrams(output_dir: str) -> bool:
    """生成所有 workflow 的架构图

    Args:
        output_dir: 输出目录

    Returns:
        是否至少生成一个图表
    """
    try:
        from workflows.f1_learning_research import create_f1_workflow
        from workflows.f2_qa_enhanced import create_f2_workflow
        from workflows.f3_academic_writing import create_f3_workflow
        from workflows.f4_review_planning import create_f4_workflow

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        workflows = [
            ("f1_learning_research", create_f1_workflow()),
            ("f2_qa_enhanced", create_f2_workflow()),
            ("f3_academic_writing", create_f3_workflow()),
            ("f4_review_planning", create_f4_workflow()),
        ]

        generated_count = 0

        for name, workflow in workflows:
            nodes, edges = extract_workflow_structure(workflow)

            output_file = output_path / name

            if generate_workflow_diagram(name, nodes, edges, str(output_file)):
                generated_count += 1
                print(f"✓ Generated: {name}.png")
            else:
                print(f"✗ Skipped: {name}")

        return generated_count > 0

    except ImportError as e:
        print(f"Error importing workflows: {e}")
        return False
    except Exception as e:
        print(f"Error generating diagrams: {e}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成 workflow 架构图")
    parser.add_argument(
        "--output",
        default="docs/architecture",
        help="输出目录"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="生成所有 workflow 的图表"
    )
    parser.add_argument(
        "--workflow",
        help="指定 workflow 名称"
    )

    args = parser.parse_args()

    if args.all:
        success = generate_all_diagrams(args.output)
        if success:
            print(f"\n✓ 架构图已生成到: {args.output}")
        else:
            print("\n✗ 未生成任何图表")
            sys.exit(1)
    elif args.workflow:
        # 单个 workflow
        try:
            module = __import__(f"workflows.{args.workflow}")
            workflow_func = getattr(module, f"create_{args.workflow}")
            workflow = workflow_func()

            nodes, edges = extract_workflow_structure(workflow)
            output_path = Path(args.output) / args.workflow

            if generate_workflow_diagram(args.workflow, nodes, edges, str(output_path)):
                print(f"✓ 生成图表: {output_path}.png")
            else:
                print(f"✗ 生成失败: {args.workflow}")
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
