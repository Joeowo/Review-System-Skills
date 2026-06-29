# Agent Framework 使用指南

## 快速启动

### 方法 1: 使用启动脚本

**Windows:**
```bash
cd agent_framework
start.bat
```

**Linux/Mac:**
```bash
cd agent_framework
chmod +x start.sh
./start.sh
```

### 方法 2: 直接运行 Python

```bash
cd agent_framework
python main.py
```

## 交互式菜单功能

启动后，你将看到主菜单：

```
╔═════════════════════════════════════════════════════════════╗
║                  🚀 Agent Framework                        ║
║              ComindFlow 核心编排引擎 v0.1.0                  ║
╚═════════════════════════════════════════════════════════════╝

会话目录: sessions    会话数: 0

1. 选择 Workflow          选择并运行工作流 (F1/F2/F3/F4)
2. 会话管理            创建新会话 / 恢复已有会话
3. 查看状态            显示配置和系统状态
4. 快速启动            快速启动最近使用的会话
0. 退出                退出系统
```

## Workflow 说明

| Workflow | 名称 | 功能描述 |
|----------|------|----------|
| **F1** | 学习研究一体化 | 从研究到掌握的完整学习流程 |
| **F2** | 知识问答增强 | 基于知识库的智能问答 |
| **F3** | 学术写作全流程 | 从澄清到完成的学术写作 |
| **F4** | 复习计划生成 | 基于 SM2 算法的复习计划 |

## 配置

首次使用前，请复制环境配置模板：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入你的 API Key 和配置。

## 使用示例

### 示例 1: 学习新主题 (F1)

1. 启动程序后选择 `1. 选择 Workflow`
2. 选择 `f1` - 学习研究一体化
3. 选择 `新会话`，输入会话名称（如：`学习_RAG技术`）
4. 输入学习主题（如：`RAG 技术调研`）
5. Workflow 自动执行：
   - 调用 AutoResearch 生成研究报告
   - 提取关键概念
   - 分解学习任务
   - 进入交互式学习循环

### 示例 2: 知识问答 (F2)

1. 启动程序后选择 `1. 选择 Workflow`
2. 选择 `f2` - 知识问答增强
3. 选择一个已有会话（包含 CONTEXT.md 和 sources/）
4. 输入你的问题
5. 获得基于知识库的回答

### 示例 3: 学术写作 (F3)

1. 启动程序后选择 `1. 选择 Workflow`
2. 选择 `f3` - 学术写作全流程
3. 创建新会话，输入写作主题
4. Workflow 执行：
   - 生成澄清问题
   - 执行文献调研
   - 生成论文大纲
   - 分章节写作
   - 质量审查

## 会话目录结构

```
sessions/
└── 你的会话名/
    ├── CONTEXT.md      # 术语定义和领域语言
    ├── Task.md         # 学习任务进度
    ├── handoff.md      # 会话交接记录
    └── draft/          # 写作草稿 (F3)
```

## 状态持久化

- **执行时**: 状态保存在 LangGraph 运行时
- **Checkpoint**: 自动保存到 `checkpoints.db`
- **持久层**: 同步到会话文件的 CONTEXT.md 和 Task.md

## 依赖要求

```
langgraph
langchain
rich
pydantic-settings
python-dotenv
```

安装依赖：
```bash
pip install langgraph langchain rich pydantic-settings python-dotenv
```
