# ComindFlow 术语定义

本文档定义 ComindFlow 项目及 Agent 框架的核心术语，确保跨模块一致性。

---

## Agent Framework 相关

### 执行层状态 (Execution State)
LangGraph 运行时维护的临时状态，包括当前步骤、中间结果、重试计数等。
- **生命周期**: 单次会话，运行时
- **存储位置**: LangGraph StateGraph 内存
- **同步时机**: 每个节点执行后

**避免**: 持久化状态、文件状态（用"持久层状态"）

---

### 持久层状态 (Persistence State)
跨会话保存的长期状态，存储在文件系统中。
- **生命周期**: 跨会话，长期存储
- **存储位置**: CONTEXT.md, Task.md, handoff.md
- **同步时机**: 关键节点（任务完成、会话中断）

**避免**: 运行时状态、临时变量（用"执行层状态"）

---

### 缓存层状态 (Cached State)
从持久层文件读取到内存的数据，避免频繁文件 I/O。
- **生命周期**: 会话期间
- **来源**: CONTEXT.md 解析、Task.md 解析
- **更新策略**: 关键节点后同步写入文件

---

## 工具与编排

### LangChain Tool
封装的可调用单元，被 Agent 用于执行特定功能。
- **示例**: `research_single_tool`, `knowledge_query_tool`
- **特点**: 单一职责，有明确输入输出

**避免**: Tool、函数、方法（仅在技术实现语境）

---

### Workflow (业务流程)
由多个节点和边组成的业务执行路径，用 LangGraph 编排。
- **示例**: F1 学习研究一体化、F3 学术写作全流程
- **特点**: 有明确起止点，可能包含分支和循环

**避免**: 流程、工作流（用 Workflow 或具体名称）

---

### Checkpoint (检查点)
LangGraph 在特定节点保存的状态快照，用于断点恢复。
- **存储位置**: SQLite (agent_framework/checkpoints.db)
- **对应文件**: handoff.md (人类可读版本)

---

## 业务流程命名

| 缩写 | 全称 | 说明 |
|------|------|------|
| F1 | 学习研究一体化 | AutoResearch + review-system + grill-me |
| F2 | 知识问答增强 | review_agent + LLM + WebSearch |
| F3 | 学术写作全流程 | Research → Writing → Review 循环 |
| F4 | 复习计划生成 | 知识提取 → SM2 调度 → 复习计划 |

---

## 会话文件

### CONTEXT.md
术语定义和学前问卷的存储文件。
- **内容**: 术语定义、关系、示例对话、待澄清歧义
- **更新者**: grill-me, grill-you, continue-task

### Task.md
学习任务列表和进度的存储文件。
- **内容**: 任务列表、每任务的轮次、完成状态
- **更新者**: review-session, continue-task, advance-task

### handoff.md
会话交接状态的存储文件，人类可读的断点恢复信息。
- **内容**: 当前状态、进度、未决问题、下一步动作
- **更新者**: advance-task, LangGraph checkpoint 节点

---

## 标志性歧义

### "研究"
可能指代:
- **AutoResearch 模块调用** (技术语境)
- **用户主动学习动作** (业务语境)

**澄清**: 技术实现用"调用 AutoResearch"，业务描述用"用户研究"

---

### "状态"
可能指代:
- **执行层状态** (LangGraph 运行时)
- **持久层状态** (文件系统)
- **应用状态** (应用程序整体)

**澄清**: 明确使用"执行层状态"或"持久层状态"，避免单独使用"状态"

---

### "复习"
可能指代:
- **review-system skills 调用** (技术实现)
- **SM2 间隔重复算法** (算法层面)
- **用户主动复习动作** (用户行为)

**澄清**: 技术用"调用 review-system"，算法用"SM2 调度"，行为用"用户复习"

---

## Agent 技能系统 (新增)

### Skill Registry (技能注册表)
维护可用技能列表的中心化注册机制，通过扫描 SKILL.md 文件自动发现和注册技能。
- **注册来源**: 扫描 skills/ 目录下的 SKILL.md frontmatter
- **发现机制**: 解析 YAML 元数据（name, description）
- **生命周期**: 按需加载，延迟初始化

### Middleware 调度层 (Middleware Dispatch Layer)
位于技能执行流程中的中间件层，负责数据流拦截和路由。
- **请求拦截**: 在技能执行前/后拦截数据流
- **上下文管理**: 注入、转换、过滤上下文信息
- **技能路由**: 根据请求内容调度合适的 skill/tool

### Dynamic On-demand Injection (动态按需注入)
技能加载的三层解耦策略：
1. **架构层面**: 通过 Registry/Provider 模式，移除硬编码的 Skill 类名
2. **接口层面**: Skill 通过抽象契约（**kwargs / Interface Layer）与 State 解耦
3. **内容层面**: Skill 定义（SKILL.md）与执行逻辑分离，按需加载

