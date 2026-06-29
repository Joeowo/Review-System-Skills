# 需求 1：技能注册表与中间件调度层

**版本**: 1.0
**日期**: 2026-06-29
**状态**: 草案

---

## 需求概述

实现业务技能与模型逻辑的解耦，通过构建统一的 Skill Registry 与 Middleware 调度层，支持动态按需注入和多技能并行兼容。

---

## 功能需求

### FR-1.1：Skill Registry（技能注册表）

**描述**：自动发现、注册和管理所有可用 Skills。

**功能规格**：

| 子需求 | 规格 |
|--------|------|
| **发现机制** | 扫描 `skills/` 目录，解析 SKILL.md frontmatter |
| **注册格式** | 提取 `name` 和 `description` 字段 |
| **生命周期** | 按需加载，延迟初始化 |
| **查询接口** | 支持按 name、category、tags 查询 |

**接口定义**：

```python
class SkillRegistry:
    """技能注册表"""

    @staticmethod
    def discover(skills_dir: Path) -> Dict[str, SkillMetadata]:
        """扫描 skills/ 目录，解析 SKILL.md frontmatter
        Args:
            skills_dir: Skills 目录路径
        Returns:
            {skill_name: SkillMetadata} 字典
        """

    def register(self, metadata: SkillMetadata) -> None:
        """注册技能到注册表"""

    def get(self, name: str) -> Optional[SkillMetadata]:
        """按 name 查询技能"""

    def find_by_task(self, task_type: str) -> List[SkillMetadata]:
        """根据任务类型查找相关技能"""

    def list_all(self) -> List[SkillMetadata]:
        """列出所有已注册技能"""
```

**数据结构**：

```python
@dataclass
class SkillMetadata:
    """技能元数据"""
    name: str              # 来自 SKILL.md frontmatter
    description: str       # 来自 SKILL.md frontmatter
    path: Path             # SKILL.md 文件路径
    version: str = "1.0"
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
```

---

### FR-1.2：Middleware 调度层

**描述**：位于技能执行流程中的中间件层，负责数据流拦截和路由。

**功能规格**：

| 子需求 | 规格 |
|--------|------|
| **请求拦截** | 在技能执行前/后拦截数据流 |
| **上下文管理** | 注入、转换、过滤上下文信息 |
| **技能路由** | 根据请求内容调度合适的 skill/tool |

**接口定义**：

```python
class SkillMiddleware:
    """技能调度中间件"""

    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.interceptors: List[Interceptor] = []

    def add_interceptor(self, interceptor: Interceptor) -> None:
        """添加拦截器"""

    def route(self, state: AgentState) -> Optional[str]:
        """根据状态路由到对应的 Skill
        Args:
            state: 当前 Agent 状态
        Returns:
            Skill name 或 None
        """

    def execute_skill(
        self,
        skill_name: str,
        context: SkillContext
    ) -> SkillResult:
        """执行指定 Skill，应用拦截器"""

class Interceptor(Protocol):
    """拦截器接口"""
    def before(self, skill_name: str, context: SkillContext) -> SkillContext:
        """执行前拦截"""

    def after(self, skill_name: str, result: SkillResult) -> SkillResult:
        """执行后拦截"""
```

---

### FR-1.3：动态选择机制

**描述**：运行时根据任务需求动态选择和加载不同的 Skills。

**功能规格**：

| 触发条件 | 行为 |
|----------|------|
| **基于任务类型** | `state["task_type"] == "grilling"` → 加载 grill-me |
| **基于用户查询** | 用户输入包含 `/grill-me` → 加载 grill-me |
| **基于 LLM 工具调用** | LLM 决定调用 Skill 工具时 → 按需加载 |

**接口定义**：

