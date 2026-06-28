"""
知识点数据持久化
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from models import KnowledgePoint
from config import KNOWLEDGE_BASE_DIR, REVIEW_SOURCES


class KnowledgeRepository:
    """知识点存储库"""

    def __init__(self):
        """初始化存储库"""
        self._cache: Dict[str, List[KnowledgePoint]] = {}
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_id: str, points: List[KnowledgePoint]) -> None:
        """
        保存单个会话的知识点

        Args:
            session_id: 会话ID
            points: 知识点列表
        """
        output_file = KNOWLEDGE_BASE_DIR / f"{session_id}.json"
        data = [p.to_dict() for p in points]
        output_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        self._cache[session_id] = points

    def load_session(self, session_id: str) -> List[KnowledgePoint]:
        """
        加载单个会话的知识点

        Args:
            session_id: 会话ID

        Returns:
            知识点列表
        """
        # 先检查缓存
        if session_id in self._cache:
            return self._cache[session_id]

        output_file = KNOWLEDGE_BASE_DIR / f"{session_id}.json"
        if not output_file.exists():
            return []

        data = json.loads(output_file.read_text(encoding="utf-8"))
        points = [KnowledgePoint.from_dict(d) for d in data]
        self._cache[session_id] = points
        return points

    def load_all(self) -> Dict[str, List[KnowledgePoint]]:
        """
        加载所有会话的知识点

        Returns:
            会话ID -> 知识点列表的字典
        """
        results = {}
        for session_file in KNOWLEDGE_BASE_DIR.glob("*.json"):
            session_id = session_file.stem
            results[session_id] = self.load_session(session_id)
        return results

    def get_point_by_id(self, point_id: str) -> Optional[KnowledgePoint]:
        """
        根据ID获取知识点

        Args:
            point_id: 知识点ID

        Returns:
            知识点对象或None
        """
        all_points = self.load_all()
        for points in all_points.values():
            for point in points:
                if point.id == point_id:
                    return point
        return None

    def search(self, keyword: str, session_id: Optional[str] = None) -> List[KnowledgePoint]:
        """
        搜索知识点

        Args:
            keyword: 搜索关键词
            session_id: 可选的会话ID限制

        Returns:
            匹配的知识点列表
        """
        results = []

        sessions = [session_id] if session_id else self.load_all().keys()

        for sid in sessions:
            points = self.load_session(sid)
            for point in points:
                # 搜索标题、内容和关键词
                if (keyword.lower() in point.title.lower() or
                    keyword.lower() in point.content.lower() or
                    any(keyword.lower() in kw.lower() for kw in point.keywords)):
                    results.append(point)

        return results

    def get_by_type(self, knowledge_type: str) -> List[KnowledgePoint]:
        """
        根据类型获取知识点

        Args:
            knowledge_type: 知识点类型

        Returns:
            匹配的知识点列表
        """
        results = []
        for points in self.load_all().values():
            for point in points:
                if point.type.value == knowledge_type:
                    results.append(point)
        return results

    def get_stats(self) -> Dict:
        """
        获取知识点统计信息

        Returns:
            统计信息字典
        """
        all_points = self.load_all()
        total_points = sum(len(points) for points in all_points.values())

        # 按类型统计
        type_counts = {}
        for points in all_points.values():
            for point in points:
                type_name = point.type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # 按会话统计
        session_counts = {sid: len(points) for sid, points in all_points.items()}

        return {
            "total_points": total_points,
            "total_sessions": len(all_points),
            "by_type": type_counts,
            "by_session": session_counts,
            "last_updated": datetime.now().isoformat()
        }

    def is_extracted(self, session_id: str) -> bool:
        """
        检查会话是否已提取

        Args:
            session_id: 会话ID

        Returns:
            是否已提取
        """
        output_file = KNOWLEDGE_BASE_DIR / f"{session_id}.json"
        return output_file.exists()
