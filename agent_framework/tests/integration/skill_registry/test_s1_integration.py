"""
S1-T8: S1 集成测试

测试 Skill Registry + Middleware + Loader 的端到端集成
"""
import pytest
import tempfile
from pathlib import Path

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.middleware import SkillMiddleware, LoggingInterceptor
from agent_framework.skills.executor import ParallelSkillExecutor
from agent_framework.skills.models.context import SkillContext


class TestS1Integration:
    """S1 组件集成测试"""

    def test_end_to_end_skill_discovery_and_execution(self, tmp_path):
        """测试端到端技能发现和执行流程"""
        # 创建测试技能
        (tmp_path / "test-skill").mkdir()
        (tmp_path / "test-skill" / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Integration test skill\n---\n# Test Skill\n\nThis is a test skill for integration testing.",
            encoding="utf-8"
        )

        # 1. 创建 Registry 并发现技能
        registry = SkillRegistry(tmp_path)
        registry.discover()

        skills = registry.list_all()
        assert len(skills) == 1
        assert skills[0].name == "test-skill"

        # 2. 创建 Loader 并加载技能
        loader = SkillLoader(registry)
        content = loader.load_skill("test-skill")
        assert "Integration test skill" in content

        # 3. 创建 Middleware 并路由技能
        middleware = SkillMiddleware(registry)
        middleware.add_route("test", "test-skill")

        state = {"task_type": "test"}
        skill_name = middleware.route(state)
        assert skill_name == "test-skill"

        # 4. 使用 Middleware 执行技能
        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test-skill", context, loader)
        assert result.success is True
        assert "Test Skill" in result.output

    def test_integration_with_interceptor(self, tmp_path):
        """测试带拦截器的集成流程"""
        (tmp_path / "skill-1").mkdir()
        (tmp_path / "skill-1" / "SKILL.md").write_text(
            "---\nname: skill-1\ndescription: Skill 1\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 添加日志拦截器
        middleware.add_interceptor(LoggingInterceptor())

        context = SkillContext(session_path=tmp_path, state={"test": "data"})
        result = middleware.execute_skill("skill-1", context, loader)

        assert result.success is True
        assert result.metadata["skill_name"] == "skill-1"

    def test_integration_with_parallel_executor(self, tmp_path):
        """测试并行执行器集成"""
        # 创建多个技能
        for i in range(3):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: skill-{i}\ndescription: Skill {i}\n---\nContent {i}",
                encoding="utf-8"
            )

        # 初始化所有组件
        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        # 并行执行
        contexts = [
            SkillContext(session_path=tmp_path, state={"id": i})
            for i in range(3)
        ]

        results = executor.execute_parallel(
            ["skill-0", "skill-1", "skill-2"],
            contexts,
            loader
        )

        assert len(results) == 3
        assert all(r.success for r in results)

    def test_full_workflow_routing_to_execution(self, tmp_path):
        """测试完整工作流：从路由到执行"""
        # 创建多个不同类型的技能
        (tmp_path / "grill-me").mkdir()
        (tmp_path / "grill-me" / "SKILL.md").write_text(
            "---\nname: grill-me\ndescription: Interview skill\n---",
            encoding="utf-8"
        )
        (tmp_path / "advance-task").mkdir()
        (tmp_path / "advance-task" / "SKILL.md").write_text(
            "---\nname: advance-task\ndescription: Task progress\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 测试路由到 grilling
        state1 = {"task_type": "grilling"}
        skill1 = middleware.route(state1)
        assert skill1 == "grill-me"

        context1 = SkillContext(session_path=tmp_path, state=state1)
        result1 = middleware.execute_skill(skill1, context1, loader)
        assert result1.success is True

        # 测试路由到 advance
        state2 = {"task_type": "advance"}
        skill2 = middleware.route(state2)
        assert skill2 == "advance-task"

        context2 = SkillContext(session_path=tmp_path, state=state2)
        result2 = middleware.execute_skill(skill2, context2, loader)
        assert result2.success is True

    def test_keyword_routing_integration(self, tmp_path):
        """测试关键词路由集成"""
        (tmp_path / "review-session").mkdir()
        (tmp_path / "review-session" / "SKILL.md").write_text(
            "---\nname: review-session\ndescription: Review skill\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 测试关键词路由
        state = {"user_query": "Can you review my code?"}
        skill = middleware.route(state)
        assert skill == "review-session"

        context = SkillContext(session_path=tmp_path, state=state)
        result = middleware.execute_skill(skill, context, loader)
        assert result.success is True

    def test_error_handling_integration(self, tmp_path):
        """测试错误处理集成"""
        # 只创建一个技能
        (tmp_path / "good-skill").mkdir()
        (tmp_path / "good-skill" / "SKILL.md").write_text(
            "---\nname: good-skill\ndescription: Good\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 测试路由失败
        state = {"task_type": "nonexistent"}
        with pytest.raises(Exception):  # RouteNotFoundError
            middleware.route(state)

        # 测试执行失败（execute_skill 对不存在的技能会抛出异常）
        context = SkillContext(session_path=tmp_path, state={})
        with pytest.raises(Exception, match="not found"):
            middleware.execute_skill("bad-skill", context, loader)

    def test_component_compatibility(self, tmp_path):
        """测试组件兼容性"""
        # 验证所有组件可以正确协作
        (tmp_path / "test").mkdir()
        (tmp_path / "test" / "SKILL.md").write_text(
            "---\nname: test\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()

        # Registry 可以与 Loader 协作
        loader = SkillLoader(registry)
        assert loader.is_loaded("test") is False
        loader.load_skill("test")
        assert loader.is_loaded("test") is True

        # Loader 可以与 Middleware 协作
        middleware = SkillMiddleware(registry)
        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test", context, loader)
        assert result.success is True

        # Middleware 可以与 Executor 协作
        executor = ParallelSkillExecutor(middleware)
        results = executor.execute_parallel(["test"], [context], loader)
        assert len(results) == 1
        assert results[0].success is True


class TestS1Performance:
    """S1 性能相关测试"""

    def test_registry_discovery_performance(self, tmp_path):
        """测试 Registry 发现性能"""
        import time

        # 创建 10 个技能
        for i in range(10):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: skill-{i}\ndescription: Skill {i}\n---",
                encoding="utf-8"
            )

        registry = SkillRegistry(tmp_path)

        start = time.time()
        registry.discover()
        elapsed = time.time() - start

        # 发现 10 个技能应该很快（< 1 秒）
        assert elapsed < 1.0
        assert len(registry.list_all()) == 10

    def test_loader_caching_performance(self, tmp_path):
        """测试 Loader 缓存性能"""
        import time

        (tmp_path / "test").mkdir()
        (tmp_path / "test" / "SKILL.md").write_text(
            "---\nname: test\ndescription: Test\n---" + "Content" * 1000,
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)

        # 首次加载
        start = time.time()
        loader.load_skill("test")
        first_load = time.time() - start

        # 缓存加载（应该更快）
        start = time.time()
        loader.load_skill("test")
        cached_load = time.time() - start

        # 缓存加载应该更快（虽然差异可能很小）
        assert cached_load <= first_load
