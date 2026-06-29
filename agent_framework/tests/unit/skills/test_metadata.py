"""
S1-T1: 数据模型单元测试

测试 SkillMetadata, SkillContext, SkillResult 等数据模型
"""
import pytest
from pathlib import Path
from dataclasses import FrozenInstanceError
from agent_framework.skills.models.metadata import SkillMetadata
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult


class TestSkillMetadata:
    """SkillMetadata 数据模型测试"""

    def test_create_minimal_metadata(self):
        """测试创建最小元数据：只包含必需字段"""
        metadata = SkillMetadata(
            name="test-skill",
            description="Test skill description",
            path=Path("/tmp/test/SKILL.md")
        )

        assert metadata.name == "test-skill"
        assert metadata.description == "Test skill description"
        assert metadata.path == Path("/tmp/test/SKILL.md")

    def test_create_full_metadata(self):
        """测试创建完整元数据：包含所有字段"""
        metadata = SkillMetadata(
            name="grill-me",
            description="Interview the user relentlessly",
            path=Path("/skills/grill-me/SKILL.md"),
            version="1.0",
            category="learning",
            tags=["interview", "context", "planning"]
        )

        assert metadata.name == "grill-me"
        assert metadata.version == "1.0"
        assert metadata.category == "learning"
        assert len(metadata.tags) == 3
        assert "interview" in metadata.tags

    def test_default_values(self):
        """测试默认值：version 默认为 1.0，category 默认为 general"""
        metadata = SkillMetadata(
            name="test-skill",
            description="Test",
            path=Path("/tmp/test.md")
        )

        assert metadata.version == "1.0"
        assert metadata.category == "general"
        assert metadata.tags == []

    def test_metadata_is_frozen(self):
        """测试数据模型是不可变的（frozen）"""
        metadata = SkillMetadata(
            name="test-skill",
            description="Test",
            path=Path("/tmp/test.md")
        )

        # frozen dataclass 不允许修改属性
        with pytest.raises(FrozenInstanceError):
            metadata.name = "new-name"

    def test_repr(self):
        """测试字符串表示"""
        metadata = SkillMetadata(
            name="grill-me",
            description="Interview the user",
            path=Path("/skills/grill-me/SKILL.md")
        )

        repr_str = repr(metadata)
        assert "grill-me" in repr_str
        assert "SkillMetadata" in repr_str


class TestSkillContext:
    """SkillContext 数据模型测试"""

    def test_create_minimal_context(self):
        """测试创建最小上下文"""
        context = SkillContext(
            session_path=Path("/tmp/session")
        )

        assert context.session_path == Path("/tmp/session")
        assert context.state == {}

    def test_create_context_with_state(self):
        """测试创建带状态的上下文"""
        state = {"task_type": "grilling", "user_query": "test query"}
        context = SkillContext(
            session_path=Path("/tmp/session"),
            state=state
        )

        assert context.state["task_type"] == "grilling"
        assert context.state["user_query"] == "test query"

    def test_default_state_is_empty_dict(self):
        """测试默认 state 为空字典"""
        context = SkillContext(session_path=Path("/tmp/session"))
        assert context.state == {}


class TestSkillResult:
    """SkillResult 数据模型测试"""

    def test_create_success_result(self):
        """测试创建成功结果"""
        result = SkillResult(
            success=True,
            output="Task completed successfully"
        )

        assert result.success is True
        assert result.output == "Task completed successfully"
        assert result.error is None

    def test_create_failure_result(self):
        """测试创建失败结果"""
        result = SkillResult(
            success=False,
            output=None,
            error="Failed to execute skill"
        )

        assert result.success is False
        assert result.error == "Failed to execute skill"

    def test_result_with_metadata(self):
        """测试带元数据的结果"""
        result = SkillResult(
            success=True,
            output="Done",
            metadata={"rounds": 3, "mastery_level": "good"}
        )

        assert result.metadata["rounds"] == 3
        assert result.metadata["mastery_level"] == "good"

    def test_default_metadata_is_empty(self):
        """测试默认 metadata 为空字典"""
        result = SkillResult(success=True, output="test")
        assert result.metadata == {}
