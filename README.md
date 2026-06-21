# Review System Skills

基于 Claude Skills 的人机协同学术复习系统，通过多阶段工作流实现系统化学习。

![Architecture](Review%20System%20Skills%20Architecture.png)

## 📋 目录

- [项目概述](#项目概述)
- [系统架构](#系统架构)
- [核心技能](#核心技能)
- [快速开始](#快速开始)
- [工作流程](#工作流程)
- [文件结构](#文件结构)
- [配置与定制](#配置与定制)

## 🎯 项目概述

Review System Skills 是一套为学术复习和考试准备设计的 Claude Skills，支持：

- 📄 **文档转换** - 自动将 PDF/DOCX 转换为 Markdown
- 📝 **任务分解** - 按章节/主题智能分解学习任务
- 💬 **交互式问答** - 双向 Q&A 强化理解（AI考你 + 你考AI）
- 🔄 **断点恢复** - 通过 handoff.md 支持跨天学习
- 📚 **术语管理** - CONTEXT.md 统一术语定义
- ✅ **进度跟踪** - Task.md 记录每个任务的学习状态

## 🏗️ 系统架构

### 两层结构

系统采用简化的两层架构：

```
┌─────────────────────────────────────────────────────────────┐
│              Orchestration Layer (编排层)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 1: Initialize                                │   │
│  │  ┌──────────────┐  ┌──────────────────┐            │   │
│  │  │review-session│ → │PDF/DOCX → source/│            │   │
│  │  └──────────────┘  └──────────────────┘            │   │
│  │         ↓                   ↓                        │   │
│  │  ┌──────────────────────────────────────┐            │   │
│  │  │           Task.md 初始化              │            │   │
│  │  └──────────────────────────────────────┘            │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Phase 2: Loop (学习循环)                           │   │
│  │  ┌──────────────┐  ┌──────────┐  ┌──────────┐      │   │
│  │  │continue-task│ → │grill-me  │ ↔ │grill-you │      │   │
│  │  └──────────────┘  └──────────┘  └──────────┘      │   │
│  │                       ↓                              │   │
│  │              ┌──────────────────┐                     │   │
│  │              │  advance-task    │ ←──────┐           │   │
│  │              └──────────────────┘        │ (循环)      │   │
│  │                      │                  └─────────────┘   │
│  └──────────────────────┼──────────────────────────────────┘
│                         ↓
└─────────────────────────┼───────────────────────────────────
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                 Data Layer (数据层)                           │
│  📁 Session/                                                 │
│    ├── CONTEXT.md      (术语定义与学前问卷)                    │
│    ├── Task.md         (任务列表与进度)                       │
│    ├── handoff.md      (会话交接状态)                         │
│    ├── README.md       (会话概要)                             │
│    └── sources/        (转换后的学习资料 .md 文件)             │
└─────────────────────────────────────────────────────────────┘
```

### 颜色编码

| 颜色 | 用途 | 说明 |
|------|------|------|
| 🟡 黄色 | 编排层背景 | Orchestration Layer 容器 |
| 🩷 粉色 | 数据层背景 | Data Layer 容器 |
| 🔵 蓝色 | 会话/任务管理 | `review-session`, `continue-task` |
| 🩵 浅蓝 | 文档转换 | PDF/DOCX → Markdown |
| 🟠 橙色 | Q&A 交互 | `grill-me`, `grill-you` |
| 🟢 绿色 | 进度推进 | `advance-task` |

## 🧩 核心技能

### 1. review-system
**编排系统** - 协调整个复习工作流

```bash
/review-system 复习经济管理
```

### 2. review-session
**初始化会话** - 创建文件夹、转换文档、分解任务

```bash
/review-session 复习经济管理，资料在 d:\学习\21CoreDocs\经管\复习资料
```

### 3. continue-task
**恢复会话** - 读取 handoff.md，生成学前问卷

```bash
/continue-task review-20250619-经济管理
```

### 4. grill-me
**AI 考你** - 主动提问，检查理解，维护 CONTEXT.md

```bash
/grill-me Task 3 关于货币政策
```

### 5. grill-you
**你考 AI** - 指导你提出好问题，深化理解

```bash
/grill-you 再考我几个货币传导机制的问题
```

### 6. advance-task
**保存进度** - 更新 Task.md、生成 handoff.md

```bash
/advance-task Task 3 已完成第2轮，理解良好
```

## 🚀 快速开始

### 前置要求

- Claude Code CLI
- Python 3.12+
- 可选：`pypdf`, `python-docx`（用于文档转换）

### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/review_system_skills.git
cd review_system_skills

# 复制技能到 Claude Skills 目录
# Windows: C:\Users\[username]\.claude\skills\
# macOS/Linux: ~/.claude/skills/
```

### 开始第一次复习

```bash
# 1. 初始化会话
/review-session 复习数据结构，资料在 d:\学习\data_structure\复习资料

# 2. 打开新窗口恢复上下文
/continue-task review-20250619-数据结构

# 3. 开始学习循环
/grill-me 检查我对链表的理解
```

## 📖 工作流程

### 完整学习循环

```
┌─────────────────────────────────────────────────────────────┐
│                         学习循环                              │
└─────────────────────────────────────────────────────────────┘

1️⃣ 初始化 (review-session)
   │
   ├─ 创建 Session 文件夹
   ├─ 初始化 CONTEXT.md, Task.md, README.md
   ├─ 转换 PDF/DOCX → sources/*.md
   ├─ 按章节分解任务
   └─ 生成 handoff.md
   ↓
2️⃣ 开始学习 (continue-task)
   │
   ├─ 读取 handoff.md 恢复状态
   ├─ 读取 CONTEXT.md 恢复术语
   ├─ 确定当前 Task
   ├─ 生成学前问卷
   └─ 写入 CONTEXT.md
   ↓
3️⃣ Q&A 循环 (grill-me ↔ grill-you)
   │
   ├─ /grill-me: AI 持续提问，检查理解
   ├─ 用户回答
   ├─ /grill-you: 用户反向提问 AI
   └─ 循环直到掌握
   ↓
4️⃣ 保存进度 (advance-task)
   │
   ├─ 更新 Task.md 轮次
   ├─ 更新 handoff.md
   ├─ 若完成 → 进入下一 Task
   └─ 若继续 → 回到 2️⃣
```

### 多 Session 协作

```
Day 1: review-20250619-经济管理/
├── Task 1-3 完成
└── handoff.md 记录当前位置

Day 2: 同一 Session
├── 从 Task 4 继续
└── handoff.md 更新

Day 3: 同一 Session
├── Task 5-6 完成
└── 生成最终总结
```

## 📁 文件结构

### 技能目录

```
review_system_skills/
├── advance-task/
│   ├── SKILL.md        # 技能说明
│   └── REFERENCE.md    # 详细参考
├── continue-task/
│   ├── SKILL.md
│   └── REFERENCE.md
├── grill-me/
│   ├── SKILL.md
│   └── CONTEXT-FORMAT.md
├── grill-you/
│   ├── SKILL.md
│   └── CONTEXT-FORMAT.md
├── review-session/
│   ├── SKILL.md
│   ├── REFERENCE.md
│   └── scripts/
│       └── convert_docs.py
└── review-system/
    ├── SKILL.md
    └── REFERENCE.md
```

### Session 目录

```
review-YYYYMMDD-主题/
├── CONTEXT.md          # 术语定义上下文
├── Task.md             # 学习任务列表和进度
├── handoff.md          # 会话交接文件
├── README.md           # 会话概要
└── sources/            # 转换后的学习资料
    ├── chapter-01.md
    ├── chapter-02.md
    └── ...
```

### 文件写入责任矩阵

| 文件 | review-session | continue-task | advance-task | grill-me | grill-you |
|------|----------------|---------------|--------------|----------|-----------|
| CONTEXT.md | 初始化模板 | 写入学前问卷 | 补充术语/答案 | 更新术语 | 更新术语 |
| Task.md | 初始化列表 | 更新状态为 in_progress | 更新轮次/完成 | - | - |
| handoff.md | 初始化 | - | 完全重写 | - | - |
| sources/ | 转换写入 | 读取 | - | - | - |

## ⚙️ 配置与定制

### 学前问卷设计原则

1. **引导性** - 问题本身包含学习线索
   ```
   好: 货币政策工具中，利率和存款准备金率对经济的影响有什么不同？
   差: 什么是货币政策？
   ```

2. **层次递进** - 概念理解 → 应用场景 → 深层原理

3. **数量控制** - 3-5 题为宜

### 完成标准

一个 Task 标记为 `completed` 需满足：

- ✅ 至少 2 轮 Q&A
- ✅ 能回答所有学前问卷问题
- ✅ 无明显待解决问题
- ✅ 用户表示理解或通过验收问题

### CONTEXT.md 格式

```markdown
# Session 上下文

学习经济管理的复习会话，确保术语一致性。

## Language

**货币政策**:
央行调节货币供应量和利率的政策工具
_Avoid_: 宽松政策、紧缩政策（使用具体工具名）

**时滞**:
政策实施到产生效果的延迟时间

## Relationships

- **利率** 影响 **投资成本**
- **准备金率** 影响 **银行流动性**

## Example dialogue

> **User**: "当央行降低利率时会发生什么？"
> **Agent**: "降低利率会降低借款成本，刺激投资和消费。"

## Flagged ambiguities
- "政策工具" 曾同时指代利率和准备金率 — 已明确分开定义。
```

## 🛠️ 故障恢复

| 症状 | 原因 | 解决 |
|------|------|------|
| Task.md 为空 | 转换失败 | 重新 `/review-session` |
| handoff.md 缺失 | 用户未调用 `/advance-task` | 读取 Task.md 推断 |
| sources/ 为空 | 转换脚本未运行 | 检查 pypdf/python-docx 安装 |
| CONTEXT.md 丢失 | 意外删除 | 从 handoff.md 重建 |

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- 作者: Joeowo
- 项目主页: https://github.com/Joeowo/Review-System-Skills
