"""
S1-T6: Middleware 执行功能单元测试

测试 Middleware 的执行功能：应用拦截器并执行技能
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.middleware import SkillMiddleware, StopExecution
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult


class TestMiddlewareExecuteSkill:
    """测试技能执行功能"""

    def test_execute_skill_success(self, tmp_path):
        """测试成功执行技能"""
        # 创建测试技能
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test skill\n---\nContent here",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        context = SkillContext(session_path=tmp_path, state={"key": "value"})
        result = middleware.execute_skill("test-skill", context, loader)

        assert result.success is True
        assert "Content here" in result.output

    def test_execute_skill_not_found_raises_error(self, tmp_path):
        """测试执行不存在的技能抛出异常"""
        registry = SkillRegistry(tmp_path)
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        context = SkillContext(session_path=tmp_path, state={})

        with pytest.raises(Exception, match="Skill.*not found"):
            middleware.execute_skill("nonexistent", context, loader)

    def test_execute_skill_applies_interceptors(self, tmp_path):
        """测试执行时应用拦截器"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 添加测试拦截器
        before_called = []
        after_called = []

        class TestInterceptor:
            def before(self, skill_name, context):
                before_called.append(skill_name)
                # 修改上下文
                new_state = dict(context.state)
                new_state["intercepted"] = True
                return SkillContext(session_path=context.session_path, state=new_state)

            def after(self, skill_name, result):
                after_called.append(skill_name)
                # 修改结果
                return SkillResult(
                    success=result.success,
                    output=result.output + " [processed]",
                    error=result.error,
                    metadata={**result.metadata, "intercepted": True}
                )

        middleware.add_interceptor(TestInterceptor())

        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test-skill", context, loader)

        assert len(before_called) == 1
        assert before_called[0] == "test-skill"
        assert len(after_called) == 1
        assert after_called[0] == "test-skill"
        assert "[processed]" in result.output
        assert result.metadata.get("intercepted") is True


class TestMiddlewareInterceptorErrors:
    """测试拦截器错误处理"""

    def test_interceptor_stops_execution(self, tmp_path):
        """测试拦截器阻止执行"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 添加阻止拦截器
        class BlockingInterceptor:
            def before(self, skill_name, context):
                raise StopExecution("Blocked by interceptor")

            def after(self, skill_name, result):
                return result

        middleware.add_interceptor(BlockingInterceptor())

        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test-skill", context, loader)

        # 被阻止的结果
        assert result.success is False
        assert "Blocked by interceptor" in result.error or "stopped" in result.error.lower()

    def test_interceptor_before_error_is_handled(self, tmp_path):
        """测试 before 拦截器错误被处理"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        class FailingInterceptor:
            def before(self, skill_name, context):
                raise RuntimeError("Interceptor failed")

            def after(self, skill_name, result):
                return result

        middleware.add_interceptor(FailingInterceptor())

        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test-skill", context, loader)

        # 应该返回错误结果
        assert result.success is False
        assert "Interceptor failed" in result.error

    def test_interceptor_after_error_is_handled(self, tmp_path):
        """测试 after 拦截器错误被处理"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        class FailingAfterInterceptor:
            def before(self, skill_name, context):
                return context

            def after(self, skill_name, result):
                raise RuntimeError("After interceptor failed")

        middleware.add_interceptor(FailingAfterInterceptor())

        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test-skill", context, loader)

        # after 拦截器错误应该被捕获，返回原始结果
        assert result.success is True  # 技能执行成功


class TestMiddlewareExecuteWithLoader:
    """测试与 Loader 集成的执行"""

    def test_execute_uses_loader_to_load_content(self, tmp_path):
        """测试执行时使用 Loader 加载内容"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---\nOriginal content",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test-skill", context, loader)

        assert result.success is True
        assert "Original content" in result.output

    def test_execute_caches_loaded_content(self, tmp_path):
        """测试执行时缓存加载的内容"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: test-skill\ndescription: Test\n---\nVersion 1",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        context = SkillContext(session_path=tmp_path, state={})

        # 第一次执行
        result1 = middleware.execute_skill("test-skill", context, loader)
        assert "Version 1" in result1.output

        # 修改文件
        skill_md.write_text(
            "---\nname: test-skill\ndescription: Test\n---\nVersion 2",
            encoding="utf-8"
        )

        # 第二次执行（应该使用缓存）
        result2 = middleware.execute_skill("test-skill", context, loader)
        # 由于使用缓存，仍然是 Version 1
        assert "Version 1" in result2.output


class TestMiddlewareExecuteState:
    """测试执行状态管理"""

    def test_execute_with_state_modification(self, tmp_path):
        """测试执行时修改状态"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 添加状态修改拦截器
        class StateModifier:
            def before(self, skill_name, context):
                new_state = dict(context.state)
                new_state["executed_at"] = "2024-01-01"
                new_state["execution_count"] = new_state.get("execution_count", 0) + 1
                return SkillContext(session_path=context.session_path, state=new_state)

            def after(self, skill_name, result):
                new_metadata = dict(result.metadata)
                new_metadata["final_state"] = "modified"
                return SkillResult(
                    success=result.success,
                    output=result.output,
                    error=result.error,
                    metadata=new_metadata
                )

        middleware.add_interceptor(StateModifier())

        context = SkillContext(session_path=tmp_path, state={"execution_count": 0})
        result = middleware.execute_skill("test-skill", context, loader)

        assert result.metadata.get("final_state") == "modified"


class TestMiddlewareExecuteResult:
    """测试执行结果"""

    def test_execute_returns_result_metadata(self, tmp_path):
        """测试执行返回包含元数据的结果"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        context = SkillContext(session_path=tmp_path, state={})
        result = middleware.execute_skill("test-skill", context, loader)

        # 结果应该包含基本元数据
        assert "skill_name" in result.metadata
        assert result.metadata["skill_name"] == "test-skill"
