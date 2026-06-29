# ComindFlow

基于 Claude Skills 与 LangGraph Agent Framework 的人机协同学术复习与知识管理系统。

## 概述

**ComindFlow** 是一套为学术研究、写作和知识管理设计的智能工具集，采用双层架构：

- **上层**：Claude Skills - 提供与 Claude Code CLI 的直接交互接口
- **底层**：Agent Framework - 基于 LangGraph 的状态机编排引擎

### 核心能力

| 能力 | 说明 |
|------|------|
| 📄 **文档转换** | 自动将 PDF/DOCX 转换为 Markdown |
| 🔍 **智能研究** | AutoResearch 自动化文献/技术调研 |
| 💬 **交互式问答** | 双向 Q&A 强化理解（AI考你 + 你考AI） |
| 🔄 **断点恢复** | 通过 handoff.md 支持跨天学习 |
| 📊 **状态管理** | 双状态并行策略（执行层 + 持久层） |
| 🧠 **间隔复习** | review_agent SM2 算法辅助记忆 |
| 🎓 **学术写作** | 人机协同学术写作全流程 |
| 📅 **日程管理** | 基于 IMA notes 的任务/习惯/日记管理 |

---

## Agent Framework

### 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Framework (LangGraph)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   Workflows   │  │     Tools     │  │  Core State    │       │
│  │               │  │               │  │  Management    │       │
│  │ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │       │
│  │ │    F1     │ │  │ │AutoResearch│ │  │ │AgentState │ │       │
│  │ │  学习研究  │ │  │ │  Adapter  │ │  │ │  定义     │ │       │
│  │ └───────────┘ │  │ └───────────┘ │  │ └───────────┘ │       │
│  │ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │       │
│  │ │    F2     │ │  │ │Review Agent│ │  │ │Checkpoint │ │       │
│  │ │  知识问答  │ │  │ │  Adapter  │ │  │ │  管理     │ │       │
│  │ └───────────┘ │  │ └───────────┘ │  │ └───────────┘ │       │
│  │ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │       │
│  │ │    F3     │ │  │ │  Skills   │ │  │ │State Sync │ │       │
│  │ │  学术写作  │ │  │ │ Adapters  │ │  │ │  同步     │ │       │
│  │ └───────────┘ │  │ └───────────┘ │  │ └───────────┘ │       │
│  │ ┌───────────┐ │  │               │  │               │       │
│  │ │    F4     │ │  │               │  │               │       │
│  │ │  复习计划  │ │  │               │  │               │       │
│  │ └───────────┘ │  │               │  │               │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │   CLI 入口    │  │   日志系统    │  │   配置管理    │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Persistence Layer                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  CONTEXT.md   │  │   Task.md     │  │  handoff.md    │       │
│  │  术语定义     │  │   任务进度     │  │  会话交接      │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
agent_framework/
├── core/                    # 核心模块
│   ├── state.py           # AgentState 定义与文件解析
│   ├── checkpoint.py      # 检查点管理
│   ├── exceptions.py      # 异常定义
│   ├── confirmation.py   # 用户确认机制
│   └── base_nodes.py      # 基础节点装饰器
│
├── tools/                  # 工具适配器
│   ├── autoresearch_tools.py    # AutoResearch 集成
│   ├── review_agent_tools.py    # Review Agent 集成
│   └── skills_adapters.py       # Skills 文件接口适配
│
├── workflows/               # 业务流程
│   ├── f1_learning_research.py    # F1: 学习研究一体化
│   ├── f2_qa_enhanced.py          # F2: 知识问答增强
│   ├── f3_academic_writing.py     # F3: 学术写作全流程
│   └── f4_review_planning.py      # F4: 复习计划生成
│
├── infrastructure/          # 基础设施
│   ├── cli.py              # 命令行接口
│   └── logging.py          # 日志系统
│
├── config/                 # 配置管理
│   └── settings.py         # Pydantic 配置定义
│
└── tests/                  # 测试套件
    ├── unit/               # 单元测试
    ├── integration/        # 集成测试
    └── verification/       # 验收测试
