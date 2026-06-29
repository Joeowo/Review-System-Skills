"""
S1-T5: Middleware 路由功能单元测试

测试 Middleware 的核心路由功能：根据状态路由到合适的 Skill
"""
import pytest
import tempfile
from pathlib import Path
from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.middleware import SkillMiddleware, RouteNotFoundError


class TestMiddlewareRouteByTaskType:
    """测试按 task_type 路由"""

    def test_route_by_task_type_grilling(self, tmp_path):
        """测试路由 grilling 任务类型"""
        # 创建测试技能
        (tmp_path / "grill-me").mkdir()
        (tmp_path / "grill-me" / "SKILL.md").write_text(
            "---\nname: grill-me\ndescription: Interview skill\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        state = {"task_type": "grilling"}
        skill_name = middleware.route(state)
        assert skill_name == "grill-me"

    def test_route_by_task_type_advance_task(self, tmp_path):
        """测试路由 advance-task 任务类型"""
        (tmp_path / "advance-task").mkdir()
        (tmp_path / "advance-task" / "SKILL.md").write_text(
            "---\nname: advance-task\ndescription: Task progress\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        state = {"task_type": "advance"}
        skill_name = middleware.route(state)
        assert skill_name == "advance-task"


class TestMiddlewareRouteByUserQuery:
    """测试按 user_query 路由"""

    def test_route_by_keyword_grill(self, tmp_path):
        """测试按关键词 'grill' 路由"""
        (tmp_path / "grill-me").mkdir()
        (tmp_path / "grill-me" / "SKILL.md").write_text(
            "---\nname: grill-me\ndescription: Interview skill\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        state = {"user_query": "Can you grill me on this plan?"}
        skill_name = middleware.route(state)
        assert skill_name == "grill-me"

    def test_route_by_keyword_advance(self, tmp_path):
        """测试按关键词 'advance' 路由"""
        (tmp_path / "advance-task").mkdir()
        (tmp_path / "advance-task" / "SKILL.md").write_text(
            "---\nname: advance-task\ndescription: Task progress\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        state = {"user_query": "I want to advance to the next task"}
        skill_name = middleware.route(state)
        assert skill_name == "advance-task"


class TestMiddlewareRouteErrors:
    """测试路由错误处理"""

    def test_route_with_no_match_raises_error(self, tmp_path):
        """测试无匹配路由时抛出异常"""
        registry = SkillRegistry(tmp_path)
        middleware = SkillMiddleware(registry)

        state = {"task_type": "nonexistent"}

        with pytest.raises(RouteNotFoundError, match="No route found"):
            middleware.route(state)

    def test_route_with_empty_state_raises_error(self, tmp_path):
        """测试空状态时抛出异常"""
        registry = SkillRegistry(tmp_path)
        middleware = SkillMiddleware(registry)

        state = {}

        with pytest.raises(RouteNotFoundError, match="No route found"):
            middleware.route(state)


class TestMiddlewareDefaultRoute:
    """测试默认路由策略"""

    def test_default_route_fallback(self, tmp_path):
        """测试默认路由回退"""
        (tmp_path / "default-skill").mkdir()
        (tmp_path / "default-skill" / "SKILL.md").write_text(
            "---\nname: default-skill\ndescription: Default\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry, default_route="default-skill")

        state = {"task_type": "unknown"}
        skill_name = middleware.route(state)
        assert skill_name == "default-skill"


class TestMiddlewareRouteMatching:
    """测试路由匹配逻辑"""

    def test_task_type_priority_over_user_query(self, tmp_path):
        """测试 task_type 优先级高于 user_query"""
        (tmp_path / "grill-me").mkdir()
        (tmp_path / "grill-me" / "SKILL.md").write_text(
            "---\nname: grill-me\ndescription: Interview\n---",
            encoding="utf-8"
        )
        (tmp_path / "grill-you").mkdir()
        (tmp_path / "grill-you" / "SKILL.md").write_text(
            "---\nname: grill-you\ndescription: Q&A\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        # task_type 应该优先
        state = {"task_type": "grilling", "user_query": "grill you"}
        skill_name = middleware.route(state)
        assert skill_name == "grill-me"

    def test_fuzzy_matching(self, tmp_path):
        """测试模糊匹配"""
        (tmp_path / "review-session").mkdir()
        (tmp_path / "review-session" / "SKILL.md").write_text(
            "---\nname: review-session\ndescription: Review\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        state = {"user_query": "I need a review of my code"}
        skill_name = middleware.route(state)
        assert skill_name == "review-session"


class TestMiddlewareCustomRouteMapping:
    """测试自定义路由映射"""

    def test_custom_route_mapping(self, tmp_path):
        """测试自定义路由映射"""
        (tmp_path / "test-skill").mkdir()
        (tmp_path / "test-skill" / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        # 添加自定义路由
        middleware.add_route("custom_task", "test-skill")

        state = {"task_type": "custom_task"}
        skill_name = middleware.route(state)
        assert skill_name == "test-skill"

    def test_custom_route_with_keyword(self, tmp_path):
        """测试自定义关键词路由"""
        (tmp_path / "help-skill").mkdir()
        (tmp_path / "help-skill" / "SKILL.md").write_text(
            "---\nname: help-skill\ndescription: Help\n---",
            encoding="utf-8"
        )

        registry = SkillRegistry(tmp_path)
        registry.discover()
        middleware = SkillMiddleware(registry)

        middleware.add_route("help", "help-skill")

        state = {"user_query": "I need help with this"}
        skill_name = middleware.route(state)
        assert skill_name == "help-skill"
