# Tasks: Sub-Spec S1 - 核心框架层

**父文档**: [10-master-plan.md](10-master-plan.md)
**预估总 LOC**: ~1,700

---

## Task 1: 实现 AgentState 定义 (~80 LOC)

**描述**: 定义 AgentState TypedDict 和相关类型

**验收标准**:
- [ ] AgentState 包含所有必需字段
- [ ] 字段类型注解正确
- [ ] 默认值合理

**实现要点**:
```python
# core/state.py
from typing import TypedDict, Dict, Any, Optional

class AgentState(TypedDict):
    """Agent 运行时状态"""
    current_step: str
    tool_results: Dict[str, Any]
    retry_count: int
    error_message: Optional[str]
    session_path: str
    current_task_id: str
    cached_terminology: Dict[str, str]
    cached_task_progress: Dict[str, Any]
    workflow_name: str
    start_time: str
```

**测试**:
- 类型验证测试
- 默认值测试

**依赖**: 无

**预计时间**: 2 小时

---

## Task 2: 实现 State 加载逻辑 (~100 LOC)

**描述**: 从文件加载状态到缓存层

**验收标准**:
- [ ] 可正确解析 CONTEXT.md
- [ ] 可正确解析 Task.md
- [ ] 空文件处理正确
- [ ] 格式错误有友好提示

**实现要点**:
```python
def parse_context_md(filepath: str) -> Dict[str, str]:
    """解析 CONTEXT.md 为术语字典"""
    # 读取文件
    # 解析术语定义
    # 返回字典
    pass

def parse_task_md(filepath: str) Dict[str, Any]:
    """解析 Task.md 为进度字典"""
    # 读取文件
    # 解析任务列表
    # 返回字典
    pass

def load_session_state(session_path: str) -> AgentState:
    """加载会话状态"""
    # 调用上述解析函数
    # 返回完整状态
    pass
```

**测试**:
- 正常文件加载测试
- 空文件测试
- 格式错误测试

**依赖**: Task 1

**预计时间**: 4 小时

---

## Task 3: 实现 State 同步逻辑 (~120 LOC)

**描述**: 同步缓存层到持久层文件

**验收标准**:
- [ ] 状态更新正确写入文件
- [ ] 使用原子写入（临时文件 + 重命名）
- [ ] 保留文件格式一致性
- [ ] 并发写入安全

**实现要点**:
```python
def sync_to_persistence(state: AgentState) -> None:
    """同步状态到持久层文件"""
    # 原子写入 CONTEXT.md
    # 原子写入 Task.md
    pass

def update_context_md(session_path: str, updates: Dict[str, str]) -> None:
    """更新 CONTEXT.md"""
    # 读取现有内容
    # 应用更新
    # 原子写入
    pass

def update_task_md(session_path: str, task_id: str, status: str) -> None:
    """更新 Task.md"""
    # 读取现有内容
    # 更新指定任务
    # 原子写入
    pass
```

**测试**:
- 更写测试
- 并发测试
- 原子性验证

**依赖**: Task 2

**预计时间**: 5 小时

---

## Task 4: 实现 CheckpointManager (~150 LOC)

**描述**: 封装 SQLite checkpoint 操作

**验收标准**:
- [ ] 可创建 checkpointer
- [ ] 可列出 checkpoints
- [ ] 可清理旧 checkpoints
- [ ] 多 thread 互不干扰

**实现要点**:
```python
# core/checkpoint.py
from langgraph.checkpoint.sqlite import SqliteSaver

class CheckpointManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_exists()

    def get_checkpointer(self) -> SqliteSaver:
        return SqliteSaver.from_conn_string(self.db_path)

    def cleanup_old_checkpoints(self, days: int = 30) -> int:
        # 实现清理逻辑
        pass

    def list_checkpoints(self, thread_id: str) -> List[Dict]:
        # 列出 checkpoints
        pass
```

