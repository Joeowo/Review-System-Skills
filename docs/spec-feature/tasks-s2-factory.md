# Tasks: Sub-Spec S2 - 标准化技能工厂与生命周期

**父规范**: [spec-s2-factory.md](spec-s2-factory.md)
**估算总 LOC**: ~1,250
**总任务数**: 7
**关键路径**: S1-T8 → S2-T1 → S2-T2 → S2-T3 → S2-T4 → S2-T5 → S2-T6 → S2-T7

---

## Task Breakdown

### Task 1: SKILL.md 验证器 (~150 LOC)

**描述**: 实现 SKILL.md 规范验证器，检查文件是否符合 write-a-skill 规范。

**验收标准**:
- [ ] 可验证 YAML frontmatter 完整性
- [ ] 可验证 description 字段格式
- [ ] 可验证文件行数 < 100
- [ ] 可验证必需章节存在
- [ ] 返回清晰的验证报告

**验证方式**:
```python
# 测试验证器功能
validator = SkillValidator()
result = validator.validate(Path("skills/grill-me/SKILL.md"))
assert result.valid is True  # 或根据实际情况断言
```

**涉及文件**:
- `agent_framework/skills/validator.py`
- `agent_framework/tests/unit/skills/test_validator.py`

**依赖**: S1-T8 (S1 完成)

**估算时间**: 3-4 小时

---

### Task 2: 标准化指令集 (~100 LOC)

**描述**: 定义标准化的 LLM 指令格式和 TOOLS 调用接口。

**验收标准**:
- [ ] 定义标准指令模板
- [ ] 定义标准工具接口
- [ ] 提供指令格式验证
- [ ] 提供示例指令

**验证方式**:
```python
# 测试标准化指令
from agent_framework.skills.standards.instructions import get_standard_instruction
instruction = get_standard_instruction("grill-me")
assert "Instructions for Claude" in instruction
```

**涉及文件**:
- `agent_framework/skills/standards/instructions.py`
- `agent_framework/skills/standards/tools.py`
- `agent_framework/tests/unit/skills/test_standards.py`

**依赖**: Task 1 (验证器)

**估算时间**: 2-3 小时

---

### Task 3: SKILL.md 迁移工具 (~250 LOC)

**描述**: 实现迁移工具，自动将不符合规范的 SKILL.md 迁移到新规范。

**验收标准**:
- [ ] 可拆分超长内容到 REFERENCE.md
- [ ] 可标准化 description 格式
- [ ] 可添加缺失的必需章节
- [ ] 迁移前自动备份原文件
- [ ] 返回迁移报告

**验证方式**:
```python
# 测试迁移工具
migrator = SkillMigrator()
report = migrator.migrate(Path("skills/old/SKILL.md"))
assert report.success is True
assert report.changes > 0
```

**涉及文件**:
- `agent_framework/skills/migrator.py`
- `agent_framework/tests/unit/skills/test_migrator.py`

**依赖**: Task 1 (验证器)

**估算时间**: 4-5 小时

---

### Task 4: 生命周期管理 - 注册与发现 (~150 LOC)

**描述**: 实现技能生命周期的注册与发现功能。

**验收标准**:
- [ ] 可扫描并解析 SKILL.md frontmatter
- [ ] 可注册技能到 Registry
- [ ] 可注销技能
- [ ] 提供注册事件日志

**验证方式**:
```python
# 测试生命周期注册
lifecycle = SkillLifecycle(registry)
metadata_list = lifecycle.discover(Path("skills/"))
assert len(metadata_list) > 0
lifecycle.register(metadata_list[0])
```

**涉及文件**:
- `agent_framework/skills/lifecycle.py` (发现与注册部分)
- `agent_framework/tests/unit/skills/test_lifecycle.py`

**依赖**: S1-T8 (SkillRegistry)

**估算时间**: 3-4 小时

---

### Task 5: 生命周期管理 - 加载与卸载 (~150 LOC)

**描述**: 实现技能生命周期的加载与卸载功能。

**验收标准**:
- [ ] 可按需加载 Skill 模块
- [ ] 可卸载释放内存
- [ ] 支持热重载（开发时）
- [ ] 提供加载状态查询

**验证方式**:
```python
# 测试生命周期加载
lifecycle = SkillLifecycle(registry)
skill = lifecycle.load("grill-me")
assert skill is not None
lifecycle.unload("grill-me")
```

**涉及文件**:
- `agent_framework/skills/lifecycle.py` (加载与卸载部分)
- `agent_framework/tests/unit/skills/test_lifecycle.py`

**依赖**: Task 4 (注册与发现)

**估算时间**: 3-4 小时

---

### Task 6: 生命周期管理 - 监控与诊断 (~150 LOC)

**描述**: 实现技能生命周期的监控与诊断功能。

**验收标准**:
- [ ] 可获取技能使用统计
- [ ] 可进行健康检查
- [ ] 可返回诊断报告
- [ ] 提供性能指标

**验证方式**:
```python
# 测试生命周期监控
stats = lifecycle.get_stats("grill-me")
assert stats.execution_count >= 0
health = lifecycle.get_health("grill-me")
assert health.healthy is True
```

**涉及文件**:
- `agent_framework/skills/lifecycle.py` (监控与诊断部分)
- `agent_framework/tests/unit/skills/test_lifecycle.py`

**依赖**: Task 5 (加载与卸载)

**估算时间**: 3-4 小时

---

### Task 7: 集成测试与文档 (~300 LOC)

**描述**: 编写 S2 的集成测试、CLI 工具和文档。

**验收标准**:
- [ ] 验证 + 迁移集成测试通过
- [ ] 生命周期 + Registry 集成测试通过
- [ ] CLI 工具可用（validate, migrate, health）
- [ ] 用户文档完整

**验证方式**:
```bash
# 运行集成测试
pytest agent_framework/tests/integration/skills/test_factory_integration.py

# 使用 CLI 工具
python -m agent_framework.skills.validator validate skills/grill-me/SKILL.md
python -m agent_framework.skills.migrator migrate skills/old/SKILL.md
```

**涉及文件**:
- `agent_framework/tests/integration/skills/test_factory_integration.py`
- `agent_framework/skills/__main__.py` (CLI 入口)
- `docs/spec-feature/user/migration_guide.md`

**依赖**: Task 6 (所有之前任务)

**估算时间**: 4-5 小时

---

## Summary

- **总任务数**: 7
- **总估算 LOC**: ~1,250
- **关键路径**: S1-T8 → S2-T1 → S2-T2 → S2-T3 → S2-T4 → S2-T5 → S2-T6 → S2-T7
- **估算总时间**: ~22-30 小时

---

## Dependencies on Other Sub-Specs

- **依赖 S1**: SkillRegistry, SkillLoader API
- **被 S5 依赖**: 验证和迁移工具

---

## Parallel Opportunities

- **S2-T1, S2-T2, S2-T3 可以并行开发** (都只依赖 S1)
- **S2-T2 可以与 S3 并行开发** (无相互依赖)

---

**文档版本**: 1.0
**最后更新**: 2026-06-29
**下一步**: 查看 [tasks-s3-context.md](tasks-s3-context.md)
