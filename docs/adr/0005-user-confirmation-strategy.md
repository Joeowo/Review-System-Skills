# ADR 0005: 用户确认点策略

**状态**: 已采纳
**日期**: 2026-06-28
**决策者**: Agent 框架设计团队

---

## 上下文

LangGraph 支持在流程中插入"人类循环"（human-in-the-loop），暂停执行等待用户输入。

需要确定哪些节点需要用户确认，平衡自动化与用户控制：

| 确认点 | 价值 | 成本 |
|--------|------|------|
| **研究完成后** | 确认研究方向，避免偏离 | 增加交互步骤 |
| **概念提取后** | 校验提取准确性 | 概念通常准确，确认价值低 |
| **会话初始化前** | 确认会话名称和路径 | 自动生成即可 |

---

## 决策

采用**选择性确认策略**：

| 确认点 | 是否需要确认 | 理由 |
|--------|-------------|------|
| **研究完成后** | ✅ 是 | 高价值节点，可能需要调整方向 |
| **概念提取后** | ❌ 否 | 自动提取通常准确，后续可修正 |
| **会话初始化前** | ❌ 否 | 自动生成足够，用户可手动调整 |
| **每轮 grilling 后** | ❌ 否 | 已有正确率指标，无需额外确认 |
| **循环退出前** | ✅ 是 | 重要决策点，确认是否继续 |

---

## 理由

### 支持选择性确认的论据

1. **高价值确认**: 关键节点让用户参与决策
2. **流畅体验**: 避免过度打断用户
3. **可逆性**: 非关键决策可在后期修正

### 反对全确认的论据

1. **体验差**: 频繁确认影响流畅度
2. **认知负担**: 用户可能随意点击

### 反对无确认的论据

1. **偏离风险**: 自动执行可能偏离用户意图
2. **错误传播**: 早期错误影响后续所有步骤

---

## 后果

### 正面影响

- 关键决策点有用户把关
- 流程执行更流畅
- 降低认知负担

### 负面影响

- 非关键节点的错误可能传播
- 用户可能在确认点遗漏检查

### 缓解措施

- **日志记录**: 记录所有自动决策，便于追溯
- **撤销机制**: 支持回退到上一个确认点
- **可配置**: 允许用户调整确认级别

---

## 实施细节

### LangGraph 人类循环

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

# 添加确认节点
def research_completion_confirmation(state: AgentState) -> dict:
    """研究完成确认节点"""
    # 暂停，等待用户输入
    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": f"""
研究已完成！

主题: {state['topic']}
报告: {state['report_path']}
关键概念: {', '.join(state['key_concepts'])}

是否继续基于此报告学习？回复 '继续' 或 '重新研究'
        """
    }

# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("research_complete", research_completion_confirmation)

# 添加条件边
workflow.add_conditional_edges(
    "research_complete",
    should_continue,
    {
        "continue": "extract_concepts",
        "rethink": "research"
    }
)
```

### 确认级别配置

```python
# config/settings.py

class ConfirmationLevel:
    """确认级别"""
    MINIMAL = "minimal"      # 仅关键节点
    BALANCED = "balanced"    # 默认级别
    THOROUGH = "thorough"    # 更多确认点

DEFAULT_CONFIRMATION_LEVEL = ConfirmationLevel.BALANCED

# 根据级别动态添加确认节点
CONFIRMATION_NODES = {
    ConfirmationLevel.MINIMAL: ["research_complete"],
    ConfirmationLevel.BALANCED: ["research_complete", "loop_exit"],
    ConfirmationLevel.THOROUGH: [
        "research_complete", 
        "concepts_extracted",
        "session_initialized",
        "loop_exit"
    ]
}
```

---

## 相关决策

- [ADR 0001: 双状态并行管理策略](0001-dual-state-management.md)
- [ADR 0004: 异常处理与降级策略](0004-exception-handling-strategy.md)

---

**文档版本**: 1.0