```

---

## 四大业务流程

### F1: 学习研究一体化

**流程图：**
```
研究 → 确认 → 概念提取 → 任务分解 → Grilling 循环 → 保存进度
```

**核心节点：**
1. **Research Node** - 调用 AutoResearch 生成研究报告
2. **Concept Extraction** - 从报告中提取关键概念
3. **Task Breakdown** - 按概念分解学习任务
4. **Grilling Loop** - grill-me + grill-you 交互学习
5. **Mastery Evaluation** - 评估掌握程度
6. **Progress Save** - 更新 Task.md 和 handoff.md

**适用场景：** 新主题学习、技术调研、知识体系构建

---

### F2: 知识问答增强

**功能：**
- 基于已有知识库的智能问答
- 集成 review_agent 知识查询
- 支持网络搜索补充
- 自动更新 CONTEXT.md

**核心能力：**
- 精准知识检索
- 答案质量评估
- 术语一致性维护

**适用场景：** 复习答疑、知识点查询、概念澄清

---

### F3: 学术写作全流程

**流程阶段：**
```
Clarification → Research → Writing → Review → 循环
```

**核心特性：**
- 核心论点提炼
- 研究计划生成
- 论文大纲构建
- 分章节写作
- 质量审查评分

**适用场景：** 学术论文、研究报告、毕业论文

---

### F4: 复习计划生成

**功能：**
- 知识点自动提取
- SM2 间隔重复调度
- 个性化复习计划

**核心算法：**
- SuperMemo 2 (SM2) 间隔重复算法
- 遗忘曲线建模
- 动态调度优化

**适用场景：** 长期记忆保持、考试准备、知识巩固

---

## Claude Skills

上层提供直接与 Claude Code CLI 交互的 Skills：

| Skill | 功能 | 调用方式 |
|-------|------|----------|
| `review-system` | 编排系统 | `/review-system 复习经济管理` |
| `review-session` | 会话初始化 | `/review-session 复习数据结构` |
| `continue-task` | 断点恢复 | `/continue-task review-20250619` |
| `grill-me` | AI 考你 | `/grill-me 检查链表理解` |
| `grill-you` | 你考 AI | `/grill-you 再问几个问题` |
| `advance-task` | 保存进度 | `/advance-task Task 3 完成` |
| `academic-coevolution` | 学术协作 | `/academic-coevolution-main` |
| `academic-writing-assist` | 写作助手 | 直接对话交互 |
| `ima-schedule-agent` | 日程管理 | 直接对话交互 |
| `write-a-skill` | 技能创作 | `/write-a-skill` |

---

## 扩展功能

### AutoResearch

智能自动化研究工具，基于 DeepSeek V4-Pro + WebSearch。

```bash
# 基础用法
python -m autoresearch "RAG 技术调研"

# 深度研究
python -m autoresearch "大模型微调" --mode deep --type 技术

# 自然语言模式
python -m autoresearch "帮我调研 Agent 技能和工作流优化"
```

**核心特性：**
- 多维度搜索
- 结构化报告生成
- arXiv 编号追踪
- 置信度标注

---

### review_agent

智能复习助手，基于 SM2 间隔重复算法。

```bash
# 启动复习界面
python -m review_agent
```

**核心特性：**
- SM2 算法调度
- 智能出题
- 答案评估
- 错题管理

---

## 快速开始

### 前置要求

- Claude Code CLI
- Python 3.12+
- LangGraph

### 安装

```bash
# 克隆项目
git clone https://github.com/Joeowo/ComindFlow.git
cd ComindFlow

# 安装 Agent Framework 依赖
cd agent_framework
pip install -r requirements.txt

# 安装扩展功能依赖
cd ../AutoResearch && pip install -r requirements.txt
cd ../review_agent && pip install -r requirements.txt
```

### 配置

创建 `.env` 文件：

```env
# LLM 配置
LLM_API_KEY=sk-your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# Checkpoint 配置
CHECKPOINT_DB_PATH=agent_framework/checkpoints.db
CHECKPOINT_CLEANUP_DAYS=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE_PATH=agent_framework/logs/agent.log
```

### 使用示例

```bash
# 1. 初始化会话
python -m infrastructure.cli init "RAG技术调研" --workflow f1

# 2. 运行 F1 Workflow
python -m infrastructure.cli run f1 --topic "RAG技术"

# 3. 恢复会话
python -m infrastructure.cli resume sessions/RAG技术调研

# 4. 查看状态
python -m infrastructure.cli status
```

---

## 测试

```bash
# 运行所有测试
pytest agent_framework/

# 运行单元测试
pytest agent_framework/tests/unit/

# 运行集成测试
pytest agent_framework/tests/integration/

# 查看覆盖率
pytest agent_framework/ --cov=agent_framework --cov-report=html
```

---

## 术语定义

详见 [CONTEXT.md](CONTEXT.md) 核心术语：
- **执行层状态** - LangGraph 运行时状态
- **持久层状态** - 跨会话文件存储状态
- **缓存层状态** - 内存中的状态副本
- **Checkpoint** - 状态快照与断点恢复机制

---

## 许可证

MIT License

---

## 联系方式

- 作者: Joeowo
- 项目主页: https://github.com/Joeowo/ComindFlow

---

**ComindFlow** - 让思维流动，让知识生长。
