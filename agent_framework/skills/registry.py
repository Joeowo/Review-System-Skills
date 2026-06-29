"""
S1-T2: Skill Registry

实现技能注册表，负责发现、注册、查询技能。
"""

from pathlib import Path
from typing import Dict, List, Optional
import yaml
from loguru import logger

from agent_framework.skills.models.metadata import SkillMetadata


class DuplicateSkillError(Exception):
    """重复注册技能错误"""

    pass


class SkillNotFoundError(Exception):
    """技能不存在错误"""

    pass


class SkillRegistry:
    """技能注册表

    管理所有技能的元数据，提供注册、查询、发现功能。
    """

    def __init__(self, skills_dir: Path) -> None:
        """初始化技能注册表

        Args:
            skills_dir: 技能目录路径，包含各个技能的子目录
        """
        self.skills_dir = Path(skills_dir)
        self._skills: Dict[str, SkillMetadata] = {}
        logger.info("SkillRegistry initialized", skills_dir=str(self.skills_dir))

    def register(self, metadata: SkillMetadata) -> None:
        """注册技能到注册表

        Args:
            metadata: 技能元数据

        Raises:
            DuplicateSkillError: 技能已存在时
        """
        if metadata.name in self._skills:
            raise DuplicateSkillError(f"Skill '{metadata.name}' already registered")
        self._skills[metadata.name] = metadata
        logger.info("Skill registered", name=metadata.name)

    def get(self, name: str) -> SkillMetadata:
        """按 name 查询技能

        Args:
            name: 技能名称

        Returns:
            技能元数据

        Raises:
            SkillNotFoundError: 技能不存在时
        """
        if name not in self._skills:
            raise SkillNotFoundError(f"Skill '{name}' not found in registry")
        return self._skills[name]

    def find_by_category(self, category: str) -> List[SkillMetadata]:
        """按 category 查询技能

        Args:
            category: 技能分类

        Returns:
            该分类下的所有技能，可能为空列表
        """
        return [skill for skill in self._skills.values() if skill.category == category]

    def list_all(self) -> List[SkillMetadata]:
        """列出所有已注册技能

        Returns:
            所有技能元数据列表，可能为空列表
        """
        return list(self._skills.values())

    def discover(self) -> None:
        """扫描 skills 目录发现所有技能

        遍历 skills_dir 下的所有子目录，查找 SKILL.md 文件，
        解析其 YAML frontmatter 并注册到注册表。

        跳过没有 SKILL.md 的目录和 frontmatter 格式错误的文件。
        """
        if not self.skills_dir.exists():
            logger.warning("Skills directory does not exist", path=str(self.skills_dir))
            return

        discovered = 0
        skipped = 0

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md_path = skill_dir / "SKILL.md"
            if not skill_md_path.exists():
                skipped += 1
                continue

            try:
                metadata = self._parse_skill_md(skill_md_path)
                if metadata:
                    try:
                        self.register(metadata)
                        discovered += 1
                    except DuplicateSkillError:
                        logger.warning("Skill already registered, skipping", name=metadata.name)
            except Exception as e:
                logger.warning(
                    "Failed to parse SKILL.md",
                    path=str(skill_md_path),
                    error=str(e)
                )
                skipped += 1

        logger.info(
            "Discovery complete",
            discovered=discovered,
            skipped=skipped
        )

    def _parse_skill_md(self, skill_md_path: Path) -> Optional[SkillMetadata]:
        """解析 SKILL.md 文件提取元数据

        Args:
            skill_md_path: SKILL.md 文件路径

        Returns:
            解析出的技能元数据，解析失败返回 None
        """
        content = skill_md_path.read_text(encoding="utf-8")

        # 提取 YAML frontmatter (--- 之间的内容)
        if not content.startswith("---"):
            return None

        end_marker = content.find("\n---", 3)
        if end_marker == -1:
            return None

        frontmatter = content[3:end_marker]

        try:
            data = yaml.safe_load(frontmatter)
            if not data or not isinstance(data, dict):
                return None

            name = data.get("name")
            description = data.get("description")

            if not name or not description:
                logger.warning("SKILL.md missing required fields", path=str(skill_md_path))
                return None

            return SkillMetadata(
                name=name,
                description=description,
                path=skill_md_path,
                version=data.get("version", "1.0"),
                category=data.get("category", "general"),
                tags=data.get("tags", [])
            )
        except yaml.YAMLError as e:
            logger.warning("Failed to parse YAML frontmatter", path=str(skill_md_path), error=str(e))
            return None
