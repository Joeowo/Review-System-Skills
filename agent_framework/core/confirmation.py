"""
C4: 用户确认机制

实现 Human-in-the-loop 确认节点（ADR-0005）：
- ConfirmationLevel: 确认级别枚举
- ConfirmationManager: 确认管理器
- should_confirm: 判断节点是否需要确认
- create_confirmation_node: 创建确认节点函数
"""

from enum import Enum
from typing import Callable, Dict, Any


# =============================================================================
# ConfirmationLevel 枚举
# =============================================================================

class ConfirmationLevel(Enum):
    """确认级别

    定义不同级别的确认策略：
    - MINIMAL: 仅关键节点确认
    - BALANCED: 默认级别，平衡自动化与控制
    - THOROUGH: 更多确认点，更细粒度控制
    """
    MINIMAL = "minimal"
    BALANCED = "balanced"
    THOROUGH = "thorough"


# =============================================================================
# 确认点配置
# =============================================================================

CONFIRMATION_NODES: Dict[ConfirmationLevel, list] = {
    ConfirmationLevel.MINIMAL: [
        "research_complete",
    ],
    ConfirmationLevel.BALANCED: [
        "research_complete",
        "loop_exit",
    ],
    ConfirmationLevel.THOROUGH: [
        "research_complete",
        "concepts_extracted",
        "session_initialized",
        "loop_exit",
    ]
}


# =============================================================================
# ConfirmationManager 类
# =============================================================================

class ConfirmationManager:
    """确认管理器

    根据确认级别管理哪些节点需要用户确认。

    Attributes:
        level: 当前确认级别
    """

    def __init__(self, level: ConfirmationLevel = ConfirmationLevel.BALANCED):
        """初始化确认管理器

        Args:
            level: 确认级别，默认 BALANCED
        """
        self.level = level
        self._confirmation_nodes = CONFIRMATION_NODES[level]

    def should_confirm(self, node_name: str) -> bool:
        """判断指定节点是否需要确认

        Args:
            node_name: 节点名称

        Returns:
            是否需要确认
        """
        return node_name in self._confirmation_nodes

    def create_confirmation_node(self, next_node: str, prompt: str) -> Callable:
        """创建确认节点函数

        Args:
            next_node: 确认后跳转的节点
            prompt: 确认提示信息

        Returns:
            节点函数
        """
        def confirmation_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """确认节点

            暂停执行，等待用户确认。

            Args:
                state: 当前状态

            Returns:
                更新后的状态
            """
            return {
                "awaiting_confirmation": True,
                "confirmation_prompt": prompt,
                "next_node": next_node,
            }

        return confirmation_node

    def get_confirmation_nodes(self) -> list:
        """获取当前级别的所有确认节点

        Returns:
            确认节点名称列表
        """
        return self._confirmation_nodes.copy()

    def set_level(self, level: ConfirmationLevel) -> None:
        """设置确认级别

        Args:
            level: 新的确认级别
        """
        self.level = level
        self._confirmation_nodes = CONFIRMATION_NODES[level]
