# S1: 技能注册表与中间件调度层

## 概述

S1 模块实现了技能系统的基础设施层，提供技能发现、注册、路由和执行功能。

## 核心组件

### 1. SkillRegistry (`registry.py`)

技能注册表，负责发现和管理所有技能。

```python
from agent_framework.skills.registry import SkillRegistry
from pathlib import Path

registry = SkillRegistry(Path("skills/"))
registry.discover()

# 查询技能
skill = registry.get("grill-me")
learning_skills = registry.find_by_category("learning")
all_skills = registry.list_all()
```

### 2. SkillLoader (`loader.py`)

技能加载器，支持按需加载和缓存。

```python
from agent_framework.skills.loader import SkillLoader

loader = SkillLoader(registry)

# 加载技能
content = loader.load_skill("grill-me")

# 检查加载状态
if loader.is_loaded("grill-me"):
    print("Skill is loaded")

# 卸载技能
loader.unload_skill("grill-me")
```

### 3. SkillMiddleware (`middleware.py`)

技能中间件，提供路由和执行功能。

```python
from agent_framework.skills.middleware import SkillMiddleware, LoggingInterceptor

middleware = SkillMiddleware(registry)

# 添加拦截器
middleware.add_interceptor(LoggingInterceptor())

# 路由到技能
state = {"task_type": "grilling"}
skill_name = middleware.route(state)

# 执行技能
from agent_framework.skills.models.context import SkillContext
context = SkillContext(session_path=Path("."), state=state)
result = middleware.execute_skill(skill_name, context, loader)
```

### 4. ParallelSkillExecutor (`executor.py`)

并行执行器，支持多个技能同时执行。

```python
from agent_framework.skills.executor import ParallelSkillExecutor

executor = ParallelSkillExecutor(middleware, max_workers=4)

# 并行执行多个技能
results = executor.execute_parallel(
    ["skill-1", "skill-2", "skill-3"],
    [context1, context2, context3],
    loader
)
```

## 数据模型

### SkillMetadata

技能元数据，从 SKILL.md 的 frontmatter 解析：

```python
@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str
    path: Path
    version: str = "1.0"
    category: str = "general"
    tags: list[str] = field(default_factory=list)
```

### SkillContext

技能执行上下文：

```python
@dataclass(frozen=True)
class SkillContext:
    session_path: Path
    state: Dict[str, Any] = field(default_factory=dict)
```

### SkillResult

技能执行结果：

```python
@dataclass(frozen=True)
class SkillResult:
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## 路由规则

Middleware 按以下优先级路由：

1. 自定义路由映射
2. task_type 默认映射 (`grilling` → `grill-me`)
3. user_query 关键词匹配
4. 默认路由回退

### 默认路由映射

| task_type | skill_name |
|-----------|------------|
| `grilling` | `grill-me` |
| `qa` | `grill-you` |
| `advance` | `advance-task` |
| `continue` | `continue-task` |
| `review` | `review-session` |

### 关键词映射

| 关键词 | skill_name |
|--------|------------|
| `grill` | `grill-me` |
| `advance` | `advance-task` |
| `continue` | `continue-task` |
| `review` | `review-session` |
| `help` | `review-system` |

## 拦截器

拦截器允许在技能执行前后插入自定义逻辑。

### Interceptor 接口

```python
from agent_framework.skills.middleware import Interceptor

class CustomInterceptor:
    def before(self, skill_name: str, context: SkillContext) -> SkillContext:
        # 执行前处理
        return context

    def after(self, skill_name: str, result: SkillResult) -> SkillResult:
        # 执行后处理
        return result
```

### 内置拦截器

- **LoggingInterceptor**: 记录技能执行日志

### StopExecution

拦截器可以抛出 `StopExecution` 异常来阻止技能执行：

```python
from agent_framework.skills.middleware import StopExecution

class BlockingInterceptor:
    def before(self, skill_name: str, context: SkillContext) -> SkillContext:
        if some_condition:
            raise StopExecution("Blocked by policy")
        return context
```

## 异常类

- `DuplicateSkillError`: 重复注册技能
- `SkillNotFoundError`: 技能不存在
- `RouteNotFoundError`: 路由未找到
- `SkillLoadError`: 技能加载失败
- `StopExecution`: 拦截器停止执行

## 测试覆盖

- 单元测试: 76 个测试
- 集成测试: 9 个测试
- 总计: 85 个测试全部通过
- 代码覆盖率: ~80% (skills 模块)

运行测试：

```bash
pytest agent_framework/tests/unit/skills/
pytest agent_framework/tests/integration/skill_registry/
```

## 性能指标

| 指标 | 目标 |
|------|------|
| 发现时间 (100 个 Skills) | < 500ms |
| 查询时间 (按 name) | < 10ms |
| 路由延迟 | < 50ms |

## 使用示例

### 完整工作流

```python
from pathlib import Path
from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.skills.models.context import SkillContext

# 1. 初始化组件
skills_dir = Path("skills/")
registry = SkillRegistry(skills_dir)
registry.discover()

loader = SkillLoader(registry)
middleware = SkillMiddleware(registry)

# 2. 路由到技能
state = {"task_type": "grilling", "user_query": "Help me plan"}
skill_name = middleware.route(state)

# 3. 创建上下文
context = SkillContext(
    session_path=Path("./session"),
    state=state
)

# 4. 执行技能
result = middleware.execute_skill(skill_name, context, loader)

if result.success:
    print(result.output)
else:
    print(f"Error: {result.error}")
```

## 下一步

- S2: 标准化技能工厂与生命周期
- S3: 上下文优化策略
- S4: Agent 可观测性建设
