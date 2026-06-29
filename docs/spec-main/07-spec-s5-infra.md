# Sub-Spec S5: 基础设施层

**父文档**: [01-master-spec.md](01-master-spec.md)
**预估 LOC**: ~1,200
**依赖**: 可独立开发，但完整功能依赖所有层

---

## 目标 (Objective)

提供配置、日志、测试、文档、CLI 等基础设施支持。

---

## 组件分解 (Component Breakdown)

### I1: 配置管理 (~150 LOC)

**目标**: 提供类型安全的配置管理

**接口定义**:

```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class LLMConfig(BaseSettings):
    """LLM 配置"""
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000

    class Config:
        env_prefix = "LLM_"

class CheckpointConfig(BaseSettings):
    """Checkpoint 配置"""
    db_path: str = "agent_framework/checkpoints.db"
    cleanup_days: int = 30

    class Config:
        env_prefix = "CHECKPOINT_"

class LogConfig(BaseSettings):
    """日志配置"""
    level: str = "INFO"
    file_path: Optional[str] = "agent_framework/logs/agent.log"
    rotation: str = "100 MB"
    retention: str = "30 days"

    class Config:
        env_prefix = "LOG_"

class AgentConfig(BaseSettings):
    """Agent 框架总配置"""
    llm: LLMConfig
    checkpoint: CheckpointConfig
    log: LogConfig

    confirmation_level: str = "balanced"  # minimal/balanced/thorough
    max_retries: int = 3
    timeout_seconds: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 全局配置实例
config = AgentConfig()
```

**环境变量示例**:

```env
# .env.example
# LLM 配置
LLM_API_KEY=sk-your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Checkpoint 配置
CHECKPOINT_DB_PATH=agent_framework/checkpoints.db
CHECKPOINT_CLEANUP_DAYS=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE_PATH=agent_framework/logs/agent.log
LOG_ROTATION=100 MB
LOG_RETENTION=30 days

# Agent 配置
AGENT_CONFIRMATION_LEVEL=balanced
AGENT_MAX_RETRIES=3
AGENT_TIMEOUT_SECONDS=60
```

**成功标准**:
- 配置可从环境变量加载
- 类型验证正确
- 支持默认值

---

### I2: 日志系统 (~200 LOC)

**目标**: 提供结构化日志系统

**接口定义**:

```python
# infrastructure/logging.py
from loguru import logger
import sys
from pathlib import Path

class LoggerConfig:
    """日志配置"""

    @staticmethod
    def setup(
        level: str = "INFO",
        file_path: str = None,
        rotation: str = "100 MB",
        retention: str = "30 days"
    ):
        """配置日志系统"""

        # 移除默认处理器
        logger.remove()

        # 添加控制台处理器（带颜色）
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=level,
            colorize=True
        )

        # 添加文件处理器
        if file_path:
            log_path = Path(file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            logger.add(
                file_path,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level=level,
                rotation=rotation,
                retention=retention,
                compression="zip"
            )

        logger.info("日志系统初始化完成")

# 初始化日志
def init_logger(config: LogConfig):
    """初始化日志系统"""
    LoggerConfig.setup(
        level=config.level,
        file_path=config.file_path,
        rotation=config.rotation,
        retention=config.retention
    )
```

**日志使用**:

```python
from infrastructure.logging import logger

# 在各模块中使用
logger.info("任务开始", extra={"task_id": "123"})
logger.warning("研究内容不足", extra={"topic": topic})
logger.error("API 调用失败", extra={"error": str(e)})
```

**成功标准**:
- 日志正确输出到控制台和文件
- 支持日志轮转和压缩
- 结构化字段正确

---

### I3: 测试框架 (~400 LOC)

**目标**: 提供完整的测试基础设施

**测试结构**:

```
tests/
├── conftest.py                    # pytest 配置
├── unit/                          # 单元测试
│   ├── core/                      # 核心框架测试
│   ├── tools/                     # 工具测试
│   └── infrastructure/            # 基础设施测试
├── integration/                   # 集成测试
│   ├── test_state_sync.py
│   ├── test_checkpoint.py
│   └── test_tools_integration.py
└── e2e/                          # 端到端测试
    ├── test_f1_workflow.py
    ├── test_f3_workflow.py
    └── test_recovery.py
```

**pytest 配置**:

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver
from core.state import AgentState
from config.settings import AgentConfig

@pytest.fixture
def temp_session(tmp_path):
    """临时会话目录"""
    session_path = tmp_path / "test_session"
    session_path.mkdir()
    (session_path / "CONTEXT.md").write_text("# 测试上下文\n")
    (session_path / "Task.md").write_text("# 测试任务\n")
    return str(session_path)

