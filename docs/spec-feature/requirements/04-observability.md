# 需求 4：Agent 可观测性建设

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## 需求概述

建立技能调试（Debugging）与链路追踪机制，针对 Skill 执行过程中的工具调用异常、幻觉输出及上下文污染问题进行诊断与修复，保障多跳推理任务的任务完成率。

---

## 功能需求

### FR-4.1：可观测性数据收集

**描述**：收集 Skill 执行过程中的关键可观测性数据。

**数据类型**：

#### 4.1.1 执行链路追踪

```python
@dataclass
class TraceData:
    """执行链路追踪数据"""
    trace_id: str                  # 全局追踪 ID
    parent_span_id: Optional[str]  # 父 span ID
    span_id: str                   # 当前 span ID

    skill_chain: List[str]         # Skill 调用链
    timestamps: Dict[str, datetime] # 各阶段时间戳

    state_transitions: List[StateTransition]  # 状态转换记录

@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: str
    to_state: str
    timestamp: datetime
    trigger: str                   # 触发原因
```

#### 4.1.2 工具调用记录

```python
@dataclass
class ToolCallRecord:
    """工具调用记录"""
    tool_name: str                 # 工具名称
    skill_name: str                # 所属 Skill
    input: Dict[str, Any]          # 输入参数
    output: Any                    # 输出结果
    duration_ms: float             # 执行耗时
    status: str                    # success | error | timeout
    error: Optional[str] = None    # 错误信息
```

#### 4.1.3 异常与错误

```python
@dataclass
class ErrorRecord:
    """异常与错误记录"""
    error_type: str                # 错误类型
    skill_name: str                # 发生在哪个 Skill
    message: str                   # 错误消息
    stack_trace: str               # 堆栈跟踪
    recovery_action: str           # 恢复动作
    timestamp: datetime
```

#### 4.1.4 上下文变化

```python
@dataclass
class ContextChange:
    """上下文变化记录"""
    skill_name: str                # 哪个 Skill 修改的
    before: Dict[str, Any]         # 修改前状态
    after: Dict[str, Any]          # 修改后状态
    delta: Delta                   # 变更明细

@dataclass
class Delta:
    """变更明细"""
    added: List[str]               # 新增的字段
    removed: List[str]             # 删除的字段
    modified: Dict[str, Change]    # 修改的字段

@dataclass
class Change:
    """字段变更详情"""
    old_value: Any
    new_value: Any
```

---

### FR-4.2：链路追踪

**描述**：覆盖跨 Skill 和 Workflow 层的链路追踪。

**追踪边界**：

```
┌─────────────────────────────────────────────────────────┐
│                    Workflow 层追踪                        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  节点 A → 节点 B → 节点 C → 节点 D                │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   跨 Skill 追踪                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  grill-me → grill-you → advance-task               │ │
│  │  (trace_id: xxx)  (trace_id: xxx)  (trace_id: xxx)  │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**接口定义**：

```python
class TraceManager:
    """链路追踪管理器"""

    def start_trace(self, context: SkillContext) -> str:
        """开始一个新的追踪
        Returns:
            trace_id
        """

    def create_span(
        self,
        trace_id: str,
        skill_name: str,
        parent_span_id: Optional[str] = None
    ) -> str:
        """创建一个 span
        Returns:
            span_id
        """

    def end_span(
        self,
        trace_id: str,
        span_id: str,
        result: SkillResult
    ) -> None:
        """结束一个 span"""

    def get_trace(self, trace_id: str) -> TraceData:
        """获取完整的追踪数据"""
```

---

### FR-4.3：工具调用异常诊断

**描述**：诊断五类工具调用异常。

**异常分类与处理**：

| 优先级 | 类型 | 说明 | 检测方式 |
|--------|------|------|----------|
| **P0** | 可用性异常 | Tool 不存在或无法加载 | ToolNotFoundError, ToolLoadError |
| **P0** | 执行异常 | Tool 执行过程中的错误 | ToolExecutionError, TimeoutError |
| **P0** | 数据异常 | 输入输出数据问题 | InvalidInputError, MalformedOutputError |
| **P1** | 依赖异常 | 依赖的资源不可用 | ContextFileNotFoundError |
| **P2** | 性能异常 | 执行过慢或资源消耗高 | SlowExecutionWarning |

**诊断接口**：

```python
class ErrorDiagnostics:
    """错误诊断器"""

    def diagnose(
        self,
        error: Exception,
        context: SkillContext
    ) -> DiagnosisReport:
        """诊断错误并提供恢复建议
        Returns:
            DiagnosisReport
        """

    def get_recovery_action(
        self,
        error_type: str
    ) -> str:
        """获取错误类型的恢复动作"""

@dataclass
class DiagnosisReport:
    """诊断报告"""
    error_type: str
    severity: str                  # P0 | P1 | P2
    root_cause: str               # 根本原因分析
    recovery_action: str          # 恢复动作
    prevention_suggestion: str    # 预防建议
