"""
F1 学习研究一体化 Workflow 测试

测试 F1 Workflow 的创建、编译和基本执行流程。

测试策略：
- 单元测试：使用 mock 验证节点行为
- 集成测试：真实调用 AutoResearch
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# 导入目标模块
from agent_framework.workflows.f1_learning_research import create_f1_workflow


class TestF1WorkflowCreation:
    """F1 Workflow 创建测试 - Tracer Bullet"""

    def test_f1_workflow_can_be_created(self):
        """F1 workflow 应该可以被创建和编译

        这是 tracer bullet 测试，验证整个流程可以端到端运行。
        """
        # When: 创建 workflow
        workflow = create_f1_workflow()

        # Then: workflow 应该被创建
        assert workflow is not None
        assert hasattr(workflow, "compile")

    def test_f1_workflow_has_entry_point(self):
        """F1 workflow 应该有正确的入口点"""
        # Given: workflow 被创建
        workflow = create_f1_workflow()

        # When: 编译它
        app = workflow.compile()

        # Then: 应该可以获取入口点信息
        assert app is not None

    def test_f1_workflow_has_all_nodes(self):
        """F1 workflow 应该包含所有必需的节点"""
        # 预期的节点列表
        expected_nodes = [
            "research",
            "research_confirmation",
            "extract_concepts",
            "breakdown_tasks",
            "grill_me",
            "grill_you",
            "evaluate_mastery",
            "save_progress",
        ]

        # Given: workflow 被创建
        workflow = create_f1_workflow()

        # When: 获取所有节点
        # LangGraph StateGraph 使用 builder
        if hasattr(workflow, "builder"):
            nodes = list(workflow.builder.nodes.keys())
        else:
            nodes = list(workflow.nodes.keys())

        # Then: 应该包含所有预期节点
        for node in expected_nodes:
            assert node in nodes, f"节点 {node} 未找到"


class TestResearchNode:
    """研究节点测试"""

    def test_research_node_updates_state_on_success(self):
        """研究节点成功时应该正确更新状态"""
        from agent_framework.workflows.f1_learning_research import research_node

        # Given: 初始状态和 mock 的 tool
        state = {
            "topic": "RAG 技术调研",
            "current_step": "start",
            "error_message": None,
        }

        with patch("agent_framework.workflows.f1_learning_research.research_single_tool") as mock_tool:
            mock_tool.invoke.return_value = "output/reports/rag_20250628.md"

            # When: 执行研究节点
            result = research_node(state)

            # Then: 状态应该被正确更新
            assert result["current_step"] == "research_complete"
            assert result["report_path"] == "output/reports/rag_20250628.md"
            assert result["error_message"] is None

    def test_research_node_handles_error(self):
        """研究节点应该正确处理错误"""
        from agent_framework.workflows import f1_learning_research
        from agent_framework.workflows.f1_learning_research import research_node

        # Given: 状态和模拟错误
        state = {"topic": "测试主题", "current_step": "start"}

        # Mock at the module level where it's used
        original_tool = f1_learning_research.research_single_tool

        # Create a mock that raises exception
        mock_tool = MagicMock()
        mock_tool.invoke.side_effect = Exception("网络错误")

        # Replace the tool
        f1_learning_research.research_single_tool = mock_tool

        try:
            # When: 执行研究节点
            result = research_node(state)

            # Then: 错误应该被捕获
            assert result["current_step"] == "research_failed"
            assert result["error_message"] is not None
            assert "网络错误" in result["error_message"]
            assert result["report_path"] is None
        finally:
            # Restore original
            f1_learning_research.research_single_tool = original_tool


class TestResearchConfirmationNode:
    """研究确认节点测试"""

    def test_confirmation_node_sets_awaiting_flag(self):
        """确认节点应该设置等待确认标志"""
        from agent_framework.workflows.f1_learning_research import research_confirmation_node

        # Given: 研究完成的状态
        state = {
            "topic": "测试主题",
            "report_path": "output/reports/test.md",
        }

        # When: 执行确认节点
        result = research_confirmation_node(state)

        # Then: 应该设置等待确认
        assert result["awaiting_confirmation"] is True
        assert "是否继续" in result["confirmation_prompt"]
        assert result["next_node"] == "extract_concepts"


class TestExtractConceptsNode:
    """概念提取节点测试"""

    def test_extract_concepts_parses_report(self):
        """概念提取节点应该解析报告文件"""
        from agent_framework.workflows.f1_learning_research import extract_concepts_node

        # Given: 有报告路径的状态
        state = {"report_path": "output/reports/test.md"}

        with patch("agent_framework.workflows.f1_learning_research.extract_concepts_from_report") as mock_extract:
            mock_extract.return_value = ["概念1", "概念2", "概念3"]

            # When: 执行概念提取
            result = extract_concepts_node(state)

            # Then: 概念应该被提取
            assert result["key_concepts"] == ["概念1", "概念2", "概念3"]
            assert result["current_step"] == "concepts_extracted"


class TestBreakdownTasksNode:
    """任务分解节点测试"""

    def test_breakdown_tasks_creates_task_list(self):
        """任务分解节点应该创建任务列表"""
        from agent_framework.workflows.f1_learning_research import breakdown_tasks_node

        # Given: 有概念列表的状态
        state = {
            "key_concepts": ["概念1", "概念2"],
            "session_path": "/tmp/test_session"
        }

        with patch("agent_framework.workflows.f1_learning_research.initialize_task_md") as mock_init:
            # When: 执行任务分解
            result = breakdown_tasks_node(state)

            # Then: 任务应该被创建
            assert len(result["tasks"]) == 2
            assert result["current_task_id"] == "task_1"
            assert result["current_step"] == "tasks_breakdown"
            mock_init.assert_called_once()


class TestGrillingLoop:
    """Grilling 循环测试"""

    def test_grill_me_node_generates_questions(self):
        """grill-me 节点应该生成问题"""
        from agent_framework.workflows.f1_learning_research import grill_me_node

        # Given: 有当前任务的状态
        state = {
            "current_task_id": "task_1",
            "session_path": "/tmp/test_session"
        }

        with patch("agent_framework.workflows.f1_learning_research.GrillMeAdapter") as mock_adapter_class:
            mock_adapter = mock_adapter_class.return_value
            mock_adapter.generate_questions.return_value = ["问题1", "问题2"]

            # When: 执行 grill-me
            result = grill_me_node(state)

            # Then: 问题应该被生成
            assert len(result["current_questions"]) == 2
            assert result["current_step"] == "grilling_me"

    def test_evaluate_mastery_checks_completion(self):
        """评估节点应该检查掌握程度"""
        from agent_framework.workflows.f1_learning_research import evaluate_mastery_node

        # Given: 有答案的状态
        state = {"answers": ["答案1", "答案2", "答案3"]}

        # When: 评估掌握程度
        result = evaluate_mastery_node(state)

        # Then: 应该设置掌握级别
        assert result["mastery_level"] in ["completed", "continuing"]
        assert result["current_step"] == "mastery_evaluated"

    def test_grilling_loop_exits_when_mastered(self):
        """Grilling 循环应该在掌握时退出"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 掌握的状态
        state = {"mastery_level": "completed"}

        # When: 检查是否应该继续
        should_continue = check_mastery(state)

        # Then: 应该退出到保存进度
        assert should_continue == "completed"


