# 需求 3：上下文优化策略

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## 需求概述

采用 "目录注入+按需加载" 的调度策略，在保持模型高响应精度的同时，将单次任务的 Token 消耗降低。

---

## 背景分析

### 当前问题

| 问题 | 影响 |
|------|------|
| **全量加载** | 所有 SKILL.md 内容完整加载到上下文 |
| **Token 浪费** | 不相关的 Skill 内容占用 Token |
| **性能下降** | 上下文过长影响 LLM 响应速度 |

### 当前估算

```
完整加载所有 Skills（10个 × 平均1000 tokens）= ~10,000 tokens
```

---

## 功能需求

### FR-3.1：目录注入（Metadata Injection）

**描述**：只注入 SKILL.md 的目录（TOC）而非完整内容。

**注入内容**：

| 内容 | 说明 |
|------|------|
| **YAML frontmatter** | name, description（~100 tokens/Skill） |
| **章节结构** | Quick start, Workflows, Advanced features |

**注入格式**：

```python
# 初始上下文注入（所有 Skills）
METADATA_INJECTION = """
## Skills Available

### grill-me
Interview user about plans and designs to achieve shared understanding.
Use when stress-testing plans or user mentions "grill me".

### grill-you
Guide users to ask clarifying questions to the agent.
Use when user needs help structuring inquiries.

### advance-task
Update session state by recording progress to Task.md and handoff.md.
Use after completing a Q&A round to save progress.

... (其他 Skills)
"""
```

**数据结构**：

```python
@dataclass
class SkillMetadata:
    """技能元数据（常驻上下文）"""
    name: str
    description: str          # < 1024 字符
    triggers: List[str]       # 触发关键词列表
    quick_summary: str        # 一句话功能描述

@dataclass
class SkillTOC:
    """技能目录结构"""
    name: str
    sections: List[str]      # ["Quick start", "Workflows", "Advanced features"]
```

---

### FR-3.2：按需加载（On-Demand Loading）

**描述**：完整 Skill 内容的延迟加载机制。

**触发条件**：

| 触发方式 | 条件 | 行为 |
|----------|------|------|
| **基于任务类型** | `state["task_type"] == "grilling"` | 加载 grill-me 完整内容 |
| **基于用户查询** | 用户输入包含 `/grill-me` | 加载 grill-me 完整内容 |
| **基于 LLM 调用** | LLM 决定调用 Skill 工具时 | 加载对应 Skill 完整内容 |

**加载策略**：

```python
class ContextOptimizer:
    """上下文优化器"""

    def should_load_full_content(
        self,
        skill_name: str,
        state: AgentState
    ) -> bool:
        """判断是否需要加载完整内容
        触发条件：
        1. state["task_type"] 匹配 Skill 的 category
        2. state["user_query"] 包含 Skill 的触发关键词
        3. state["pending_skill_calls"] 包含该 Skill
        """

    def load_full_content(
        self,
        skill_name: str
    ) -> str:
        """加载 Skill 的完整内容
        包括：
        - SKILL.md 完整内容
        - REFERENCE.md（如果存在）
        - EXAMPLES.md（如果需要）
        """
```

---

### FR-3.3：两阶段加载（Two-Phase Loading）

**描述**：目录注入与按需加载的协调策略。

**阶段划分**：

```python
# 阶段1：初始化时注入目录
class Phase1Injector:
    def inject_metadata(self, registry: SkillRegistry) -> str:
        """注入所有 Skills 的元数据
        - 所有 Skills 的 YAML frontmatter
        - 章节结构（TOC）
        返回：注入的上下文字符串
        """

# 阶段2：运行时按需加载完整内容
class Phase2Loader:
    def load_on_demand(
        self,
        skill_name: str,
        trigger_reason: str
    ) -> str:
        """按需加载 Skill 完整内容
        - SKILL.md 完整内容
        - REFERENCE.md（如果需要）
        - scripts/ 说明（如果需要）
        返回：加载的完整内容
        """
```

**数据流**：

