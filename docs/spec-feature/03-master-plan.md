# Master Implementation Plan: 技能系统重构

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## Implementation Strategy

### 整体策略

采用 **渐进式增量实施** 策略：

1. **自底向上** - 从基础设施（S1）开始，逐步构建上层功能
2. **并行开发** - S2 和 S3 可以并行开发（都只依赖 S1）
3. **持续集成** - 每个子规范完成后立即集成测试
4. **风险控制** - 高风险组件（S4 幻觉检测）延后实施

### 关键原则

- ✅ **保持向后兼容** - 现有 Skills 和 Workflow 继续工作
- ✅ **渐进式迁移** - 支持新旧两种方式并存
- ✅ **持续验证** - 每个阶段都有明确的验证标准
- ✅ **风险可控** - 高风险组件有降级方案

---

## Sub-Spec Implementation Order

### Phase 1: Foundation (Week 1-2)

**目标**: 构建技能系统基础设施

- [ ] **S1: 技能注册表与中间件调度层** (~1,450 LOC)
  - **Why First**: 所有其他组件的基础依赖
  - **Key Deliverables**:
    - SkillRegistry 实现
    - Middleware 调度层实现
    - SkillLoader 动态加载
    - 并行执行器
  - **Verification**:
    - 可自动发现 skills/ 目录下所有 SKILL.md
    - 可按 name、category 查询 Skills
    - 单元测试覆盖率 ≥ 80%

---

### Phase 2: Standardization & Optimization (Week 2-3)

**目标**: 实现技能标准化和上下文优化

- [ ] **S2: 标准化技能工厂与生命周期** (~1,250 LOC)
  - **Why Now**: 依赖 S1，与 S3 并行开发
  - **Key Deliverables**:
    - SKILL.md 验证器
    - SKILL.md 迁移工具
    - 生命周期管理
  - **Verification**:
    - 验证工具可检测不符合规范的 SKILL.md
    - 迁移工具可自动修复常见问题

- [ ] **S3: 上下文优化策略** (~600 LOC)
  - **Why Now**: 依赖 S1，与 S2 并行开发
  - **Key Deliverables**:
    - 上下文优化器（目录注入）
    - 按需加载器
    - 预算管理器
  - **Verification**:
    - 初始化时只注入元数据（~1,000 tokens）
    - Token 消耗降低 ≥ 30%

---

### Phase 3: Observability (Week 3-4)

**目标**: 建立可观测性体系

- [ ] **S4: Agent 可观测性建设** (~1,350 LOC)
  - **Why Now**: 依赖 S1, S2, S3，高风险组件延后
  - **Key Deliverables**:
    - 链路追踪管理器
    - 异常诊断器
    - 幻觉检测器
    - 污染检测器
    - 可观测性 Dashboard
  - **Verification**:
    - 链路追踪可完整记录 Skill 调用链
    - 幻觉检测准确率 ≥ 70%

---

### Phase 4: Integration & Validation (Week 5-6)

**目标**: 整体验证和文档完善

- [ ] **S5: 集成测试与文档** (~900 LOC)
  - **Why Last**: 依赖所有其他组件
  - **Key Deliverables**:
    - 端到端集成测试
    - 性能基准测试
    - A/B 测试框架
    - 用户文档
  - **Verification**:
    - 所有端到端测试通过
    - 性能目标达成
    - 文档完整

---

## Dependency Graph

```
                    ┌─────────────┐
                    │     S1      │
                    │  Registry + │  Week 1-2
                    │ Middleware  │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼──────┐    ┌────▼────┐
    │   S2    │      │     S3     │    │         │
    │ Factory │      │  Context   │    │         │  Week 2-3
    └────┬────┘      └─────┬──────┘    │         │
         │                 │            │         │
         └─────────────────┼────────────┘         │
                           │                      │
                    ┌──────▼──────┐               │
                    │     S4      │               │
                    │ Observability│              │  Week 3-4
                    └──────┬──────┘               │
                           │                      │
                    ┌──────▼──────┐               │
                    │     S5      │◄──────────────┘
                    │ Integration │
                    └─────────────┘  Week 5-6
```

---

## Risk Mitigation

| 风险 | 影响组件 | 影响 | 缓解措施 |
|------|----------|------|----------|
| **SKILL.md 格式迁移成本** | S2, S5 | 中 | 1. 提供自动化迁移工具<br>2. 渐进式迁移策略<br>3. 保持向后兼容 |
| **上下文优化影响 LLM 精度** | S3, S5 | 高 | 1. A/B 测试验证<br>2. 支持回退到全量加载<br>3. 可配置触发阈值 |
| **可观测性系统性能开销** | S4, S5 | 中 | 1. 异步处理幻觉检测<br>2. 采样策略优化<br>3. 降级机制 |
| **幻觉检测准确率不足** | S4 | 中 | 1. 多方法组合验证<br>2. 可配置检测阈值<br>3. 人工审核机制 |
| **现有 Skills 兼容性** | 全部 | 中 | 1. 保持现有 API<br>2. 新旧方式并存<br>3. 完整的迁移文档 |

