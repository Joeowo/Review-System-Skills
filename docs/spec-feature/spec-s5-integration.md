# Sub-Spec: S5 - 集成测试与文档

**父规范**: [01-master-spec.md](01-master-spec.md)
**估算 LOC**: ~900
**依赖**: S1, S2, S3, S4
**优先级**: P0

---

## Objective

确保技能系统重构的整体质量和可维护性。通过端到端集成测试、性能基准测试、A/B 测试框架和完整的用户文档，验证所有子规范的集成效果和系统性能。

---

## Interfaces

### Consumes（消费）

- **S1 SkillRegistry**: 测试注册和查询功能
- **S2 SkillValidator**: 测试验证和迁移功能
- **S3 ContextOptimizer**: 测试上下文优化功能
- **S4 Observability**: 测试可观测性功能

### Produces（产出）

- **集成测试套件**: 端到端测试覆盖
- **性能基准**: Token 消耗、响应时间对比
- **A/B 测试框架**: 优化前后对比
- **用户文档**: 使用指南、API 文档

### External Dependencies（外部依赖）

- `pytest` - 测试框架
- `pytest-benchmark` - 性能基准测试
- `matplotlib` - 可视化（可选）

---

## Component Structure

```
agent_framework/tests/
├── e2e/
│   └── skill_system/              # 端到端集成测试 (~300 LOC)
│       ├── test_e2e_full_flow.py
│       ├── test_e2e_grill_me.py
│       └── test_e2e_parallel_skills.py
│
├── performance/
│   └── benchmarks/               # 性能基准测试 (~200 LOC)
│       ├── test_token_consumption.py
│       ├── test_response_time.py
│       └── test_trace_overhead.py
│
└── ab_testing/
    └── comparisons/              # A/B 测试框架 (~200 LOC)
        ├── test_optimization_ab.py
        └── test_accuracy_ab.py

Documentation:
docs/spec-feature/user/
├── user_guide.md                 # 用户指南 (~100 LOC)
├── api_reference.md             # API 文档 (~100 LOC)
└── migration_guide.md           # 迁移指南 (~100 LOC)
```

---

## Commands

```bash
# 运行所有集成测试
pytest agent_framework/tests/e2e/

# 运行性能基准测试
pytest agent_framework/tests/performance/ --benchmark-only

# 运行 A/B 测试
pytest agent_framework/tests/ab_testing/

# 生成测试覆盖率报告
pytest --cov=agent_framework --cov-report=html
```

---

## Code Style

遵循主规范编码风格，示例：

```python
"""agent_framework/tests 集成测试示例代码风格"""

import pytest
from pathlib import Path
from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.observability.tracing import TraceManager

class TestE2ESkillFlow:
    """端到端技能流程测试"""

    def test_full_grill_me_flow(self):
        """测试完整的 grill-me 技能流程"""
        # 1. 初始化 Registry
        registry = SkillRegistry(Path("skills/"))
        registry.discover()

        # 2. 初始化 Middleware
        middleware = SkillMiddleware(registry)

        # 3. 初始化追踪
        trace_manager = TraceManager()
        trace_id = trace_manager.start_trace({})

        # 4. 执行技能
        state = {"task_type": "grilling", "user_query": "/grill-me"}
        result = middleware.route_and_execute(state)

        # 5. 验证结果
        assert result.success
        assert "grill-me" in result.data.get("skills_used", [])

        # 6. 验证追踪
        trace = trace_manager.get_trace(trace_id)
        assert "grill-me" in trace.skill_chain

class TestTokenConsumption:
    """Token 消耗测试"""

    def test_metadata_injection_tokens(self):
        """测试元数据注入的 Token 消耗"""
        registry = SkillRegistry(Path("skills/"))
        registry.discover()

        optimizer = ContextOptimizer(registry)
        metadata = optimizer.inject_metadata()

        # 验证元数据注入 < 1500 tokens
        estimated_tokens = len(metadata) // 4
        assert estimated_tokens < 1500
```