```

---

### FR-4.4：幻觉输出与上下文污染检测

**描述**：检测 Skill 执行过程中的幻觉输出和上下文污染。

#### 4.4.1 幻觉检测

**检测方法**：

```python
class HallucinationDetector:
    """幻觉检测器"""

    def check_by_source_validation(
        self,
        output: str,
        grounding_sources: List[str]
    ) -> HallucinationReport:
        """基于引用源验证
        检查输出是否基于给定的引用源
        Returns:
            HallucinationReport
        """

    def check_by_llm_self_critique(
        self,
        output: str
    ) -> HallucinationReport:
        """基于 LLM 自我评估
        让 LLM 评估自己输出的幻觉概率
        Returns:
            HallucinationReport
        """

    def extract_claims(self, output: str) -> List[str]:
        """从输出中提取主张（claims）"""

    def verify_claim_against_sources(
        self,
        claim: str,
        sources: List[str]
    ) -> bool:
        """验证主张是否基于引用源"""

@dataclass
class HallucinationReport:
    """幻觉检测报告"""
    has_hallucination: bool
    hallucinated_claims: List[str]     # 幻觉的主张
    grounding_score: float             # 贴地度分数
    critique_result: Optional[str]     # LLM 自我评估结果
```

#### 4.4.2 上下文污染检测

**检测方法**：

```python
class ContextPollutionDetector:
    """上下文污染检测器"""

    def check_by_snapshot_comparison(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> PollutionReport:
        """基于状态快照对比
        执行前后对比状态快照
        Returns:
            PollutionReport
        """

    def check_by_whitelist(
        self,
        skill_name: str,
        actual_writes: List[str],
        whitelist: Dict[str, List[str]]
    ) -> PollutionReport:
        """基于写入白名单
        检测未授权的写入
        Returns:
            PollutionReport
        """

    def detect_unexpected_changes(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> List[UnexpectedChange]:
        """检测意外变更"""

@dataclass
class PollutionReport:
    """上下文污染报告"""
    has_pollution: bool
    unauthorized_writes: List[str]     # 未授权写入
    unexpected_changes: List[UnexpectedChange]
    severity: str                      # low | medium | high

@dataclass
class UnexpectedChange:
    """意外变更"""
    field: str
    old_value: Any
    new_value: Any
    expected: bool                    # 是否为预期变更
```

---

## 非功能需求

### NFR-4.1：性能

- 链路追踪开销 < 5%
- 异常记录延迟 < 10ms
- 幻觉检测 < 1s（异步）

### NFR-4.2：可扩展性

- 支持自定义异常类型
- 支持自定义检测规则

### NFR-4.3：可靠性

- 可观测性系统故障不影响主流程
- 提供降级机制

---

## 数据存储

### 存储结构

```
agent_framework/
├── observability/
│   ├── traces/              # 链路追踪数据
│   │   ├── {date}/
│   │   │   └── {trace_id}.json
│   ├── errors/              # 异常记录
│   │   ├── {date}/
│   │   │   └── {error_id}.json
│   └── metrics/             # 性能指标
│       └── skill_metrics.json
```

### 数据保留策略

| 数据类型 | 保留时间 | 原因 |
|----------|----------|------|
| 链路追踪 | 7 天 | 用于调试和问题排查 |
| 异常记录 | 30 天 | 用于趋势分析 |
| 性能指标 | 90 天 | 用于性能优化 |

---

## 可观测性 Dashboard

### 显示指标

| 类别 | 指标 |
|------|------|
| **执行统计** | 总调用次数、成功率、平均耗时 |
| **异常统计** | 异常分类统计、异常趋势 |
| **Skill 排行** | 调用次数、平均耗时、错误率 |
| **链路追踪** | 实时追踪流、慢查询分析 |

---

## 架构决策

### AD-4.1：可观测性数据来源

**决策**：收集四类核心数据（链路追踪 + 工具调用 + 异常错误 + 上下文变化）

**理由**：
- 覆盖执行全生命周期
- 支持问题回溯和诊断
- 不收集敏感数据

### AD-4.2：链路追踪边界

**决策**：覆盖跨 Skill + Workflow 层

**理由**：
- 两者是主要的执行边界
- Skill 内部追踪作为可选的细粒度调试

### AD-4.3：异常诊断范围

**决策**：五类异常全覆盖，优先级分层

**理由**：
- P0/P1 影响功能，必须处理
- P2 作为性能优化的参考

### AD-4.4：幻觉与污染检测

**决策**：
- 幻觉检测：引用源验证 + LLM 自我评估
- 污染检测：状态快照对比 + 写入白名单

**理由**：
- 多方法组合提高准确率
- 白名单机制防止误报

---

## 验收标准

- [ ] 链路追踪可完整记录 Skill 调用链
- [ ] 异常诊断可识别 P0/P1 异常类型
- [ ] 幻觉检测准确率 ≥ 70%
- [ ] 污染检测可捕获未授权写入
- [ ] 可观测性数据可通过 Dashboard 查看

---

## 测试计划

### 链路追踪测试

- 验证 trace_id 和 span_id 的正确传递
- 验证父子关系的正确性

### 异常诊断测试

- 模拟各类异常，验证诊断准确性
- 验证恢复建议的有效性

### 幻觉检测测试

- 构造已知有幻觉的输出，验证检测能力
- A/B 测试不同检测方法的准确率

### 污染检测测试

- 模拟未授权写入，验证检测能力
- 验证白名单机制的有效性

---

## 相关文档

- [01-skill-registry-middleware.md](01-skill-registry-middleware.md) - 技能注册表与中间件
- [02-skill-factory.md](02-skill-factory.md) - 标准化技能工厂
- [03-context-optimization.md](03-context-optimization.md) - 上下文优化策略
- [CONTEXT.md](../../CONTEXT.md) - 术语定义

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
