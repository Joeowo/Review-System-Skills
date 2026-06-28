# ADR 0001: 双状态并行管理策略

**状态**: 已采纳
**日期**: 2026-06-28
**决策者**: Agent 框架设计团队

---

## 上下文

ComindFlow 项目已有一套基于文件的状态管理系统（CONTEXT.md、Task.md、handoff.md），被现有 skills（grill-me、grill-you 等）依赖。

新的 Agent 框架引入 LangGraph，其 StateGraph 提供了自己的状态管理机制。

面临选择：
1. 完全迁移到 LangGraph 状态，废弃文件系统
2. LangGraph 状态作为唯一真相源，定期同步到文件
3. 双状态并行，各司其职

---

## 决策

采用**双状态并行策略**：

| 维度 | 执行层状态 (LangGraph) | 持久层状态 (文件系统) |
|------|----------------------|-------------------|
| **生命周期** | 单次会话，运行时 | 跨会话，长期存储 |
| **存储位置** | StateGraph 内存 | CONTEXT.md, Task.md, handoff.md |
| **更新频率** | 每个节点后 | 关键节点写入 |
| **数据类型** | 临时变量、中间结果 | 术语定义、任务进度 |

---

## 理由

### 支持双状态的论据

1. **兼容性**: 不破坏现有 skills 对文件的依赖
2. **职责分离**: 执行层 vs 持久层，各司其职
3. **人类可读**: 文件状态可直接查看和编辑
4. **跨会话**: 文件状态支持长期存储和跨天恢复

### 反对单一状态源的论据

1. **完全迁移成本**: 需要重构所有现有 skills
2. **LangGraph 状态局限**: 运行时状态不适合长期存储
3. **单点故障**: 仅依赖 LangGraph checkpoint 可能丢失数据

### 反对双状态的论据

1. **同步复杂**: 需要保证两套状态一致性
2. **性能开销**: 文件 I/O 可能成为瓶颈

**反驳**: 通过缓存层和关键节点写入策略，最小化同步开销

---

## 后果

### 正面影响

- 现有 skills 无需修改，继续使用文件状态
- LangGraph 可以独立管理执行流程
- 用户可以直接查看和编辑文件状态
- 支持灵活的断点恢复策略

### 负面影响

- 需要维护状态同步逻辑
- 增加了系统复杂度
- 潜在的状态不一致风险

### 缓解措施

- **缓存层**: 一次性读取文件到内存，避免频繁 I/O
- **关键节点写入**: 仅在状态发生有意义变化时同步
- **事务性写入**: 先写临时文件，再原子替换
- **一致性检查**: 启动时验证文件状态完整性

---

## 实施细节

### 状态定义

```python
class AgentState(TypedDict):
    # 执行层状态（LangGraph 专属）
    current_step: str
    tool_results: Dict[str, Any]
    retry_count: int
    error_message: Optional[str]
    
    # 持久层引用（指向文件）
    session_path: str
    current_task_id: str
    
    # 缓存层状态（从文件读取）
    cached_terminology: Dict[str, str]
    cached_task_progress: Dict
```

### 同步策略

**读取**: 会话开始时一次性加载
```python
def load_session_node(state: AgentState) -> AgentState:
    state["cached_terminology"] = parse_context_md(
        f"{state['session_path']}/CONTEXT.md"
    )
    state["cached_task_progress"] = parse_task_md(
        f"{state['session_path']}/Task.md"
    )
    return state
```

**写入**: 关键节点后同步
```python
def complete_task_node(state: AgentState) -> AgentState:
    state["cached_task_progress"][state["current_task_id"]] = "completed"
    update_task_md_file(...)  # 同步到文件
    return state
```

---

## 替代方案

### 方案 A: 单一 LangGraph 状态
- **优点**: 架构简洁，无同步问题
- **缺点**: 破坏兼容性，人类不可读
- **未采纳原因**: 不符合项目需求

### 方案 B: 单一文件状态
- **优点**: 简单，人类可读
- **缺点**: 无运行时状态支持，性能差
- **未采纳原因**: LangGraph 能力未充分利用

---

## 相关决策

- [ADR 0002: SQLite 作为 LangGraph Checkpoint 后端](0002-sqlite-checkpoint.md)

---

**文档版本**: 1.0