---

## Testing Strategy

### 端到端集成测试

| 场景 | 测试内容 | 验证点 |
|------|----------|--------|
| **完整流程** | 用户请求 → 路由 → 执行 → 返回 | 成功完成 |
| **错误处理** | 技能加载失败、异常情况 | 正确降级 |
| **并行执行** | 多技能同时执行 | 状态隔离 |
| **可观测性** | 链路追踪完整记录 | 数据完整 |

### 性能基准测试

| 指标 | 测试方法 | 目标 |
|------|----------|------|
| **Token 消耗** | 统计元数据注入和完整加载 | 优化后降低 ≥ 30% |
| **响应时间** | 测量端到端执行时间 | < 2s |
| **追踪开销** | 对比有无可观测性 | < 5% |

### A/B 测试

| 维度 | 测试内容 | 验证方法 |
|------|----------|----------|
| **Token 消耗** | 优化前后对比 | 统计检验 |
| **响应准确率** | 优化前后对比 | 人工评估 |
| **用户体验** | 优化前后对比 | 用户反馈 |

---

## Boundaries

### Always Do（必须做）

- ✅ 所有集成测试必须有明确的目标和验证点
- ✅ 性能测试必须有明确的目标值
- ✅ A/B 测试必须有统计显著性检验
- ✅ 用户文档必须包含示例和故障排除

### Ask First（先询问）

- 🤔 修改性能目标值
- 🤔 添加新的测试场景
- 🤔 修改文档结构

### Never Do（禁止做）

- ❌ 编写无明确验证点的测试
- ❌ 绕过测试直接标记为通过
- ❌ 编写过时或不准确的文档

---

## Success Criteria

### 功能验证

- [ ] 所有端到端测试通过
- [ ] 性能基准测试达成目标
- [ ] A/B 测试显示显著改善
- [ ] 用户文档完整准确

### 质量指标

- [ ] 集成测试覆盖率 ≥ 70%
- [ ] 性能测试目标达成率 100%
- [ ] 文档完整性 100%

### 测试目标

| 目标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| **Token 消耗降低** | 0% | ≥ 30% | 性能测试 |
| **响应准确率** | 100% | 下降 < 5% | A/B 测试 |
| **集成测试通过率** | N/A | 100% | CI/CD |

---

## Documentation Structure

### User Guide (user_guide.md)

```
1. 快速开始
2. 技能系统概览
3. 使用技能
   3.1 基本使用
   3.2 并行执行
   3.3 错误处理
4. 管理技能
   4.1 验证 SKILL.md
   4.2 迁移旧格式
   4.3 查看技能统计
5. 可观测性
   5.1 查看链路追踪
   5.2 分析异常
   5.3 Dashboard 使用
6. 故障排除
```

### API Reference (api_reference.md)

```
1. Skill Registry API
2. Middleware API
3. Context Optimizer API
4. Observability API
```

### Migration Guide (migration_guide.md)

```
1. 迁移概览
2. 准备工作
3. 迁移步骤
4. 验证结果
5. 回滚方案
```

---

## Open Questions

1. **性能目标**: Token 消耗降低 30% 是否可实现？（需要实际测试验证）
2. **A/B 测试周期**: A/B 测试需要运行多久？（当前假设 1 周）
3. **文档语言**: 用户文档使用中文还是英文？（当前假设中文）

---

## Related Documents

- [01-master-spec.md](01-master-spec.md) - 主规范
- [02-sub-spec-index.md](02-sub-spec-index.md) - 子规范索引
- [spec-s1-registry.md](spec-s1-registry.md) - 依赖的 S1 规范
- [spec-s2-factory.md](spec-s2-factory.md) - 依赖的 S2 规范
- [spec-s3-context.md](spec-s3-context.md) - 依赖的 S3 规范
- [spec-s4-observability.md](spec-s4-observability.md) - 依赖的 S4 规范

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 进入实施阶段，编写详细任务