@pytest.fixture
def temp_checkpointer(tmp_path):
    """临时 checkpoint fixture"""
    db_path = tmp_path / "test.db"
    return SqliteSaver.from_conn_string(f"file:{db_path}")

@pytest.fixture
def sample_state():
    """示例状态 fixture"""
    return AgentState(
        topic="测试主题",
        session_path="/tmp/test",
        current_step="init",
        workflow_name="f1",
        retry_count=0,
        cached_terminology={},
        cached_task_progress={},
        tool_results={},
        error_message=None,
        current_task_id="task_1",
        start_time="2024-01-01T00:00:00"
    )

@pytest.fixture
def mock_config(monkeypatch):
    """Mock 配置 fixture"""
    monkeypatch.setenv("LLM_API_KEY", "test_key")
    monkeypatch.setenv("CHECKPOINT_DB_PATH", ":memory:")
    return AgentConfig()

# 测试标记
def pytest_configure(config):
    """配置 pytest 标记"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "e2e: 端到端测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
```

**测试工具函数**:

```python
# tests/utils.py
from typing import Dict, Any

def assert_state_step(state: Dict[str, Any], expected_step: str):
    """断言状态步骤"""
    assert state["current_step"] == expected_step, \
        f"Expected step {expected_step}, got {state['current_step']}"

def assert_no_error(state: Dict[str, Any]):
    """断言无错误"""
    assert state["error_message"] is None, \
        f"Unexpected error: {state['error_message']}"

def load_test_report(path: str) -> str:
    """加载测试报告"""
    return Path(path).read_text(encoding="utf-8")
```

**测试运行命令**:

```bash
# 快速测试（跳过 E2E 和慢速测试）
poetry run pytest -m "not e2e and not slow"

# 单元测试
poetry run pytest -m unit

# 集成测试
poetry run pytest -m integration

# 端到端测试
poetry run pytest -m e2e

# 覆盖率报告
poetry run pytest --cov=agent_framework --cov-report=html --cov-report=term

# 详细输出
poetry run pytest -vv -s
```

**成功标准**:
- 所有测试可独立运行
- 测试覆盖率 ≥ 80%
- Fixtures 可正确复用

---

### I4: 文档生成 (~250 LOC)

**目标**: 自动生成 API 文档和架构图

**文档结构**:

```
docs/
├── api/                           # API 文档
│   ├── core.md                   # 核心框架 API
│   ├── tools.md                  # 工具 API
│   ├── workflows.md              # Workflow API
│   └── config.md                 # 配置 API
├── guides/                        # 使用指南
│   ├── quickstart.md             # 快速开始
│   ├── workflows.md              # Workflow 指南
│   └── customization.md          # 定制指南
└── architecture/                  # 架构文档
    ├── overview.md               # 架构概览
    ├── state-management.md       # 状态管理
    └── checkpoint.md             # Checkpoint 机制
```

**API 文档生成**:

```python
# scripts/generate_api_docs.py
"""生成 API 文档"""
import inspect
from pathlib import Path

def generate_module_docs(module_path: str, output_path: str):
    """生成模块文档"""
    # 使用 pydoc 或 inspect 生成文档
    pass

if __name__ == "__main__":
    generate_module_docs("core", "docs/api/core.md")
```

**架构图生成**:

```python
# scripts/generate_diagrams.py
"""生成架构图"""
import graphviz

def generate_workflow_diagram(workflow_name: str, nodes: list, edges: list):
    """生成 Workflow 架构图"""
    dot = graphviz.Digraph(comment=workflow_name)

    for node in nodes:
        dot.node(node["id"], node["label"])

    for edge in edges:
        dot.edge(edge["from"], edge["to"], label=edge.get("label", ""))

    dot.render(f"docs/architecture/{workflow_name}", format="png", cleanup=True)
```

**成功标准**:
- API 文档自动更新
- 架构图与代码一致
- 文档格式统一

---

### I5: CLI 入口 (~200 LOC)

**目标**: 提供命令行接口

**CLI 结构**:

```python
# infrastructure/cli.py
import click
from pathlib import Path
from config.settings import config
from workflows.f1_learning_research import create_f1_workflow
from workflows.f3_academic_writing import create_f3_workflow
from core.checkpoint import CheckpointManager

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ComindFlow Agent Framework CLI"""
    pass

