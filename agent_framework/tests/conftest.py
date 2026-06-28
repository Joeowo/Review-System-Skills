"""
pytest 配置和 fixtures

为 S1 核心框架层 TDD 提供测试基础设施
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta


# =============================================================================
# 目录和文件 fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """临时目录 fixture

    提供一个临时目录用于测试，测试后自动清理
    """
    return tmp_path


@pytest.fixture
def sample_session_dir(temp_dir: Path) -> Path:
    """示例会话目录 fixture

    创建包含 CONTEXT.md 和 Task.md 的示例会话目录
    """
    session_path = temp_dir / "test-session"
    session_path.mkdir()

    # 创建 CONTEXT.md
    context_md = session_path / "CONTEXT.md"
    context_md.write_text("""# Session 上下文

测试会话的术语定义。

## Language

**货币政策**:
央行调节货币供应量和利率的政策工具
_Avoid_: 宽松政策、紧缩政策（使用具体工具名）

**时滞**:
政策实施到产生效果的延迟时间

## Relationships

- **利率** 影响 **投资成本**
- **准备金率** 影响 **银行流动性**

## Example dialogue

> **User**: "当央行降低利率时会发生什么？"
> **Agent**: "降低利率会降低借款成本，刺激投资和消费。"
""")

    # 创建 Task.md
    task_md = session_path / "Task.md"
    task_md.write_text("""# 学习任务列表

## Task 1: 基础概念理解

**状态**: in_progress
**轮次**: 1
**完成时间**: -

## Task 2: 政策工具分析

**状态**: pending
**轮次**: 0
**完成时间**: -

## Task 3: 传导机制研究

**状态**: completed
**轮次**: 3
**完成时间**: 2026-06-27
""")

    return session_path


@pytest.fixture
def empty_session_dir(temp_dir: Path) -> Path:
    """空会话目录 fixture

    创建空的会话目录，用于测试初始化场景
    """
    session_path = temp_dir / "empty-session"
    session_path.mkdir()
    return session_path


# =============================================================================
# Checkpoint fixtures
# =============================================================================

@pytest.fixture
def temp_checkpoint_db(tmp_path: Path) -> str:
    """临时 checkpoint 数据库 fixture

    提供临时 SQLite 数据库用于 checkpoint 测试
    """
    db_path = tmp_path / "test_checkpoints.db"
    return str(db_path)


@pytest.fixture
def sample_thread_id() -> str:
    """示例 thread_id fixture"""
    return "test-thread-001"


# =============================================================================
# State fixtures
# =============================================================================

@pytest.fixture
def base_state_dict(sample_session_dir: Path) -> Dict[str, Any]:
    """基础状态字典 fixture

    提供符合 AgentState 定义的基础字典
    """
    return {
        # 执行层状态
        "current_step": "init",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,

        # 持久层引用
        "session_path": str(sample_session_dir),
        "current_task_id": "task-1",

        # 缓存层状态
        "cached_terminology": {},
        "cached_task_progress": {},

        # 元数据
        "workflow_name": "test_workflow",
        "start_time": datetime.now().isoformat(),
    }


@pytest.fixture
def populated_state_dict(base_state_dict: Dict[str, Any]) -> Dict[str, Any]:
    """已填充数据的状态字典 fixture

    提供包含缓存数据的状态字典
    """
    state = base_state_dict.copy()
    state["cached_terminology"] = {
        "货币政策": "央行调节货币供应量和利率的政策工具",
        "时滞": "政策实施到产生效果的延迟时间",
    }
    state["cached_task_progress"] = {
        "task-1": "in_progress",
        "task-2": "pending",
        "task-3": "completed",
    }
    state["current_step"] = "running"
    return state


# =============================================================================
# 异常测试 fixtures
# =============================================================================

@pytest.fixture
def error_context() -> Dict[str, Any]:
    """异常处理器测试上下文 fixture"""
    return {
        "retry_count": 0,
        "node_name": "test_node",
        "current_step": "processing",
    }


# =============================================================================
# Pytest hooks
# =============================================================================

def pytest_configure(config):
    """pytest 配置 hook

    注册自定义标记
    """
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "e2e: 端到端测试")
    config.addinivalue_line("markers", "slow: 慢速测试")


def pytest_collection_modifyitems(config, items):
    """修改测试收集 hook

    为测试自动添加标记
    """
    for item in items:
        # 根据文件路径自动添加标记
        path = Path(item.fspath)
        if "e2e" in path.parts:
            item.add_marker(pytest.mark.e2e)
        elif "integration" in path.parts:
            item.add_marker(pytest.mark.integration)
        elif "unit" in path.parts:
            item.add_marker(pytest.mark.unit)
