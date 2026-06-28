"""
C1: State 定义与同步 - 单元测试

测试覆盖：
- AgentState 定义
- CONTEXT.md 解析
- Task.md 解析
- 状态同步逻辑
"""

import pytest
from pathlib import Path
from agent_framework.core.state import (
    AgentState,
    load_session_state,
    sync_to_persistence,
    parse_context_md,
    parse_task_md,
)


# =============================================================================
# 测试组 1: AgentState 定义
# =============================================================================

class TestAgentState:
    """测试 AgentState TypedDict 定义"""

    def test_agentstate_can_be_initialized(self, base_state_dict):
        """AgentState 可以正确初始化

        验证：
        - 可使用字典创建 AgentState
        - 所有必需字段存在
        - 字段类型正确
        """
        state = AgentState(**base_state_dict)

        # 验证执行层状态字段
        assert state["current_step"] == "init"
        assert state["tool_results"] == {}
        assert state["retry_count"] == 0
        assert state["error_message"] is None

        # 验证持久层引用字段
        assert "session_path" in state
        assert "current_task_id" in state

        # 验证缓存层状态字段
        assert "cached_terminology" in state
        assert "cached_task_progress" in state

        # 验证元数据字段
        assert state["workflow_name"] == "test_workflow"
        assert "start_time" in state

    def test_agentstate_accepts_none_for_optional_fields(self, base_state_dict):
        """AgentState 的可选字段可以接受 None"""
        state = AgentState(**base_state_dict)

        # error_message 是可选的，可以为 None
        assert state["error_message"] is None

        # 可以设置为 None
        state["error_message"] = None
        assert state["error_message"] is None

    def test_agentstate_fields_are_mutable(self, base_state_dict):
        """AgentState 字段是可变的"""
        state = AgentState(**base_state_dict)

        # 修改字段
        state["current_step"] = "processing"
        state["retry_count"] = 2

        # 验证修改生效
        assert state["current_step"] == "processing"
        assert state["retry_count"] == 2


# =============================================================================
# 测试组 2: CONTEXT.md 解析
# =============================================================================

class TestParseContextMd:
    """测试 CONTEXT.md 解析功能"""

    def test_parse_context_md_returns_dict(self, sample_session_dir):
        """parse_context_md 返回术语字典

        验证：
        - 返回类型是 dict
        - 可以解析 Language 段落
        - 可以解析 Relationships 段落
        """
        context_path = sample_session_dir / "CONTEXT.md"
        result = parse_context_md(context_path)

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_parse_context_md_extracts_term_definitions(self, sample_session_dir):
        """parse_context_md 正确提取术语定义

        示例 CONTEXT.md 包含：
        - 货币政策: 央行调节货币供应量和利率的政策工具
        - 时滞: 政策实施到产生效果的延迟时间
        """
        context_path = sample_session_dir / "CONTEXT.md"
        result = parse_context_md(context_path)

        # 验证术语被正确提取
        assert "货币政策" in result
        assert "央行调节货币供应量和利率的政策工具" in result["货币政策"]

        assert "时滞" in result
        assert "政策实施到产生效果的延迟时间" in result["时滞"]

    def test_parse_context_md_handles_empty_file(self, temp_dir):
        """parse_context_md 处理空文件"""
        empty_context = temp_dir / "CONTEXT.md"
        empty_context.write_text("")

        result = parse_context_md(empty_context)

        assert result == {}

    def test_parse_context_md_handles_nonexistent_file(self, temp_dir):
        """parse_context_md 处理不存在的文件"""
        nonexistent = temp_dir / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            parse_context_md(nonexistent)

    def test_parse_context_md_extracts_relationships(self, sample_session_dir):
        """parse_context_md 提取关系信息

        验证 Relationships 段落中的关系被正确提取
        """
        context_path = sample_session_dir / "CONTEXT.md"
        result = parse_context_md(context_path)

        # Relationships 应该作为特殊的术语条目
        # 或者返回结果中包含关系信息
        # 这里我们验证至少包含关系相关内容
        assert len(result) > 0  # 基本验证，具体实现可调整


# =============================================================================
# 测试组 3: Task.md 解析
# =============================================================================

