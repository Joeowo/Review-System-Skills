# Sub-Spec: S4 - Agent 可观测性建设

**父规范**: [01-master-spec.md](01-master-spec.md)
**估算 LOC**: ~1,350
**依赖**: S1, S2, S3
**优先级**: P0

---

## Objective

建立技能调试（Debugging）与链路追踪机制，针对 Skill 执行过程中的工具调用异常、幻觉输出及上下文污染问题进行诊断与修复。通过可观测性数据收集、链路追踪、异常诊断和幻觉检测，保障多跳推理任务的任务完成率。

---

## Interfaces

### Consumes（消费）

- **S1 Middleware**: 拦截执行流程，收集可观测性数据
- **S1 SkillResult**: 获取技能执行结果
- **AgentState**: 获取状态变化
- **LLM API**: 获取模型输出（用于幻觉检测）

### Produces（产出）

- **Tracing API**: 链路追踪数据
- **Diagnostics API**: 异常诊断报告
- **Hallucination API**: 幻觉检测结果
- **Pollution API**: 污染检测结果
- **Dashboard API**: 可观测性数据查询接口

### External Dependencies（外部依赖）

- `datetime` - 时间戳
- `uuid` - trace_id 生成
- `json` - 数据存储
- `dataclasses` - 数据模型
- `asyncio` - 异步处理（幻觉检测）

---

## Component Structure

```
agent_framework/observability/
├── __init__.py
├── tracing.py                # 链路追踪 (~350 LOC)
├── diagnostics.py           # 异常诊断 (~300 LOC)
├── hallucination.py          # 幻觉检测 (~400 LOC)
├── pollution.py             # 污染检测 (~250 LOC)
└── dashboard.py             # 可观测性 Dashboard (~500 LOC)

Models:
agent_framework/observability/models/
├── __init__.py
├── trace.py                 # 链路追踪数据模型 (~100 LOC)
├── error.py                 # 错误记录模型 (~50 LOC)
└── metrics.py               # 性能指标模型 (~50 LOC)

Tests:
agent_framework/tests/unit/observability/
├── test_tracing.py
├── test_diagnostics.py
├── test_hallucination.py
└── test_pollution.py

Integration Tests:
agent_framework/tests/integration/observability/
└── test_observability_integration.py

Storage:
agent_framework/observability/storage/
├── traces/                 # 链路追踪数据
│   └── {date}/{trace_id}.json
├── errors/                 # 异常记录
│   └── {date}/{error_id}.json
└── metrics/                # 性能指标
    └── skill_metrics.json
```

---

## Commands

```bash
# 查看链路追踪数据
python -m agent_framework.observability.tracing view --trace-id xxx

# 查看异常统计
python -m agent_framework.observability.diagnostics stats

# 运行幻觉检测
python -m agent_framework.observability.hallucination check --output "..."

# 启动可观测性 Dashboard
python -m agent_framework.observability.dashboard
```

---

## Code Style

遵循主规范编码风格，示例：

```python
"""agent_framework/observability 可观测性示例代码风格"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import uuid
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class TraceData:
    """执行链路追踪数据"""
    trace_id: str
    parent_span_id: Optional[str]
    span_id: str
    skill_chain: list[str]
    timestamps: dict[str, datetime]
    state_transitions: list[StateTransition]

class TraceManager:
    """链路追踪管理器"""

    def start_trace(self, context: dict) -> str:
        """开始一个新的追踪

        Returns:
            trace_id
        """
        trace_id = str(uuid.uuid4())
        logger.info("Trace started", trace_id=trace_id)
        return trace_id

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
        span_id = str(uuid.uuid4())
        logger.info(
            "Span created",
            trace_id=trace_id,
            span_id=span_id,
            skill=skill_name
        )
        return span_id

    def end_span(
        self,
        trace_id: str,
        span_id: str,
        result: dict
    ) -> None:
        """结束一个 span"""
        logger.info(
            "Span ended",
            trace_id=trace_id,
            span_id=span_id,
            success=result.get("success", False)
        )
```

