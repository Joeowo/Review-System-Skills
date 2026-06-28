"""
C3: 异常处理器

实现异常处理逻辑（ADR-0004）：
- 根据异常层级执行不同策略
- retry: 重试直到达到上限
- degrade: 执行降级策略
- skip: 跳过当前步骤
- terminate: 终止执行
"""

from typing import Dict, Any
from agent_framework.core.exceptions import (
    AgentException,
    RetryableError,
    DegradableError,
    SkippableError,
    TerminalError,
)


# =============================================================================
# ExceptionHandler 类
# =============================================================================

class ExceptionHandler:
    """异常处理器

    根据异常类型和上下文，决定下一步动作。

    处理策略：
    - retry: 重试操作（有次数限制）
    - degrade: 降级继续（执行 fallback）
    - skip: 跳过当前步骤
    - terminate: 终止执行
    """

    def handle(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理异常，返回下一步动作

        Args:
            error: 捕获的异常
            context: 执行上下文，包含 retry_count 等信息

        Returns:
            处理结果字典，包含 next_action 和相关信息
        """
        # 检查异常类型并分发处理
        if isinstance(error, RetryableError):
            return self._retry(error, context)
        elif isinstance(error, DegradableError):
            return self._degrade(error, context)
        elif isinstance(error, SkippableError):
            return self._skip(error, context)
        elif isinstance(error, TerminalError):
            return self._terminate(error, context)
        else:
            # 未知异常，按终止处理
            return self._terminate(error, context)

    def _retry(self, error: RetryableError, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理可重试错误

        Args:
            error: 可重试错误
            context: 执行上下文

        Returns:
            处理结果
        """
        retry_count = context.get("retry_count", 0)

        if retry_count < error.max_retries:
            # 可以继续重试
            return {
                "next_action": "retry",
                "retry_count": retry_count + 1,
                "message": f"重试 {retry_count + 1}/{error.max_retries}: {error.message}"
            }
        else:
            # 超过重试次数，降级或终止
            # 如果是 DegradableError 的子类，可以降级
            if isinstance(error, DegradableError):
                return self._degrade(error, context)
            else:
                return self._terminate(error, context)

    def _degrade(self, error: DegradableError, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理可降级错误

        Args:
            error: 可降级错误
            context: 执行上下文

        Returns:
            处理结果
        """
        return {
            "next_action": "degrade",
            "fallback": error.fallback,
            "message": f"降级: 执行 {error.fallback} 策略 - {error.message}"
        }

    def _skip(self, error: SkippableError, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理可跳过错误

        Args:
            error: 可跳过错误
            context: 执行上下文

        Returns:
            处理结果
        """
        return {
            "next_action": "skip",
            "message": f"跳过: {error.message}"
        }

    def _terminate(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理终止错误

        Args:
            error: 异常
            context: 执行上下文

        Returns:
            处理结果
        """
        error_type = type(error).__name__
        return {
            "next_action": "terminate",
            "error": str(error),
            "error_type": error_type,
            "message": f"终止: [{error_type}] {error.message if hasattr(error, 'message') else str(error)}"
        }
