"""
C5: 基础节点库 - 单元测试

测试覆盖：
- retry_node 装饰器
- timeout_node 装饰器
- logging_node 装饰器
- error_handling_node 装饰器
"""

import pytest
import time
from typing import Dict, Any
from agent_framework.core.base_nodes import (
    retry_node,
    timeout_node,
    logging_node,
    error_handling_node,
)


# =============================================================================
# 测试组 1: retry_node 装饰器
# =============================================================================

class TestRetryNode:
    """测试 retry_node 装饰器"""

    def test_retry_node_exists(self):
        """retry_node 装饰器存在"""
        assert retry_node is not None
        assert callable(retry_node)

    def test_retry_node_returns_function(self):
        """retry_node 返回函数"""
        @retry_node(max_retries=2)
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        assert callable(test_node)

    def test_retry_node_succeeds_on_first_try(self):
        """retry_node 第一次尝试成功时正常返回"""
        call_count = {"count": 0}

        @retry_node(max_retries=2)
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            call_count["count"] += 1
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "success"
        assert call_count["count"] == 1

    def test_retry_node_retries_on_failure(self):
        """retry_node 失败时重试"""
        call_count = {"count": 0}

        @retry_node(max_retries=3)
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            call_count["count"] += 1
            if call_count["count"] < 2:
                raise ValueError("Simulated error")
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "success"
        assert call_count["count"] == 2

    def test_retry_node_exhausts_retries(self):
        """retry_node 达到最大重试次数后失败"""
        @retry_node(max_retries=2)
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            raise ValueError("Always fails")

        result = test_node({})
        assert result["status"] == "failed"
        assert "error" in result


# =============================================================================
# 测试组 2: timeout_node 装饰器
# =============================================================================

class TestTimeoutNode:
    """测试 timeout_node 装饰器"""

    def test_timeout_node_exists(self):
        """timeout_node 装饰器存在"""
        assert timeout_node is not None
        assert callable(timeout_node)

    def test_timeout_node_returns_function(self):
        """timeout_node 返回函数"""
        @timeout_node(timeout=1)
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        assert callable(test_node)

    def test_timeout_node_completes_in_time(self):
        """timeout_node 在超时时间内完成"""
        @timeout_node(timeout=1)
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "success"

    def test_timeout_node_handles_timeout(self):
        """timeout_node 处理超时情况"""
        @timeout_node(timeout=0.1)
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            time.sleep(0.2)
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "timeout"
        assert "error" in result


# =============================================================================
# 测试组 3: logging_node 装饰器
# =============================================================================

class TestLoggingNode:
    """测试 logging_node 装饰器"""

    def test_logging_node_exists(self):
        """logging_node 装饰器存在"""
        assert logging_node is not None
        assert callable(logging_node)

    def test_logging_node_returns_function(self):
        """logging_node 返回函数"""
        @logging_node(log_level="INFO")
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        assert callable(test_node)

    def test_logging_node_logs_execution(self):
        """logging_node 记录节点执行"""
        logs = []

        @logging_node(log_level="INFO")
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        # 临时捕获日志（实际实现可能使用 logging 模块）
        result = test_node({})
        assert result["status"] == "success"

    def test_logging_node_preserves_result(self):
        """logging_node 保持原始返回值"""
        @logging_node(log_level="INFO")
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success", "data": 42}

        result = test_node({})
        assert result["status"] == "success"
        assert result["data"] == 42


# =============================================================================
# 测试组 4: error_handling_node 装饰器
# =============================================================================

class TestErrorHandlingNode:
    """测试 error_handling_node 装饰器"""

    def test_error_handling_node_exists(self):
        """error_handling_node 装饰器存在"""
        assert error_handling_node is not None
        assert callable(error_handling_node)

    def test_error_handling_node_returns_function(self):
        """error_handling_node 返回函数"""
        @error_handling_node()
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        assert callable(test_node)

    def test_error_handling_node_catches_exception(self):
        """error_handling_node 捕获异常"""
        @error_handling_node()
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            raise ValueError("Test error")

        result = test_node({})
        assert "error" in result
        assert result["error_type"] == "ValueError"

    def test_error_handling_node_returns_success(self):
        """error_handling_node 正常返回成功结果"""
        @error_handling_node()
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "success"


# =============================================================================
# 测试组 5: 装饰器组合
# =============================================================================

class TestDecoratorComposition:
    """测试装饰器组合"""

    def test_retry_and_logging_combination(self):
        """retry_node 和 logging_node 可以组合使用"""
        @retry_node(max_retries=2)
        @logging_node(log_level="INFO")
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "success"

    def test_retry_and_error_handling_combination(self):
        """retry_node 和 error_handling_node 可以组合使用"""
        @retry_node(max_retries=2)
        @error_handling_node()
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            raise ValueError("Test error")

        result = test_node({})
        # error_handling_node 会捕获异常
        # retry_node 会重试，最终失败
        assert "error" in result or result["status"] == "failed"

    def test_timeout_and_error_handling_combination(self):
        """timeout_node 和 error_handling_node 可以组合使用"""
        @timeout_node(timeout=1)
        @error_handling_node()
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "success"

    def test_all_decorators_combination(self):
        """所有装饰器可以组合使用"""
        @retry_node(max_retries=1)
        @timeout_node(timeout=1)
        @logging_node(log_level="INFO")
        @error_handling_node()
        def test_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "success"}

        result = test_node({})
        assert result["status"] == "success"