---

## Testing Strategy

### 单元测试

| 组件 | 测试内容 | 覆盖率目标 |
|------|----------|-----------|
| **TraceManager** | trace_id/span_id 传递、父子关系 | ≥ 80% |
| **ErrorDiagnostics** | 异常分类、诊断准确性 | ≥ 80% |
| **HallucinationDetector** | 幻觉检测准确率 | ≥ 70% |
| **PollutionDetector** | 污染检测能力 | ≥ 80% |

### 集成测试

- 完整链路追踪测试
- 异常诊断 + 恢复测试
- 幻觉检测端到端测试

### A/B 测试

- 不同幻觉检测方法的准确率对比
- 有无可观测性的性能对比

### 测试示例

```python
class TestTraceManager:
    """链路追踪管理器单元测试"""

    def test_trace_id_propagation(self):
        """测试 trace_id 正确传递"""
        manager = TraceManager()
        trace_id = manager.start_trace({})
        span_id = manager.create_span(trace_id, "test-skill")
        manager.end_span(trace_id, span_id, {"success": True})

        trace = manager.get_trace(trace_id)
        assert trace.trace_id == trace_id
        assert len(trace.skill_chain) == 1

    def test_parent_child_relationship(self):
        """测试父子关系正确性"""
        manager = TraceManager()
        trace_id = manager.start_trace({})
        parent_span = manager.create_span(trace_id, "parent-skill")
        child_span = manager.create_span(
            trace_id,
            "child-skill",
            parent_span_id=parent_span
        )

        trace = manager.get_trace(trace_id)
        # 验证父子关系
```

---

## Boundaries

### Always Do（必须做）

- ✅ 记录所有关键执行事件
- ✅ 记录所有异常和错误
- ✅ 异步处理幻觉检测（不阻塞主流程）
- ✅ 提供降级机制（可观测性系统故障不影响主流程）

### Ask First（先询问）

- 🤔 修改数据保留策略
- 🤔 添加新的异常类型
- 🤔 修改检测算法

### Never Do（禁止做）

- ❌ 记录敏感信息（API key、用户数据）
- ❌ 可观测性系统故障导致主流程失败
- ❌ 同步执行幻觉检测（阻塞主流程）

---

## Success Criteria

### 功能验证

- [ ] 链路追踪可完整记录 Skill 调用链
- [ ] 异常诊断可识别 P0/P1 异常类型
- [ ] 幻觉检测准确率 ≥ 70%
- [ ] 污染检测可捕获未授权写入
- [ ] 可观测性数据可通过 Dashboard 查看

### 质量指标

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 链路追踪开销 < 5%
- [ ] 幻觉检测准确率 ≥ 70%

### 性能目标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| **链路追踪开销** | < 5% | 性能测试 |
| **异常记录延迟** | < 10ms | 单元测试 |
| **幻觉检测时间** | < 1s (异步) | 单元测试 |

---

## Open Questions

1. **数据保留策略**: traces 保留 7 天是否足够？（当前假设 7 天）
2. **幻觉检测触发**: 何时触发幻觉检测？（当前假设异步，所有输出）
3. **Dashboard 实现**: 使用 Web 还是 CLI？（当前假设 CLI + HTML 报告）

---

## Related Documents

- [01-master-spec.md](01-master-spec.md) - 主规范
- [02-sub-spec-index.md](02-sub-spec-index.md) - 子规范索引
- [spec-s1-registry.md](spec-s1-registry.md) - 依赖的 S1 规范
- [spec-s2-factory.md](spec-s2-factory.md) - 依赖的 S2 规范
- [spec-s3-context.md](spec-s3-context.md) - 依赖的 S3 规范
- [docs/spec-feature/requirements/04-observability.md](requirements/04-observability.md) - 对应需求文档

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 进入实施阶段，编写详细任务