### Progressive Disclosure (渐进式披露)
SKILL.md 的四层架构，按需加载以优化 Token 消耗：
- **L1 Always-On**: YAML Frontmatter 元数据（~100 tokens，常驻）
- **L2 On-Demand**: Markdown Instructions 指令（需要时加载）
- **L3 Context-Triggered**: resources/ 参考文档（上下文触发加载）
- **L4 Execution-Only**: scripts/ 可执行脚本（仅执行时加载）

### 并行技能兼容 (Parallel Skill Compatibility)
多个技能同时处于可用状态并可并行执行的能力。
- **状态隔离**: 技能之间的上下文互不污染
- **并行执行**: 支持多个 Skills 同时调用
- **路由调度**: Middleware 根据请求分发到对应技能

---

## Skills 标准化 (基于 write-a-skill 规范)

### SKILL.md 标准结构
```
skill-name/
├── SKILL.md           # 主指令（必需，<100 行）
├── REFERENCE.md       # 详细文档（如需要）
├── EXAMPLES.md        # 使用示例（如需要）
└── scripts/           # 工具脚本（如需要）
    └── helper.py
```

### SKILL.md 模板
```markdown
---
name: skill-name
description: 能力简述。Use when [具体触发条件]。
---

# Skill Name

## Quick start
[最小工作示例]

## Workflows
[带检查清单的详细流程]

## Advanced features
See [REFERENCE.md](REFERENCE.md) for details
```

### 描述字段规范（Description Requirements）
- **长度**: 最大 1024 字符
- **人称**: 第三人称
- **结构**:
  - 第一句：能力描述
  - 第二句："Use when [具体触发条件]"
- **目的**: 让 Agent 能据此选择正确的 Skill

### 标准化指令集 (Standardized Instructions)
1. **LLM 指令格式**: 统一的 Claude 指令风格
2. **TOOLS 调用**: 标准化的工具命令接口

### 技能生命周期管理 (Skill Lifecycle Management)
管理范围包含：
- **注册与发现**: 扫描 SKILL.md，解析 frontmatter，注册到 Registry
- **加载与卸载**: 按需加载 Skill 模块，支持热重载
- **监控与诊断**: 使用统计、健康检查、错误追踪

### 拆分原则
- SKILL.md 超过 100 行时拆分到 REFERENCE.md
- 操作具有确定性时使用 scripts/（验证、格式化）
- 避免重复生成代码时使用 scripts/
- 需要显式错误处理时使用 scripts/

---

## 上下文优化策略 (Context Optimization)

### 目录注入 (Metadata Injection)
只注入 SKILL.md 的目录（TOC）而非完整内容，包括：
- YAML frontmatter 元数据（name, description）
- 章节结构（Quick start, Workflows, Advanced features）

### 按需加载 (On-Demand Loading)
完整 Skill 内容的延迟加载机制，触发条件包括：
- **基于任务类型**: `state["task_type"]` 匹配时加载
- **基于用户查询**: 用户输入包含 `/skill-name` 时加载
- **基于 LLM 工具调用**: LLM 决定调用 Skill 工具时加载

### 两阶段加载 (Two-Phase Loading)
目录注入与按需加载的协调策略：
```python
# 阶段1：初始化时注入目录
inject_skill_metadata()  # 所有 Skills 的 frontmatter

# 阶段2：运行时按需加载完整内容
load_skill_on_demand(skill_name)
```

### 优化目标
- 降低单次任务的 Token 消耗
- 保持模型高响应精度
- 通过实际测试确定最佳阈值

---

## Agent 可观测性 (Agent Observability)

### 可观测性数据来源
收集以下四类核心数据：
- **执行链路追踪 (A)**: trace_id、skill_chain、timestamps、state_transitions
- **工具调用记录 (B)**: tool_calls、input/output、duration、status
- **异常与错误 (C)**: error_type、message、stack_trace、recovery_action
- **上下文变化 (D)**: before/after 状态对比、delta 变更记录

### 链路追踪边界
覆盖两个核心边界：
- **跨 Skill 追踪 (B)**: 多个 Skill 的调用链路
- **Workflow 层追踪 (C)**: 节点间的流转和状态变化

可选：Skill 内部追踪 (A) 作为细粒度调试选项

### 工具异常诊断范围
五类异常全覆盖，优先级分层：
- **P0 核心 (A+B+C)**: 可用性异常、执行异常、数据异常
- **P1 增强 (D)**: 依赖异常（如文件缺失）
- **P2 可选 (E)**: 性能异常（慢执行、高内存）

### 幻觉与污染检测
**幻觉检测**: A + C 组合
- **引用源验证 (A)**: 检查输出是否基于给定的引用源
- **LLM 自我评估 (C)**: 让 LLM 评估自己输出的幻觉概率

**污染检测**: D + E 组合
- **状态快照对比 (D)**: 执行前后对比状态快照
- **写入白名单 (E)**: 定义 Skill 允许修改的状态字段，检测未授权写入