class TestSaveProgressNode:
    """保存进度节点测试"""

    def test_save_progress_updates_task_md(self):
        """保存进度节点应该更新 Task.md"""
        from agent_framework.workflows.f1_learning_research import save_progress_node

        # Given: 要完成的任务
        state = {
            "current_task_id": "task_1",
            "round": 2,
            "session_path": "/tmp/test_session"
        }

        with patch("agent_framework.workflows.f1_learning_research.AdvanceTaskAdapter") as mock_adapter_class:
            mock_adapter = mock_adapter_class.return_value

            # When: 保存进度
            result = save_progress_node(state)

            # Then: 任务应该被标记完成
            mock_adapter.complete_task.assert_called_once_with("task_1", notes="完成 2 轮学习")
            assert result["current_step"] == "progress_saved"


class TestExtractConceptsFromReport:
    """extract_concepts_from_report 辅助函数测试"""

    def test_extract_concepts_from_basic_report(self):
        """应该从基础报告中提取核心概念"""
        from agent_framework.workflows.f1_learning_research import extract_concepts_from_report
        import tempfile
        import os

        # Given: 一个包含概念的研究报告
        report_content = """# RAG 技术调研 研究报告

## 研究概述

技术调研，了解最新技术发展

## 关键发现

- RAG 是一种检索 + 生成的混合框架
- 检索增强生成可缓解幻觉问题

## 1. 概念与背景

**定义**
RAG 是一种"检索 + 生成"的混合框架

**核心动机**
- 补足 LLM 的静态知识
- 缓解幻觉

## 2. 技术架构

### 2.1 朴素 RAG
经典的检索-阅读流水线

### 2.2 高级 RAG
增加检索前预处理和检索后优化

### 2.3 模块化 RAG
可组合的功能模块

## 3. 技术栈

- 分块策略
- 嵌入模型
- 检索算法
- 重排序
- 提示组织
"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(report_content)
            temp_path = f.name

        try:
            # When: 从报告中提取概念
            concepts = extract_concepts_from_report(temp_path)

            # Then: 应该提取出关键概念
            assert len(concepts) > 0
            # 应该包含核心概念
            assert any("RAG" in str(c) or "检索" in str(c) for c in concepts)
            # 概念应该是字符串或字典格式
            assert all(isinstance(c, (str, dict)) for c in concepts)

        finally:
            # 清理临时文件
            os.unlink(temp_path)

    def test_extract_concepts_handles_empty_report(self):
        """应该处理空报告"""
        from agent_framework.workflows.f1_learning_research import extract_concepts_from_report
        import tempfile
        import os

        # Given: 一个空报告
        report_content = "# 空报告\n\n没有内容"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(report_content)
            temp_path = f.name

        try:
            # When: 从空报告中提取概念
            concepts = extract_concepts_from_report(temp_path)

            # Then: 应该返回空列表
            assert concepts == []

        finally:
            os.unlink(temp_path)

    def test_extract_concepts_handles_missing_file(self):
        """应该处理文件不存在的情况"""
        from agent_framework.workflows.f1_learning_research import extract_concepts_from_report
        import pytest

        # Given: 一个不存在的文件路径
        nonexistent_path = "/tmp/nonexistent_report_12345.md"

        # When: 尝试从不存在的文件中提取概念
        # Then: 应该返回空列表或抛出异常
        # 这里选择返回空列表，保持函数健壮性
        concepts = extract_concepts_from_report(nonexistent_path)
        assert concepts == []

    def test_extract_concepts_returns_structured_format(self):
        """应该返回结构化的概念格式"""
        from agent_framework.workflows.f1_learning_research import extract_concepts_from_report
        import tempfile
        import os

        # Given: 包含明确概念定义的报告
        report_content = """# 测试报告

