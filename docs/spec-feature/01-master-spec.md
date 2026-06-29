# Master Spec: 技能系统重构

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## Objective

构建基于 **动态按需注入（Dynamic On-demand Injection）** 范式的高扩展性 Agent 技能系统，实现以下目标：

1. **业务技能与模型逻辑解耦** - 通过 Registry 和 Middleware 模式移除硬编码依赖
2. **提升通用能力复用率** - 通过标准化 SKILL.md 规范和生命周期管理
3. **降低 Token 消耗** - 通过目录注入 + 按需加载策略
4. **建立可观测性机制** - 通过链路追踪、异常诊断、幻觉检测

---

## Scope Boundaries

### IN SCOPE（包含）

| 组件 | 说明 |
|------|------|
| **Skill Registry** | 自动发现、注册、管理所有 Skills |
| **Middleware 调度层** | 请求拦截、上下文管理、技能路由 |
| **SKILL.md 标准化** | 遵循 write-a-skill 规范，提供验证和迁移工具 |
| **上下文优化** | 目录注入 + 按需加载 + 预算管理 |
| **可观测性** | 链路追踪、异常诊断、幻觉检测、污染检测 |
| **测试覆盖** | 单元测试、集成测试、端到端测试 |

### OUT OF SCOPE（不包含）

| 项目 | 说明 |
|------|------|
| **Skill 行为变更** | 保持现有 Skills 的业务逻辑不变 |
| **LLM 集成方式变更** | 继续使用 DeepSeek API |
| **多租户支持** | 单用户本地运行 |
| **分布式部署** | 本地执行为主 |
| **现有 Workflow 重构** | F1-F4 Workflow 保持现有结构 |

### FUTURE PHASE（未来阶段）

| 项目 | 说明 |
|------|------|
| **远程 Skill 支持** | 从远程仓库加载 Skills |
| **Skill Marketplace** | 技能分享和发现机制 |
| **多模型支持** | 支持 Claude、GPT 等其他 LLM |
| **性能优化** | 缓存、批处理等高级优化 |

---

## Tech Stack

### 核心技术

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **语言** | Python | 3.12+ | 主要开发语言 |
| **Agent 编排** | LangGraph | Latest | Workflow 和状态管理 |
| **数据验证** | Pydantic | v2 | 数据模型和验证 |
| **配置管理** | PyYAML | Latest | SKILL.md frontmatter 解析 |
| **LLM 调用** | DeepSeek API | v4 | 模型调用 |

### 开发工具

| 工具 | 用途 |
|------|------|
| pytest | 单元测试和集成测试 |
| pytest-asyncio | 异步测试支持 |
| structlog | 结构化日志 |
| ruff | 代码格式化和 linting |
| mypy | 类型检查 |

---

## Architecture Overview

### 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Code CLI / 用户入口                   │
│                   /grill-me  /grill-you /advance-task            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      Middleware 调度层                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 请求拦截     │  │ 上下文管理  │  │ 技能路由     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ 可观测性收集 │  │ 预算管理     │  │ 并行执行     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────▼─────────────────────────────────────┐
        │              Skill Registry (技能注册表)                  │
        │  扫描 SKILL.md → 解析 frontmatter → 注册技能             │
        └─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────▼─────────────────────────────────────┐
        │              Skills (按需加载)                          │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
        │  │  grill-me   │  │  grill-you  │  │ advance-task │   │
        │  │  SKILL.md   │  │  SKILL.md   │  │  SKILL.md   │   │
        │  │  REFERENCE  │  │  REFERENCE  │  │  REFERENCE  │   │
        │  │  scripts/   │  │  scripts/   │  │  scripts/   │   │
        │  └─────────────┘  └─────────────┘  └─────────────┘   │
        └───────────────────────────────────────────────────────┘
                          │
        ┌─────────────────▼─────────────────────────────────────┐
        │              Observability (可观测性)                   │
        │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
        │  │  链路追踪     │  │  异常诊断    │  │  幻觉检测    │   │
        │  └─────────────┘  └─────────────┘  └─────────────┘   │
        │  ┌─────────────┐  ┌─────────────┐                       │
        │  │  污染检测     │  │  Dashboard   │                       │
        │  └─────────────┘  └─────────────┘                       │
        └───────────────────────────────────────────────────────┘
