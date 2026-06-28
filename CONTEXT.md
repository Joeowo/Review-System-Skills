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