```python
class SkillLoader:
    """技能加载器"""

    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.loaded: Dict[str, Skill] = {}

    def load_skill(self, skill_name: str) -> Skill:
        """按需加载 Skill 模块
        Args:
            skill_name: 技能名称
        Returns:
            Skill 实例
        Raises:
            SkillNotFoundError: 技能不存在
        """

    def unload_skill(self, skill_name: str) -> None:
        """卸载不再需要的 Skill"""

    def reload_skill(self, skill_name: str) -> Skill:
        """热重载（开发时）"""
```

---

### FR-1.4：多技能并行兼容

**描述**：支持多个 Skills 同时处于可用状态并可并行执行。

**功能规格**：

| 子需求 | 规格 |
|--------|------|
| **状态隔离** | 技能之间的上下文互不污染 |
| **并行执行** | 支持多个 Skills 同时调用 |
| **路由调度** | Middleware 根据请求分发到对应技能 |

**接口定义**：

```python
class ParallelSkillExecutor:
    """并行技能执行器"""

    async def execute_parallel(
        self,
        skill_names: List[str],
        contexts: List[SkillContext]
    ) -> List[SkillResult]:
        """并行执行多个 Skills
        Args:
            skill_names: 技能名称列表
            contexts: 对应的上下文列表
        Returns:
            执行结果列表
        """

    def validate_isolation(
        self,
        results: List[SkillResult]
    ) -> IsolationReport:
        """验证技能状态隔离"""
```

---

## 非功能需求

### NFR-1.1：性能

- **发现时间**：< 500ms（扫描 100 个 Skills）
- **查询时间**：< 10ms（按 name 查询）
- **路由延迟**：< 50ms（包含拦截器）

### NFR-1.2：可扩展性

- 支持通过插件机制扩展拦截器
- 支持自定义 Skill 来源（文件系统、数据库、远程）

### NFR-1.3：可靠性

- Skill 加载失败不应影响 Registry 的其他功能
- 提供降级机制：Skill 不可用时返回友好错误

---

## 数据模型

### SkillMetadata

```python
@dataclass
class SkillMetadata:
    """技能元数据（来自 SKILL.md frontmatter）"""
    name: str                    # 技能名称
    description: str             # 技能描述（< 1024 字符）
    path: Path                   # SKILL.md 文件路径

    # 可选字段
    version: str = "1.0"
    category: str = "general"     # interaction | state-update | analysis
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    # 运行时字段
    loaded: bool = False
    load_time: Optional[float] = None
```

### SkillContext

```python
@dataclass
class SkillContext:
    """技能执行上下文"""
    session_path: str           # 会话目录路径
    state: Dict[str, Any]        # 当前状态
    metadata: Dict[str, Any]     # 额外元数据
```

### SkillResult

```python
@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
```

---

## 架构决策

### AD-1.1：注册来源

**决策**：扫描 SKILL.md 文件

**理由**：
- 现有 Skills 已有 SKILL.md 格式
- YAML frontmatter 包含足够元数据
- 符合 Progressive Disclosure 原则

### AD-1.2：Middleware 职责

**决策**：组合职责（请求拦截 + 上下文管理 + 技能路由）

**理由**：
- 三者紧密关联，分离会增加复杂度
- 便于统一管理和调试

### AD-1.3：解耦实现方式

**决策**：三层分离

1. **架构层**：Registry/Provider 模式
2. **接口层**：抽象契约（**kwargs）
3. **内容层**：SKILL.md 与执行逻辑分离

---

## 验收标准

- [ ] SkillRegistry 可自动发现 skills/ 目录下所有 SKILL.md
- [ ] 可按 name、category 查询 Skills
- [ ] Middleware 可正确路由到目标 Skill
- [ ] 支持并行执行多个 Skills 且状态隔离
- [ ] 拦截器可在执行前后修改上下文

---

## 相关文档

- [02-skill-factory.md](02-skill-factory.md) - 标准化技能工厂
- [03-context-optimization.md](03-context-optimization.md) - 上下文优化策略
- [skills/write-a-skill/SKILL.md](../../skills/write-a-skill/SKILL.md) - SKILL.md 规范

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
