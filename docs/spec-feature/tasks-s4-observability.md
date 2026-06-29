# Tasks: Sub-Spec S4 - Agent 可观测性建设

**父规范**: [spec-s4-observability.md](spec-s4-observability.md)
**估算总 LOC**: ~1,350
**总任务数**: 8
**关键路径**: S1-T8, S2-T7, S3-T4 → S4-T1 → S4-T2 → S4-T3 → S4-T4 → S4-T5 → S4-T6 → S4-T7 → S4-T8

---

## Task Breakdown

### Task 1: 可观测性数据模型 (~150 LOC)

**描述**: 定义可观测性系统的核心数据模型，包括 TraceData、ToolCallRecord、ErrorRecord 等。

**验收标准**:
- [ ] TraceData 包含 trace_id、span_id、skill_chain
- [ ] ToolCallRecord 包含工具调用完整信息
- [ ] ErrorRecord 包含异常类型和恢复动作
- [ ] ContextChange 包含状态变化明细
- [ ] 通过 mypy 类型检查

**验证方式**:
```python
# 测试数据模型
trace = TraceData(
    trace_id="xxx",
    parent_span_id=None,
    span_id="yyy",
    skill_chain=["grill-me"],
    timestamps={},
    state_transitions=[]
)
assert trace.trace_id == "xxx"
```

**涉及文件**:
- `agent_framework/observability/models/__init__.py`
- `agent_framework/observability/models/trace.py`
- `agent_framework/observability/models/error.py`
- `agent_framework/observability/models/metrics.py`

**依赖**: S1-T8, S2-T7, S3-T4

**估算时间**: 3-4 小时

---

### Task 2: 链路追踪管理器 (~200 LOC)

**描述**: 实现链路追踪管理器，记录 Skill 调用链和状态转换。

**验收标准**:
- [ ] 可开始新的追踪并生成 trace_id
- [ ] 可创建 span 并记录父子关系
- [ ] 可结束 span 并记录结果
- [ ] 可获取完整追踪数据
- [ ] 支持跨 Skill 和 Workflow 层追踪

**验证方式**:
```python
# 测试链路追踪
manager = TraceManager()
trace_id = manager.start_trace({})
span_id = manager.create_span(trace_id, "grill-me")
manager.end_span(trace_id, span_id, {"success": True})
trace = manager.get_trace(trace_id)
assert trace.skill_chain == ["grill-me"]
```

**涉及文件**:
- `agent_framework/observability/tracing.py`
- `agent_framework/tests/unit/observability/test_tracing.py`

**依赖**: Task 1 (数据模型)

**估算时间**: 4-5 小时

---

### Task 3: 异常诊断器 (~150 LOC)

**描述**: 实现异常诊断器，识别五类异常并提供恢复建议。

**验收标准**:
- [ ] 可识别 P0 异常（可用性、执行、数据）
- [ ] 可识别 P1 异常（依赖）
- [ ] 可识别 P2 异常（性能）
- [ ] 可提供恢复建议
- [ ] 可返回诊断报告

**验证方式**:
```python
# 测试异常诊断
diagnostics = ErrorDiagnostics()
report = diagnostics.diagnate(
    ToolNotFoundError("tool-not-found"),
    SkillContext(session_path="/tmp", state={})
)
assert report.severity == "P0"
assert report.recovery_action is not None
```

**涉及文件**:
- `agent_framework/observability/diagnostics.py`
- `agent_framework/tests/unit/observability/test_diagnostics.py`

**依赖**: Task 1 (数据模型)

**估算时间**: 3-4 小时

---

### Task 4: 幻觉检测器 - 引用源验证 (~200 LOC)

**描述**: 实现基于引用源验证的幻觉检测。

**验收标准**:
- [ ] 可从输出中提取主张（claims）
- [ ] 可验证主张是否基于引用源
- [ ] 可返回幻觉检测报告
- [ ] 可计算贴地度分数

**验证方式**:
```python
# 测试幻觉检测
detector = HallucinationDetector()
report = detector.check_by_source_validation(
    "The capital of France is Paris.",
    ["France is a country in Europe."]
)
assert report.has_hallucination is False
```

**涉及文件**:
- `agent_framework/observability/hallucination.py` (引用源验证部分)
- `agent_framework/tests/unit/observability/test_hallucination.py`

**依赖**: Task 1 (数据模型)

