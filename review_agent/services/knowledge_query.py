"""
知识点快速查询系统
用于咨询模块的快速检索
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import jieba
from collections import defaultdict


class KnowledgeQuerySystem:
    """知识点快速查询系统"""

    def __init__(self, knowledge_base_dir: Optional[Path] = None):
        """
        初始化查询系统

        Args:
            knowledge_base_dir: 知识库目录
        """
        if knowledge_base_dir is None:
            from config import KNOWLEDGE_BASE_DIR
            knowledge_base_dir = KNOWLEDGE_BASE_DIR

        self.kb_dir = Path(knowledge_base_dir)
        self._knowledge_index = {}  # ID -> 知识点
        self._keyword_index = defaultdict(set)  # 关键词 -> 知识点ID集合
        self._title_index = defaultdict(set)  # 标题词 -> 知识点ID集合
        self._category_index = defaultdict(set)  # 类别 -> 知识点ID集合

        self._load_all()

    def _load_all(self):
        """加载所有知识点并构建索引"""
        for json_file in self.kb_dir.glob("*.json"):
            data = json.loads(json_file.read_text(encoding="utf-8"))
            session_id = json_file.stem

            for point in data:
                point_id = point["id"]
                self._knowledge_index[point_id] = point

                # 索引关键词
                for kw in point.get("keywords", []):
                    self._keyword_index[kw].add(point_id)

                # 索引标题词
                title_words = list(jieba.cut(point["title"]))
                for word in title_words:
                    if len(word) >= 2:
                        self._title_index[word].add(point_id)

                # 索引类别
                category = point.get("category", "")
                if category:
                    self._category_index[category].add(point_id)

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索知识点

        Args:
            query: 搜索查询
            limit: 返回数量限制

        Returns:
            匹配的知识点列表，按相关性排序
        """
        if not query or len(query) < 2:
            return []

        query_lower = query.lower()
        query_words = list(jieba.cut(query))

        # 收集匹配的知识点ID
        matched_ids = {}
        max_score = 0

        # 1. 精确关键词匹配
        for kw in self._keyword_index:
            if kw in query or kw in query_lower:
                for point_id in self._keyword_index[kw]:
                    matched_ids[point_id] = matched_ids.get(point_id, 0) + 10

        # 2. 标题匹配
        for word in query_words:
            if len(word) >= 2:
                for point_id in self._title_index[word]:
                    matched_ids[point_id] = matched_ids.get(point_id, 0) + 5

        # 3. 类别匹配
        for category, point_ids in self._category_index.items():
            if query in category:
                for point_id in point_ids:
                    matched_ids[point_id] = matched_ids.get(point_id, 0) + 3

        # 4. 内容包含匹配
        for point_id, point in self._knowledge_index.items():
            content = point.get("content", "")
            if query in content or query_lower in content.lower():
                matched_ids[point_id] = matched_ids.get(point_id, 0) + 2

        # 排序并返回
        sorted_ids = sorted(matched_ids.items(), key=lambda x: x[1], reverse=True)[:limit]

        results = []
        for point_id, score in sorted_ids:
            point = self._knowledge_index[point_id]
            results.append({
                "id": point_id,
                "title": point["title"],
                "type": point["type"],
                "category": point["category"],
                "content": point["content"][:200] + "..." if len(point["content"]) > 200 else point["content"],
                "score": score,
                "session_id": point["session_id"],
            })

        return results

    def get_by_id(self, point_id: str) -> Optional[Dict]:
        """
        根据ID获取知识点

        Args:
            point_id: 知识点ID

        Returns:
            知识点字典或None
        """
        return self._knowledge_index.get(point_id)

    def get_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """
        根据类别获取知识点

        Args:
            category: 类别名称
            limit: 返回数量限制

        Returns:
            知识点列表
        """
        point_ids = list(self._category_index.get(category, []))[:limit]
        return [self._knowledge_index[pid] for pid in point_ids if pid in self._knowledge_index]

    def get_by_session(self, session_id: str, limit: int = 50) -> List[Dict]:
        """
        根据会话获取知识点

        Args:
            session_id: 会话ID
            limit: 返回数量限制

        Returns:
            知识点列表
        """
        results = []
        for point in self._knowledge_index.values():
            if point["session_id"] == session_id:
                results.append({
                    "id": point["id"],
                    "title": point["title"],
                    "type": point["type"],
                    "category": point["category"],
                    "content": point["content"][:200] + "..." if len(point["content"]) > 200 else point["content"],
                })
                if len(results) >= limit:
                    break
        return results

    def get_categories(self) -> List[str]:
        """获取所有类别"""
        return list(self._category_index.keys())

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "total_points": len(self._knowledge_index),
            "total_keywords": len(self._keyword_index),
            "total_categories": len(self._category_index),
            "sessions": len(set(p["session_id"] for p in self._knowledge_index.values())),
        }


# 测试代码
if __name__ == "__main__":
    from config import KNOWLEDGE_BASE_DIR

    qs = KnowledgeQuerySystem()

    print("=== 知识点查询系统测试 ===\n")
    print(f"统计信息: {qs.get_stats()}\n")

    # 测试搜索
    queries = ["机会成本", "需求弹性", "市场", "生产"]
    for q in queries:
        print(f"搜索: {q}")
        results = qs.search(q, limit=3)
        for r in results:
            print(f"  - [{r['type']}] {r['title']} (分数: {r['score']})")
        print()
