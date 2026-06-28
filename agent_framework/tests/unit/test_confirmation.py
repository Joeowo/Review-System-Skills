"""
C4: 用户确认机制 - 单元测试

测试覆盖：
- ConfirmationLevel 枚举
- ConfirmationManager 类
- should_confirm 判断逻辑
- create_confirmation_node 创建
"""

import pytest
from enum import Enum
from agent_framework.core.confirmation import (
    ConfirmationLevel,
    ConfirmationManager,
    CONFIRMATION_NODES,
)


# =============================================================================
# 测试组 1: ConfirmationLevel 枚举
# =============================================================================

class TestConfirmationLevel:
    """测试 ConfirmationLevel 枚举"""

    def test_confirmation_level_exists(self):
        """ConfirmationLevel 枚举存在"""
        assert ConfirmationLevel is not None
        assert issubclass(ConfirmationLevel, Enum)

    def test_confirmation_level_has_minimal(self):
        """ConfirmationLevel 有 MINIMAL 级别"""
        assert hasattr(ConfirmationLevel, "MINIMAL")
        assert ConfirmationLevel.MINIMAL.value == "minimal"

    def test_confirmation_level_has_balanced(self):
        """ConfirmationLevel 有 BALANCED 级别"""
        assert hasattr(ConfirmationLevel, "BALANCED")
        assert ConfirmationLevel.BALANCED.value == "balanced"

    def test_confirmation_level_has_thorough(self):
        """ConfirmationLevel 有 THOROUGH 级别"""
        assert hasattr(ConfirmationLevel, "THOROUGH")
        assert ConfirmationLevel.THOROUGH.value == "thorough"


# =============================================================================
# 测试组 2: CONFIRMATION_NODES 配置
# =============================================================================

class TestConfirmationNodesConfig:
    """测试 CONFIRMATION_NODES 配置"""

    def test_confirmation_nodes_exists(self):
        """CONFIRMATION_NODES 配置存在"""
        assert CONFIRMATION_NODES is not None
        assert isinstance(CONFIRMATION_NODES, dict)

    def test_confirmation_nodes_has_minimal_config(self):
        """CONFIRMATION_NODES 有 MINIMAL 配置"""
        assert ConfirmationLevel.MINIMAL in CONFIRMATION_NODES
        assert isinstance(CONFIRMATION_NODES[ConfirmationLevel.MINIMAL], list)

    def test_confirmation_nodes_has_balanced_config(self):
        """CONFIRMATION_NODES 有 BALANCED 配置"""
        assert ConfirmationLevel.BALANCED in CONFIRMATION_NODES
        assert isinstance(CONFIRMATION_NODES[ConfirmationLevel.BALANCED], list)

    def test_confirmation_nodes_has_thorough_config(self):
        """CONFIRMATION_NODES 有 THOROUGH 配置"""
        assert ConfirmationLevel.THOROUGH in CONFIRMATION_NODES
        assert isinstance(CONFIRMATION_NODES[ConfirmationLevel.THOROUGH], list)

    def test_balanced_includes_research_complete(self):
        """BALANCED 级别包含 research_complete 节点"""
        nodes = CONFIRMATION_NODES[ConfirmationLevel.BALANCED]
        assert "research_complete" in nodes

    def test_thorough_has_more_nodes_than_balanced(self):
        """THOROUGH 级别有比 BALANCED 更多确认点"""
        thorough_nodes = CONFIRMATION_NODES[ConfirmationLevel.THOROUGH]
        balanced_nodes = CONFIRMATION_NODES[ConfirmationLevel.BALANCED]
        assert len(thorough_nodes) > len(balanced_nodes)


# =============================================================================
# 测试组 3: ConfirmationManager 初始化
# =============================================================================

class TestConfirmationManagerInit:
    """测试 ConfirmationManager 初始化"""

    def test_confirmation_manager_can_be_initialized(self):
        """ConfirmationManager 可以正确初始化"""
        manager = ConfirmationManager()
        assert manager is not None

    def test_confirmation_manager_with_default_level(self):
        """ConfirmationManager 默认使用 BALANCED 级别"""
        manager = ConfirmationManager()
        assert manager.level == ConfirmationLevel.BALANCED

    def test_confirmation_manager_with_minimal_level(self):
        """ConfirmationManager 可以设置为 MINIMAL 级别"""
        manager = ConfirmationManager(level=ConfirmationLevel.MINIMAL)
        assert manager.level == ConfirmationLevel.MINIMAL

    def test_confirmation_manager_with_thorough_level(self):
        """ConfirmationManager 可以设置为 THOROUGH 级别"""
        manager = ConfirmationManager(level=ConfirmationLevel.THOROUGH)
        assert manager.level == ConfirmationLevel.THOROUGH