**估算时间**: 4-5 小时

---

### Task 5: 幻觉检测器 - LLM 自我评估 (~150 LOC)

**描述**: 实现基于 LLM 自我评估的幻觉检测。

**验收标准**:
- [ ] 可让 LLM 评估自己输出的幻觉概率
- [ ] 可异步执行（不阻塞主流程）
- [ ] 可返回评估结果
- [ ] 可与引用源验证组合使用

**验证方式**:
```python
# 测试 LLM 自我评估（异步）
import asyncio
detector = HallucinationDetector()
async def test():
    report = await detector.check_by_llm_self_critique_async("...")
    assert report.critique_result is not None
```

**涉及文件**:
- `agent_framework/observability/hallucination.py` (LLM 自我评估部分)
- `agent_framework/tests/unit/observability/test_hallucination.py`

**依赖**: Task 4 (引用源验证)

**估算时间**: 3-4 小时

---

### Task 6: 污染检测器 (~200 LOC)

**描述**: 实现上下文污染检测器，检测未授权的状态修改。

**验收标准**:
- [ ] 可通过状态快照对比检测污染
- [ ] 可通过写入白名单检测污染
- [ ] 可返回污染检测报告
- [ ] 可列出意外变更

**验证方式**:
```python
# 测试污染检测
detector = ContextPollutionDetector()
before = {"user": "Alice", "session": "123"}
after = {"user": "Alice", "session": "456", "unauthorized": True}
report = detector.check_by_snapshot_comparison(before, after)
assert report.has_pollution is True
```

**涉及文件**:
- `agent_framework/observability/pollution.py`
- `agent_framework/tests/unit/observability/test_pollution.py`

**依赖**: Task 1 (数据模型)

**估算时间**: 4-5 小时

---

### Task 7: 可观测性 Dashboard (~200 LOC)

**描述**: 实现可观测性 Dashboard，提供 CLI 和 HTML 报告。

**验收标准**:
- [ ] 可查看链路追踪数据
- [ ] 可查看异常统计
- [ ] 可查看技能排行（调用次数、错误率）
- [ ] 可生成 HTML 报告

**验证方式**:
```bash
# 测试 Dashboard
python -m agent_framework.observability.dashboard view --trace-id xxx
python -m agent_framework.observability.dashboard report --output report.html
```

**涉及文件**:
- `agent_framework/observability/dashboard.py`
- `agent_framework/tests/unit/observability/test_dashboard.py`

**依赖**: Task 2, Task 3, Task 5, Task 6

**估算时间**: 4-5 小时

---

### Task 8: 集成测试与存储 (~200 LOC)

**描述**: 编写 S4 的集成测试、数据存储和清理机制。

**验收标准**:
- [ ] 完整链路追踪测试通过
- [ ] 异常诊断 + 恢复测试通过
- [ ] 幻觉检测端到端测试通过
- [ ] 数据存储和保留策略生效
- [ ] 数据清理任务正常运行

**验证方式**:
```bash
# 运行集成测试
pytest agent_framework/tests/integration/observability/test_observability_integration.py

# 验证数据存储
ls agent_framework/observability/storage/traces/
```

**涉及文件**:
- `agent_framework/tests/integration/observability/test_observability_integration.py`
- `agent_framework/observability/storage/` (目录结构)
- `agent_framework/observability/cleanup.py`

**依赖**: Task 7 (所有之前任务)

**估算时间**: 3-4 小时

---

## Summary

- **总任务数**: 8
- **总估算 LOC**: ~1,350
- **关键路径**: S1-T8, S2-T7, S3-T4 → S4-T1 → S4-T2 → S4-T3 → S4-T4 → S4-T5 → S4-T6 → S4-T7 → S4-T8
- **估算总时间**: ~28-38 小时

---

## Dependencies on Other Sub-Specs

- **依赖 S1**: Middleware API
- **依赖 S2**: 生命周期管理
- **依赖 S3**: ContextOptimizer API
- **被 S5 依赖**: 所有可观测性数据

---

## Risk Mitigation

- **异步处理**: S4-T5 (LLM 自我评估) 必须异步执行，不阻塞主流程
- **降级机制**: Dashboard 故障不应影响主流程
- **性能控制**: 链路追踪开销 < 5%

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 查看 [tasks-s5-integration.md](tasks-s5-integration.md)
