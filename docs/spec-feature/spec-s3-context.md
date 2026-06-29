# Sub-Spec: S3 - 上下文优化策略

**父规范**: [01-master-spec.md](01-master-spec.md)
**估算 LOC**: ~600
**依赖**: S1 (技能注册表与中间件调度层)
**优先级**: P0

---

## Objective

采用 "目录注入+按需加载" 的调度策略，在保持模型高响应精度的同时，将单次任务的 Token 消耗降低 30% 以上。通过两阶段加载策略和预算管理，实现最优的上下文使用效率。

---

## Interfaces

### Consumes（消费）

- **S1 SkillRegistry**: 查询已注册的技能元数据
- **S1 SkillLoader**: 按需加载完整技能内容
- **AgentState**: 当前执行状态（用于判断加载时机）

### Produces（产出）

- **ContextOptimizer API**: 上下文优化和注入
- **OnDemandLoader API**: 按需加载触发和执行
- **BudgetManager API**: 预算管理和驱逐策略

### External Dependencies（外部依赖）

- `typing` - 类型注解
- `dataclasses` - 数据模型
- `structlog` - 日志记录

---

## Component Structure

```
agent_framework/skills/
├── context_optimizer.py      # 上下文优化器 (~400 LOC)
└── budget_manager.py         # 预算管理器 (~200 LOC)

Tests:
agent_framework/tests/unit/skills/
├── test_context_optimizer.py
└── test_budget_manager.py

Integration Tests:
agent_framework/tests/integration/skills/
└── test_context_integration.py
```

---

## Commands

```bash
# 分析上下文使用情况
python -m agent_framework.skills.context_optimizer analyze

# 设置预算限制
python -m agent_framework.skills.budget_manager set --limit 8000

# 查看预算使用情况
python -m agent_framework.skills.budget_manager status
```

---

## Code Style

遵循主规范编码风格，示例：

```python
"""agent_framework/skills 上下文优化示例代码风格"""

from dataclasses import dataclass, field
from typing import Optional, List
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class InjectionMetadata:
    """注入元数据"""
    skills: list[str]  # 技能名称列表
    estimated_tokens: int  # 预估 Token 数
    timestamp: float  # 注入时间

class ContextOptimizer:
    """上下文优化器"""

    def __init__(self, registry: 'SkillRegistry') -> None:
        self.registry = registry
        self._loaded_full: dict[str, str] = {}
        logger.info("ContextOptimizer initialized")

    def inject_metadata(self) -> str:
        """注入所有 Skills 的元数据

        返回: 注入的上下文字符串（YAML frontmatter + TOC）
        """
        metadata_injection = ["## Skills Available\n"]

        for skill in self.registry.list_all():
            metadata_injection.append(f"\n### {skill.name}")
            metadata_injection.append(f"{skill.description}")
            if skill.tags:
                metadata_injection.append(f"**Tags:** {', '.join(skill.tags)}")

        result = "\n".join(metadata_injection)
        logger.info(
            "Metadata injected",
            skill_count=len(self.registry.list_all()),
            estimated_tokens=len(result) // 4
        )
        return result

    def should_load_full_content(
        self,
        skill_name: str,
        state: dict
    ) -> bool:
        """判断是否需要加载完整内容

        触发条件:
        1. state["task_type"] 匹配 Skill 的 category
        2. state["user_query"] 包含 Skill 的触发关键词
        3. state["pending_skill_calls"] 包含该 Skill
        """
        skill = self.registry.get(skill_name)
        if not skill:
            return False

        # 检查任务类型匹配
        if state.get("task_type") == skill.category:
            logger.info("Loading full content by task_type", skill=skill_name)
            return True

        # 检查用户查询匹配
        user_query = state.get("user_query", "")
        if any(tag in user_query for tag in skill.tags):
            logger.info("Loading full content by user_query", skill=skill_name)
            return True

        return False
```

---

## Testing Strategy

### 单元测试

| 组件 | 测试内容 | 覆盖率目标 |
|------|----------|-----------|
| **ContextOptimizer** | 元数据注入、加载判断 | ≥ 80% |
| **BudgetManager** | 预算管理、驱逐策略 | ≥ 80% |

### 集成测试

- 优化器 + Registry 集成
- 优化器 + Loader 集成
- 预算管理器端到端测试

### A/B 测试

- 优化前后 Token 消耗对比
- 优化前后 LLM 响应准确率对比
- 不同预算阈值的性能对比

### 测试示例

```python
class TestContextOptimizer:
    """上下文优化器单元测试"""

    def test_metadata_injection_contains_all_skills(self):
        """测试元数据注入包含所有技能"""
        registry = MockSkillRegistry()
        registry.add_skill(SkillMetadata(
            name="test-skill",
            description="Test skill for testing",
            path=Path("/tmp/test.md")
        ))
        optimizer = ContextOptimizer(registry)
        result = optimizer.inject_metadata()
        assert "test-skill" in result
        assert "Test skill for testing" in result

    def test_should_load_by_task_type(self):
        """测试基于任务类型触发加载"""
        registry = MockSkillRegistry()
        registry.add_skill(SkillMetadata(
            name="grill-me",
            description="Interview user",
            path=Path("/tmp/grill-me.md"),
            category="grilling"
        ))
        optimizer = ContextOptimizer(registry)
        state = {"task_type": "grilling"}
        assert optimizer.should_load_full_content("grill-me", state) is True
```

---

## Boundaries

### Always Do（必须做）

- ✅ 记录每次加载的 Token 消耗
- ✅ 记录驱逐决策和原因
- ✅ 支持 A/B 测试验证
- ✅ 提供预算使用报告

### Ask First（先询问）

- 🤔 修改预算管理策略
- 🤔 调整触发条件阈值
- 🤔 修改驱逐算法

### Never Do（禁止做）

- ❌ 在没有预算时强制加载
- ❌ 驱逐当前正在使用的 Skill
- ❌ 静默失败而不记录日志

---

## Success Criteria

### 功能验证

- [ ] 初始化时只注入元数据（~1,000 tokens）
- [ ] 触发时正确加载完整内容
- [ ] 上下文预算管理有效防止过度加载
- [ ] LLM 响应准确率下降 < 5%
- [ ] 加载/驱逐决策有完整日志

### 质量指标

- [ ] 单元测试覆盖率 ≥ 80%
- [ ] A/B 测试显示 Token 消耗降低 ≥ 30%
- [ ] LLM 响应准确率下降 < 5%

### 性能目标

| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| **初始 Token 消耗** | ~10,000 | ~1,000 | 集成测试 |
| **峰值 Token 消耗** | ~10,000 | ~3,000 | 集成测试 |
| **平均 Token 消耗** | ~10,000 | 通过测试确定 | 实际运行统计 |
| **元数据注入时间** | N/A | < 100ms | 单元测试 |
| **按需加载时间** | N/A | < 200ms | 单元测试 |

---

## Open Questions

1. **最佳预算阈值**: 需要通过实际测试确定最佳预算值（当前假设 8000 tokens）
2. **驱逐策略选择**: LRU vs LFU vs 优先级？（当前假设优先级）
3. **缓存策略**: 是否缓存已加载的内容？（当前假设不缓存，每次重新读取）

---

## Related Documents

- [01-master-spec.md](01-master-spec.md) - 主规范
- [02-sub-spec-index.md](02-sub-spec-index.md) - 子规范索引
- [spec-s1-registry.md](spec-s1-registry.md) - 依赖的 S1 规范
- [docs/spec-feature/requirements/03-context-optimization.md](requirements/03-context-optimization.md) - 对应需求文档

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 进入实施阶段，编写详细任务
