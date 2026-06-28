# ADR 0002: SQLite 作为 LangGraph Checkpoint 后端

**状态**: 已采纳
**日期**: 2026-06-28
**决策者**: Agent 框架设计团队

---

## 上下文

LangGraph 支持多种 checkpoint 后端用于状态持久化：

| 选项 | 包 | 优点 | 缺点 |
|------|---|------|------|
| **Memory** | langgraph.checkpoint.memory | 无依赖，开发方便 | 重启丢失，无持久化 |
| **SQLite** | langgraph.checkpoint.sqlite | 本地文件，可持久，无额外服务 | 单进程限制 |
| **PostgreSQL** | langgraph.checkpoint.postgres | 生产级，多进程，高可用 | 需要额外服务 |

Agent 框架需要支持断点恢复（特别是 F3 学术写作流程可能跨天执行）。

---

## 决策

采用 **SQLite** 作为 LangGraph Checkpoint 后端。

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("agent_framework/checkpoints.db")
```

---

## 理由

### 支持 SQLite 的论据

1. **持久化**: 支持跨天断点恢复，满足 F3 需求
2. **无额外服务**: 文件存储，无需安装配置数据库
3. **简单部署**: checkpoints.db 可随项目版本控制
4. **性能**: 单进程场景下性能足够
5. **可扩展**: 后期可升级到 PostgreSQL

### 反对 Memory 的论据

1. **重启丢失**: 不符合断点恢复需求
2. **调试困难**: 无法回溯历史状态

### 反对 PostgreSQL 的论据

1. **过度工程**: 单机场景不需要
2. **部署复杂**: 增加环境依赖
3. **资源消耗**: 单进程场景下浪费

---

## 后果

### 正面影响

- 支持跨会话断点恢复
- 无需额外基础设施
- checkpoint 文件可备份和版本控制
- 后期可平滑升级到 PostgreSQL

### 负面影响

- 单进程限制（同一时刻只能有一个 agent 实例写入）
- 并发写入可能导致锁定

### 缓解措施

- **写入锁**: 使用 SQLite 内置锁机制
- **定期清理**: 实现 checkpoint 清理策略，避免数据库膨胀
- **升级路径**: 保留升级到 PostgreSQL 的选项

---

## 实施细节

### 初始化

```python
# core/checkpoint.py
from langgraph.checkpoint.sqlite import SqliteSaver

def get_checkpointer(db_path: str = "agent_framework/checkpoints.db"):
    """获取 checkpoint saver"""
    return SqliteSaver.from_conn_string(db_path)
```

### 清理策略

```python
def cleanup_old_checkpoints(db_path: str, days: int = 30):
    """清理 N 天前的 checkpoint"""
    # 实现清理逻辑
    pass
```

### 升级路径

```python
# 生产环境可切换到 PostgreSQL
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string("postgresql://...")
```

---

## 相关决策

- [ADR 0001: 双状态并行管理策略](0001-dual-state-management.md)

---

**文档版本**: 1.0
