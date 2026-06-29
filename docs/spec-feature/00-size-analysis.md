# Size Analysis: 技能系统重构

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## Requirements Summary

基于 **动态按需注入（Dynamic On-demand Injection）** 范式，构建高扩展性 Agent 技能系统。包含四个核心需求：

1. **技能注册表与中间件调度层** - 实现业务技能与模型逻辑的解耦
2. **标准化技能工厂** - 提升通用能力复用率
3. **上下文优化策略** - 降低单次任务的 Token 消耗
4. **Agent 可观测性建设** - 建立技能调试与链路追踪机制

---

## Component Breakdown

| 组件 | 估算 LOC | 复杂度 | 依赖项 | 优先级 |
|------|----------|--------|--------|--------|
| **Skill Registry** | ~400 | 中 | 文件系统、YAML解析 | P0 |
| **Middleware 调度层** | ~500 | 高 | Skill Registry | P0 |
| **Skill Loader（动态加载）** | ~300 | 中 | Skill Registry | P0 |
| **并行执行器** | ~250 | 中 | Middleware | P1 |
| **SKILL.md 验证器** | ~200 | 低 | 文件系统 | P0 |
| **SKILL.md 迁移工具** | ~300 | 低 | 验证器 | P1 |
| **生命周期管理** | ~350 | 中 | Skill Registry | P1 |
| **上下文优化器** | ~400 | 中 | Skill Registry | P0 |
| **预算管理器** | ~200 | 低 | 上下文优化器 | P1 |
| **链路追踪管理器** | ~350 | 中 | Middleware | P0 |
| **异常诊断器** | ~300 | 中 | 链路追踪 | P0 |
| **幻觉检测器** | ~400 | 高 | 链路追踪 | P1 |
| **污染检测器** | ~250 | 中 | 链路追踪 | P1 |
| **可观测性 Dashboard** | ~500 | 中 | 所有可观测性组件 | P1 |
| **测试代码（估算60%覆盖率）** | ~2400 | - | - | P0 |

---

## Total Estimate

```
核心功能代码: ~4,650 LOC
测试代码:     ~2,400 LOC
配置/文档:    ~500 LOC
-----------------------------------
总计:        ~7,550 LOC
```

### Recommended Approach

**总估算 LOC: ~7,550 行**

由于超过 **2000 LOC** 的阈值，且包含多个相对独立的模块，推荐采用 **分层子规范（Hierarchical Sub-Specs）** 方案。

### Sub-Spec Breakdown

| ID | 子规范名称 | 估算 LOC | 依赖 | 状态 |
|----|-----------|----------|------|------|
| **S1** | 技能注册表与中间件调度层 | ~1,450 | - | Pending |
| **S2** | 标准化技能工厂与生命周期 | ~1,250 | S1 | Pending |
| **S3** | 上下文优化策略 | ~600 | S1 | Pending |
| **S4** | Agent 可观测性建设 | ~1,350 | S1, S2, S3 | Pending |
| **S5** | 集成测试与文档 | ~900 | S1-S4 | Pending |

**子规范总估算 LOC: ~7,550 LOC**

---

## Identified Risks

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| SKILL.md 格式迁移成本 | 中 | 提供自动化迁移工具 |
| 上下文优化影响 LLM 精度 | 高 | A/B 测试验证，支持回退 |
| 可观测性系统性能开销 | 中 | 采样策略，异步处理 |
| 现有 Skills 兼容性 | 中 | 渐进式迁移，保持向后兼容 |

---

## Dependencies

### 内部依赖
- 现有 `agent_framework/` 模块（core、tools、workflows）
- 现有 `skills/` 目录结构
- `CONTEXT.md` 术语定义

### 外部依赖
- Python 3.12+
- Pydantic（数据验证）
- PyYAML（SKILL.md 解析）
- LangChain/LangGraph（Agent 集成）

---

## Tech Stack

- **语言**: Python 3.12+
- **框架**: LangGraph（Agent 编排）
- **数据验证**: Pydantic v2
- **测试**: pytest + pytest-asyncio
- **日志**: structlog

---

## Key Assumptions

1. **现有 Skills 保持兼容** - 重构不改变现有 Skills 的业务逻辑
2. **渐进式迁移** - 支持新旧两种方式并存，逐步迁移
3. **本地运行** - 单用户本地执行，无需多租户支持
4. **LLM 集成方式不变** - 仍通过 Claude Code CLI 调用

---

**→ 人类: 请确认规模分析后，再进入 Master Spec 阶段**

**文档版本**: 1.0
**最后更新**: 2026-06-29