## 1. 核心概念

### 概念1：向量嵌入
将文本转换为数值向量的技术

### 概念2：语义检索
基于语义相似度的检索方法

### 概念3：重排序
对检索结果重新排序的过程
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(report_content)
            temp_path = f.name

        try:
            # When: 提取概念
            concepts = extract_concepts_from_report(temp_path)

            # Then: 概念应该有合理的结构
            # 可能的格式：
            # - 字符串列表: ["概念1", "概念2"]
            # - 字典列表: [{"name": "概念1", "description": "..."}, ...]
            assert isinstance(concepts, list)
            if concepts:
                # 检查第一个元素的结构
                first = concepts[0]
                assert isinstance(first, (str, dict))

        finally:
            os.unlink(temp_path)


class TestInitializeTaskMd:
    """initialize_task_md 辅助函数测试"""

    def test_initialize_task_md_creates_file(self):
        """应该创建 Task.md 文件"""
        from agent_framework.workflows.f1_learning_research import initialize_task_md
        import tempfile
        from pathlib import Path

        # Given: 临时会话目录和任务列表
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks = [
                {"id": "task_1", "concept": "RAG 检索增强生成", "status": "pending", "round": 0},
                {"id": "task_2", "concept": "向量嵌入", "status": "pending", "round": 0},
                {"id": "task_3", "concept": "语义检索", "status": "pending", "round": 0},
            ]

            # When: 初始化 Task.md
            initialize_task_md(temp_dir, tasks)

            # Then: 文件应该被创建
            task_md_path = Path(temp_dir) / "Task.md"
            assert task_md_path.exists()

            # 文件内容应该包含任务信息
            content = task_md_path.read_text(encoding="utf-8")
            assert "task_1" in content
            assert "RAG 检索增强生成" in content
            assert "task_2" in content
            assert "task_3" in content

    def test_initialize_task_md_overwrites_existing(self):
        """应该覆盖已存在的 Task.md"""
        from agent_framework.workflows.f1_learning_research import initialize_task_md
        import tempfile
        from pathlib import Path

        # Given: 已有 Task.md 文件
        with tempfile.TemporaryDirectory() as temp_dir:
            task_md_path = Path(temp_dir) / "Task.md"
            task_md_path.write_text("# 旧任务\n\n旧的测试内容", encoding="utf-8")

            tasks = [
                {"id": "task_1", "concept": "新概念", "status": "pending", "round": 0},
            ]

            # When: 重新初始化
            initialize_task_md(temp_dir, tasks)

            # Then: 旧内容应该被覆盖
            content = task_md_path.read_text(encoding="utf-8")
            assert "旧任务" not in content
            assert "新概念" in content

    def test_initialize_task_md_handles_empty_tasks(self):
        """应该处理空任务列表"""
        from agent_framework.workflows.f1_learning_research import initialize_task_md
        import tempfile
        from pathlib import Path

        # Given: 空任务列表
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks = []

            # When: 初始化
            initialize_task_md(temp_dir, tasks)

            # Then: 文件仍然应该被创建，但内容为空或提示无任务
            task_md_path = Path(temp_dir) / "Task.md"
            assert task_md_path.exists()
            content = task_md_path.read_text(encoding="utf-8")
            # 可以是完全空的，或者包含"无任务"提示
            assert len(content) < 200  # 内容应该很少

    def test_initialize_task_md_format(self):
        """应该生成正确的 Markdown 格式"""
        from agent_framework.workflows.f1_learning_research import initialize_task_md
        import tempfile
        from pathlib import Path

        # Given: 任务列表
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks = [
                {"id": "task_1", "concept": "测试概念", "status": "pending", "round": 0},
            ]

            # When: 生成 Task.md
            initialize_task_md(temp_dir, tasks)

            # Then: 应该包含 Markdown 标题
            content = (Path(temp_dir) / "Task.md").read_text(encoding="utf-8")
            assert "# Task" in content or "# 学习任务" in content

    def test_initialize_task_md_creates_directory_if_needed(self):
        """如果目录不存在应该创建"""
        from agent_framework.workflows.f1_learning_research import initialize_task_md
        import tempfile
        from pathlib import Path

        # Given: 一个不存在的子目录路径
        with tempfile.TemporaryDirectory() as temp_dir:
            sub_dir = Path(temp_dir) / "sub_session"

            tasks = [{"id": "task_1", "concept": "测试", "status": "pending", "round": 0}]

            # When: 初始化（应该创建目录）
            initialize_task_md(str(sub_dir), tasks)

            # Then: 目录和文件应该被创建
            assert sub_dir.exists()
            assert (sub_dir / "Task.md").exists()


