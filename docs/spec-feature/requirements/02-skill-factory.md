# 需求 2：标准化技能工厂

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## 需求概述

设计并实现 Agent 技能注册表（Skill Registry）与生命周期管理模块，通过标准化 SKILL.md 指令集与脚本资源，将通用能力复用率提升。

---

## 功能需求

### FR-2.1：SKILL.md 标准化

**描述**：遵循 `write-a-skill` 规范，确保所有 SKILL.md 格式一致。

**标准结构**：

```
skill-name/
├── SKILL.md           # 主指令（必需，<100 行）
├── REFERENCE.md       # 详细文档（如需要）
├── EXAMPLES.md        # 使用示例（如需要）
└── scripts/           # 工具脚本（如需要）
    └── helper.py
```

**SKILL.md 模板**：

```markdown
---
name: skill-name
description: 能力简述。Use when [具体触发条件]。
---

# Skill Name

## Quick start
[最小工作示例]

## Workflows
[带检查清单的详细流程]

## Advanced features
See [REFERENCE.md](REFERENCE.md) for details
```

**描述字段规范**：

| 属性 | 规格 |
|------|------|
| **长度** | 最大 1024 字符 |
| **人称** | 第三人称 |
| **结构** | 第一句：能力描述；第二句："Use when [具体触发条件]" |
| **目的** | 让 Agent 能据此选择正确的 Skill |

**拆分原则**：

- SKILL.md 超过 100 行时拆分到 REFERENCE.md
- 操作具有确定性时使用 scripts/（验证、格式化）
- 避免重复生成代码时使用 scripts/
- 需要显式错误处理时使用 scripts/

---

### FR-2.2：标准化指令集

**描述**：统一 LLM 指令格式和 TOOLS 调用接口。

#### 2.2.1 LLM 指令格式标准化

**标准格式**：

```markdown
## Instructions for Claude
When this skill is invoked:
1. Always read CONTEXT.md first
2. Use <thinking> to plan before execution
3. Update CONTEXT.md using the format in CONTEXT-FORMAT.md
```

**指令组件**：

| 组件 | 说明 |
|------|------|
| {{context_reader}} | 标准化的上下文读取组件 |
| {{state_updater}} | 标准化的状态更新组件 |
| {{terminology_manager}} | 标准化的术语管理组件 |

#### 2.2.2 TOOLS 调用接口标准化

**标准接口**：

```python
from agent_framework.tools import Tool

@tool
def skill_tool(input: str) -> str:
    """标准化的 skill 工具接口"""
    pass
```

**工具分类**：

| 类型 | 说明 | 示例 |
|------|------|------|
| **读取工具** | 读取文件或状态 | read_context, read_task |
| **写入工具** | 更新文件或状态 | update_context, save_progress |
| **验证工具** | 验证输入或状态 | validate_input, check_completeness |

---

### FR-2.3：技能生命周期管理

**描述**：管理 Skills 的注册、加载、卸载和监控。

**管理范围**：

#### 2.3.1 注册与发现

```python
class SkillLifecycle:
    def discover(self, skills_dir: Path) -> List[SkillMetadata]:
        """扫描 SKILL.md，解析 frontmatter"""

    def register(self, metadata: SkillMetadata) -> None:
        """注册到 Registry"""

    def unregister(self, skill_name: str) -> None:
        """注销技能"""
```

#### 2.3.2 加载与卸载

```python
class SkillLifecycle:
    def load(self, skill_name: str) -> Skill:
        """按需加载 Skill 模块"""

    def unload(self, skill_name: str) -> None:
        """卸载释放内存"""

    def reload(self, skill_name: str) -> Skill:
        """热重载（开发时）"""
```

#### 2.3.3 监控与诊断

```python
class SkillLifecycle:
    def get_stats(self, skill_name: str) -> SkillStats:
        """获取使用统计"""

    def get_health(self, skill_name: str) -> HealthStatus:
        """健康检查"""

@dataclass
class SkillStats:
    load_time: float
    execution_count: int
    avg_execution_time: float
    error_count: int

@dataclass
class HealthStatus:
    healthy: bool
    last_check: str
    issues: List[str]
```

---

## 非功能需求

### NFR-2.1：可维护性

- SKILL.md 符合标准后应通过验证检查
- 提供迁移工具辅助不符合规范的 Skills

### NFR-2.2：可扩展性

- 支持自定义指令组件
- 支持自定义工具接口

### NFR-2.3：性能

- 生命周期操作开销 < 5%
- 监控数据收集不影响 Skill 执行

---

## 验证机制

### SKILL.md 验证

```python
class SkillValidator:
    """SKILL.md 规范验证器"""

    def validate(self, skill_path: Path) -> ValidationResult:
        """验证 SKILL.md 是否符合规范
        检查项：
        - YAML frontmatter 完整性
        - description 字段格式
        - 文件行数 < 100
        - 必需章节存在（Quick start, Workflows）
        """

 ValidationResult = {
    "valid": bool,
    "errors": List[str],
    "warnings": List[str]
}
```

### 迁移工具

```python
class SkillMigrator:
    """SKILL.md 迁移工具"""

    def migrate(self, skill_path: Path) -> MigrationReport:
        """迁移不符合规范的 SKILL.md
        操作：
        - 拆分超长内容到 REFERENCE.md
        - 标准化 description 格式
        - 添加缺失的必需章节
        """
```

---

## 数据模型

### SkillSpec

```python
@dataclass
class SkillSpec:
    """技能规范（来自 SKILL.md）"""
    # Frontmatter
    name: str
    description: str
    version: str = "1.0"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    # Content structure
    has_quick_start: bool = False
    has_workflows: bool = False
    has_advanced_features: bool = False

    # File references
    reference_exists: bool = False
    examples_exists: bool = False
    scripts_count: int = 0
```

---

## 验收标准

- [ ] 所有现有 SKILL.md 符合 write-a-skill 规范
- [ ] 验证工具可检测不符合规范的 SKILL.md
- [ ] 迁移工具可自动修复常见问题
- [ ] 生命周期管理可正确加载/卸载 Skills
- [ ] 监控数据准确反映 Skill 使用情况

---

## 相关文档

- [01-skill-registry-middleware.md](01-skill-registry-middleware.md) - 技能注册表与中间件
- [skills/write-a-skill/SKILL.md](../../skills/write-a-skill/SKILL.md) - SKILL.md 规范
- [CONTEXT.md](../../CONTEXT.md) - 术语定义

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