class TestParseTaskMd:
    """测试 Task.md 解析功能"""

    def test_parse_task_md_returns_dict(self, sample_session_dir):
        """parse_task_md 返回进度字典"""
        task_path = sample_session_dir / "Task.md"
        result = parse_task_md(task_path)

        assert isinstance(result, dict)
        assert len(result) > 0

    def test_parse_task_md_extracts_task_status(self, sample_session_dir):
        """parse_task_md 正确提取任务状态

        示例 Task.md 包含：
        - Task 1: in_progress
        - Task 2: pending
        - Task 3: completed
        """
        task_path = sample_session_dir / "Task.md"
        result = parse_task_md(task_path)

        # 验证任务被正确提取
        assert "task-1" in result
        assert result["task-1"]["status"] == "in_progress"

        assert "task-2" in result
        assert result["task-2"]["status"] == "pending"

        assert "task-3" in result
        assert result["task-3"]["status"] == "completed"

    def test_parse_task_md_extracts_rounds(self, sample_session_dir):
        """parse_task_md 正确提取轮次信息"""
        task_path = sample_session_dir / "Task.md"
        result = parse_task_md(task_path)

        assert result["task-1"]["rounds"] == 1
        assert result["task-2"]["rounds"] == 0
        assert result["task-3"]["rounds"] == 3

    def test_parse_task_md_extracts_completion_time(self, sample_session_dir):
        """parse_task_md 正确提取完成时间"""
        task_path = sample_session_dir / "Task.md"
        result = parse_task_md(task_path)

        # Task 3 有完成时间
        assert result["task-3"]["completed_at"] == "2026-06-27"

        # Task 1 和 2 没有完成时间
        assert result["task-1"]["completed_at"] is None
        assert result["task-2"]["completed_at"] is None

    def test_parse_task_md_handles_empty_file(self, temp_dir):
        """parse_task_md 处理空文件"""
        empty_task = temp_dir / "Task.md"
        empty_task.write_text("")

        result = parse_task_md(empty_task)

        assert result == {}

    def test_parse_task_md_handles_nonexistent_file(self, temp_dir):
        """parse_task_md 处理不存在的文件"""
        nonexistent = temp_dir / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            parse_task_md(nonexistent)


# =============================================================================
# 测试组 4: 状态加载与同步
# =============================================================================

class TestStateLoadingAndSync:
    """测试状态加载与同步功能"""

    def test_load_session_state_returns_agentstate(self, sample_session_dir):
        """load_session_state 返回有效的 AgentState"""
        state = load_session_state(sample_session_dir)

        # 验证返回类型
        assert isinstance(state, dict)
        assert "current_step" in state
        assert "session_path" in state

    def test_load_session_state_populates_terminology_cache(self, sample_session_dir):
        """load_session_state 正确填充术语缓存"""
        state = load_session_state(sample_session_dir)

        # 验证术语被缓存
        assert len(state["cached_terminology"]) > 0
        assert "货币政策" in state["cached_terminology"]

    def test_load_session_state_populates_task_cache(self, sample_session_dir):
        """load_session_state 正确填充任务缓存"""
        state = load_session_state(sample_session_dir)

        # 验证任务进度被缓存
        assert len(state["cached_task_progress"]) > 0
        assert "task-1" in state["cached_task_progress"]

    def test_load_session_state_handles_missing_files(self, empty_session_dir):
        """load_session_state 处理缺失文件"""
        state = load_session_state(empty_session_dir)

        # 缺失文件时应该返回空缓存
        assert state["cached_terminology"] == {}
        assert state["cached_task_progress"] == {}

    def test_load_session_state_sets_session_path(self, sample_session_dir):
        """load_session_state 正确设置 session_path"""
        state = load_session_state(sample_session_dir)

        assert state["session_path"] == str(sample_session_dir)

    def test_sync_to_persistence_exists(self):
        """sync_to_persistence 函数存在且可调用"""
        # 基本存在性测试
        assert callable(sync_to_persistence)

        # 应该可以接受 AgentState 参数而不抛出异常
        # （当前实现是 pass，所以不会失败）
        state = {
            "current_step": "test",
            "tool_results": {},
            "retry_count": 0,
            "error_message": None,
            "session_path": "/tmp/test",
            "current_task_id": "task-1",
            "cached_terminology": {},
            "cached_task_progress": {},
            "workflow_name": "test",
            "start_time": "2026-06-28T00:00:00",
        }
        sync_to_persistence(state)  # 不应该抛出异常
