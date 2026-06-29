# Master Spec: ComindFlow Agent Framework

**版本**: 1.0
**日期**: 2026-06-28
**状态**: 草案

---

## 目标 (Objective)

构建基于 LangGraph 的统一 Agent Framework，作为 ComindFlow 项目的核心编排引擎，实现：

1. **统一编排**: 整合现有 10+ skills（review-system, grill-me, grill-you 等）和模块（AutoResearch、review_agent）
2. **智能状态管理**: 实现 ADR-0001 双状态并行策略（执行层 + 持久层）
3. **断点恢复**: 基于 SQLite checkpoint 支持跨天、跨会话恢复（ADR-0002）
4. **模块集成**: 提供标准化的 Tool 封装，方便调用 AutoResearch、review_agent
5. **Workflow 编排**: 支持 F1-F4 四大核心业务流程的端到端执行

---

## 范围边界 (Scope Boundaries)

### IN SCOPE（包含）

| 模块 | 说明 |
|------|------|
| **核心框架** | State 管理、Checkpoint、异常处理、用户确认机制 |
| **工具适配** | AutoResearch、review_agent 的 LangChain Tool 封装 |
| **Skills 适配** | 现有 skills 的适配器层（保留文件接口） |
| **Workflow** | F1 学习研究一体化、F3 学术写作全流程 |
| **基础设施** | 配置、日志、测试框架、CLI 入口 |

### OUT OF SCOPE（不包含）

| 项目 | 说明 |
|------|------|
| **多用户支持** | 单用户本地运行，无认证/权限系统 |
| **Web UI** | 无 Web 界面，保持 CLI/交互模式 |
| **云部署** | 仅本地运行，不考虑容器化/K8s |
| **实时协作** | 无多人协作编辑功能 |

### FUTURE PHASE（未来阶段）

| 功能 | 说明 |
|------|------|
| **F2 知识问答增强** | review_agent 深度集成 |
| **F4 复习计划生成** | SM2 调度器完整集成 |
| **Web Dashboard** | 可选的 Web 管理界面 |
| **多模型支持** | 扩展到其他 LLM 提供商 |

---

## 技术栈 (Tech Stack)

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **语言** | Python | 3.12+ | 主要开发语言 |
| **编排框架** | LangGraph | latest | Workflow 编排 |
| **工具框架** | LangChain | latest | Tool 封装 |
| **Checkpoint** | SQLite | 内置 | 状态持久化 |
| **LLM 接口** | OpenAI API | - | LLM 调用 |
| **测试框架** | pytest | latest | 单元/集成测试 |
| **日志** | loguru | latest | 结构化日志 |
| **配置** | pydantic-settings | latest | 类型安全配置 |

---

## 架构概览 (Architecture Overview)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Agent Framework                                │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    Orchestration Layer                          │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐ │ │
│  │  │  LangGraph    │  │  Checkpoint   │  │  Exception Handler  │ │ │
│  │  │  Workflows    │  │  (SQLite)     │  │  + Degradation      │ │ │
│  │  └───────────────┘  └───────────────┘  └─────────────────────┘ │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐ │ │
│  │  │  State Sync   │  │  Confirmation │  │  Base Node Library  │ │ │
│  │  │  (Dual Layer) │  │  (Human-in-   │  │  (Common Patterns)  │ │ │
│  │  │               │  │   the-Loop)   │  │                      │ │ │
│  │  └───────────────┘  └───────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                 ↕                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                      Tool Adapters Layer                         │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐ │ │
│  │  │ AutoResearch  │  │ review_agent  │  │   Skills Adapters    │ │ │
│  │  │     Tools     │  │     Tools     │  │ (grill-me, etc.)    │ │ │
│  │  └───────────────┘  └───────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                 ↕                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    Persistence Layer                             │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐ │ │
│  │  │  CONTEXT.md   │  │   Task.md     │  │    handoff.md       │ │ │
│  │  │ (Terminology) │  │ (Progress)    │  │  (Checkpoint HR)    │ │ │
│  │  └───────────────┘  └───────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 核心概念

| 概念 | 定义 |
|------|------|
| **AgentState** | LangGraph 运行时状态，包含执行层和缓存层数据 |
| **Checkpoint** | SQLite 持久化的执行快照，用于断点恢复 |
| **持久层文件** | CONTEXT.md、Task.md、handoff.md，人类可读 |
| **Tool** | LangChain Tool 封装的可调用单元 |
| **Workflow** | 由节点和边组成的业务执行路径 |
| **Node** | Workflow 中的执行单元，接收/返回 AgentState |

