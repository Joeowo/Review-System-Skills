# Sub-Spec: S1 - 技能注册表与中间件调度层

**父规范**: [01-master-spec.md](01-master-spec.md)
**估算 LOC**: ~1,450
**依赖**: 无
**优先级**: P0

---

## Objective

构建技能系统的基础设施层，实现业务技能与模型逻辑的解耦。通过 Skill Registry 自动发现和注册技能，通过 Middleware 调度层实现请求拦截、上下文管理和技能路由。

---

## Interfaces

### Consumes（消费）

- **文件系统**: 读取 `skills/` 目录下的 SKILL.md 文件
- **YAML 解析器**: 解析 SKILL.md frontmatter
- **现有 agent_framework**: 复用 core/state.py 等模块

### Produces（产出）

- **SkillRegistry API**: 查询、注册、管理技能的接口
- **Middleware API**: 拦截、路由、执行技能的接口
- **SkillLoader API**: 按需加载技能的接口

### External Dependencies（外部依赖）

- `pathlib.Path` - 文件路径操作
- `yaml` - YAML 解析
- `pydantic` - 数据验证
- `structlog` - 日志记录

---

## Component Structure

```
agent_framework/skills/
├── __init__.py
├── registry.py              # Skill Registry 实现 (~400 LOC)
├── middleware.py            # Middleware 调度层 (~500 LOC)
├── loader.py               # Skill Loader (~300 LOC)
├── executor.py             # 并行执行器 (~250 LOC)
└── models/
    ├── __init__.py
    ├── metadata.py         # SkillMetadata 数据模型 (~100 LOC)
    ├── context.py          # SkillContext 数据模型 (~50 LOC)
    └── result.py           # SkillResult 数据模型 (~50 LOC)

Tests:
agent_framework/tests/unit/skills/
├── test_registry.py
├── test_middleware.py
├── test_loader.py
└── test_executor.py
```

---

## Commands

```bash
# 开发
pip install -e .

# 测试
pytest agent_framework/tests/unit/skills/
pytest agent_framework/tests/integration/skill_registry/

# 运行
python -m agent_framework.skills.registry list
```

---

## Code Style

遵循主规范编码风格，示例：

```python
"""agent_framework/skills 示例代码风格"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str
    description: str
    path: Path
    version: str = "1.0"
    category: str = "general"
    tags: list[str] = field(default_factory=list)

class SkillRegistry:
    """技能注册表"""

    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir
        self._skills: dict[str, SkillMetadata] = {}
        logger.info("SkillRegistry initialized", skills_dir=str(skills_dir))

    def register(self, metadata: SkillMetadata) -> None:
        """注册技能到注册表"""
        if metadata.name in self._skills:
            raise DuplicateSkillError(f"Skill {metadata.name} already registered")
        self._skills[metadata.name] = metadata
        logger.info("Skill registered", name=metadata.name)
```

---

## Testing Strategy

### 单元测试

| 组件 | 测试内容 | 覆盖率目标 |
|------|----------|-----------|
| **SkillRegistry** | 注册、查询、发现技能 | ≥ 80% |
| **Middleware** | 路由、拦截、上下文管理 | ≥ 80% |
| **SkillLoader** | 加载、卸载、重载 | ≥ 80% |
| **ParallelExecutor** | 并行执行、状态隔离 | ≥ 80% |

### 集成测试

- Registry + Middleware 集成
- Middleware + Loader 集成
- 端到端路由测试

### 测试示例

```python
class TestSkillRegistry:
    """Skill Registry 单元测试"""

    def test_register_skill_success(self):
        """测试成功注册技能"""
        metadata = SkillMetadata(
            name="test-skill",
            description="Test skill",
            path=Path("/tmp/test/SKILL.md")
        )
        registry = SkillRegistry(Path("/tmp/skills"))
        registry.register(metadata)
        assert registry.get("test-skill") == metadata

    def test_register_duplicate_raises_error(self):
        """测试重复注册抛出异常"""
        metadata = SkillMetadata(
            name="test-skill",
            description="Test skill",
            path=Path("/tmp/test/SKILL.md")
        )
        registry = SkillRegistry(Path("/tmp/skills"))
        registry.register(metadata)
        with pytest.raises(DuplicateSkillError):
            registry.register(metadata)
```

---

## Boundaries

### Always Do（必须做）

- ✅ 所有 API 必须有类型提示
- ✅ 所有操作必须记录日志
- ✅ 使用自定义异常处理错误
- ✅ 所有公开 API 必须有单元测试

### Ask First（先询问）

- 🤔 修改现有 core/state.py 结构
- 🤔 添加新的外部依赖
- 🤔 修改数据模型定义

### Never Do（禁止做）

- ❌ 硬编码 Skill 类名或路径
- ❌ 直接修改 SKILL.md 文件内容
- ❌ 绕过 Registry 直接访问 Skills

---

## Success Criteria

### 功能验证

- [ ] SkillRegistry 可自动发现 skills/ 目录下所有 SKILL.md
- [ ] 可按 name、category 查询 Skills
- [ ] Middleware 可正确路由到目标 Skill
- [ ] 支持并行执行多个 Skills 且状态隔离
- [ ] 拦截器可在执行前后修改上下文

### 质量指标

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 所有 API 通过 mypy 类型检查
- [ ] 集成测试通过
- [ ] 日志完整记录关键操作

### 性能目标

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| **发现时间** | < 500ms (100 个 Skills) | 单元测试 |
| **查询时间** | < 10ms (按 name 查询) | 单元测试 |
| **路由延迟** | < 50ms (包含拦截器) | 单元测试 |

---

## Open Questions

1. **Skills 目录结构**: 是否支持嵌套子目录？（当前假设扁平结构）
2. **SKILL.md 缺失**: 如何处理没有 SKILL.md 的目录？（当前假设跳过）
3. **热重载策略**: 开发时是否支持自动重载？（当前假设手动重载）

---

## Related Documents

- [01-master-spec.md](01-master-spec.md) - 主规范
- [02-sub-spec-index.md](02-sub-spec-index.md) - 子规范索引
- [docs/spec-feature/requirements/01-skill-registry-middleware.md](requirements/01-skill-registry-middleware.md) - 对应需求文档

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 进入实施阶段，编写详细任务