class TestShouldContinueResearch:
    """should_continue_research 条件边函数测试"""

    def test_should_continue_research_when_user_approves(self):
        """用户确认应该继续时返回 continue"""
        from agent_framework.workflows.f1_learning_research import should_continue_research

        # Given: 用户确认继续
        state = {
            "user_confirmation": "继续",
            "report_path": "output/reports/test.md"
        }

        # When: 检查是否继续
        result = should_continue_research(state)

        # Then: 应该返回 continue
        assert result == "continue"

    def test_should_continue_research_when_user_rethinks(self):
        """用户要求重新研究时返回 rethink"""
        from agent_framework.workflows.f1_learning_research import should_continue_research

        # Given: 用户要求重新研究
        state = {
            "user_confirmation": "重新研究",
            "report_path": "output/reports/test.md"
        }

        # When: 检查是否继续
        result = should_continue_research(state)

        # Then: 应该返回 rethink
        assert result == "rethink"

    def test_should_continue_research_default_to_continue(self):
        """没有明确确认时默认继续"""
        from agent_framework.workflows.f1_learning_research import should_continue_research

        # Given: 没有用户确认状态
        state = {
            "report_path": "output/reports/test.md"
        }

        # When: 检查是否继续
        result = should_continue_research(state)

        # Then: 默认应该继续
        assert result == "continue"

    def test_should_continue_research_varied_confirmations(self):
        """支持多种确认表达方式"""
        from agent_framework.workflows.f1_learning_research import should_continue_research

        # 支持继续的表达
        continue_phrases = ["继续", "OK", "好的", "确认", "yes", "Yes", "确认继续"]

        for phrase in continue_phrases:
            state = {"user_confirmation": phrase, "report_path": "output/reports/test.md"}
            result = should_continue_research(state)
            assert result == "continue", f"Failed for phrase: {phrase}"

        # 支持重新研究的表达
        rethink_phrases = ["重新研究", "重新", "再研究一次", "不满意", "重做"]

        for phrase in rethink_phrases:
            state = {"user_confirmation": phrase, "report_path": "output/reports/test.md"}
            result = should_continue_research(state)
            assert result == "rethink", f"Failed for phrase: {phrase}"

    def test_should_continue_research_case_insensitive(self):
        """应该对用户输入不区分大小写"""
        from agent_framework.workflows.f1_learning_research import should_continue_research

        # Given: 大写的确认
        state = {
            "user_confirmation": "YES",
            "report_path": "output/reports/test.md"
        }

        # When: 检查
        result = should_continue_research(state)

        # Then: 应该继续
        assert result == "continue"


