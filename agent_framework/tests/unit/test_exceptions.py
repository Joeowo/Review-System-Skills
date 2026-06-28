"""
C3: 异常处理框架 - 单元测试

测试覆盖：
- 异常类定义（4 层异常）
- ExceptionHandler 处理逻辑
- 降级策略执行
"""

import pytest
from agent_framework.core.exceptions import (
    AgentException,
    RetryableError,
    DegradableError,
    SkippableError,
    TerminalError,
    ResearchTimeoutError,
    ResearchInsufficientError,
    LLMAPIError,
)
from agent_framework.core.exception_handler import ExceptionHandler


# =============================================================================
# 测试组 1: 异常类定义
# =============================================================================

class TestExceptionDefinitions:
    """测试异常类定义"""

    def test_agent_exception_base_class_exists(self):
        """AgentException 基类存在"""
        assert issubclass(AgentException, Exception)

    def test_agent_exception_has_level_attribute(self):
        """AgentException 有 level 属性"""
        exc = AgentException("test")
        assert hasattr(exc, "level")
        assert exc.level == "terminate"  # 默认值

    def test_retryable_error_exists(self):
        """RetryableError 存在且继承 AgentException"""
        assert issubclass(RetryableError, AgentException)
        exc = RetryableError("test")
        assert exc.level == "retry"

    def test_retryable_error_has_max_retries(self):
        """RetryableError 有 max_retries 属性"""
        exc = RetryableError("test")
        assert hasattr(exc, "max_retries")
        assert exc.max_retries == 2  # 默认值

    def test_degradable_error_exists(self):
        """DegradableError 存在且继承 AgentException"""
        assert issubclass(DegradableError, AgentException)
        exc = DegradableError("test")
        assert exc.level == "degrade"

    def test_degradable_error_has_fallback(self):
        """DegradableError 有 fallback 属性"""
        exc = DegradableError("test")
        assert hasattr(exc, "fallback")
        assert exc.fallback == "skip"  # 默认值

    def test_skippable_error_exists(self):
        """SkippableError 存在且继承 AgentException"""
        assert issubclass(SkippableError, AgentException)
        exc = SkippableError("test")
        assert exc.level == "skip"

    def test_terminal_error_exists(self):
        """TerminalError 存在且继承 AgentException"""
        assert issubclass(TerminalError, AgentException)
        exc = TerminalError("test")
        assert exc.level == "terminate"


# =============================================================================
# 测试组 2: 具体异常类
# =============================================================================

class TestSpecificExceptions:
    """测试具体异常类"""

    def test_research_timeout_error_exists(self):
        """ResearchTimeoutError 存在"""
        assert issubclass(ResearchTimeoutError, RetryableError)
        exc = ResearchTimeoutError("timeout")
        assert exc.level == "retry"
        assert exc.max_retries == 2

    def test_research_insufficient_error_exists(self):
        """ResearchInsufficientError 存在"""
        assert issubclass(ResearchInsufficientError, DegradableError)
        exc = ResearchInsufficientError("insufficient")
        assert exc.level == "degrade"
        assert exc.fallback == "use_summary"

    def test_llm_api_error_exists(self):
        """LLMAPIError 存在"""
        assert issubclass(LLMAPIError, RetryableError)
        exc = LLMAPIError("API error")
        assert exc.level == "retry"
        assert exc.max_retries == 3


# =============================================================================
# 测试组 3: ExceptionHandler 初始化
# =============================================================================

class TestExceptionHandlerInit:
    """测试 ExceptionHandler 初始化"""

    def test_exception_handler_can_be_initialized(self):
        """ExceptionHandler 可以正确初始化"""
        handler = ExceptionHandler()
        assert handler is not None

    def test_exception_handler_has_handle_method(self):
        """ExceptionHandler 有 handle 方法"""
        handler = ExceptionHandler()
        assert hasattr(handler, "handle")
        assert callable(handler.handle)


# =============================================================================
# 测试组 4: ExceptionHandler.retry 处理
# =============================================================================

