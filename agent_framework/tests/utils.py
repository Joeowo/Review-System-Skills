"""
测试工具函数

提供测试中常用的辅助函数
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime


def assert_state_step(state: Dict[str, Any], expected_step: str) -> None:
    """断言状态步骤

    Args:
        state: 状态字典
        expected_step: 期望的步骤名称

    Raises:
        AssertionError: 如果当前步骤与期望不符
    """
    actual_step = state.get("current_step")
    assert actual_step == expected_step, \
        f"Expected step {expected_step}, got {actual_step}"


def assert_no_error(state: Dict[str, Any]) -> None:
    """断言无错误

    Args:
        state: 状态字典

    Raises:
        AssertionError: 如果存在错误信息
    """
    error = state.get("error_message")
    assert error is None, f"Unexpected error: {error}"


def load_test_report(path: str) -> str:
    """加载测试报告

    Args:
        path: 报告文件路径

    Returns:
        报告内容（UTF-8 编码）
    """
    return Path(path).read_text(encoding="utf-8")


def create_sample_state(**kwargs) -> Dict[str, Any]:
    """创建示例状态

    Args:
        **kwargs: 自定义字段值

    Returns:
        状态字典
    """
    default_state = {
        "current_step": "init",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": "/tmp/test",
        "current_task_id": "task-1",
        "cached_terminology": {},
        "cached_task_progress": {},
        "workflow_name": "test_workflow",
        "start_time": datetime.now().isoformat(),
    }
    default_state.update(kwargs)
    return default_state


def wait_for_condition(
    condition: Callable[[Any], bool],
    value: Any,
    timeout: float = 5.0,
    interval: float = 0.1
) -> bool:
    """等待条件满足

    Args:
        condition: 条件函数
        value: 传递给条件函数的值
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）

    Returns:
        条件是否满足
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition(value):
            return True
        time.sleep(interval)
    return False


def mock_llm_response(
    content: Optional[str] = None,
    tool_calls: Optional[list] = None
) -> Any:
    """创建模拟 LLM 响应

    Args:
        content: 文本内容
        tool_calls: 工具调用列表

    Returns:
        模拟的响应对象
    """
    from types import SimpleNamespace

    response = SimpleNamespace()

    if content is not None:
        response.content = [{"type": "text", "text": content}]
    else:
        response.content = []

    if tool_calls is not None:
        response.tool_calls = [
            SimpleNamespace(
                name=call.get("name"),
                args=call.get("args", {})
            )
            for call in tool_calls
        ]
    else:
        response.tool_calls = []

    return response


def compare_workflow_states(
    state1: Dict[str, Any],
    state2: Dict[str, Any],
    ignored_fields: Optional[list] = None
) -> bool:
    """比较两个 workflow 状态（忽略指定字段）

    Args:
        state1: 第一个状态
        state2: 第二个状态
        ignored_fields: 忽略的字段列表

    Returns:
        状态是否相等
    """
    ignored = ignored_fields or ["start_time", "last_updated"]

    filtered1 = {k: v for k, v in state1.items() if k not in ignored}
    filtered2 = {k: v for k, v in state2.items() if k not in ignored}

    return filtered1 == filtered2


def extract_workflow_nodes(workflow: Any) -> list:
    """提取 workflow 的节点列表

    Args:
        workflow: LangGraph workflow 对象

    Returns:
        节点名称列表
    """
    if hasattr(workflow, "graph"):
        return list(workflow.graph.nodes.keys())
    return []


def extract_workflow_edges(workflow: Any) -> list:
    """提取 workflow 的边列表

    Args:
        workflow: LangGraph workflow 对象

    Returns:
        边列表 [(from, to, label), ...]
    """
    if hasattr(workflow, "graph"):
        edges = []
        for edge in workflow.graph.edges:
            edges.append((edge[0], edge[1], None))
        return edges
    return []