```

### 数据流

```
用户请求 (/grill-me)
    │
    ▼
Middleware (拦截)
    │
    ├─► 识别任务类型 (task_type: grilling)
    │
    ├─► 查询 Skill Registry (查找匹配的 Skill)
    │
    ├─► 注入目录元数据 (YAML frontmatter + TOC)
    │
    ├─► 路由到目标 Skill (grill-me)
    │
    ▼
Skill 执行 (按需加载完整内容)
    │
    ├─► 收集可观测性数据 (trace_id, span_id, metrics)
    │
    ├─► 执行业务逻辑
    │
    ├─► 记录异常/错误（如有）
    │
    ├─► 检测幻觉和污染（异步）
    │
    ▼
返回结果
```

---

## Project Structure

```
agent_framework/
├── skills/                          # 新增：技能系统核心模块
│   ├── __init__.py
│   ├── registry.py                  # S1: Skill Registry
│   ├── middleware.py                # S1: Middleware 调度层
│   ├── loader.py                   # S1: Skill Loader
│   ├── validator.py                # S2: SKILL.md 验证器
│   ├── migrator.py                 # S2: SKILL.md 迁移工具
│   ├── lifecycle.py                # S2: 生命周期管理
│   ├── context_optimizer.py        # S3: 上下文优化器
│   ├── budget_manager.py           # S3: 预算管理器
│   └── models/
│       ├── __init__.py
│       ├── metadata.py             # 技能元数据模型
│       ├── context.py              # 技能上下文模型
│       └── result.py               # 技能结果模型
│
├── observability/                   # 新增：可观测性模块
│   ├── __init__.py
│   ├── tracing.py                  # S4: 链路追踪
│   ├── diagnostics.py              # S4: 异常诊断
│   ├── hallucination.py            # S4: 幻觉检测
│   ├── pollution.py                # S4: 污染检测
│   ├── dashboard.py                # S4: 可观测性 Dashboard
│   └── models/
│       ├── __init__.py
│       ├── trace.py                # 链路追踪数据模型
│       ├── error.py                # 错误记录模型
│       └── metrics.py              # 性能指标模型
│
├── core/                            # 现有：核心模块（不变）
├── tools/                           # 现有：工具适配器（重构）
├── workflows/                       # 现有：Workflow 定义（不变）
├── config/                          # 现有：配置管理（不变）
├── infrastructure/                  # 现有：基础设施（不变）
│
└── tests/                           # 测试代码
    ├── unit/
    │   ├── skills/                  # 技能系统单元测试
    │   └── observability/           # 可观测性单元测试
    ├── integration/
    │   ├── skill_registry/         # 集成测试
    │   └── observability/           # 集成测试
    └── e2e/
        └── skill_system/           # S5: 端到端测试

skills/                              # 现有：Skills 目录（重构）
├── write-a-skill/                   # SKILL.md 规范
├── grill-me/
│   ├── SKILL.md                    # 标准化后的主指令
│   ├── REFERENCE.md                # 详细文档（如需要）
│   └── scripts/                    # 工具脚本（如需要）
├── grill-you/
├── advance-task/
└── ...