# =============================================================================
# 测试组 4: should_confirm 方法
# =============================================================================

class TestShouldConfirm:
    """测试 should_confirm 方法"""

    def test_should_confirm_exists(self):
        """should_confirm 方法存在"""
        manager = ConfirmationManager()
        assert hasattr(manager, "should_confirm")
        assert callable(manager.should_confirm)

    def test_should_confirm_returns_bool(self):
        """should_confirm 返回布尔值"""
        manager = ConfirmationManager()
        result = manager.should_confirm("test_node")
        assert isinstance(result, bool)

    def test_should_confirm_balanced_research_complete(self):
        """BALANCED 级别下 research_complete 需要确认"""
        manager = ConfirmationManager(level=ConfirmationLevel.BALANCED)
        assert manager.should_confirm("research_complete") is True

    def test_should_confirm_balanced_loop_exit(self):
        """BALANCED 级别下 loop_exit 需要确认"""
        manager = ConfirmationManager(level=ConfirmationLevel.BALANCED)
        assert manager.should_confirm("loop_exit") is True

    def test_should_confirm_minimal_fewer_confirmations(self):
        """MINIMAL 级别确认点较少"""
        manager = ConfirmationManager(level=ConfirmationLevel.MINIMAL)
        # MINIMAL 只确认关键节点
        assert manager.should_confirm("research_complete") is True

    def test_should_confirm_thorough_more_confirmations(self):
        """THOROUGH 级别确认更多节点"""
        manager = ConfirmationManager(level=ConfirmationLevel.THOROUGH)
        # THOROUGH 确认更多节点
        assert manager.should_confirm("concepts_extracted") is True

    def test_should_confirm_unknown_node(self):
        """未知节点不需要确认"""
        manager = ConfirmationManager(level=ConfirmationLevel.BALANCED)
        assert manager.should_confirm("unknown_node") is False


# =============================================================================
# 测试组 5: create_confirmation_node 方法
# =============================================================================

class TestCreateConfirmationNode:
    """测试 create_confirmation_node 方法"""

    def test_create_confirmation_node_exists(self):
        """create_confirmation_node 方法存在"""
        manager = ConfirmationManager()
        assert hasattr(manager, "create_confirmation_node")
        assert callable(manager.create_confirmation_node)

    def test_create_confirmation_node_returns_function(self):
        """create_confirmation_node 返回函数"""
        manager = ConfirmationManager()
        node_func = manager.create_confirmation_node("next_node", "确认提示")
        assert callable(node_func)

    def test_create_confirmation_node_with_next_node(self):
        """create_confirmation_node 正确设置 next_node"""
        manager = ConfirmationManager()
        node_func = manager.create_confirmation_node("next_step", "是否继续？")

        # 调用节点函数应返回包含 next_node 的结果
        result = node_func({})
        assert "next_node" in result or "awaiting_confirmation" in result


# =============================================================================
# 测试组 6: 确认点级别比较
# =============================================================================

class TestConfirmationLevelsComparison:
    """测试不同级别的确认行为"""

    def test_minimal_has_least_confirmations(self):
        """MINIMAL 级别确认点最少"""
        minimal = ConfirmationManager(level=ConfirmationLevel.MINIMAL)
        balanced = ConfirmationManager(level=ConfirmationLevel.BALANCED)
        thorough = ConfirmationManager(level=ConfirmationLevel.THOROUGH)

        # 同一个节点在不同级别可能有不同确认要求
        test_nodes = ["research_complete", "concepts_extracted", "loop_exit"]

        minimal_count = sum(1 for node in test_nodes if minimal.should_confirm(node))
        balanced_count = sum(1 for node in test_nodes if balanced.should_confirm(node))
        thorough_count = sum(1 for node in test_nodes if thorough.should_confirm(node))

        assert minimal_count <= balanced_count <= thorough_count

    def test_all_levels_confirm_critical_nodes(self):
        """所有级别都确认关键节点"""
        minimal = ConfirmationManager(level=ConfirmationLevel.MINIMAL)
        balanced = ConfirmationManager(level=ConfirmationLevel.BALANCED)
        thorough = ConfirmationManager(level=ConfirmationLevel.THOROUGH)

        # research_complete 应该是所有级别都确认的
        assert minimal.should_confirm("research_complete")
        assert balanced.should_confirm("research_complete")
        assert thorough.should_confirm("research_complete")
