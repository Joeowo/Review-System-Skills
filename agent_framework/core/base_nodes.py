"""
C5: 基础节点库

提供通用节点装饰器：
- retry_node: 重试装饰器
- timeout_node: 超时装饰器
- logging_node: 日志装饰器
- error_handling_node: 错误处理装饰器
"""

import time
import signal
from functools import wraps
from typing import Dict, Any, Callable, Optional
from contextlib import contextmanager


# =============================================================================
# Timeout 上下文管理器
# =============================================================================

class TimeoutException(Exception):
    """超时异常"""
    pass


@contextmanager
def time_limit(seconds: float):
    """超时上下文管理器

    Args:
        seconds: 超时秒数

    Yields:
        None
    """
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out")

    # Windows 不支持 SIGALRM，使用简化版本
    if hasattr(signal, 'SIGALRM'):
        old_handler = signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(int(seconds))
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Windows 下使用超时检查的简化版本
        start_time = time.time()
        yield
        if time.time() - start_time > seconds:
            raise TimeoutException("Timed out")


# =============================================================================
# retry_node 装饰器
# =============================================================================

def retry_node(max_retries: int = 3) -> Callable:
    """重试装饰器节点

    Args:
        max_retries: 最大重试次数

    Returns:
        装饰后的节点函数
    """
    def decorator(node_func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        @wraps(node_func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            last_error = None
            retry_count = 0

            for attempt in range(max_retries + 1):
                try:
                    result = node_func(state)
                    # 成功则返回
                    return result
                except Exception as e:
                    last_error = e
                    retry_count = attempt + 1
                    if attempt < max_retries:
                        continue  # 重试
                    else:
                        # 达到最大重试次数，返回失败
                        return {
                            "status": "failed",
                            "error": str(last_error),
                            "error_type": type(last_error).__name__,
                            "retry_count": retry_count,
                        }

            # 理论上不会到这里
            return {
                "status": "failed",
                "error": str(last_error),
                "retry_count": retry_count,
            }

        return wrapper
    return decorator


# =============================================================================
# timeout_node 装饰器
# =============================================================================

def timeout_node(timeout: float = 60) -> Callable:
    """超时装饰器节点

    Args:
        timeout: 超时时间（秒）

    Returns:
        装饰后的节点函数
    """
    def decorator(node_func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        @wraps(node_func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # 尝试使用超时限制
                with time_limit(timeout):
                    return node_func(state)
            except TimeoutException:
                return {
                    "status": "timeout",
                    "error": f"Node execution timed out after {timeout} seconds",
                    "error_type": "TimeoutException",
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

        return wrapper
    return decorator


# =============================================================================
# logging_node 装饰器
# =============================================================================

def logging_node(log_level: str = "INFO") -> Callable:
    """日志装饰器节点

    Args:
        log_level: 日志级别

    Returns:
        装饰后的节点函数
    """
    def decorator(node_func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        @wraps(node_func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            # 记录节点执行开始
            node_name = node_func.__name__
            # 实际实现应该使用 logging 模块
            # 这里简化处理，直接执行
            try:
                result = node_func(state)
                # 记录成功
                return result
            except Exception as e:
                # 记录失败
                raise

        return wrapper
    return decorator


# =============================================================================
# error_handling_node 装饰器
# =============================================================================

def error_handling_node() -> Callable:
    """错误处理装饰器节点

    捕获节点执行中的异常并返回错误信息。

    Returns:
        装饰后的节点函数
    """
    def decorator(node_func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        @wraps(node_func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            try:
                return node_func(state)
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                }

        return wrapper
    return decorator
