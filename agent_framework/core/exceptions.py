"""
C3: 异常处理框架

实现分层异常处理和降级策略（ADR-0004）：
- AgentException: 基类，定义 level 属性
- RetryableError: 可重试错误
- DegradableError: 可降级错误
- SkippableError: 可跳过错误
- TerminalError: 终止错误
"""

from typing import Optional


# =============================================================================
# 异常基类
# =============================================================================

class AgentException(Exception):
    """Agent 框架异常基类

    所有框架异常的基类，定义异常层级和默认行为。

    Attributes:
        level: 异常层级 (retry, degrade, skip, terminate)
    """

    level: str = "terminate"  # 默认终止

    def __init__(self, message: str):
        """初始化异常

        Args:
            message: 错误消息
        """
        super().__init__(message)
        self.message = message


# =============================================================================
# 可重试错误
# =============================================================================

class RetryableError(AgentException):
    """可重试错误

    用于瞬时错误，如网络超时、API 限流等。

    Attributes:
        level: 固定为 "retry"
        max_retries: 最大重试次数
    """

    level = "retry"
    max_retries: int = 2

    def __init__(self, message: str, max_retries: Optional[int] = None):
        """初始化可重试错误

        Args:
            message: 错误消息
            max_retries: 最大重试次数，默认使用类定义的值
        """
        super().__init__(message)
        if max_retries is not None:
            self.max_retries = max_retries


# =============================================================================
# 可降级错误
# =============================================================================

class DegradableError(AgentException):
    """可降级错误

    用于可以降低服务质量继续执行的情况。

    Attributes:
        level: 固定为 "degrade"
        fallback: 降级策略标识
    """

    level = "degrade"
    fallback: str = "skip"

    def __init__(self, message: str, fallback: Optional[str] = None):
        """初始化可降级错误

        Args:
            message: 错误消息
            fallback: 降级策略，默认使用类定义的值
        """
        super().__init__(message)
        if fallback is not None:
            self.fallback = fallback


# =============================================================================
# 可跳过错误
# =============================================================================

class SkippableError(AgentException):
    """可跳过错误

    用于非关键功能失败的情况。

    Attributes:
        level: 固定为 "skip"
    """

    level = "skip"


# =============================================================================
# 终止错误
# =============================================================================

class TerminalError(AgentException):
    """终止错误

    用于无法继续执行的严重错误。

    Attributes:
        level: 固定为 "terminate"
    """

    level = "terminate"


# =============================================================================
# 具体异常类
# =============================================================================

class ResearchTimeoutError(RetryableError):
    """研究超时错误"""

    max_retries = 2


class ResearchInsufficientError(DegradableError):
    """研究内容不足错误"""

    fallback = "use_summary"


class LLMAPIError(RetryableError):
    """LLM API 错误"""

    max_retries = 3


class SessionExistsError(DegradableError):
    """会话已存在错误"""

    fallback = "create_new_session"


class ConceptExtractionFailedError(DegradableError):
    """概念提取失败错误"""

    fallback = "use_topic_as_concept"