```
初始化阶段:
┌─────────────────────────────────────────┐
│  注入元数据（~100 tokens × 10 = 1,000）  │
│  - YAML frontmatter                      │
│  - 章节结构（TOC）                       │
└─────────────────────────────────────────┘

运行时阶段（触发时）:
┌─────────────────────────────────────────┐
│  按需加载完整内容（~1,000 tokens）         │
│  - SKILL.md 完整内容                     │
│  - REFERENCE.md（如需要）                │
│  - EXAMPLES.md（如需要）                  │
└─────────────────────────────────────────┘
```

---

### FR-3.4：上下文预算管理

**描述**：管理上下文 Token 预算，防止过度加载。

**预算策略**：

```python
class ContextBudget:
    """上下文预算管理器"""

    def __init__(
        self,
        total_budget: int = 8000,
        metadata_reserve: int = 1000
    ):
        self.total_budget = total_budget        # 总预算
        self.metadata_reserve = metadata_reserve  # 元数据保留
        self.available = total_budget - metadata_reserve

    def can_load(self, skill_name: str, estimated_tokens: int) -> bool:
        """判断是否可以加载（预算是否充足）"""

    def evict_if_needed(self, required_tokens: int) -> List[str]:
        """如果预算不足，驱逐最少使用的 Skills
        返回：被驱逐的 Skill 名称列表
        """
```

**驱逐策略**：

| 策略 | 说明 |
|------|------|
| **LRU** | 驱逐最近最少使用的 Skill |
| **LFU** | 驱逐使用频率最低的 Skill |
| **优先级** | 优先驱逐低优先级 Skills |

---

## 非功能需求

### NFR-3.1：性能

- 元数据注入时间 < 100ms
- 按需加载时间 < 200ms
- 预算管理开销 < 5%

### NFR-3.2：精度

- 优化后 LLM 响应准确率下降 < 5%
- 支持 A/B 测试验证

### NFR-3.3：可观测性

- 记录每次加载的 Token 消耗
- 记录驱逐决策和原因

---

## 优化目标

| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| **初始 Token 消耗** | ~10,000 | ~1,000 | 统计元数据注入 |
| **峰值 Token 消耗** | ~10,000 | ~3,000 | 统计最大加载 |
| **平均 Token 消耗** | ~10,000 | 通过测试确定 | 实际运行统计 |

---

## 架构决策

### AD-3.1：目录注入内容

**决策**：只注入 YAML frontmatter + 章节结构

**理由**：
- frontmatter 包含选择 Skill 所需的所有信息
- 章节结构帮助理解 Skill 组织
- 完整内容按需加载节省 Token

### AD-3.2：按需加载触发

**决策**：多触发条件（任务类型 + 用户查询 + LLM 调用）

**理由**：
- 覆盖多种使用场景
- 提高响应速度
- 支持 CLI 和 Workflow 两种模式

### AD-3.3：加载协调策略

**决策**：两阶段加载

**理由**：
- 初始化时轻量，启动快
- 运行时按需，节省 Token
- 实现简单，易于维护

---

## 验收标准

- [ ] 初始化时只注入元数据（~1,000 tokens）
- [ ] 触发时正确加载完整内容
- [ ] 上下文预算管理有效防止过度加载
- [ ] LLM 响应准确率下降 < 5%
- [ ] 加载/驱逐决策有完整日志

---

## 测试计划

### 性能测试

- 测量元数据注入时间
- 测量按需加载时间
- 测量预算管理开销

### 精度测试

- A/B 测试：优化前后 LLM 响应准确率
- 不同预算阈值的精度对比

### 压力测试

- 大量 Skills（50+）的加载性能
- 频繁加载/驱逐的稳定性

---

## 相关文档

- [01-skill-registry-middleware.md](01-skill-registry-middleware.md) - 技能注册表与中间件
- [02-skill-factory.md](02-skill-factory.md) - 标准化技能工厂
- [04-observability.md](04-observability.md) - Agent 可观测性
- [CONTEXT.md](../../CONTEXT.md) - 术语定义

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