---

## 命令 (Commands)

```bash
# 开发
poetry install              # 安装依赖
poetry run agent-dev         # 开发模式启动

# 测试
poetry run pytest           # 运行所有测试
poetry run pytest -v        # 详细输出
poetry run pytest --cov     # 覆盖率报告

# 代码质量
poetry run ruff check       # 代码检查
poetry run ruff format      # 代码格式化
poetry run mypy             # 类型检查

# 运行
poetry run agent init <session>   # 初始化会话
poetry run agent resume <id>      # 恢复会话
poetry run agent workflow <name> # 运行指定 workflow
```

---

## 项目结构 (Project Structure)

```
agent_framework/
├── core/                          # 核心框架
│   ├── __init__.py
│   ├── state.py                  # AgentState 定义
│   ├── state_sync.py             # 状态同步逻辑
│   ├── checkpoint.py              # Checkpoint 管理
│   ├── exceptions.py              # 异常定义
│   ├── exception_handler.py      # 异常处理器
│   ├── confirmation.py            # 用户确认机制
│   └── base_nodes.py             # 基础节点库
│
├── tools/                         # 工具适配
│   ├── __init__.py
│   ├── autoresearch_tools.py     # AutoResearch Tools
│   ├── review_agent_tools.py     # review_agent Tools
│   ├── skills_adapters.py        # Skills 适配器
│   └── adapters/                 # 适配器层
│       ├── __init__.py
│       └── autoresearch_adapter.py
│
├── workflows/                     # Workflow 定义
│   ├── __init__.py
│   ├── base.py                   # Workflow 基类
│   ├── f1_learning_research.py  # F1: 学习研究一体化
│   ├── f2_qa_enhanced.py        # F2: 知识问答增强
│   ├── f3_academic_writing.py   # F3: 学术写作全流程
│   └── f4_review_planning.py    # F4: 复习计划生成
│
├── config/                        # 配置管理
│   ├── __init__.py
│   ├── settings.py               # 配置定义
│   └── defaults.py               # 默认配置
│
├── infrastructure/                # 基础设施
│   ├── __init__.py
│   ├── logging.py                # 日志系统
│   └── cli.py                    # CLI 入口
│
├── tests/                         # 测试
│   ├── __init__.py
│   ├── conftest.py               # pytest 配置
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   └── e2e/                      # 端到端测试
│
├── checkpoints.db                 # SQLite checkpoint 文件
├── pyproject.toml                # 项目配置
└── README.md                     # 项目说明
```

---

## 代码风格 (Code Style)

### Python 风格指南

遵循 **PEP 8** 和以下项目约定：

```python
# 类型注解（必需）
from typing import Dict, List, Optional
from langchain_core.tools import tool

def process_task(task_id: str, options: Dict[str, Any]) -> Optional[str]:
    """处理任务

    Args:
        task_id: 任务标识符
        options: 处理选项

    Returns:
        处理结果路径，失败返回 None
    """
    if not task_id:
        return None
    # 实现...
    return result_path

# Tool 封装风格
@tool
def research_tool(topic: str, depth: str = "comprehensive") -> str:
    """执行研究任务

    Args:
        topic: 研究主题
        depth: 研究深度 (comprehensive/deep/survey)

    Returns:
        报告文件路径
    """
    return research_single(topic, "技术", depth)

# 异常定义风格
class ResearchError(AgentException):
    """研究相关异常"""
    level = "degrade"
    fallback = "use_summary"

# 节点定义风格
def research_node(state: AgentState) -> Dict[str, Any]:
    """研究节点

    输入: state["topic"]
    输出: state["report_path"], state["key_concepts"]
    """
    try:
        result = research_tool.invoke(state["topic"])
        return {
            "report_path": result,
            "current_step": "research_complete",
            "error_message": None
        }
    except Exception as e:
        return {
            "error_message": str(e),
            "current_step": "research_failed"
        }
```

### 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 模块 | snake_case | `state_sync.py`, `autoresearch_tools.py` |
| 类 | PascalCase | `AgentState`, `ExceptionHandler` |
| 函数/方法 | snake_case | `process_task()`, `load_session()` |
| 常量 | UPPER_SNAKE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 私有成员 | _前缀 | `_internal_method()` |

### 文档约定

