# Sub-Spec Index

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## Overview

本主规范拆分为 **5 个子规范**，每个子规范负责一个独立的功能模块，遵循以下原则：

1. **最大 2000 LOC per sub-spec** - 理想范围 500-1500 LOC
2. **内聚边界** - 每个子规范是逻辑完整的功能单元
3. **最小耦合** - 子规范之间有清晰的接口
4. **独立测试** - 每个子规范可独立测试

---

## Sub-Spec Breakdown

| ID | 子规范名称 | 估算 LOC | 依赖 | 优先级 | 状态 |
|----|-----------|----------|------|--------|------|
| **S1** | 技能注册表与中间件调度层 | ~1,450 | - | P0 | Pending |
| **S2** | 标准化技能工厂与生命周期 | ~1,250 | S1 | P0 | Pending |
| **S3** | 上下文优化策略 | ~600 | S1 | P0 | Pending |
| **S4** | Agent 可观测性建设 | ~1,350 | S1, S2, S3 | P0 | Pending |
| **S5** | 集成测试与文档 | ~900 | S1-S4 | P0 | Pending |

**子规范总估算 LOC: ~7,550 LOC**

---

## Dependency Graph

```
                    ┌─────────────┐
                    │     S1      │
                    │  Registry + │
                    │ Middleware  │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼──────┐    ┌────▼────┐
    │   S2    │      │     S3     │    │   S4    │
    │ Factory │      │  Context   │    │Observing│
    └────┬────┘      └─────┬──────┘    └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │     S5      │
                    │ Integration │
                    │  + Docs     │
                    └─────────────┘
```

---

## Sub-Spec Summaries

### S1: 技能注册表与中间件调度层 (~1,450 LOC)

**目标**: 实现业务技能与模型逻辑的解耦

**核心组件**:
- Skill Registry（技能注册表）
- Middleware 调度层
- Skill Loader（动态加载）
- 并行执行器

**文件**: [spec-s1-registry.md](spec-s1-registry.md)

---

### S2: 标准化技能工厂与生命周期 (~1,250 LOC)

**目标**: 提升通用能力复用率

**核心组件**:
- SKILL.md 验证器
- SKILL.md 迁移工具
- 生命周期管理
- 标准化指令集

**文件**: [spec-s2-factory.md](spec-s2-factory.md)

---

### S3: 上下文优化策略 (~600 LOC)

**目标**: 降低单次任务的 Token 消耗

**核心组件**:
- 上下文优化器（目录注入）
- 按需加载器
- 预算管理器
- 两阶段加载协调

**文件**: [spec-s3-context.md](spec-s3-context.md)

---

### S4: Agent 可观测性建设 (~1,350 LOC)

**目标**: 建立技能调试与链路追踪机制

**核心组件**:
- 链路追踪管理器
- 异常诊断器
- 幻觉检测器
- 污染检测器
- 可观测性 Dashboard

**文件**: [spec-s4-observability.md](spec-s4-observability.md)

---

### S5: 集成测试与文档 (~900 LOC)

**目标**: 确保系统整体质量和可维护性

**核心组件**:
- 端到端集成测试
- 性能基准测试
- A/B 测试框架
- 用户文档

**文件**: [spec-s5-integration.md](spec-s5-integration.md)

---

## Implementation Order

### Phase 1: Foundation (Week 1-2)
- [ ] S1: 技能注册表与中间件调度层

### Phase 2: Standardization (Week 2-3)
- [ ] S2: 标准化技能工厂与生命周期
- [ ] S3: 上下文优化策略

### Phase 3: Observability (Week 3-4)
- [ ] S4: Agent 可观测性建设

### Phase 4: Integration (Week 5-6)
- [ ] S5: 集成测试与文档

---

## Risk Mitigation

| 风险 | 影响子规范 | 缓解措施 |
|------|-----------|----------|
| SKILL.md 格式迁移成本 | S2, S5 | 提供自动化迁移工具 |
| 上下文优化影响 LLM 精度 | S3, S5 | A/B 测试验证，支持回退 |
| 可观测性系统性能开销 | S4, S5 | 采样策略，异步处理 |
| 现有 Skills 兼容性 | 全部 | 渐进式迁移，保持向后兼容 |

---

## Success Criteria

### 每个 Sub-Spec 完成
- [ ] 所有接口定义明确
- [ ] 所有数据模型实现
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过
- [ ] 文档完整

### 整体系统完成
- [ ] 所有子规范集成成功
- [ ] 端到端测试通过
- [ ] 性能目标达成
- [ ] 用户文档完整

---

## Related Documents

- [01-master-spec.md](01-master-spec.md) - 主规范
- [03-master-plan.md](03-master-plan.md) - 主实施计划（待生成）
- [docs/spec-feature/requirements/](requirements/) - 需求文档

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 审查子规范分解后，进入 Phase 3: 主实施计划
