# Sub-Spec S1: 核心框架层

**父文档**: [01-master-spec.md](01-master-spec.md)
**预估 LOC**: ~1,700
**依赖**: 无（其他层的基础）

---

## 目标 (Objective)

实现 Agent Framework 的核心基础设施，包括：
1. State 定义与同步（ADR-0001）
2. Checkpoint 管理（ADR-0002）
3. 异常处理框架（ADR-0004）
4. 用户确认机制（ADR-0005）
5. 基础节点库

---

## 组件分解 (Component Breakdown)

### C1: State 定义与同步 (~400 LOC)

**目标**: 实现 AgentState 和双状态同步逻辑

**接口定义**:

```python
# core/state.py
from typing import TypedDict, Dict, Any, Optional

class AgentState(TypedDict):
    """Agent 运行时状态"""
    # 执行层状态 (LangGraph 专属)
    current_step: str
    tool_results: Dict[str, Any]
    retry_count: int
    error_message: Optional[str]

    # 持久层引用 (指向文件)
    session_path: str
    current_task_id: str

    # 缓存层状态 (从文件读取)
    cached_terminology: Dict[str, str]
    cached_task_progress: Dict[str, Any]

    # 元数据
    workflow_name: str
    start_time: str
```

**关键函数**:

```python
def load_session_state(session_path: str) -> AgentState:
    """加载会话状态到缓存层"""
    pass

def sync_to_persistence(state: AgentState) -> None:
    """同步状态到持久层文件"""
    pass

def parse_context_md(filepath: str) -> Dict[str, str]:
    """解析 CONTEXT.md 为术语字典"""
    pass

def parse_task_md(filepath: str) Dict[str, Any]:
    """解析 Task.md 为进度字典"""
    pass
```

**成功标准**:
- 可正确加载和解析 CONTEXT.md、Task.md
- 状态更新可正确同步到文件
- 缓存层与持久层保持一致

---

### C2: Checkpoint 管理 (~300 LOC)

**目标**: 封装 SQLite checkpoint 操作

**接口定义**:

```python
# core/checkpoint.py
from langgraph.checkpoint.sqlite import SqliteSaver

class CheckpointManager:
    """Checkpoint 管理器"""

    def __init__(self, db_path: str = "agent_framework/checkpoints.db"):
        """初始化 checkpoint 管理器"""
        pass

    def get_checkpointer(self) -> SqliteSaver:
        """获取 LangGraph checkpointer"""
        pass

    def cleanup_old_checkpoints(self, days: int = 30) -> int:
        """清理 N 天前的 checkpoint，返回清理数量"""
        pass

    def list_checkpoints(self, thread_id: str) -> List[Dict]:
        """列出指定 thread 的所有 checkpoint"""
        pass
```

**成功标准**:
- 可成功创建和恢复 checkpoint
- 清理策略正确执行
- 多 thread 互不干扰

---

### C3: 异常处理框架 (~350 LOC)

**目标**: 实现分层异常处理和降级策略

**接口定义**:

```python
# core/exceptions.py
class AgentException(Exception):
    """Agent 框架异常基类"""
    level: str = "terminate"  # retry, degrade, skip, terminate

class RetryableError(AgentException):
    """可重试错误"""
    level = "retry"
    max_retries: int = 2

class DegradableError(AgentException):
    """可降级错误"""
    level = "degrade"
    fallback: str = "skip"

class SkippableError(AgentException):
    """可跳过错误"""
    level = "skip"

class TerminalError(AgentException):
    """终止错误"""
    level = "terminate"

# 具体异常
class ResearchTimeoutError(RetryableError):
    """研究超时"""
    max_retries = 2

class ResearchInsufficientError(DegradableError):
    """研究内容不足"""
    fallback = "use_summary"

class LLMAPIError(RetryableError):
    """LLM API 错误"""
    max_retries = 3
```

```python
# core/exception_handler.py
class ExceptionHandler:
    """异常处理器"""

    def handle(self, error: Exception, context: dict) -> dict:
        """处理异常，返回下一步动作"""
        pass
```

**成功标准**:
- 所有异常有明确的层级定义
- 处理器可正确执行 retry/degrade/skip/terminate
- 降级策略符合 ADR-0004

---

### C4: 用户确认机制 (~250 LOC)

**目标**: 实现 Human-in-the-loop 确认节点

**接口定义**:

```python
# core/confirmation.py
from enum import Enum

class ConfirmationLevel(Enum):
    """确认级别"""
    MINIMAL = "minimal"      # 仅关键节点
    BALANCED = "balanced"    # 默认级别
    THOROUGH = "thorough"    # 更多确认点

class ConfirmationManager:
    """确认管理器"""

    def __init__(self, level: ConfirmationLevel = ConfirmationLevel.BALANCED):
        """初始化确认管理器"""
        pass

    def should_confirm(self, node_name: str) -> bool:
        """判断指定节点是否需要确认"""
        pass

    def create_confirmation_node(self, next_node: str, prompt: str):
        """创建确认节点函数"""
        pass
```

**确认点配置**:

```python
CONFIRMATION_NODES = {
    ConfirmationLevel.MINIMAL: ["research_complete"],
    ConfirmationLevel.BALANCED: ["research_complete", "loop_exit"],
    ConfirmationLevel.THOROUGH: [
        "research_complete", "concepts_extracted",
        "session_initialized", "loop_exit"
    ]
}
```

**成功标准**:
- 可按级别动态启用/禁用确认点
- 确认节点可正确暂停和恢复
- 用户输入可正确处理

---

### C5: 基础节点库 (~400 LOC)

**目标**: 提供通用节点模式

**接口定义**:

```python
# core/base_nodes.py
def retry_node(node_func: Callable, max_retries: int = 3):
    """重试装饰器节点"""
    pass

def timeout_node(node_func: Callable, timeout: int = 60):
    """超时装饰器节点"""
    pass

def logging_node(node_func: Callable, log_level: str = "INFO"):
    """日志装饰器节点"""
    pass

def error_handling_node(node_func: Callable):
    """错误处理装饰器节点"""
    pass
```

**成功标准**:
- 装饰器可正确组合使用
- 所有节点统一处理异常和日志
- 支持自定义装饰器链

---

## 测试策略

### 单元测试

| 组件 | 测试重点 |
|------|----------|
| State 同步 | 加载/解析/同步逻辑 |
| Checkpoint | 创建/恢复/清理 |
| 异常处理 | 各层级异常处理 |
| 确认机制 | 级别判断/节点创建 |

### 集成测试

- State 与 Checkpoint 联合测试
- 异常处理与降级策略端到端测试

---

## 边界规则

### Always Do
- 所有文件操作使用原子写入（临时文件 + 重命名）
- Checkpoint 写入前验证状态完整性
- 异常必须记录结构化日志

### Ask First
- 新增异常类型
- 修改确认级别定义

### Never Do
- 直接操作 CONTEXT.md/Task.md（必须通过 StateSync）
- 忽略任何 TerminalError

---

## 成功标准

- [ ] 所有单元测试通过
- [ ] State 加载/同步成功率 100%
- [ ] Checkpoint 恢复成功率 ≥ 95%
- [ ] 异常降级符合预期行为
- [ ] 确认机制可正确暂停/恢复

---

## 依赖项

```toml
[tool.poetry.dependencies]
python = "^3.12"
langgraph = "*"
langchain-core = "*"

[tool.poetry.dev-dependencies]
pytest = "*"
pytest-cov = "*"
```

---

**下一步**: S2 工具适配层