---

## Verification Checkpoints

### After Phase 1 (S1 完成)

- [ ] SkillRegistry 可自动发现 skills/ 目录下所有 SKILL.md
- [ ] Middleware 可正确路由到目标 Skill
- [ ] 支持并行执行多个 Skills 且状态隔离
- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试通过

### After Phase 2 (S2, S3 完成)

- [ ] 所有现有 SKILL.md 符合 write-a-skill 规范
- [ ] 迁移工具可自动修复常见问题
- [ ] 初始化时只注入元数据（~1,000 tokens）
- [ ] Token 消耗降低 ≥ 30%
- [ ] A/B 测试显示 LLM 精度下降 < 5%

### After Phase 3 (S4 完成)

- [ ] 链路追踪可完整记录 Skill 调用链
- [ ] 异常诊断可识别 P0/P1 异常类型
- [ ] 幻觉检测准确率 ≥ 70%
- [ ] 污染检测可捕获未授权写入
- [ ] 可观测性 Dashboard 可正常使用

### After Phase 4 (S5 完成)

- [ ] 所有端到端测试通过
- [ ] 性能基准测试达成目标
- [ ] 用户文档完整准确
- [ ] 系统可稳定运行

---

## Rollback Strategy

### S1 Rollback

- **条件**: Registry 发现功能异常
- **动作**: 回退到现有硬编码 Adapter 方式
- **影响**: 中等，需要重新集成现有 Skills

### S2 Rollback

- **条件**: SKILL.md 迁移导致大量 Skills 失效
- **动作**: 暂停强制验证，支持新旧格式并存
- **影响**: 低，保持向后兼容

### S3 Rollback

- **条件**: 上下文优化导致 LLM 精度严重下降
- **动作**: 回退到全量加载策略
- **影响**: 低，性能下降但功能正常

### S4 Rollback

- **条件**: 可观测性系统性能开销过大
- **动作**: 禁用异步检测，只保留核心链路追踪
- **影响**: 低，失去高级检测能力

---

## Parallel Opportunities

### Week 2-3: S2 + S3 并行

- S2 和 S3 都只依赖 S1
- 可以由不同开发者并行开发
- 需要定期同步以避免接口冲突

### Week 4: S4 测试 + S5 准备

- S4 开发完成后，立即开始集成测试
- S5 可以提前准备测试框架
- 减少整体开发周期

---

## Resource Estimation

| 角色 | Week 1-2 | Week 2-3 | Week 3-4 | Week 5-6 | 总计 |
|------|----------|----------|----------|----------|------|
| **后端开发** | 1 人 | 1-2 人 | 1 人 | 1 人 | ~5 人周 |
| **测试工程师** | 0.5 人 | 0.5 人 | 1 人 | 1 人 | ~3 人周 |
| **技术文档** | 0 人 | 0.5 人 | 0.5 人 | 1 人 | ~2 人周 |

**总计**: ~10 人周

---

## Success Criteria

### 功能验证

- [ ] Skill Registry 可自动发现并注册所有 Skills
- [ ] Middleware 可正确路由 Skill 调用
- [ ] 上下文优化后 Token 消耗降低 ≥ 30%
- [ ] 可观测性数据完整收集链路追踪
- [ ] 所有 SKILL.md 符合 write-a-skill 规范

### 质量指标

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 集成测试覆盖率 ≥ 70%
- [ ] 幻觉检测准确率 ≥ 70%
- [ ] 代码通过 mypy 类型检查
- [ ] 代码通过 ruff 格式检查

### 性能目标

| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| **Token 消耗** | ~10,000 | ~3,000 (峰值) | 集成测试 |
| **Skill 加载时间** | N/A | < 100ms | 单元测试 |
| **链路追踪开销** | 0 | < 5% | 性能测试 |

---

## Related Documents

- [01-master-spec.md](01-master-spec.md) - 主规范
- [02-sub-spec-index.md](02-sub-spec-index.md) - 子规范索引
- [spec-s1-registry.md](spec-s1-registry.md) - 子规范 S1
- [spec-s2-factory.md](spec-s2-factory.md) - 子规范 S2
- [spec-s3-context.md](spec-s3-context.md) - 子规范 S3
- [spec-s4-observability.md](spec-s4-observability.md) - 子规范 S4
- [spec-s5-integration.md](spec-s5-integration.md) - 子规范 S5

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 审查主实施计划后，进入 Phase 4: 子规范任务生成