- 所有公开模块/类/函数必须有 docstring
- 使用 Google 风格 docstring
- 复杂逻辑添加行内注释

---

## 测试策略 (Testing Strategy)

### 测试金字塔

```
        ┌─────────┐
        │   E2E   │  ~15%  - 端到端 Workflow 测试
        ├─────────┤
        │  集成测试 │  ~35%  - 节点、Tool、状态同步
        ├─────────┤
        │ 单元测试  │  ~50%  - 核心逻辑、工具函数
        └─────────┘
```

### 测试框架

```python
# pytest 配置 (tests/conftest.py)
import pytest
from langgraph.checkpoint.sqlite import SqliteSaver

@pytest.fixture
def mock_checkpointer(tmp_path):
    """临时 checkpoint fixture"""
    return SqliteSaver.from_conn_string(f"file:{tmp_path}/test.db")

@pytest.fixture
def sample_state():
    """示例状态 fixture"""
    return AgentState(
        topic="测试主题",
        session_path="/tmp/test_session",
        current_step="init",
        # ...
    )
```

### 覆盖率要求

| 模块 | 最低覆盖率 |
|------|-----------|
| core/ | 85% |
| tools/ | 80% |
| workflows/ | 75% |
| infrastructure/ | 70% |

### 测试运行

```bash
# 快速测试（跳过 E2E）
poetry run pytest -m "not e2e"

# 完整测试
poetry run pytest

# 覆盖率
poetry run pytest --cov=agent_framework --cov-report=html
```

---

## 边界规则 (Boundaries)

### Always Do（始终执行）

| 规则 | 说明 |
|------|------|
| 运行测试 | 提交前必须通过所有测试 |
| 类型注解 | 所有公开 API 必须有类型注解 |
| 文件锁 | SQLite 写入使用事务性锁 |
| 日志记录 | 关键节点必须记录结构化日志 |
| 错误处理 | 遵循 ADR-0004 异常处理策略 |

### Ask First（先询问）

| 操作 | 说明 |
|------|------|
| ADR 变更 | 修改已有决策需要新的 ADR |
| 依赖升级 | 主要依赖版本升级需评估影响 |
| 接口变更 | 公开 API 变更需通知使用者 |
| 数据迁移 | 文件格式变更需提供迁移脚本 |

### Never Do（禁止操作）

| 禁止项 | 原因 |
|--------|------|
| 直接修改持久层文件 | 必须通过 state_sync 接口 |
| 硬编码路径 | 使用配置管理 |
| 捕获所有异常 | 必须区分异常类型 |
| 提交敏感信息 | API Key 等需用环境变量 |

---

## 成功标准 (Success Criteria)

### 技术指标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 测试覆盖率 | ≥ 80% | pytest --cov |
| 类型检查 | 通过 | mypy |
| 代码规范 | 通过 | ruff check |
| 集成测试 | 100% 通过 | pytest -m integration |

### 功能验证

- [ ] F1 Workflow 可端到端执行
- [ ] F3 Workflow 可端到端执行
- [ ] Checkpoint 恢复成功率 ≥ 95%
- [ ] 异常降级符合 ADR-0004
- [ ] 现有 skills 可无修改调用

### 用户验收

- [ ] 可成功初始化会话并恢复
- [ ] AutoResearch 调用成功
- [ ] grill-me/grill-you 可通过 Framework 调用
- [ ] 跨天断点恢复正常工作

---

## 子规范目录 (Sub-Spec Directory)

| ID | 名称 | 预估 LOC | 文档路径 |
|----|------|----------|----------|
| S1 | 核心框架层 | ~1,700 | [02-spec-s1-core.md](02-spec-s1-core.md) |
| S2 | 工具适配层 | ~1,150 | [03-spec-s2-tools.md](03-spec-s2-tools.md) |
| S3 | Workflow - 学习研究 | ~850 | [04-spec-s3-workflow-lr.md](04-spec-s3-workflow-lr.md) |
| S4 | Workflow - 学术写作复习 | ~950 | [05-spec-s4-workflow-aw.md](05-spec-s4-workflow-aw.md) |
| S5 | 基础设施层 | ~1,200 | [06-spec-s5-infra.md](06-spec-s5-infra.md) |

---

## 相关文档

- [ADR 索引](../adr/README.md)
- [规模分析](00-size-analysis.md)
- [术语定义](../../CONTEXT.md)

---

**文档版本**: 1.0
**下一步**: Phase 2 - 分解 Sub-Specs
