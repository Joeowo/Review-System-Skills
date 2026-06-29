# Sub-Spec Index

**父文档**: [01-master-spec.md](01-master-spec.md)
**生成日期**: 2026-06-28

---

## 子规范列表

| ID | 子规范名称 | 预估 LOC | 依赖 | 状态 |
|----|-----------|----------|------|------|
| S1 | 核心框架层 | ~1,700 | - | Pending |
| S2 | 工具适配层 | ~1,150 | S1 (部分) | Pending |
| S3 | Workflow - 学习研究 | ~850 | S1, S2 | Pending |
| S4 | Workflow - 学术写作复习 | ~950 | S1, S2 | Pending |
| S5 | 基础设施层 | ~1,200 | - | Pending |

**总估算 LOC**: ~5,850

---

## S1: 核心框架层

**目标**: 实现 Agent Framework 的核心基础设施

### 组件分解

| 组件 | 估算 LOC | 说明 |
|------|----------|------|
| C1: State 定义与同步 | ~400 | AgentState 定义、执行层/持久层同步逻辑 |
| C2: Checkpoint 管理 | ~300 | SQLite checkpoint 封装、清理策略 |
| C3: 异常处理框架 | ~350 | 异常分类、处理器、降级策略 |
| C4: 用户确认机制 | ~250 | Human-in-the-loop 节点、确认级别 |
| C5: 基础节点库 | ~400 | 通用节点模式（重试、超时、日志等） |

### 接口

**Produces**:
- `AgentState` 类型定义
- `StateSync` 服务
- `CheckpointManager` 服务
- `ExceptionHandler` 服务
- `ConfirmationManager` 服务
- 基础节点函数库

**Consumes**:
- LangGraph 核心库
- SQLite

**Dependencies**: 无（其他层的基础）

---

## S2: 工具适配层

**目标**: 封装现有模块为 LangChain Tools

### 组件分解

| 组件 | 估算 LOC | 说明 |
|------|----------|------|
| T1: AutoResearch Tools | ~300 | 单次/深度研究 Tool 封装 |
| T2: review_agent Tools | ~250 | 问题生成、答案评估 Tool |
| T3: Skills 适配器 | ~600 | grill-me、grill-you 等 skills 适配 |

### 接口

**Consumes**:
- `AutoResearch.autoresearch.main`
- `review_agent.*`
- 现有 skills

**Produces**:
- LangChain Tools 定义
- 适配器层

**Dependencies**:
- S1: 异常处理（用于 Tool 错误处理）

---

## S3: Workflow - 学习研究

**目标**: 实现 F1、F2 业务流程

### 组件分解

| 组件 | 估算 LOC | 说明 |
|------|----------|------|
| W1: F1 学习研究一体化 | ~500 | 研究 → 概念提取 → grilling 循环 |
| W2: F2 知识问答增强 | ~350 | review_agent 深度集成 |

### 接口

**Consumes**:
- S1: 核心框架
- S2: AutoResearch Tools、Skills 适配器

**Produces**:
- F1 Workflow 图
- F2 Workflow 图

**Dependencies**:
- S1: 全部
- S2: T1, T3

---

## S4: Workflow - 学术写作复习

**目标**: 实现 F3、F4 业务流程

### 组件分解

| 组件 | 估算 LOC | 说明 |
|------|----------|------|
| W3: F3 学术写作全流程 | ~550 | 研究 → 写作 → Review 循环 |
| W4: F4 复习计划生成 | ~400 | SM2 调度器集成 |

### 接口

**Consumes**:
- S1: 核心框架
- S2: 所有 Tools

**Produces**:
- F3 Workflow 图
- F4 Workflow 图

**Dependencies**:
- S1: 全部
- S2: 全部

---

## S5: 基础设施层

**目标**: 提供配置、日志、测试、CLI 支持

### 组件分解

| 组件 | 估算 LOC | 说明 |
|------|----------|------|
| I1: 配置管理 | ~150 | Pydantic Settings、环境变量 |
| I2: 日志系统 | ~200 | Loguru 配置、结构化日志 |
| I3: 测试框架 | ~400 | Fixtures、测试工具 |
| I4: 文档生成 | ~250 | API 文档、架构图 |
| I5: CLI 入口 | ~200 | 命令行接口 |

### 接口

**Consumes**:
- 所有其他层（用于测试、文档）

**Produces**:
- 配置系统
- 日志系统
- 测试基础设施
- CLI 可执行文件

**Dependencies**:
- 可独立开发，但完整功能依赖所有层

---

## 依赖关系图

```
     S5 (基础设施)
         │
         ↓
     S1 (核心框架)
         │
         ↓
     S2 (工具适配) ───────┐
         │                │
         ↓                ↓
     S3 (学习研究)    S4 (学术写作复习)
```

**实施顺序**: S1 → S2 → (S3, S4 并行) → S5（S5 可早期并行）

---

→ **Human**: 审查子规范分解，确认后进入 Phase 3 (Master Plan)
