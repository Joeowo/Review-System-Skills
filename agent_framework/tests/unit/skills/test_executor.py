"""
S1-T7: 并行执行器单元测试

测试并行执行器：支持多个 Skills 同时执行且状态隔离
"""
import pytest
import tempfile
from pathlib import Path
from concurrent.futures import wait
from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.skills.executor import ParallelSkillExecutor
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult


class TestParallelExecution:
    """测试并行执行功能"""

    def test_execute_parallel_two_skills(self, tmp_path):
        """测试并行执行两个技能"""
        # 创建测试技能
        (tmp_path / "skill-1").mkdir()
        (tmp_path / "skill-1" / "SKILL.md").write_text(
            "---\nname: skill-1\ndescription: First\n---",
            encoding="utf-8"
        )
        (tmp_path / "skill-2").mkdir()
        (tmp_path / "skill-2" / "SKILL.md").write_text(
            "---\nname: skill-2\ndescription: Second\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        context1 = SkillContext(session_path=tmp_path, state={"id": 1})
        context2 = SkillContext(session_path=tmp_path, state={"id": 2})

        results = executor.execute_parallel(
            ["skill-1", "skill-2"],
            [context1, context2],
            loader
        )

        assert len(results) == 2
        assert all(r.success for r in results)
        assert results[0].metadata["skill_name"] == "skill-1"
        assert results[1].metadata["skill_name"] == "skill-2"

    def test_execute_parallel_with_single_skill(self, tmp_path):
        """测试并行执行单个技能"""
        (tmp_path / "skill-1").mkdir()
        (tmp_path / "skill-1" / "SKILL.md").write_text(
            "---\nname: skill-1\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        context = SkillContext(session_path=tmp_path, state={})

        results = executor.execute_parallel(["skill-1"], [context], loader)

        assert len(results) == 1
        assert results[0].success is True

    def test_execute_parallel_empty_list(self, tmp_path):
        """测试并行执行空列表"""
        registry = SkillRegistry(tmp_path)
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        results = executor.execute_parallel([], [], loader)

        assert len(results) == 0


class TestStateIsolation:
    """测试状态隔离"""

    def test_parallel_executions_state_isolated(self, tmp_path):
        """测试并行执行时状态隔离"""
        # 创建测试技能
        for i in range(3):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: skill-{i}\ndescription: Skill {i}\n---",
                encoding="utf-8"
            )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        # 添加状态修改拦截器
        from agent_framework.skills.middleware import Interceptor

        class StateModifier:
            def before(self, skill_name, context):
                new_state = dict(context.state)
                new_state["modified_by"] = skill_name
                new_state["timestamp"] = "2024-01-01"
                return SkillContext(session_path=context.session_path, state=new_state)

            def after(self, skill_name, result):
                return result

        middleware.add_interceptor(StateModifier())

        contexts = [
            SkillContext(session_path=tmp_path, state={"id": i})
            for i in range(3)
        ]

        results = executor.execute_parallel(
            ["skill-0", "skill-1", "skill-2"],
            contexts,
            loader
        )

        # 验证每个执行结果都是独立的
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.success is True
            # 由于拦截器修改，元数据应该包含修改信息
            assert result.metadata.get("skill_name") == f"skill-{i}"

    def test_parallel_failure_does_not_affect_others(self, tmp_path):
        """测试并行执行中一个失败不影响其他"""
        (tmp_path / "good-skill").mkdir()
        (tmp_path / "good-skill" / "SKILL.md").write_text(
            "---\nname: good-skill\ndescription: Good\n---",
            encoding="utf-8"
        )
        # 不创建 bad-skill，模拟失败

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        context1 = SkillContext(session_path=tmp_path, state={})
        context2 = SkillContext(session_path=tmp_path, state={})

        results = executor.execute_parallel(
            ["good-skill", "bad-skill"],
            [context1, context2],
            loader
        )

        assert len(results) == 2
        # 第一个应该成功
        assert results[0].success is True
        # 第二个应该失败
        assert results[1].success is False


class TestParallelExecutorLimits:
    """测试并行执行器限制"""

    def test_execute_with_max_workers(self, tmp_path):
        """测试使用指定最大工作线程数"""
        for i in range(5):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: skill-{i}\ndescription: Skill {i}\n---",
                encoding="utf-8"
            )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware, max_workers=2)

        contexts = [
            SkillContext(session_path=tmp_path, state={"id": i})
            for i in range(5)
        ]

        results = executor.execute_parallel(
            [f"skill-{i}" for i in range(5)],
            contexts,
            loader
        )

        assert len(results) == 5
        assert all(r.success for r in results)


class TestParallelExecutorResults:
    """测试并行执行结果"""

    def test_results_maintain_order(self, tmp_path):
        """测试结果保持顺序"""
        for i in range(3):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: skill-{i}\ndescription: Skill {i}\n---",
                encoding="utf-8"
            )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        contexts = [
            SkillContext(session_path=tmp_path, state={"index": i})
            for i in range(3)
        ]

        results = executor.execute_parallel(
            ["skill-0", "skill-1", "skill-2"],
            contexts,
            loader
        )

        # 验证结果顺序与输入一致
        assert len(results) == 3
        assert results[0].metadata["skill_name"] == "skill-0"
        assert results[1].metadata["skill_name"] == "skill-1"
        assert results[2].metadata["skill_name"] == "skill-2"

    def test_results_contain_metadata(self, tmp_path):
        """测试结果包含元数据"""
        (tmp_path / "test-skill").mkdir()
        (tmp_path / "test-skill" / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        context = SkillContext(session_path=tmp_path, state={})

        results = executor.execute_parallel(["test-skill"], [context], loader)

        assert len(results) == 1
        result = results[0]
        assert "skill_name" in result.metadata
        assert result.metadata["skill_name"] == "test-skill"


class TestParallelExecutorErrors:
    """测试并行执行器错误处理"""

    def test_mismatched_lengths_raises_error(self, tmp_path):
        """测试技能列表与上下文列表长度不匹配时抛出异常"""
        registry = SkillRegistry(tmp_path)
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        context = SkillContext(session_path=tmp_path, state={})

        with pytest.raises(ValueError, match="Length mismatch"):
            executor.execute_parallel(["skill-1", "skill-2"], [context], loader)

    def test_one_skill_fails_others_succeed(self, tmp_path):
        """测试一个技能失败其他成功"""
        (tmp_path / "good-skill").mkdir()
        (tmp_path / "good-skill" / "SKILL.md").write_text(
            "---\nname: good-skill\ndescription: Good\n---",
            encoding="utf-8"
        )
        (tmp_path / "another-good").mkdir()
        (tmp_path / "another-good" / "SKILL.md").write_text(
            "---\nname: another-good\ndescription: Another\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        contexts = [
            SkillContext(session_path=tmp_path, state={}),
            SkillContext(session_path=tmp_path, state={}),
            SkillContext(session_path=tmp_path, state={}),
        ]

        results = executor.execute_parallel(
            ["good-skill", "bad-skill", "another-good"],
            contexts,
            loader
        )

        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is False
        assert results[2].success is True
