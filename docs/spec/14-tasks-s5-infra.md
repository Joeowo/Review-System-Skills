# Tasks: Sub-Spec S5 - 基础设施层

**父文档**: [10-master-plan.md](10-master-plan.md)
**预估总 LOC**: ~1,200

---

## Task 1: 实现配置管理 (~80 LOC)

**描述**: 实现 Pydantic 配置系统

**验收标准**:
- [ ] LLMConfig 定义正确
- [ ] CheckpointConfig 定义正确
- [ ] LogConfig 定义正确
- [ ] AgentConfig 可从环境变量加载
- [ ] 默认值合理

**实现要点**:
```python
# config/settings.py
from pydantic_settings import BaseSettings

class LLMConfig(BaseSettings):
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"

    class Config:
        env_prefix = "LLM_"

class AgentConfig(BaseSettings):
    llm: LLMConfig
    checkpoint: CheckpointConfig
    log: LogConfig

    class Config:
        env_file = ".env"
```

**测试**:
- 配置加载测试
- 默认值测试
- 环境变量测试

**依赖**: 无

**预计时间**: 3 小时

---

## Task 2: 实现日志系统 (~100 LOC)

**描述**: 实现 Loguru 日志配置

**验收标准**:
- [ ] 控制台输出格式正确
- [ ] 文件输出正确
- [ ] 日志轮转工作
- [ ] 日志压缩工作

**实现要点**:
```python
# infrastructure/logging.py
from loguru import logger

class LoggerConfig:
    @staticmethod
    def setup(level: str, file_path: str, rotation: str, retention: str):
        logger.remove()
        logger.add(sys.stderr, format=..., level=level, colorize=True)
        if file_path:
            logger.add(file_path, rotation=rotation, retention=retention)
```

**测试**:
- 输出测试
- 文件测试
- 轮转测试

**依赖**: Task 1

**预计时间**: 3 小时

---

## Task 3: 实现 pytest 配置 (~80 LOC)

**描述**: 配置测试框架

**验收标准**:
- [ ] pytest 配置正确
- [ ] Fixtures 可用
- [ ] 测试标记定义

**实现要点**:
```python
# tests/conftest.py
@pytest.fixture
def temp_session(tmp_path):
    session_path = tmp_path / "test_session"
    session_path.mkdir()
    return str(session_path)

@pytest.fixture
def temp_checkpointer(tmp_path):
    return SqliteSaver.from_conn_string(f"file:{tmp_path}/test.db}")
```

**依赖**: S1

**预计时间**: 2 小时

---

## Task 4: 实现单元测试框架 (~150 LOC)

**描述**: 实现各层单元测试

**验收标准**:
- [ ] core/ 单元测试
- [ ] tools/ 单元测试
- [ ] workflows/ 单元测试
- [ ] infrastructure/ 单元测试

**依赖**: Task 3

**预计时间**: 5 小时

---

## Task 5: 实现集成测试框架 (~150 LOC)

**描述**: 实现集成测试

**验收标准**:
- [ ] State 同步集成测试
- [ ] Checkpoint 集成测试
- [ ] Tools 集成测试
- [ ] Workflow 集成测试

**依赖**: Task 4

**预计时间**: 5 小时

---

## Task 6: 实现 CLI 入口 (~150 LOC)

**描述**: 实现命令行接口

**验收标准**:
- [ ] init 命令可用
- [ ] resume 命令可用
- [ ] run 命令可用
- [ ] status 命令可用
- [ ] 帮助文档完整

**实现要点**:
```python
# infrastructure/cli.py
@click.group()
def cli():
    """ComindFlow Agent Framework CLI"""
    pass

@cli.command()
@click.argument("topic")
def init(topic: str, session: str, workflow: str):
    """初始化新会话"""
    pass
```

**测试**:
- CLI 命令测试
- 参数测试

**依赖**: Task 1

**预计时间**: 5 小时

---

## Task 7: 实现文档生成 (~100 LOC)

**描述**: 实现文档自动生成

**验收标准**:
- [ ] API 文档可生成
- [ ] 架构图可生成
- [ ] 文档格式统一

**实现要点**:
```python
# scripts/generate_api_docs.py
def generate_module_docs(module_path: str, output_path: str):
    pass
```

**依赖**: 无

**预计时间**: 3 小时

---

## Task 8: 实现测试覆盖验证 (~100 LOC)

**描述**: 验证测试覆盖率

**验收标准**:
- [ ] 覆盖率报告可生成
- [ ] 覆盖率 ≥ 80%
- [ ] 缺口分析完成

**依赖**: Task 4, Task 5

**预计时间**: 3 小时

---

## Task 9: 编写用户文档 (~150 LOC)

**描述**: 编写用户使用文档

**验收标准**:
- [ ] 快速开始指南
- [ ] Workflow 使用指南
- [ ] 定制指南
- [ ] 故障排除

**依赖**: 所有前置任务

**预计时间**: 5 小时

---

## Task 10: 全面验证 (~100 LOC)

**描述**: 端到端验证

**验收标准**:
- [ ] 所有测试通过
- [ ] 覆盖率达标
- [ ] 文档完整
- [ ] 可演示

**依赖**: 所有前置任务

**预计时间**: 3 小时

---

## Summary

- **总任务数**: 10
- **总预估 LOC**: ~1,200
- **关键路径**: Task 1 → Task 2 → Task 6
- **并行机会**: Task 3-5 可与 Task 6-7 并行

→ **Human**: 审查任务列表，批准后开始实施
