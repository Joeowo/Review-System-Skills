# Sub-Spec: S2 - 标准化技能工厂与生命周期

**父规范**: [01-master-spec.md](01-master-spec.md)
**估算 LOC**: ~1,250
**依赖**: S1 (技能注册表与中间件调度层)
**优先级**: P0

---

## Objective

设计并实现 Agent 技能标准化工厂与生命周期管理模块，通过标准化 SKILL.md 指令集与脚本资源，将通用能力复用率提升。提供验证和迁移工具，确保所有 Skills 符合 write-a-skill 规范。

---

## Interfaces

### Consumes（消费）

- **S1 SkillRegistry**: 查询已注册的技能
- **文件系统**: 读取和验证 SKILL.md 文件
- **YAML 解析器**: 解析和验证 frontmatter

### Produces（产出）

- **SkillValidator API**: 验证 SKILL.md 规范
- **SkillMigrator API**: 迁移不符合规范的 SKILL.md
- **SkillLifecycle API**: 管理技能生命周期
- **标准化指令集**: LLM 指令和 TOOLS 接口规范

### External Dependencies（外部依赖）

- `pathlib.Path` - 文件路径操作
- `yaml` - YAML 解析和验证
- `pydantic` - 数据验证
- `difflib` - 迁移差异计算

---

## Component Structure

```
agent_framework/skills/
├── validator.py              # SKILL.md 验证器 (~200 LOC)
├── migrator.py               # SKILL.md 迁移工具 (~300 LOC)
├── lifecycle.py              # 生命周期管理 (~350 LOC)
└── standards/
    ├── __init__.py
    ├── instructions.py       # 标准化指令集 (~150 LOC)
    └── tools.py             # 标准化工具接口 (~150 LOC)

Tests:
agent_framework/tests/unit/skills/
├── test_validator.py
├── test_migrator.py
├── test_lifecycle.py
└── test_standards.py

Integration Tests:
agent_framework/tests/integration/skills/
└── test_factory_integration.py
```

---

## Commands

```bash
# 验证 SKILL.md 规范
python -m agent_framework.skills.validator validate skills/grill-me/SKILL.md

# 迁移 SKILL.md 到新规范
python -m agent_framework.skills.migrator migrate skills/grill-me/SKILL.md

# 检查技能健康状态
python -m agent_framework.skills.lifecycle health grill-me

# 查看技能统计
python -m agent_framework.skills.lifecycle stats grill-me
```

---

## Code Style

遵循主规范编码风格，示例：

```python
"""agent_framework/skills 标准化示例代码风格"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: list[str]
    warnings: list[str]

class SkillValidator:
    """SKILL.md 规范验证器"""

    def validate(self, skill_path: Path) -> ValidationResult:
        """验证 SKILL.md 是否符合规范

        检查项:
        - YAML frontmatter 完整性
        - description 字段格式
        - 文件行数 < 100
        - 必需章节存在（Quick start, Workflows）
        """
        errors = []
        warnings = []

        if not skill_path.exists():
            return ValidationResult(
                valid=False,
                errors=[f"SKILL.md not found at {skill_path}"],
                warnings=warnings
            )

        # 解析 frontmatter
        content = skill_path.read_text()
        metadata = self._parse_frontmatter(content)

        # 验证必需字段
        if not metadata.get("name"):
            errors.append("Missing required field: name")
        if not metadata.get("description"):
            errors.append("Missing required field: description")

        # 验证行数
        lines = content.split("\n")
        if len(lines) > 100:
            warnings.append(f"SKILL.md exceeds 100 lines ({len(lines)} lines)")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

---

## Testing Strategy

### 单元测试

| 组件 | 测试内容 | 覆盖率目标 |
|------|----------|-----------|
| **SkillValidator** | 规范验证、错误检测 | ≥ 80% |
| **SkillMigrator** | 迁移逻辑、差异计算 | ≥ 80% |
| **SkillLifecycle** | 加载、卸载、健康检查 | ≥ 80% |
| **Standards** | 指令集、工具接口 | ≥ 80% |

### 集成测试

- 验证 + 迁移集成
- 生命周期 + Registry 集成
- 端到端标准化流程

### 测试示例

```python
class TestSkillValidator:
    """SKILL.md 验证器单元测试"""

    def test_valid_skill_passes_validation(self):
        """测试有效的 SKILL.md 通过验证"""
        validator = SkillValidator()
        result = validator.validate(Path("skills/write-a-skill/SKILL.md"))
        assert result.valid
        assert len(result.errors) == 0

    def test_missing_name_field_fails(self):
        """测试缺少 name 字段失败"""
        validator = SkillValidator()
        invalid_content = "---\ndescription: Test\n---\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md") as f:
            f.write(invalid_content)
            f.flush()
            result = validator.validate(Path(f.name))
        assert not result.valid
        assert "Missing required field: name" in result.errors
```

---

## Boundaries

### Always Do（必须做）

- ✅ 验证所有 SKILL.md 符合规范
- ✅ 提供清晰的迁移指导
- ✅ 记录生命周期关键事件
- ✅ 支持热重载（开发时）

### Ask First（先询问）

- 🤔 修改 write-a-skill 规范
- 🤔 强制迁移（破坏性变更）
- 🤔 修改现有 Skills 目录结构

### Never Do（禁止做）

- ❌ 自动修改 SKILL.md 而不备份
- ❌ 删除现有 Skills 的业务逻辑
- ❌ 强制迁移而不提供回退机制

---

## Success Criteria

### 功能验证

- [ ] 所有现有 SKILL.md 符合 write-a-skill 规范
- [ ] 验证工具可检测不符合规范的 SKILL.md
- [ ] 迁移工具可自动修复常见问题
- [ ] 生命周期管理可正确加载/卸载 Skills
- [ ] 监控数据准确反映 Skill 使用情况

### 质量指标

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] 所有 SKILL.md 通过验证
- [ ] 迁移成功率 ≥ 90%
- [ ] 生命周期操作无内存泄漏

### 迁移目标

| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| **SKILL.md 规范符合率** | ~60% | 100% | 验证工具统计 |
| **描述字段标准化** | ~50% | 100% | 验证工具统计 |
| **迁移成功率** | N/A | ≥ 90% | 迁移日志统计 |

---

## Open Questions

1. **强制迁移策略**: 是否需要强制所有 Skills 迁移？（当前假设渐进式）
2. **版本兼容**: 如何处理不同版本的 SKILL.md 规范？（当前假设向后兼容）
3. **迁移回退**: 迁移失败时如何回退？（当前假设备份原文件）

---

## Related Documents

- [01-master-spec.md](01-master-spec.md) - 主规范
- [02-sub-spec-index.md](02-sub-spec-index.md) - 子规范索引
- [spec-s1-registry.md](spec-s1-registry.md) - 依赖的 S1 规范
- [docs/spec-feature/requirements/02-skill-factory.md](requirements/02-skill-factory.md) - 对应需求文档
- [skills/write-a-skill/SKILL.md](../../skills/write-a-skill/SKILL.md) - SKILL.md 规范

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 进入实施阶段，编写详细任务
