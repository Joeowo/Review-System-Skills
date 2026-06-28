"""
C1: State 定义与同步

实现双状态并行管理策略（ADR-0001）：
- AgentState: LangGraph 运行时状态定义
- 状态同步: 执行层与持久层之间的同步逻辑
- 文件解析: CONTEXT.md 和 Task.md 解析功能
"""

from typing import TypedDict, Dict, Any, Optional
from pathlib import Path
import re


# =============================================================================
# AgentState 定义
# =============================================================================

class AgentState(TypedDict):
    """Agent 运行时状态

    实现双状态并行策略（ADR-0001）：
    - 执行层状态: LangGraph 运行时专用，单会话
    - 持久层引用: 指向长期存储的文件路径
    - 缓存层状态: 从文件加载到内存的数据
    """

    # ========== 执行层状态 ==========
    current_step: str  # 当前执行步骤标识符
    tool_results: Dict[str, Any]  # 工具调用结果缓存
    retry_count: int  # 当前步骤的重试次数
    error_message: Optional[str]  # 错误信息（如有）

    # ========== 持久层引用 ==========
    session_path: str  # 会话目录路径，指向 CONTEXT.md 和 Task.md 所在目录
    current_task_id: str  # 当前任务 ID

    # ========== 缓存层状态 ==========
    cached_terminology: Dict[str, str]  # 从 CONTEXT.md 解析的术语字典
    cached_task_progress: Dict[str, Any]  # 从 Task.md 解析的任务进度信息

    # ========== 元数据 ==========
    workflow_name: str  # 当前 workflow 名称
    start_time: str  # 会话开始时间（ISO 格式）


# =============================================================================
# CONTEXT.md 解析
# =============================================================================

def parse_context_md(filepath: str | Path) -> Dict[str, str]:
    """解析 CONTEXT.md 为术语字典

    Args:
        filepath: CONTEXT.md 文件路径

    Returns:
        术语字典，格式为 {术语: 定义}

    Raises:
        FileNotFoundError: 文件不存在

    Example:
        >>> parse_context_md("session/CONTEXT.md")
        {"货币政策": "央行调节货币供应量和利率的政策工具", ...}
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"CONTEXT.md not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")
    terminology: Dict[str, str] = {}

    # 解析 Language 段落中的术语定义
    # 格式: **术语**:\n定义内容
    in_language_section = False
    current_term = None
    current_definition = []

    for line in content.split("\n"):
        # 检测是否进入 Language 段落
        if line.strip() == "## Language":
            in_language_section = True
            continue

        # 检测是否离开 Language 段落（遇到下一个二级标题）
        if in_language_section and line.startswith("## ") and line != "## Language":
            break

        if in_language_section:
            # 解析 **术语**: 格式
            term_match = re.match(r"^\*\*(.+?)\*\*:", line)
            if term_match:
                # 保存前一个术语
                if current_term:
                    terminology[current_term] = "\n".join(current_definition).strip()

                # 开始新术语
                current_term = term_match.group(1)
                current_definition = [line[len(term_match.group(0)):].strip()]

                # 如果定义在同一行，提取出来
                if current_definition[0]:
                    pass  # 已提取
                else:
                    current_definition = []
            elif current_term:
                # 继续收集定义内容
                stripped = line.strip()
                # 跳过 _Avoid_ 标记行
                if not stripped.startswith("_Avoid:"):
                    current_definition.append(line)

    # 保存最后一个术语
    if current_term:
        terminology[current_term] = "\n".join(current_definition).strip()

    return terminology


# =============================================================================
# Task.md 解析
# =============================================================================

def parse_task_md(filepath: str | Path) -> Dict[str, Any]:
    """解析 Task.md 为进度字典

    Args:
        filepath: Task.md 文件路径

    Returns:
        进度字典，格式为 {task_id: {status, rounds, completed_at}}

    Raises:
        FileNotFoundError: 文件不存在

    Example:
        >>> parse_task_md("session/Task.md")
        {"task-1": {"status": "completed", "rounds": 3, "completed_at": "2026-06-27"}}
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Task.md not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")
    task_progress: Dict[str, Any] = {}

    # 解析任务段落
    # 格式: ## Task 1: 标题
    # **状态**: xxx
    # **轮次**: xxx
    # **完成时间**: xxx
    task_blocks = re.split(r"^## Task ", content, flags=re.MULTILINE)

    for block in task_blocks[1:]:  # 跳过第一个空块
        lines = block.strip().split("\n")
        if not lines:
            continue

        # 提取任务 ID 和标题
        first_line = lines[0]
        task_id_match = re.match(r"(\d+):\s*(.+)", first_line)
        if task_id_match:
            task_id = f"task-{task_id_match.group(1)}"
            task_info: Dict[str, Any] = {}

            # 解析任务信息
            for line in lines[1:]:
                if "**状态**:" in line:
                    status = line.split("**状态**:")[1].strip()
                    task_info["status"] = status
                elif "**轮次**:" in line:
                    rounds = line.split("**轮次**:")[1].strip()
                    task_info["rounds"] = int(rounds) if rounds.isdigit() else 0
                elif "**完成时间**:" in line:
                    completed_at = line.split("**完成时间**:")[1].strip()
                    task_info["completed_at"] = completed_at if completed_at != "-" else None

            task_progress[task_id] = task_info

    return task_progress


# =============================================================================
# 状态加载与同步
# =============================================================================

def load_session_state(session_path: str | Path) -> AgentState:
    """加载会话状态到缓存层

    Args:
        session_path: 会话目录路径

    Returns:
        加载后的 AgentState

    Raises:
        FileNotFoundError: 会话目录不存在
    """
    session_path = Path(session_path)

    if not session_path.exists():
        raise FileNotFoundError(f"Session path not found: {session_path}")

    context_path = session_path / "CONTEXT.md"
    task_path = session_path / "Task.md"

    # 解析文件
    cached_terminology = parse_context_md(context_path) if context_path.exists() else {}
    cached_task_progress = parse_task_md(task_path) if task_path.exists() else {}

    # 创建初始状态
    state: AgentState = {
        # 执行层状态
        "current_step": "init",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,

        # 持久层引用
        "session_path": str(session_path),
        "current_task_id": "",

        # 缓存层状态
        "cached_terminology": cached_terminology,
        "cached_task_progress": cached_task_progress,

        # 元数据
        "workflow_name": "",
        "start_time": "",  # 应该由调用方设置
    }

    return state


def sync_to_persistence(state: AgentState) -> None:
    """同步状态到持久层文件

    Args:
        state: 要同步的 AgentState

    注意:
        - 使用原子写入策略（临时文件 + 重命名）
        - 仅同步缓存层状态到文件
    """
    session_path = Path(state["session_path"])

    # TODO: 实现原子写入逻辑
    # 1. 将 cached_terminology 写回 CONTEXT.md
    # 2. 将 cached_task_progress 写回 Task.md
    # 3. 使用临时文件 + 原子重命名

    # 当前为简化实现，后续完善
    pass