class TestCheckMastery:
    """check_mastery 条件边函数测试"""

    def test_check_mastery_completed_with_sufficient_rounds(self):
        """完成足够轮次后应该标记为已完成"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 完成了多轮学习
        state = {
            "mastery_level": "continuing",
            "round": 3,
            "answers": ["答案1", "答案2", "答案3"]
        }

        # When: 检查掌握程度
        result = check_mastery(state)

        # Then: 应该标记为完成
        assert result == "completed"

    def test_check_mastery_continues_with_insufficient_rounds(self):
        """轮次不足时应该继续学习"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 只完成了 1 轮
        state = {
            "mastery_level": "continuing",
            "round": 1,
            "answers": ["答案1"]
        }

        # When: 检查掌握程度
        result = check_mastery(state)

        # Then: 应该继续
        assert result == "continue"

    def test_check_mastery_respects_explicit_completion(self):
        """用户明确表示完成时应该结束"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 用户明确表示完成
        state = {
            "mastery_level": "completed",
            "user_confirms_completion": True,
            "round": 1
        }

        # When: 检查掌握程度
        result = check_mastery(state)

        # Then: 应该完成
        assert result == "completed"

    def test_check_mastery_with_quality_score(self):
        """应该考虑答案质量分数"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 高质量分数
        state = {
            "mastery_level": "continuing",
            "round": 2,
            "quality_score": 0.85  # 85% 正确率
        }

        # When: 检查掌握程度
        result = check_mastery(state)

        # Then: 高质量分数应该可以完成
        assert result == "completed"

    def test_check_mastery_low_quality_requires_more_rounds(self):
        """低质量分数需要更多轮次"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 低质量分数
        state = {
            "mastery_level": "continuing",
            "round": 2,
            "quality_score": 0.5  # 50% 正确率
        }

        # When: 检查掌握程度
        result = check_mastery(state)

        # Then: 应该继续学习
        assert result == "continue"

    def test_check_mastery_default_behavior(self):
        """默认情况下应该合理判断"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 最小状态
        state = {
            "round": 2,
            "answers": ["答案1", "答案2"]
        }

        # When: 检查
        result = check_mastery(state)

        # Then: 2 轮应该足够
        assert result == "completed"


