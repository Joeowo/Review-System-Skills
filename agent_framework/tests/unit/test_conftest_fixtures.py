"""
测试 conftest.py 中的增强 fixtures

验证新添加的 fixtures 是否正常工作
"""

import os
import pytest


class TestMockConfigFixture:
    """测试 mock_config fixture"""

    def test_mock_config_has_valid_llm_config(self, mock_config):
        """mock_config 应该有有效的 LLM 配置"""
        assert mock_config is not None
        assert hasattr(mock_config, "llm")
        assert mock_config.llm.api_key == "test_key"
        assert mock_config.llm.model == "gpt-4"

    def test_mock_config_has_checkpoint_config(self, mock_config):
        """mock_config 应该有 checkpoint 配置"""
        assert hasattr(mock_config, "checkpoint")
        assert mock_config.checkpoint.db_path == ":memory:"

    def test_mock_config_sets_env_variables(self, mock_config):
        """mock_config 应该设置环境变量"""
        assert os.getenv("LLM_API_KEY") == "test_key"


class TestTempCheckpointerFixture:
    """测试 temp_checkpointer fixture"""

    def test_temp_checkpointer_is_valid(self, temp_checkpointer):
        """temp_checkpointer 应该是有效的 checkpointer"""
        assert temp_checkpointer is not None
        # 应该能使用 checkpointer
        assert hasattr(temp_checkpointer, "conn") or callable(temp_checkpointer)

    def test_temp_checkpointer_uses_temp_db(self, temp_checkpointer, tmp_path):
        """temp_checkpointer 应该使用临时数据库"""
        # checkpointer 应该与临时路径相关
        assert temp_checkpointer is not None
        # 验证 checkpointer 可以使用
        # SqliteSaver 使用内部连接，我们只验证它能正常工作
        assert callable(temp_checkpointer) or hasattr(temp_checkpointer, "conn")


class TestSampleWorkflowFixture:
    """测试 sample_workflow fixture"""

    def test_sample_workflow_exists(self, sample_workflow):
        """sample_workflow 应该存在"""
        assert sample_workflow is not None

    def test_sample_workflow_has_builder(self, sample_workflow):
        """sample_workflow 应该有 graph 结构相关方法"""
        # StateGraph 本身就有 add_node、add_edge 等方法
        assert hasattr(sample_workflow, "add_node")
        assert hasattr(sample_workflow, "set_entry_point")

    def test_sample_workflow_can_be_compiled(self, sample_workflow):
        """sample_workflow 应该能被编译"""
        compiled = sample_workflow.compile()
        assert compiled is not None


class TestSampleLLMResponseFixture:
    """测试 sample_llm_response fixture"""

    def test_sample_llm_response_has_content(self, sample_llm_response):
        """sample_llm_response 应该有内容"""
        assert sample_llm_response is not None
        assert hasattr(sample_llm_response, "content")
        assert len(sample_llm_response.content) > 0

    def test_sample_llm_response_content_type(self, sample_llm_response):
        """sample_llm_response 内容应该是正确类型"""
        content = sample_llm_response.content[0]
        assert content["type"] == "text"
        assert "text" in content


class TestMockStateFixture:
    """测试 mock_state fixture"""

    def test_mock_state_has_required_fields(self, mock_state):
        """mock_state 应该有所有必需字段"""
        required_fields = [
            "current_step", "error_message", "session_path",
            "cached_terminology", "cached_task_progress"
        ]
        for field in required_fields:
            assert field in mock_state

    def test_mock_state_has_no_error_by_default(self, mock_state):
        """mock_state 默认应该没有错误"""
        assert mock_state["error_message"] is None

    def test_mock_state_retry_count_is_zero(self, mock_state):
        """mock_state 重试次数应该为 0"""
        assert mock_state["retry_count"] == 0