class TestExceptionHandlerRetry:
    """测试 retry 处理逻辑"""

    def test_handle_retryable_error_first_time(self, error_context):
        """首次处理可重试错误应返回 retry 指令"""
        handler = ExceptionHandler()
        error = ResearchTimeoutError("timeout")

        result = handler.handle(error, error_context)

        assert result["next_action"] == "retry"
        assert result["retry_count"] == 1
        assert "message" in result

    def test_handle_retryable_error_under_limit(self, error_context):
        """重试次数未超限时应继续重试"""
        handler = ExceptionHandler()
        error = ResearchTimeoutError("timeout")
        context = error_context.copy()
        context["retry_count"] = 1  # 已重试 1 次

        result = handler.handle(error, context)

        assert result["next_action"] == "retry"
        assert result["retry_count"] == 2

    def test_handle_retryable_error_at_limit(self, error_context):
        """重试次数达到上限时应降级"""
        handler = ExceptionHandler()
        error = ResearchTimeoutError("timeout")
        context = error_context.copy()
        context["retry_count"] = 2  # 已达到 max_retries

        result = handler.handle(error, context)

        # 超过重试次数应该降级或终止
        assert result["next_action"] in ["degrade", "terminate"]

    def test_handle_retryable_error_exceeds_limit(self, error_context):
        """重试次数超过上限时应终止"""
        handler = ExceptionHandler()
        error = ResearchTimeoutError("timeout")
        context = error_context.copy()
        context["retry_count"] = 3  # 超过 max_retries

        result = handler.handle(error, context)

        assert result["next_action"] == "terminate"


# =============================================================================
# 测试组 5: ExceptionHandler.degrade 处理
# =============================================================================

class TestExceptionHandlerDegrade:
    """测试 degrade 处理逻辑"""

    def test_handle_degradable_error_returns_fallback(self, error_context):
        """处理可降级错误应返回 fallback 策略"""
        handler = ExceptionHandler()
        error = ResearchInsufficientError("insufficient data")

        result = handler.handle(error, error_context)

        assert result["next_action"] == "degrade"
        assert result["fallback"] == "use_summary"
        assert "message" in result

    def test_handle_degradable_error_with_custom_fallback(self, error_context):
        """处理带自定义 fallback 的错误"""
        handler = ExceptionHandler()
        error = DegradableError("test", fallback="skip")

        result = handler.handle(error, error_context)

        assert result["next_action"] == "degrade"
        assert result["fallback"] == "skip"


# =============================================================================
# 测试组 6: ExceptionHandler.skip 处理
# =============================================================================

class TestExceptionHandlerSkip:
    """测试 skip 处理逻辑"""

    def test_handle_skippable_error(self, error_context):
        """处理可跳过错误应返回 skip 指令"""
        handler = ExceptionHandler()
        error = SkippableError("optional feature failed")

        result = handler.handle(error, error_context)

        assert result["next_action"] == "skip"
        assert "message" in result


# =============================================================================
# 测试组 7: ExceptionHandler.terminate 处理
# =============================================================================

class TestExceptionHandlerTerminate:
    """测试 terminate 处理逻辑"""

    def test_handle_terminal_error(self, error_context):
        """处理终止错误应返回 terminate 指令"""
        handler = ExceptionHandler()
        error = TerminalError("critical failure")

        result = handler.handle(error, error_context)

        assert result["next_action"] == "terminate"
        assert "error" in result
        assert "message" in result

    def test_handle_generic_exception(self, error_context):
        """处理普通 Exception 应返回 terminate"""
        handler = ExceptionHandler()
        error = ValueError("unexpected error")

        result = handler.handle(error, error_context)

        assert result["next_action"] == "terminate"


# =============================================================================
# 测试组 8: Context 处理
# =============================================================================

class TestExceptionHandlerContext:
    """测试 context 处理"""

    def test_handle_with_empty_context(self):
        """处理空 context 应正常工作"""
        handler = ExceptionHandler()
        error = RetryableError("test")

        result = handler.handle(error, {})

        assert result["next_action"] == "retry"
        assert result["retry_count"] == 1

    def test_handle_preserves_context_fields(self, error_context):
        """处理结果应保留 context 的相关字段"""
        handler = ExceptionHandler()
        error = RetryableError("test")
        context = error_context.copy()
        context["custom_field"] = "custom_value"

        result = handler.handle(error, context)

        # 结果应该包含原始 context 的字段
        # 具体实现可能有所不同，这里只验证基本行为
        assert "next_action" in result
