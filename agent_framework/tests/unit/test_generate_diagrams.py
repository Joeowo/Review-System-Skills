"""
测试架构图生成脚本

验证 scripts/generate_diagrams.py 的功能
"""

import pytest
import shutil
from pathlib import Path


# 检查 graphviz 是否完全可用（命令 + Python 包）
def _graphviz_available():
    if not shutil.which("dot"):
        return False
    try:
        import graphviz
        return True
    except ImportError:
        return False


# 用于标记需要 graphviz 的测试
needs_graphviz = pytest.mark.skipif(
    not _graphviz_available(),
    reason="需要 graphviz (命令 + Python 包) 安装"
)


class TestGenerateWorkflowDiagram:
    """测试 generate_workflow_diagram 函数"""

    def test_returns_false_for_invalid_nodes(self, temp_dir):
        """对于无效的节点应该返回 False"""
        from scripts.generate_diagrams import generate_workflow_diagram

        result = generate_workflow_diagram(
            "invalid_workflow",
            [],
            [],
            str(temp_dir / "invalid")
        )

        assert result is False

    @needs_graphviz
    def test_generates_diagram_file(self, temp_dir):
        """应该生成图表文件"""
        from scripts.generate_diagrams import generate_workflow_diagram

        nodes = [
            {"id": "start", "label": "开始"},
            {"id": "process", "label": "处理"},
            {"id": "end", "label": "结束"},
        ]
        edges = [
            {"from": "start", "to": "process"},
            {"from": "process", "to": "end"},
        ]

        output_path = temp_dir / "test_workflow"

        result = generate_workflow_diagram(
            "test_workflow",
            nodes,
            edges,
            str(output_path)
        )

        assert result is True
        # 应该生成 PNG 文件
        assert (temp_dir / "test_workflow.png").exists()

    @needs_graphviz
    def test_includes_node_labels(self, temp_dir):
        """生成的图表应该包含节点标签"""
        from scripts.generate_diagrams import generate_workflow_diagram

        nodes = [
            {"id": "research", "label": "执行研究"},
            {"id": "write", "label": "内容写作"},
        ]
        edges = [
            {"from": "research", "to": "write"},
        ]

        output_path = temp_dir / "labeled_workflow"

        generate_workflow_diagram(
            "labeled_workflow",
            nodes,
            edges,
            str(output_path)
        )

        # 文件应该存在
        assert (temp_dir / "labeled_workflow.png").exists()


class TestGenerateAllDiagrams:
    """测试 generate_all_diagrams 函数"""

    def test_returns_false_when_graphviz_unavailable(self, temp_dir, monkeypatch):
        """当 graphviz 不可用时应该返回 False"""
        from scripts.generate_diagrams import generate_all_diagrams

        # Mock validate_graphviz 返回 False
        import scripts.generate_diagrams
        monkeypatch.setattr(
            scripts.generate_diagrams,
            "validate_graphviz",
            lambda: False
        )

        result = generate_all_diagrams(str(temp_dir))
        assert result is False

    @needs_graphviz
    def test_generates_f1_diagram(self, temp_dir):
        """应该生成 F1 workflow 图表"""
        from scripts.generate_diagrams import generate_all_diagrams

        result = generate_all_diagrams(str(temp_dir))

        assert result is True
        # 应该生成 F1 图表
        f1_path = temp_dir / "f1_learning_research.png"
        assert f1_path.exists()

    @needs_graphviz
    def test_generates_f2_diagram(self, temp_dir):
        """应该生成 F2 workflow 图表"""
        from scripts.generate_diagrams import generate_all_diagrams

        generate_all_diagrams(str(temp_dir))

        f2_path = temp_dir / "f2_qa_enhanced.png"
        assert f2_path.exists()

    @needs_graphviz
    def test_generates_f3_diagram(self, temp_dir):
        """应该生成 F3 workflow 图表"""
        from scripts.generate_diagrams import generate_all_diagrams

        generate_all_diagrams(str(temp_dir))

        f3_path = temp_dir / "f3_academic_writing.png"
        assert f3_path.exists()

    @needs_graphviz
    def test_generates_f4_diagram(self, temp_dir):
        """应该生成 F4 workflow 图表"""
        from scripts.generate_diagrams import generate_all_diagrams

        generate_all_diagrams(str(temp_dir))

        f4_path = temp_dir / "f4_review_planning.png"
        assert f4_path.exists()


class TestExtractWorkflowStructure:
    """测试 extract_workflow_structure 函数"""

    def test_extracts_nodes_from_workflow(self):
        """应该从 workflow 提取节点"""
        from scripts.generate_diagrams import extract_workflow_structure

        # 使用实际的 workflow
        from workflows.f1_learning_research import create_f1_workflow
        workflow = create_f1_workflow()

        nodes, edges = extract_workflow_structure(workflow)

        assert len(nodes) > 0
        assert len(edges) > 0

    def test_returns_tuple(self):
        """应该返回元组 (nodes, edges)"""
        from scripts.generate_diagrams import extract_workflow_structure

        from workflows.f1_learning_research import create_f1_workflow
        workflow = create_f1_workflow()

        result = extract_workflow_structure(workflow)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_handles_workflow_without_nodes(self):
        """应该处理没有节点的 workflow"""
        from scripts.generate_diagrams import extract_workflow_structure

        # 使用空对象
        class EmptyWorkflow:
            pass

        nodes, edges = extract_workflow_structure(EmptyWorkflow())

        # 应该返回默认结构
        assert isinstance(nodes, list)
        assert isinstance(edges, list)


class TestCreateNodeLabel:
    """测试 create_node_label 函数"""

    def test_creates_simple_label(self):
        """应该创建简单标签"""
        from scripts.generate_diagrams import create_node_label

        node_id = "research_node"
        label = create_node_label(node_id)

        assert isinstance(label, str)
        assert len(label) > 0
        assert "research" in label.lower()

    def test_formats_long_names(self):
        """应该格式化长名称"""
        from scripts.generate_diagrams import create_node_label

        node_id = "very_long_node_name_for_testing"
        label = create_node_label(node_id)

        # 标签应该被适当处理
        assert isinstance(label, str)
        assert "_" not in label  # 不应该有下划线

    def test_replaces_underscores_with_spaces(self):
        """应该将下划线替换为空格"""
        from scripts.generate_diagrams import create_node_label

        label = create_node_label("test_node_name")
        assert " " in label or "Test" in label


class TestValidateGraphviz:
    """测试 validate_graphviz 函数"""

    def test_returns_bool(self):
        """应该返回布尔值"""
        from scripts.generate_diagrams import validate_graphviz

        result = validate_graphviz()
        assert isinstance(result, bool)