@cli.command()
@click.argument("topic")
@click.option("--session", "-s", help="会话目录路径")
@click.option("--workflow", "-w", default="f1", help="Workflow 名称")
def init(topic: str, session: str, workflow: str):
    """初始化新会话"""
    session_path = Path(session or f"sessions/{topic.replace(' ', '_')}")

    click.echo(f"初始化会话: {session_path}")
    click.echo(f"主题: {topic}")
    click.echo(f"Workflow: {workflow}")

    # 创建会话目录
    session_path.mkdir(parents=True, exist_ok=True)

    # 初始化文件
    (session_path / "CONTEXT.md").write_text(f"# {topic}\n\n## 术语定义\n\n")
    (session_path / "Task.md").write_text(f"# {topic} - 学习任务\n\n")
    (session_path / "README.md").write_text(f"""# {topic}

初始化时间: {datetime.now().isoformat()}
Workflow: {workflow}
""")

    click.echo(f"✓ 会话已创建: {session_path}")

@cli.command()
@click.argument("session_path", type=click.Path(exists=True))
@click.option("--thread-id", "-t", help="Checkpoint thread ID")
def resume(session_path: str, thread_id: str):
    """恢复会话"""
    click.echo(f"恢复会话: {session_path}")

    checkpointer = CheckpointManager().get_checkpointer()

    # 列出 checkpoints
    checkpoints = checkpointer.list_checkpoints(thread_id or "default")

    if not checkpoints:
        click.echo("未找到可恢复的 checkpoint")
        return

    click.echo(f"找到 {len(checkpoints)} 个 checkpoint:")
    for i, cp in enumerate(checkpoints):
        click.echo(f"  {i+1}. {cp['timestamp']} - {cp['step']}")

    # 恢复最新 checkpoint
    click.echo("✓ 会话已恢复")

@cli.command()
@click.argument("workflow_name", type=click.Choice(["f1", "f2", "f3", "f4"]))
@click.option("--topic", "-t", help="研究/写作主题")
@click.option("--session", "-s", help="会话路径")
def run(workflow_name: str, topic: str, session: str):
    """运行指定 Workflow"""
    click.echo(f"运行 Workflow: {workflow_name}")

    # 选择 workflow
    workflows = {
        "f1": create_f1_workflow,
        "f3": create_f3_workflow,
    }

    if workflow_name not in workflows:
        click.echo(f"Workflow {workflow_name} 暂未实现")
        return

    workflow = workflows[workflow_name]()
    app = workflow.compile(
        checkpointer=CheckpointManager().get_checkpointer()
    )

    # 执行
    result = app.invoke({
        "topic": topic,
        "session_path": session
    })

    click.echo(f"✓ Workflow 完成: {result['current_step']}")

@cli.command()
def status():
    """显示系统状态"""
    click.echo("=== Agent Framework 状态 ===\n")

    click.echo(f"LLM 配置:")
    click.echo(f"  Model: {config.llm.model}")
    click.echo(f"  Base URL: {config.llm.base_url}")

    click.echo(f"\nCheckpoint 配置:")
    click.echo(f"  路径: {config.checkpoint.db_path}")
    click.echo(f"  清理周期: {config.checkpoint.cleanup_days} 天")

    click.echo(f"\n日志配置:")
    click.echo(f"  级别: {config.log.level}")
    click.echo(f"  文件: {config.log.file_path}")

if __name__ == "__main__":
    cli()
```

**CLI 命令**:

```bash
# 查看帮助
agent --help

# 初始化会话
agent init "机器学习基础" --session sessions/ml --workflow f1

# 恢复会话
agent resume sessions/ml --thread-id thread_123

# 运行 workflow
agent run f1 --topic "深度学习" --session sessions/dl

# 查看状态
agent status
```

**成功标准**:
- CLI 命令正确执行
- 错误信息友好
- 帮助文档完整

---

## 测试策略

### 单元测试

| 组件 | 测试重点 |
|------|----------|
| 配置管理 | 加载、验证、默认值 |
| 日志系统 | 输出格式、文件写入 |
| 测试框架 | Fixtures、工具函数 |
| CLI | 命令执行、参数解析 |

### 集成测试

- 配置与日志集成
- CLI 与 Workflow 集成

---

## 边界规则

### Always Do
- 日志记录所有关键操作
- 配置加载失败时给出明确错误
- CLI 提供友好的错误提示

### Ask First
- 修改日志格式
- 新增 CLI 命令

### Never Do
- 硬编码配置值
- 在日志中记录敏感信息

---

## 成功标准

- [ ] 配置可正确加载
- [ ] 日志正确输出
- [ ] 测试覆盖率 ≥ 70%
- [ ] 文档自动生成
- [ ] CLI 功能完整

---

## 依赖项

```toml
[tool.poetry.dependencies]
python = "^3.12"
pydantic-settings = "^2.0"
loguru = "^0.7"
click = "^8.0"

[tool.poetry.dev-dependencies]
pytest = "*"
pytest-cov = "*"
pytest-html = "*"
```

---

**文档版本**: 1.0
