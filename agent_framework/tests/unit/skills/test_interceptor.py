"""
S1-T4: Interceptor 接口单元测试

测试拦截器接口：在技能执行前后拦截和修改上下文
"""
import pytest
from pathlib import Path
from typing import Protocol
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult
from agent_framework.skills.middleware import Interceptor, InterceptorChain, LoggingInterceptor


class TestInterceptorProtocol:
    """测试 Interceptor Protocol"""

    def test_interceptor_protocol_exists(self):
        """测试 Interceptor Protocol 存在且可继承"""
        # Protocol 类型的正确检查方式
        from typing import get_origin, get_args
        # Interceptor 应该是一个可调用的类型定义
        assert callable(Interceptor) or hasattr(Interceptor, "__protocol_attrs__")

    def test_custom_interceptor_can_implement_protocol(self):
        """测试自定义拦截器可以实现 Interceptor Protocol"""

        class CustomInterceptor:
            """自定义拦截器实现"""

            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                """执行前拦截"""
                context.state["intercepted"] = True
                return context

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                """执行后拦截"""
                return result

        interceptor = CustomInterceptor()
        test_context = SkillContext(session_path=Path("/tmp"), state={})

        result_context = interceptor.before("test-skill", test_context)
        assert result_context.state["intercepted"] is True


class TestInterceptorChain:
    """测试拦截器链"""

    def test_create_interceptor_chain(self):
        """测试创建拦截器链"""
        chain = InterceptorChain()
        assert chain is not None

    def test_add_interceptor(self):
        """测试添加拦截器到链"""
        chain = InterceptorChain()
        interceptor = LoggingInterceptor()
        chain.add(interceptor)
        assert len(chain.interceptors) == 1

    def test_chain_calls_before_in_order(self, tmp_path):
        """测试拦截器链按顺序调用 before"""
        chain = InterceptorChain()
        order = []

        class FirstInterceptor:
            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                order.append("first")
                return context

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                return result

        class SecondInterceptor:
            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                order.append("second")
                return context

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                return result

        chain.add(FirstInterceptor())
        chain.add(SecondInterceptor())

        context = SkillContext(session_path=tmp_path, state={})
        chain.before("test", context)

        assert order == ["first", "second"]

    def test_chain_calls_after_in_reverse_order(self, tmp_path):
        """测试拦截器链按逆序调用 after"""
        chain = InterceptorChain()
        order = []

        class FirstInterceptor:
            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                return context

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                order.append("first")
                return result

        class SecondInterceptor:
            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                return context

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                order.append("second")
                return result

        chain.add(FirstInterceptor())
        chain.add(SecondInterceptor())

        result = SkillResult(success=True, output="test")
        chain.after("test", result)

        assert order == ["second", "first"]  # 逆序


class TestLoggingInterceptor:
    """测试日志拦截器"""

    def test_logging_interceptor_exists(self):
        """测试日志拦截器存在"""
        interceptor = LoggingInterceptor()
        assert interceptor is not None

    def test_logging_interceptor_has_before_and_after(self, tmp_path):
        """测试日志拦截器有 before 和 after 方法"""
        interceptor = LoggingInterceptor()
        context = SkillContext(session_path=tmp_path, state={})
        result = SkillResult(success=True, output="test")

        # 不应该抛出异常
        new_context = interceptor.before("test", context)
        new_result = interceptor.after("test", result)

        assert new_context is not None
        assert new_result is not None


class TestInterceptorModification:
    """测试拦截器修改上下文和结果"""

    def test_interceptor_can_modify_context(self, tmp_path):
        """测试拦截器可以修改上下文"""

        class ContextModifier:
            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                # 修改上下文
                new_state = dict(context.state)
                new_state["modified"] = True
                new_state["timestamp"] = "2024-01-01"
                return SkillContext(session_path=context.session_path, state=new_state)

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                return result

        interceptor = ContextModifier()
        context = SkillContext(session_path=tmp_path, state={})

        new_context = interceptor.before("test", context)
        assert new_context.state["modified"] is True
        assert new_context.state["timestamp"] == "2024-01-01"

    def test_interceptor_can_modify_result(self):
        """测试拦截器可以修改结果"""

        class ResultModifier:
            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                return context

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                # 由于 SkillResult 是 frozen，需要创建新实例
                return SkillResult(
                    success=result.success,
                    output=result.output + " [processed]",
                    error=result.error,
                    metadata={**result.metadata, "processed": True}
                )

        interceptor = ResultModifier()
        result = SkillResult(success=True, output="test")

        new_result = interceptor.after("test", result)
        assert new_result.output == "test [processed]"
        assert new_result.metadata["processed"] is True

    def test_interceptor_can_stop_execution(self, tmp_path):
        """测试拦截器可以阻止执行"""
        from agent_framework.skills.middleware import StopExecution

        class BlockingInterceptor:
            def before(self, skill_name: str, context: SkillContext) -> SkillContext:
                raise StopExecution("Execution blocked by interceptor")

            def after(self, skill_name: str, result: SkillResult) -> SkillResult:
                return result

        interceptor = BlockingInterceptor()
        context = SkillContext(session_path=tmp_path, state={})

        with pytest.raises(StopExecution, match="Execution blocked"):
            interceptor.before("test", context)
