# Tasks: Sub-Spec S3 - 上下文优化策略

**父规范**: [spec-s3-context.md](spec-s3-context.md)
**估算总 LOC**: ~600
**总任务数**: 4
**关键路径**: S1-T8 → S3-T1 → S3-T2 → S3-T3 → S3-T4

---

## Task Breakdown

### Task 1: 上下文优化器 - 元数据注入 (~200 LOC)

**描述**: 实现上下文优化器的元数据注入功能，只注入 SKILL.md 的目录而非完整内容。

**验收标准**:
- [ ] 可注入所有 Skills 的 YAML frontmatter
- [ ] 可注入章节结构（TOC）
- [ ] 注入内容预估 Token 数 < 1,500
- [ ] 提供注入报告

**验证方式**:
```python
# 测试元数据注入
optimizer = ContextOptimizer(registry)
metadata = optimizer.inject_metadata()
assert "grill-me" in metadata
assert len(metadata) // 4 < 1500  # 预估 tokens
```

**涉及文件**:
- `agent_framework/skills/context_optimizer.py`
- `agent_framework/tests/unit/skills/test_context_optimizer.py`

**依赖**: S1-T8 (SkillRegistry)

**估算时间**: 3-4 小时

---

### Task 2: 上下文优化器 - 按需加载 (~200 LOC)

**描述**: 实现上下文优化器的按需加载功能，根据触发条件决定是否加载完整内容。

**验收标准**:
- [ ] 支持基于任务类型触发
- [ ] 支持基于用户查询触发
- [ ] 支持基于 LLM 调用触发
- [ ] 加载决策有日志记录

**验证方式**:
```python
# 测试按需加载
optimizer = ContextOptimizer(registry)
state = {"task_type": "grilling"}
assert optimizer.should_load_full_content("grill-me", state) is True
```

**涉及文件**:
- `agent_framework/skills/context_optimizer.py`
- `agent_framework/tests/unit/skills/test_context_optimizer.py`

**依赖**: Task 1 (元数据注入)

**估算时间**: 3-4 小时

---

### Task 3: 预算管理器 (~150 LOC)

**描述**: 实现预算管理器，管理上下文 Token 预算，防止过度加载。

**验收标准**:
- [ ] 可设置总预算和元数据保留
- [ ] 可判断是否可以加载
- [ ] 支持 LRU 驱逐策略
- [ ] 提供预算使用报告

**验证方式**:
```python
# 测试预算管理
budget = ContextBudget(total_budget=8000, metadata_reserve=1000)
assert budget.can_load("grill-me", 1000) is True
evicted = budget.evict_if_needed(5000)
assert isinstance(evicted, list)
```

**涉及文件**:
- `agent_framework/skills/budget_manager.py`
- `agent_framework/tests/unit/skills/test_budget_manager.py`

**依赖**: Task 2 (按需加载)

**估算时间**: 2-3 小时

---

### Task 4: 集成测试与性能验证 (~200 LOC)

**描述**: 编写 S3 的集成测试、性能基准测试和 A/B 测试。

**验收标准**:
- [ ] 优化器 + Registry 集成测试通过
- [ ] 优化器 + Loader 集成测试通过
- [ ] Token 消耗降低 ≥ 30%
- [ ] A/B 测试显示 LLM 精度下降 < 5%

**验证方式**:
```bash
# 运行集成测试
pytest agent_framework/tests/integration/skills/test_context_integration.py

# 运行性能测试
pytest agent_framework/tests/performance/test_token_consumption.py
```

**涉及文件**:
- `agent_framework/tests/integration/skills/test_context_integration.py`
- `agent_framework/tests/performance/test_token_consumption.py`
- `agent_framework/tests/ab_testing/test_optimization_ab.py`

**依赖**: Task 3 (所有之前任务)

**估算时间**: 3-4 小时

---

## Summary

- **总任务数**: 4
- **总估算 LOC**: ~600
- **关键路径**: S1-T8 → S3-T1 → S3-T2 → S3-T3 → S3-T4
- **估算总时间**: ~11-15 小时

---

## Dependencies on Other Sub-Specs

- **依赖 S1**: SkillRegistry, SkillLoader API
- **被 S4 依赖**: ContextOptimizer API
- **被 S5 依赖**: 性能测试数据

---

## Parallel Opportunities

- **S3 可以与 S2 并行开发** (都只依赖 S1)

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 查看 [tasks-s4-observability.md](tasks-s4-observability.md)
