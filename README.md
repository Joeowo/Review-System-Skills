# ComindFlow

基于 Claude Skills 的人机协同学术复习与知识管理系统，通过多阶段工作流实现系统化学习。

![Architecture](ComindFlow%20Architecture.png)

## 📋 目录

- [项目概述](#项目概述)
- [核心理念](#核心理念)
- [系统架构](#系统架构)
- [核心技能](#核心技能)
- [扩展功能](#扩展功能)
- [快速开始](#快速开始)
- [工作流程](#工作流程)
- [文件结构](#文件结构)
- [配置与定制](#配置与定制)

## 🎯 项目概述

**ComindFlow** 是一套为学术研究、写作和知识管理设计的 Claude Skills 工具集，强调人机协同的思维流动（Mind + Flow）。

### 核心能力

**学习复习**：
- 📄 **文档转换** - 自动将 PDF/DOCX 转换为 Markdown
- 📝 **任务分解** - 按章节/主题智能分解学习任务
- 💬 **交互式问答** - 双向 Q&A 强化理解（AI考你 + 你考AI）
- 🔄 **断点恢复** - 通过 handoff.md 支持跨天学习
- 📚 **术语管理** - CONTEXT.md 统一术语定义
- ✅ **进度跟踪** - Task.md 记录每个任务的学习状态
- 🧠 **间隔复习** - review_agent SM2 算法辅助记忆

**学术写作**：
- 🎓 **协作写作** - academic-coevolution-main 人机协同学术写作
- ✍️ **写作助手** - academic-writing-assist 结构化表达优化

**效率工具**：
- 🔍 **智能研究** - AutoResearch 自动化文献/技术调研
- 📅 **日程管理** - ima-schedule-agent 任务/习惯/日记管理
- 🛠️ **技能创作** - write-a-skill 快速创建新技能

## 💡 核心理念

**ComindFlow** = **Companion**（陪伴） + **Mind**（思维） + **Flow**（心流）

- **Companion** - AI 作为学习伙伴，而非简单的工具
- **Mind** - 关注思维过程的深度理解，而非知识点的死记硬背
- **Flow** - 保持学习状态的心流，支持跨会话的连续性

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

### 7. academic-coevolution-main
**学术协作主控** - AI 与人类协作学术写作的全流程编排

```bash
/academic-coevolution-main
```

**核心特性**：
- 🔄 **三阶段流程** - Clarification → Research → Writing
- 🎯 **人机协同** - 人类负责核心论点，AI 负责表达优化
- 📚 **技能编排** - 协调 grill-me、auto-research、writing-assist 等

**适用场景**：学术论文写作、研究报告撰写

### 8. academic-writing-assist
**学术写作助手** - 人类主导、AI 辅助的协作写作

```bash
"帮我结构化引言部分"
"重写这段，使其更具学术风格"
"检查论点是否得到充分支持"
```

**核心特性**：
- ✍️ **结构模板** - Introduction、Literature Review、Results、Conclusion
- 🎨 **表达优化** - 学术语气、逻辑流畅性、语言精炼
- 🔁 **迭代改进** - 多轮协作，人类最终决策权

### 9. ima-schedule-agent (日程管理助手)
**个人日程管理** - 基于 IMA notes API 的任务、习惯、日记管理

```bash
"今天有什么任务？"
"添加一个会议到本周计划"
"写今天的日记"
```

**核心特性**：
- 📅 **多级任务** - 月/周/日任务分层管理
- 📊 **习惯追踪** - 记录任务执行数据和用户行为模式
- 📝 **智能日记** - 陪伴者视角的日记编写
- 🔄 **向下同步** - 月任务可拆解到周/日

### 10. write-a-skill
**技能创作工具** - 创建新的 Claude Skills

```bash
/write-a-skill
```

**核心特性**：
- 📝 **结构模板** - SKILL.md、REFERENCE.md、EXAMPLES.md
- 🎯 **最佳实践** - 描述规范、渐进式披露
- 🛠️ **脚本支持** - 确定性操作的实用脚本

## 🔧 扩展功能

### AutoResearch
**智能自动化研究工具** - 基于 DeepSeek V4-Pro + WebSearch 的学术/技术调研

```bash
# 基础用法
python -m autoresearch "RAG 技术调研"

# 深度研究（多维度）
python -m autoresearch "大模型微调" --mode deep --type 技术

# 自然语言模式（自动分析）
python -m autoresearch "帮我调研一下 Agent 技能和工作流优化的最新研究"
```

**核心特性**：
- 🔍 **智能搜索** - 利用 DeepSeek WebSearch 获取最新信息
- 📊 **多种研究模式** - auto/single/deep/interactive
- 📝 **自动报告** - 生成结构化 Markdown 研究报告
- 🤖 **自然语言处理** - 自动分析需求，生成研究计划
- 📚 **学术规范** - 完整参考文献格式，arXiv 编号可追溯
- 🔗 **来源追踪** - 每个观点都有 arXiv 编号和链接
- 🎯 **置信度标注** - 区分高/中/低置信度来源
- 📖 **质量保证** - 内置 METHODOLOGY.md 和 QUALITY_CHECKLIST.md

**适用场景**：论文调研、技术趋势分析、竞品研究、学术文献综述

### review_agent
**智能复习助手** - 基于 SM2 间隔重复算法的学习系统

```bash
# 启动复习界面
python -m review_agent
```

**核心特性**：
- 🧠 **SM2 算法** - 科学的间隔重复记忆调度
- 📝 **智能出题** - 自动从学习资料提取问题
- ✅ **答案评估** - AI 评估回答质量
- 📊 **进度跟踪** - 可视化学习统计
- 🔁 **错题管理** - 自动收集和重点复习

**适用场景**：长期记忆保持、考试准备、知识点巩固

## 🚀 快速开始

### 前置要求

- Claude Code CLI
- Python 3.12+
- 可选：`pypdf`, `python-docx`（用于文档转换）

### 安装

```bash
# 克隆项目
git clone https://github.com/Joeowo/ComindFlow.git
cd ComindFlow

# 复制技能到 Claude Skills 目录
# Windows: C:\Users\[username]\.claude\skills\
# macOS/Linux: ~/.claude/skills/
```

### 安装扩展功能依赖

```bash
# AutoResearch
cd AutoResearch
pip install -r requirements.txt
# 配置 .env 文件（参考 README.md）

# review_agent
cd review_agent
pip install -r requirements.txt
# 配置 .env 文件（参考 .env.example）
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

### 项目根目录

```
ComindFlow/
├── skills/                      # Claude Skills 目录
│   ├── review-system/           # 编排系统
│   ├── review-session/         # 会话初始化
│   ├── continue-task/          # 断点恢复
│   ├── grill-me/               # AI 考你
│   ├── grill-you/              # 你考 AI
│   ├── advance-task/           # 进度保存
│   ├── academic-coevolution-main/  # 学术协作主控
│   ├── academic-writing-assist/    # 学术写作助手
│   ├── ima-schedule-agent/         # 日程管理助手
│   └── write-a-skill/          # 技能创作工具
├── AutoResearch/               # 智能研究工具
│   ├── autoresearch/           # 研究模块
│   │   ├── __init__.py        # 包入口
│   │   ├── __main__.py        # CLI 入口
│   │   ├── main.py            # 主程序
│   │   ├── config.py          # 配置管理
│   │   ├── planner.py         # 任务规划器
│   │   ├── researcher.py      # 核心研究模块
│   │   ├── reporter.py        # 报告生成器
│   │   ├── METHODOLOGY.md     # 研究方法论
│   │   └── QUALITY_CHECKLIST.md  # 质量检查清单
│   ├── output/
│   │   └── reports/           # 研究报告输出
│   ├── requirements.txt        # 依赖
│   ├── test_features.py        # 功能测试
│   ├── test_research.py        # 研究测试
│   └── README.md               # AutoResearch 说明
├── review_agent/               # 智能复习助手
│   ├── core/                   # 核心逻辑
│   │   ├── __init__.py
│   │   ├── sm2_scheduler.py   # SM2 调度器
│   │   ├── answer_evaluator.py # 答案评估器
│   │   ├── question_generator.py # 问题生成器
│   │   ├── question_extractor.py # 问题提取器
│   │   └── knowledge_extractor.py # 知识提取器
│   ├── services/               # 业务服务
│   │   ├── llm_service.py     # LLM 服务
│   │   ├── qa_assistant.py    # 问答助手
│   │   ├── knowledge_query.py  # 知识查询
│   │   ├── question_dedup.py  # 问题去重
│   │   ├── question_extraction_service.py # 问题提取服务
│   │   └── wrong_question_service.py # 错题服务
│   ├── models/                 # 数据模型
│   ├── repositories/           # 数据仓库
│   ├── ui/                     # 用户界面
│   │   ├── menu.py            # 主菜单
│   │   └── quiz.py            # 测验界面
│   ├── utils/                  # 工具函数
│   ├── data/                   # 数据存储
│   ├── config.py              # 配置
│   ├── main.py                # 入口文件
│   ├── requirements.txt        # 依赖
│   └── .env.example           # 环境变量示例
├── README.md                   # 本文件
├── LICENSE                     # MIT 许可证
└── ComindFlow Architecture.png  # 架构图
```

### 技能目录

```
skills/
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
├── review-system/
│   ├── SKILL.md
│   └── REFERENCE.md
├── academic-coevolution-main/
│   └── SKILL.md        # 协作学术写作主控
├── academic-writing-assist/
│   └── SKILL.md        # 人类主导的学术写作助手
├── ima-schedule-agent/
│   ├── SKILL.md        # 日程管理主技能
│   ├── README.md       # 项目说明
│   ├── LICENSE         # 许可证
│   └── references/     # 各模块详细文档
│       ├── month-task.md
│       ├── week-task.md
│       ├── day-task.md
│       ├── habit.md
│       └── diary.md
└── write-a-skill/
    └── SKILL.md        # 创建新技能的指南
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

### AutoResearch 配置

在 `AutoResearch/.env` 文件中配置：

```env
apikey=sk-your-deepseek-api-key
base=https://api.deepseek.com
model=deepseek-v4-pro
```

### review_agent 配置

在 `review_agent/.env` 文件中配置：

```env
# 复制 .env.example 并填入实际值
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
```

## 🛠️ 故障恢复

| 症状 | 原因 | 解决 |
|------|------|------|
| Task.md 为空 | 转换失败 | 重新 `/review-session` |
| handoff.md 缺失 | 用户未调用 `/advance-task` | 读取 Task.md 推断 |
| sources/ 为空 | 转换脚本未运行 | 检查 pypdf/python-docx 安装 |
| CONTEXT.md 丢失 | 意外删除 | 从 handoff.md 重建 |
| AutoResearch API 错误 | .env 配置错误 | 检查 API Key 和 base URL |
| review_agent 启动失败 | 缺少依赖 | 运行 `pip install -r requirements.txt` |

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- 作者: Joeowo
- 项目主页: https://github.com/Joeowo/ComindFlow

---

**ComindFlow** - 让思维流动，让知识生长。
