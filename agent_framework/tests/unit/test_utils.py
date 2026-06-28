"""
测试工具函数模块

验证 tests/utils.py 中的辅助函数
"""

import pytest
from pathlib import Path
from typing import Dict, Any


class TestAssertStateStep:
    """测试 assert_state_step 函数"""

    def test_pass_with_matching_step(self):
        """当步骤匹配时应该通过"""
        from tests.utils import assert_state_step

        state = {"current_step": "processing"}
        # 不应该抛出异常
        assert_state_step(state, "processing")

    def test_fail_with_mismatched_step(self):
        """当步骤不匹配时应该抛出 AssertionError"""
        from tests.utils import assert_state_step

        state = {"current_step": "processing"}

        with pytest.raises(AssertionError) as exc_info:
            assert_state_step(state, "completed")

        assert "Expected step completed" in str(exc_info.value)
        assert "got processing" in str(exc_info.value)


class TestAssertNoError:
    """测试 assert_no_error 函数"""

    def test_pass_with_no_error(self):
        """当没有错误时应该通过"""
        from tests.utils import assert_no_error

        state = {"error_message": None}
        # 不应该抛出异常
        assert_no_error(state)

    def test_fail_with_error(self):
        """当有错误时应该抛出 AssertionError"""
        from tests.utils import assert_no_error

        state = {"error_message": "API 调用失败"}

        with pytest.raises(AssertionError) as exc_info:
            assert_no_error(state)

        assert "Unexpected error" in str(exc_info.value)
        assert "API 调用失败" in str(exc_info.value)


class TestLoadTestReport:
    """测试 load_test_report 函数"""

    def test_load_existing_file(self, temp_dir: Path):
        """应该能加载存在的文件"""
        from tests.utils import load_test_report

        report_path = temp_dir / "test_report.txt"
        report_path.write_text("测试报告内容", encoding="utf-8")

        content = load_test_report(str(report_path))
        assert content == "测试报告内容"

    def test_load_with_utf8_encoding(self, temp_dir: Path):
        """应该正确处理 UTF-8 编码"""
        from tests.utils import load_test_report

        report_path = temp_dir / "utf8_report.txt"
        report_path.write_text("测试中文 🧪", encoding="utf-8")

        content = load_test_report(str(report_path))
        assert content == "测试中文 🧪"


class TestCreateSampleState:
    """测试 create_sample_state 函数"""

    def test_create_minimal_state(self):
        """应该能创建最小状态"""
        from tests.utils import create_sample_state

        state = create_sample_state()

        assert "current_step" in state
        assert "error_message" in state
        assert "session_path" in state
        assert state["error_message"] is None
        assert state["retry_count"] == 0

    def test_create_state_with_custom_values(self):
        """应该能使用自定义值创建状态"""
        from tests.utils import create_sample_state

        state = create_sample_state(
            current_step="custom_step",
            session_path="/custom/path"
        )

        assert state["current_step"] == "custom_step"
        assert state["session_path"] == "/custom/path"


class TestWaitForCondition:
    """测试 wait_for_condition 函数"""

    def test_wait_for_true_condition(self):
        """当条件为真时应该立即返回"""
        from tests.utils import wait_for_condition

        result = wait_for_condition(lambda x: x > 5, 10, timeout=1)
        assert result is True

    def test_timeout_on_false_condition(self):
        """当条件为假时应该超时"""
        from tests.utils import wait_for_condition

        result = wait_for_condition(lambda x: x > 100, 10, timeout=0.1)
        assert result is False


class TestMockLLMResponse:
    """测试 mock_llm_response 函数"""

    def test_create_mock_response(self):
        """应该能创建模拟 LLM 响应"""
        from tests.utils import mock_llm_response

        response = mock_llm_response(content="测试内容")

        assert hasattr(response, "content")
        assert response.content == [ {"type": "text", "text": "测试内容"} ]

    def test_create_mock_response_with_tool_calls(self):
        """应该能创建带工具调用的模拟响应"""
        from tests.utils import mock_llm_response

        response = mock_llm_response(
            tool_calls=[{"name": "test_tool", "args": {"arg1": "value1"}}]
        )

        assert hasattr(response, "tool_calls")
        assert len(response.tool_calls) == 1