class TestSyncToPersistence:
    """sync_to_persistence 辅助函数测试"""

    def test_sync_to_persistence_writes_context_md(self):
        """应该将术语同步到 CONTEXT.md"""
        from agent_framework.core.state import sync_to_persistence
        import tempfile
        from pathlib import Path

        # Given: 有缓存术语的状态
        with tempfile.TemporaryDirectory() as session_dir:
            state = {
                "session_path": session_dir,
                "cached_terminology": {
                    "RAG": "检索增强生成",
                    "向量嵌入": "将文本转换为向量"
                }
            }

            # When: 同步到持久层
            sync_to_persistence(state)

            # Then: CONTEXT.md 应该被创建
            context_path = Path(session_dir) / "CONTEXT.md"
            assert context_path.exists()

            # 内容应该包含术语
            content = context_path.read_text(encoding="utf-8")
            assert "RAG" in content
            assert "检索增强生成" in content

    def test_sync_to_persistence_writes_task_md(self):
        """应该将任务进度同步到 Task.md"""
        from agent_framework.core.state import sync_to_persistence
        import tempfile
        from pathlib import Path

        # Given: 有缓存任务进度的状态
        with tempfile.TemporaryDirectory() as session_dir:
            state = {
                "session_path": session_dir,
                "cached_task_progress": [
                    {"id": "task_1", "status": "completed", "round": 3},
                    {"id": "task_2", "status": "in_progress", "round": 1}
                ]
            }

            # When: 同步到持久层
            sync_to_persistence(state)

            # Then: Task.md 应该包含任务进度
            task_path = Path(session_dir) / "Task.md"
            content = task_path.read_text(encoding="utf-8")
            assert "task_1" in content
            assert "completed" in content

    def test_sync_to_persistence_handles_missing_cache(self):
        """应该处理缺少缓存的情况"""
        from agent_framework.core.state import sync_to_persistence
        import tempfile
        from pathlib import Path

        # Given: 没有缓存的状态
        with tempfile.TemporaryDirectory() as session_dir:
            state = {
                "session_path": session_dir,
                "cached_terminology": {},
                "cached_task_progress": []
            }

            # When: 同步（不应该抛出异常）
            sync_to_persistence(state)

            # Then: 文件仍然应该被创建
            context_path = Path(session_dir) / "CONTEXT.md"
            task_path = Path(session_dir) / "Task.md"
            assert context_path.exists()
            assert task_path.exists()

    def test_sync_to_persistence_uses_atomic_write(self):
        """应该使用原子写入策略"""
        from agent_framework.core.state import sync_to_persistence
        import tempfile
        from pathlib import Path
        import time

        # Given: 状态
        with tempfile.TemporaryDirectory() as session_dir:
            state = {
                "session_path": session_dir,
                "cached_terminology": {"测试": "测试术语"},
                "cached_task_progress": [{"id": "task_1", "status": "pending"}]
            }

            # When: 同步
            sync_to_persistence(state)

            # Then: 文件应该完整写入（可以通过读取验证）
            context_path = Path(session_dir) / "CONTEXT.md"
            content = context_path.read_text(encoding="utf-8")
            # 应该是完整的 Markdown，而不是截断的
            assert content.startswith("#") or "测试" in content

    def test_sync_to_persistence_merges_with_existing(self):
        """应该与现有内容合并而不是完全覆盖"""
        from agent_framework.core.state import sync_to_persistence
        import tempfile
        from pathlib import Path

        # Given: 已有 CONTEXT.md 文件
        with tempfile.TemporaryDirectory() as session_dir:
            context_path = Path(session_dir) / "CONTEXT.md"
            context_path.write_text("# Session 上下文\n\n已有内容", encoding="utf-8")

            state = {
                "session_path": session_dir,
                "cached_terminology": {"新术语": "新定义"}
            }

            # When: 同步
            sync_to_persistence(state)

            # Then: 新内容应该被添加，而不是完全覆盖
            # （具体合并策略取决于实现）
            content = context_path.read_text(encoding="utf-8")
            assert "新术语" in content or "新定义" in content