docs/spec-feature/                   # 规范文档
├── 00-size-analysis.md             # 规模分析
├── 01-master-spec.md               # 本文件：主规范
├── 02-sub-spec-index.md           # 子规范索引
├── 03-master-plan.md              # 主实施计划
├── spec-s1-registry.md            # 子规范 S1
├── spec-s2-factory.md             # 子规范 S2
├── spec-s3-context.md             # 子规范 S3
├── spec-s4-observability.md      # 子规范 S4
└── spec-s5-integration.md         # 子规范 S5
```

---

## Code Style

### 编码规范

遵循项目现有编码风格，基于以下约定：

```python
"""agent_framework 示例代码风格"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# 使用 dataclass 定义数据模型
@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    description: str
    path: Path
    version: str = "1.0"
    category: str = "general"
    tags: list[str] = field(default_factory=list)

# 使用类型提示
def register_skill(metadata: SkillMetadata) -> None:
    """注册技能到注册表

    Args:
        metadata: 技能元数据

    Raises:
        RegistrationError: 注册失败时
    """
    pass

# 使用 Protocol 定义接口
from typing import Protocol

class Interceptor(Protocol):
    """拦截器接口"""

    def before(self, skill_name: str, context: SkillContext) -> SkillContext:
        """执行前拦截"""
        ...

    def after(self, skill_name: str, result: SkillResult) -> SkillResult:
        """执行后拦截"""
        ...
```

### 关键约定

| 约定 | 说明 |
|------|------|
| **类型提示** | 所有函数参数和返回值必须标注类型 |
| **文档字符串** | 所有公开模块、类、函数必须有 docstring |
| **命名规范** | snake_case for functions/variables, PascalCase for classes |
| **异常处理** | 使用自定义异常类，继承自 Exception |
| **日志记录** | 使用 structlog，结构化日志 |
| **测试覆盖** | 核心逻辑测试覆盖率 ≥ 80% |

---

## Testing Strategy

### 测试层级

```
┌─────────────────────────────────────────────────────────────┐
│                      E2E Tests (端到端测试)                   │
│  完整用户场景测试: /grill-me → 执行 → 验证结果                │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                  Integration Tests (集成测试)               │
│  跨模块测试: Registry + Middleware + Loader                │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                    Unit Tests (单元测试)                     │
│  单模块测试: Registry.register(), Middleware.route()        │
└─────────────────────────────────────────────────────────────┘
```

### 测试框架

| 组件 | 框架 | 说明 |
|------|------|------|
| **测试运行器** | pytest | 支持 fixtures、markers |
| **异步测试** | pytest-asyncio | 异步代码测试 |
| **覆盖率** | pytest-cov | 覆盖率报告 |
| **Mock** | pytest-mock | Mock 外部依赖 |

### 测试要求

| 层级 | 覆盖率要求 | 测试内容 |
|------|-----------|----------|
| **单元测试** | ≥ 80% | 所有核心逻辑分支 |
| **集成测试** | 关键路径 100% | 模块间交互 |
| **E2E 测试** | 主要用户场景 | 完整流程验证 |

### 测试策略

```python
# 示例：单元测试结构
class TestSkillRegistry:
    """Skill Registry 单元测试"""

    def test_register_skill_success(self):
        """测试成功注册技能"""

    def test_register_duplicate_raises_error(self):
        """测试重复注册抛出异常"""

    def test_find_by_task_type(self):
        """测试按任务类型查找技能"""

# 示例：集成测试结构
class TestRegistryMiddlewareIntegration:
    """Registry + Middleware 集成测试"""

    def test_route_to_skill_via_middleware(self):
        """测试通过 Middleware 路由到 Skill"""

    def test_interceptor_modifies_context(self):
        """测试拦截器修改上下文"""
```

---

## Commands

### 开发命令

```bash
# 安装依赖
pip install -e .

# 运行所有测试
pytest

# 运行单个模块测试
pytest agent_framework/tests/unit/skills/test_registry.py

# 运行集成测试
pytest agent_framework/tests/integration/

# 生成覆盖率报告
pytest --cov=agent_framework --cov-report=html

# 代码格式化
ruff format agent_framework/

# 类型检查
mypy agent_framework/
```

### 技能系统相关命令

```bash
# 验证 SKILL.md 规范
python -m agent_framework.skills.validator validate skills/grill-me/SKILL.md

# 迁移 SKILL.md 到新规范
python -m agent_framework.skills.migrator migrate skills/grill-me/SKILL.md

# 列出所有注册的技能
python -m agent_framework.skills.registry list

# 查看可观测性 Dashboard
python -m agent_framework.observability.dashboard
```

---

## Boundaries

### Always Do（必须做）

- ✅ 所有新代码必须有类型提示
- ✅ 所有公开 API 必须有 docstring
- ✅ 核心逻辑必须有单元测试（覆盖率 ≥ 80%）
- ✅ 使用 structlog 记录关键操作
- ✅ 使用自定义异常类处理错误
- ✅ 遵循 SKILL.md 标准规范

### Ask First（先询问）

- 🤔 修改现有 Workflow 结构 (F1-F4)
- 🤔 修改现有核心模块 (agent_framework/core/)
- 🤔 添加新的外部依赖
- 🤔 修改 CI/CD 配置
- 🤔 修改测试框架配置

### Never Do（禁止做）

- ❌ 修改现有 Skills 的业务逻辑
- ❌ 硬编码 Skill 类名或路径
- ❌ 提交敏感信息（API key、密码）
- ❌ 修改 vendor/ 第三方代码
- ❌ 移除或禁用失败的测试而不修复

---

## Success Criteria

### 功能验证

- [ ] Skill Registry 可自动发现并注册所有 Skills
- [ ] Middleware 可正确路由 Skill 调用
- [ ] 上下文优化后 Token 消耗降低 ≥ 30%
- [ ] 可观测性数据完整收集链路追踪
- [ ] SKILL.md 验证工具可检测不符合规范的文件
- [ ] 迁移工具可自动修复常见问题

### 质量指标

- [ ] 测试覆盖率 ≥ 80%
- [ ] 所有 SKILL.md 符合 write-a-skill 规范
- [ ] 可观测性覆盖 P0/P1 异常类型
- [ ] 幻觉检测准确率 ≥ 70%
- [ ] 污染检测可捕获未授权写入
- [ ] 代码通过 mypy 类型检查
- [ ] 代码通过 ruff 格式检查

### 性能目标

| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| **Skill 加载时间** | N/A | < 100ms | 单元测试 |
| **初始 Token 消耗** | ~10,000 | ~1,000 | 集成测试 |
| **峰值 Token 消耗** | ~10,000 | ~3,000 | 集成测试 |
| **链路追踪开销** | 0 | < 5% | 性能测试 |
| **注册表发现时间** | N/A | < 500ms | 单元测试 |

### 用户体验

- [ ] /skill-name 命令响应流畅
- [ ] 错误信息清晰友好
- [ ] 可观测性 Dashboard 可读性强
- [ ] SKILL.md 迁移过程平滑

---

## Sub-Spec Directory

本主规范拆分为以下子规范：

| ID | 子规范名称 | 估算 LOC | 文件 |
|----|-----------|----------|------|
| **S1** | 技能注册表与中间件调度层 | ~1,450 | [spec-s1-registry.md](spec-s1-registry.md) |
| **S2** | 标准化技能工厂与生命周期 | ~1,250 | [spec-s2-factory.md](spec-s2-factory.md) |
| **S3** | 上下文优化策略 | ~600 | [spec-s3-context.md](spec-s3-context.md) |
| **S4** | Agent 可观测性建设 | ~1,350 | [spec-s4-observability.md](spec-s4-observability.md) |
| **S5** | 集成测试与文档 | ~900 | [spec-s5-integration.md](spec-s5-integration.md) |

**子规范总估算 LOC: ~7,550 LOC**

---

## Related Documents

- [00-size-analysis.md](00-size-analysis.md) - 规模分析
- [02-sub-spec-index.md](02-sub-spec-index.md) - 子规范索引（待生成）
- [03-master-plan.md](03-master-plan.md) - 主实施计划（待生成）
- [docs/spec-feature/requirements/](requirements/) - 需求文档
- [CONTEXT.md](../../CONTEXT.md) - 术语定义
- [skills/write-a-skill/SKILL.md](../../skills/write-a-skill/SKILL.md) - SKILL.md 规范

---

## Version History

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| 1.0 | 2026-06-29 | 初始版本 | Claude |

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 审查主规范后，进入 Phase 2: 拆分子规范
