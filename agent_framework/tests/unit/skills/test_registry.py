"""
S1-T2: Skill Registry 单元测试

测试技能注册表的核心功能：发现、注册、查询技能
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from agent_framework.skills.models.metadata import SkillMetadata
from agent_framework.skills.registry import SkillRegistry, DuplicateSkillError, SkillNotFoundError


class TestSkillRegistryRegistration:
    """测试技能注册功能"""

    def test_register_skill_success(self, tmp_path):
        """测试成功注册技能"""
        registry = SkillRegistry(tmp_path)
        metadata = SkillMetadata(
            name="test-skill",
            description="Test skill",
            path=tmp_path / "test-skill" / "SKILL.md"
        )
        registry.register(metadata)

        assert registry.get("test-skill") == metadata

    def test_register_duplicate_raises_error(self, tmp_path):
        """测试重复注册抛出异常"""
        registry = SkillRegistry(tmp_path)
        metadata = SkillMetadata(
            name="test-skill",
            description="Test skill",
            path=tmp_path / "test.md"
        )
        registry.register(metadata)

        with pytest.raises(DuplicateSkillError, match="already registered"):
            registry.register(metadata)

    def test_register_multiple_skills(self, tmp_path):
        """测试注册多个技能"""
        registry = SkillRegistry(tmp_path)
        skills = [
            SkillMetadata(name="skill-1", description="First", path=tmp_path / "1.md"),
            SkillMetadata(name="skill-2", description="Second", path=tmp_path / "2.md"),
            SkillMetadata(name="skill-3", description="Third", path=tmp_path / "3.md"),
        ]
        for skill in skills:
            registry.register(skill)

        assert len(registry.list_all()) == 3
        assert registry.get("skill-1").description == "First"


class TestSkillRegistryQuery:
    """测试技能查询功能"""

    def test_get_skill_by_name(self, tmp_path):
        """测试按 name 查询技能"""
        registry = SkillRegistry(tmp_path)
        metadata = SkillMetadata(
            name="grill-me",
            description="Interview skill",
            path=tmp_path / "grill-me.md"
        )
        registry.register(metadata)

        result = registry.get("grill-me")
        assert result.name == "grill-me"
        assert result.description == "Interview skill"

    def test_get_nonexistent_skill_raises_error(self, tmp_path):
        """测试查询不存在的技能抛出异常"""
        registry = SkillRegistry(tmp_path)

        with pytest.raises(SkillNotFoundError, match="not found"):
            registry.get("nonexistent")

    def test_find_by_category(self, tmp_path):
        """测试按 category 查询技能"""
        registry = SkillRegistry(tmp_path)
        skills = [
            SkillMetadata(name="s1", description="1", path=tmp_path / "1.md", category="learning"),
            SkillMetadata(name="s2", description="2", path=tmp_path / "2.md", category="learning"),
            SkillMetadata(name="s3", description="3", path=tmp_path / "3.md", category="writing"),
        ]
        for skill in skills:
            registry.register(skill)

        learning_skills = registry.find_by_category("learning")
        assert len(learning_skills) == 2
        assert all(s.category == "learning" for s in learning_skills)

    def test_find_by_category_empty(self, tmp_path):
        """测试按 category 查询空结果"""
        registry = SkillRegistry(tmp_path)
        metadata = SkillMetadata(
            name="test",
            description="Test",
            path=tmp_path / "test.md",
            category="general"
        )
        registry.register(metadata)

        result = registry.find_by_category("nonexistent")
        assert result == []

    def test_list_all(self, tmp_path):
        """测试列出所有技能"""
        registry = SkillRegistry(tmp_path)
        skills = [
            SkillMetadata(name="a", description="A", path=tmp_path / "a.md"),
            SkillMetadata(name="b", description="B", path=tmp_path / "b.md"),
        ]
        for skill in skills:
            registry.register(skill)

        all_skills = registry.list_all()
        assert len(all_skills) == 2
        assert {s.name for s in all_skills} == {"a", "b"}

    def test_list_all_when_empty(self, tmp_path):
        """测试空注册表列出所有技能"""
        registry = SkillRegistry(tmp_path)
        assert registry.list_all() == []


class TestSkillRegistryDiscovery:
    """测试技能发现功能"""

    def test_discover_skills_from_directory(self, tmp_path):
        """测试扫描目录发现所有 SKILL.md"""
        # 创建测试目录结构
        (tmp_path / "grill-me").mkdir()
        (tmp_path / "grill-me" / "SKILL.md").write_text(
            "---\nname: grill-me\ndescription: Interview skill\n---",
            encoding="utf-8"
        )
        (tmp_path / "advance-task").mkdir()
        (tmp_path / "advance-task" / "SKILL.md").write_text(
            "---\nname: advance-task\ndescription: Task progress\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()

        skills = registry.list_all()
        assert len(skills) == 2
        skill_names = {s.name for s in skills}
        assert "grill-me" in skill_names
        assert "advance-task" in skill_names

    def test_discover_skips_directories_without_skill_md(self, tmp_path):
        """测试发现时跳过没有 SKILL.md 的目录"""
        (tmp_path / "valid-skill").mkdir()
        (tmp_path / "valid-skill" / "SKILL.md").write_text(
            "---\nname: valid-skill\ndescription: Valid\n---",
            encoding="utf-8"
        )
        (tmp_path / "invalid-dir").mkdir()
        (tmp_path / "invalid-dir" / "README.md").write_text("No SKILL.md")

        registry = SkillRegistry(tmp_path)
        registry.discover()

        skills = registry.list_all()
        assert len(skills) == 1
        assert skills[0].name == "valid-skill"

    def test_discover_handles_malformed_frontmatter(self, tmp_path):
        """测试发现时处理格式错误的 frontmatter"""
        (tmp_path / "good-skill").mkdir()
        (tmp_path / "good-skill" / "SKILL.md").write_text(
            "---\nname: good-skill\ndescription: Good\n---",
            encoding="utf-8"
        )
        (tmp_path / "bad-skill").mkdir()
        (tmp_path / "bad-skill" / "SKILL.md").write_text(
            "Invalid frontmatter without proper YAML",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        # 应该跳过格式错误的文件，不抛出异常
        registry.discover()

        skills = registry.list_all()
        assert len(skills) == 1
        assert skills[0].name == "good-skill"

    def test_discover_extracts_additional_fields(self, tmp_path):
        """测试发现时提取额外的 frontmatter 字段"""
        (tmp_path / "skill").mkdir()
        (tmp_path / "skill" / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\nversion: \"2.0\"\ncategory: learning\ntags:\n  - interview\n  - context\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()

        skill = registry.get("test-skill")
        assert skill.version == "2.0"
        assert skill.category == "learning"
        assert skill.tags == ["interview", "context"]