**测试**:
- 创建/恢复测试
- 清理测试
- 多 thread 测试

**依赖**: 无

**预计时间**: 5 小时

---

## Task 5: 实现异常定义 (~80 LOC)

**描述**: 定义异常类型层级

**验收标准**:
- [ ] 所有异常类型定义
- [ ] level 属性正确
- [ ] 具体异常包含必要信息

**实现要点**:
```python
# core/exceptions.py
class AgentException(Exception):
    level: str = "terminate"

class RetryableError(AgentException):
    level = "retry"
    max_retries: int = 2

class DegradableError(AgentException):
    level = "degrade"
    fallback: str = "skip"

# ... 具体异常
```

**测试**:
- 类型检查
- 属性验证

**依赖**: 无

**预计时间**: 2 小时

---

## Task 6: 实现异常处理器 (~150 LOC)

**描述**: 实现异常处理逻辑

**验收标准**:
- [ ] 可处理所有层级异常
- [ ] retry 逻辑正确
- [ ] degrade 返回正确 fallback
- [ ] terminate 提供清晰信息

**实现要点**:
```python
# core/exception_handler.py
class ExceptionHandler:
    def handle(self, error: Exception, context: dict) -> dict:
        # 判断异常类型
        # 执行对应处理
        # 返回下一步动作
        pass
```

**测试**:
- 各层级异常处理测试
- 边界情况测试

**依赖**: Task 5

**预计时间**: 5 小时

---

## Task 7: 实现确认机制 (~100 LOC)

**描述**: 实现 Human-in-the-loop 确认

**验收标准**:
- [ ] 确认级别定义正确
- [ ] should_confirm 判断正确
- [ ] 确认节点可暂停/恢复

**实现要点**:
```python
# core/confirmation.py
class ConfirmationLevel(Enum):
    MINIMAL = "minimal"
    BALANCED = "balanced"
    THOROUGH = "thorough"

class ConfirmationManager:
    def __init__(self, level: ConfirmationLevel):
        self.level = level

    def should_confirm(self, node_name: str) -> bool:
        return node_name in CONFIRMATION_NODES[self.level]
```

**测试**:
- 级别判断测试
- 节点暂停/恢复测试

**依赖**: 无

**预计时间**: 4 小时

---

## Task 8: 实现基础节点库 (~200 LOC)

**描述**: 实现通用节点装饰器

**验收标准**:
- [ ] retry 装饰器正确重试
- [ ] timeout 装饰器正确超时
- [ ] logging 装饰器记录日志
- [ ] error_handling 装饰器处理异常

**实现要点**:
```python
# core/base_nodes.py
def retry_node(node_func: Callable, max_retries: int = 3):
    def wrapper(state: AgentState):
        for i in range(max_retries):
            try:
                return node_func(state)
            except RetryableError:
                continue
        raise
    return wrapper

# ... 其他装饰器
```

**测试**:
- 各装饰器功能测试
- 组合测试

**依赖**: Task 6, Task 7

**预计时间**: 6 小时

---

## Task 9: 集成测试 (~100 LOC)

**描述**: S1 集成测试

**验收标准**:
- [ ] State 同步集成测试通过
- [ ] Checkpoint 集成测试通过
- [ ] 异常处理集成测试通过
- [ ] 确认机制集成测试通过

**测试**:
```python
# tests/integration/test_s1_integration.py
def test_state_sync_integration():
    # 端到端测试
    pass

def test_checkpoint_integration():
    # Checkpoint 完整流程
    pass
```

**依赖**: 所有前置任务

**预计时间**: 4 小时

---

## Summary

- **总任务数**: 9
- **总预估 LOC**: ~1,080（核心）+ 测试代码
- **关键路径**: Task 1 → Task 2 → Task 3 → Task 9
- **并行机会**: Task 4, Task 5, Task 7 可并行

→ **Human**: 审查任务列表，批准后开始实施
