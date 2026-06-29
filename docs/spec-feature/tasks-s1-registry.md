# Tasks: Sub-Spec S1 - 技能注册表与中间件调度层

**父规范**: [spec-s1-registry.md](spec-s1-registry.md)
**估算总 LOC**: ~1,450
**总任务数**: 8
**关键路径**: S1-T1 → S1-T2 → S1-T3 → S1-T4 → S1-T5 → S1-T6 → S1-T7 → S1-T8

---

## Task Breakdown

### Task 1: 数据模型定义 (~150 LOC)

**描述**: 定义技能系统的核心数据模型，包括 SkillMetadata、SkillContext、SkillResult 等。

**验收标准**:
- [ ] 所有数据模型使用 @dataclass 定义
- [ ] 所有字段有类型提示
- [ ] 所有模型有 docstring
- [ ] 通过 mypy 类型检查

**验证方式**:
```python
# 测试数据模型实例化
metadata = SkillMetadata(
    name="test-skill",
    description="Test skill",
    path=Path("/tmp/test.md")
)
assert metadata.name == "test-skill"
```

**涉及文件**:
- `agent_framework/skills/models/__init__.py`
- `agent_framework/skills/models/metadata.py`
- `agent_framework/skills/models/context.py`
- `agent_framework/skills/models/result.py`

**依赖**: 无

**估算时间**: 2-3 小时

---

### Task 2: Skill Registry 核心功能 (~250 LOC)

**描述**: 实现 Skill Registry 的核心功能，包括发现、注册、查询技能。

**验收标准**:
- [ ] 可扫描 skills/ 目录发现所有 SKILL.md
- [ ] 可解析 SKILL.md 的 YAML frontmatter
- [ ] 可按 name 查询技能
- [ ] 可按 category 查询技能
- [ ] 可列出所有已注册技能

**验证方式**:
```python
# 测试 Registry 功能
registry = SkillRegistry(Path("skills/"))
registry.discover()
skill = registry.get("grill-me")
assert skill is not None
assert skill.name == "grill-me"
```

**涉及文件**:
- `agent_framework/skills/registry.py`
- `agent_framework/tests/unit/skills/test_registry.py`

**依赖**: Task 1 (数据模型)

**估算时间**: 4-5 小时

---

### Task 3: Skill Loader 动态加载 (~200 LOC)

**描述**: 实现 Skill Loader，支持按需加载、卸载、热重载技能。

**验收标准**:
- [ ] 可按需加载 Skill 模块
- [ ] 可卸载不再需要的 Skill
- [ ] 支持热重载（开发时）
- [ ] 加载失败有友好错误提示

**验证方式**:
```python
# 测试 Loader 功能
loader = SkillLoader(registry)
skill = loader.load_skill("grill-me")
assert skill is not None
loader.unload_skill("grill-me")
```

**涉及文件**:
- `agent_framework/skills/loader.py`
- `agent_framework/tests/unit/skills/test_loader.py`

**依赖**: Task 2 (Skill Registry)

**估算时间**: 3-4 小时

---

### Task 4: Interceptor 接口定义 (~100 LOC)

**描述**: 定义 Interceptor 接口，支持在技能执行前后拦截和修改上下文。

**验收标准**:
- [ ] 定义 Interceptor Protocol
- [ ] 提供 before() 和 after() 方法
- [ ] 提供示例拦截器实现
- [ ] 支持拦截器链

**验证方式**:
```python
# 测试 Interceptor 功能
class TestInterceptor:
    def before(self, skill_name, context):
        context["intercepted"] = True
        return context

interceptor = TestInterceptor()
ctx = interceptor.before("test", {})
assert ctx["intercepted"] is True
```

**涉及文件**:
- `agent_framework/skills/middleware.py` (Interceptor 部分)

**依赖**: Task 1 (数据模型)

**估算时间**: 2-3 小时

---

### Task 5: Middleware 路由功能 (~250 LOC)

**描述**: 实现 Middleware 的核心路由功能，根据状态路由到合适的 Skill。

**验收标准**:
- [ ] 可根据 task_type 路由到对应 Skill
- [ ] 可根据 user_query 路由到对应 Skill
- [ ] 路由失败有友好错误提示
- [ ] 支持默认路由策略

**验证方式**:
```python
# 测试路由功能
middleware = SkillMiddleware(registry)
state = {"task_type": "grilling"}
skill_name = middleware.route(state)
assert skill_name == "grill-me"
```

**涉及文件**:
- `agent_framework/skills/middleware.py` (路由部分)
- `agent_framework/tests/unit/skills/test_middleware.py`

**依赖**: Task 2 (Skill Registry), Task 4 (Interceptor)

**估算时间**: 4-5 小时

---

### Task 6: Middleware 执行功能 (~250 LOC)

**描述**: 实现 Middleware 的执行功能，应用拦截器并执行技能。

**验收标准**:
- [ ] 可执行指定 Skill
- [ ] 拦截器在执行前后正确调用
- [ ] 执行结果正确返回
- [ ] 执行失败有降级机制

**验证方式**:
```python
# 测试执行功能
result = middleware.execute_skill(
    "grill-me",
    SkillContext(session_path="/tmp", state={})
)
assert result.success is True
```

**涉及文件**:
- `agent_framework/skills/middleware.py` (执行部分)
- `agent_framework/tests/unit/skills/test_middleware.py`

**依赖**: Task 3 (Skill Loader), Task 5 (路由功能)

**估算时间**: 4-5 小时

---

### Task 7: 并行执行器 (~150 LOC)

**描述**: 实现并行执行器，支持多个 Skills 同时执行且状态隔离。

**验收标准**:
- [ ] 可并行执行多个 Skills
- [ ] 技能之间状态隔离
- [ ] 并行执行结果正确返回
- [ ] 提供隔离验证方法

**验证方式**:
```python
# 测试并行执行
executor = ParallelSkillExecutor(middleware)
results = executor.execute_parallel(
    ["grill-me", "grill-you"],
    [ctx1, ctx2]
)
assert len(results) == 2
assert all(r.success for r in results)
```

**涉及文件**:
- `agent_framework/skills/executor.py`
- `agent_framework/tests/unit/skills/test_executor.py`

**依赖**: Task 6 (Middleware 执行)

**估算时间**: 3-4 小时

---

### Task 8: 集成测试与文档 (~200 LOC)

**描述**: 编写 S1 的集成测试和文档。

**验收标准**:
- [ ] Registry + Middleware 集成测试通过
- [ ] 端到端路由测试通过
- [ ] API 文档完整
- [ ] 使用示例清晰

**验证方式**:
```bash
# 运行集成测试
pytest agent_framework/tests/integration/skill_registry/
```

**涉及文件**:
- `agent_framework/tests/integration/skill_registry/test_s1_integration.py`
- `docs/spec-feature/spec-s1-registry.md` (更新)

**依赖**: Task 7 (所有之前任务)

**估算时间**: 3-4 小时

---

## Summary

- **总任务数**: 8
- **总估算 LOC**: ~1,450
- **关键路径**: 所有任务按顺序执行
- **估算总时间**: ~25-35 小时

---

## Dependencies on Other Sub-Specs

- **被 S2 依赖**: SkillRegistry API
- **被 S3 依赖**: SkillRegistry, SkillLoader API
- **被 S4 依赖**: Middleware API

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 查看 [tasks-s2-factory.md](tasks-s2-factory.md)
