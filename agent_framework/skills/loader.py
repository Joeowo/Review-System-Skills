"""
S1-T3: Skill Loader

实现技能加载器，支持按需加载、卸载、热重载技能。
"""

from pathlib import Path
from typing import Dict, Optional, Set
from loguru import logger

from agent_framework.skills.registry import SkillRegistry


class SkillLoadError(Exception):
    """技能加载错误"""

    pass


class SkillLoader:
    """技能加载器

    管理技能的加载、卸载和重载，提供缓存机制。
    """

    def __init__(self, registry: SkillRegistry) -> None:
        """初始化技能加载器

        Args:
            registry: 技能注册表
        """
        self._registry = registry
        self._loaded: Dict[str, str] = {}  # skill_name -> content
        logger.info("SkillLoader initialized")

    def load_skill(self, name: str) -> str:
        """加载技能内容

        如果技能已加载，从缓存返回；否则从文件读取。

        Args:
            name: 技能名称

        Returns:
            技能的 SKILL.md 内容

        Raises:
            SkillLoadError: 技能不存在或加载失败时
        """
        # 检查缓存
        if name in self._loaded:
            logger.debug("Skill loaded from cache", name=name)
            return self._loaded[name]

        # 从注册表获取技能元数据
        try:
            metadata = self._registry.get(name)
        except Exception as e:
            raise SkillLoadError(f"Skill '{name}' not found in registry") from e

        # 读取文件
        try:
            content = metadata.path.read_text(encoding="utf-8")
        except Exception as e:
            raise SkillLoadError(f"Failed to read skill file for '{name}': {e}") from e

        # 缓存内容
        self._loaded[name] = content
        logger.info("Skill loaded", name=name)
        return content

    def unload_skill(self, name: str) -> None:
        """卸载技能

        从缓存中移除技能内容。

        Args:
            name: 技能名称
        """
        if name in self._loaded:
            del self._loaded[name]
            logger.info("Skill unloaded", name=name)

    def reload_skill(self, name: str) -> None:
        """重载技能

        先卸载再加载，从文件重新读取内容。

        Args:
            name: 技能名称

        Raises:
            SkillLoadError: 技能不存在或加载失败时
        """
        logger.info("Reloading skill", name=name)
        self.unload_skill(name)
        self.load_skill(name)

    def is_loaded(self, name: str) -> bool:
        """检查技能是否已加载

        Args:
            name: 技能名称

        Returns:
            如果技能已加载返回 True
        """
        return name in self._loaded

    def get_loaded_skills(self) -> Set[str]:
        """获取所有已加载的技能名称

        Returns:
            已加载技能的名称集合
        """
        return set(self._loaded.keys())

    def clear_cache(self) -> None:
        """清除所有缓存"""
        self._loaded.clear()
        logger.info("Skill loader cache cleared")
