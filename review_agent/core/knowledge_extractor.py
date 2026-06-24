"""
基于Agent的知识点提取模块
使用LLM智能提取和结构化知识点
"""
import json
import re
import asyncio
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from models import KnowledgePoint, KnowledgeType
from services.llm_service import DeepSeekService
from config import REVIEW_SOURCES


class AgentKnowledgeExtractor:
    """基于Agent的知识点提取器"""

    def __init__(self):
        """初始化提取器"""
        self.llm_service = DeepSeekService()

    def extract_from_session(self, session_path: Path) -> List[KnowledgePoint]:
        """从单个会话目录提取知识点"""
        points = []
        sources_dir = session_path / "sources"

        if not sources_dir.exists():
            return points

        session_id = session_path.name

        # 处理每个文件
        for md_file in sorted(sources_dir.glob("*.md")):
            print(f"  处理文件: {md_file.name}")
            file_points = self._extract_from_file(md_file, session_id)
            points.extend(file_points)
            print(f"    提取 {len(file_points)} 个知识点")

        return points

    def extract_all(self) -> Dict[str, List[KnowledgePoint]]:
        """从所有会话目录提取知识点"""
        results = {}

        for session_path in REVIEW_SOURCES:
            if not session_path.exists():
                continue

            session_id = session_path.name
            print(f"正在处理: {session_id}")

            points = self.extract_from_session(session_path)
            results[session_id] = points

            print(f"  ✓ 共提取 {len(points)} 个知识点\n")

        return results

    def _extract_from_file(self, md_file: Path, session_id: str) -> List[KnowledgePoint]:
        """从单个文件提取知识点"""
        content = md_file.read_text(encoding="utf-8")

        # 将大文件分段处理
        chunks = self._split_content(content)

        all_points = []
        for chunk in chunks:
            points = self._extract_from_chunk(chunk, md_file, session_id)
            all_points.extend(points)

        return all_points

    def _split_content(self, content: str, max_length: int = 1500) -> List[str]:
        """将内容分成适合LLM处理的块"""
        chunks = []
        current_chunk = ""
        current_section = ""

        lines = content.split("\n")

        for line in lines:
            stripped = line.strip()

            # 检测章节标题 - 新章节开始
            if re.match(r'^第\d+章[：:]', stripped):
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk)
                # 开始新块
                current_chunk = stripped + "\n"
                current_section = stripped
                continue

            # 检测大知识点标题 - 可能需要分块
            if re.match(r'^\d+．\s*[^\d]', stripped) and len(current_chunk) > max_length // 2:
                # 当当前块已经有一定内容时，先保存
                chunks.append(current_chunk)
                # 开始新块
                current_chunk = stripped + "\n"
                continue

            # 添加到当前块
            current_chunk += line + "\n"

            # 如果当前块超过最大长度，先保存
            if len(current_chunk) >= max_length:
                chunks.append(current_chunk)
                current_chunk = ""

        # 保存剩余内容
        if current_chunk:
            chunks.append(current_chunk)

        # 过滤掉太短的块
        return [c for c in chunks if len(c.strip()) > 100]

    def _extract_from_chunk(self, chunk: str, md_file: Path, session_id: str) -> List[KnowledgePoint]:
        """从内容块中提取知识点"""
        prompt = f"""请从以下学习材料中提取知识点。只提取概念性、定义性的知识点，不要提取计算题、图表题或纯公式。

学习材料：
```
{chunk[:2000]}
```

请返回JSON格式，必须严格按照以下结构：
{{
    "knowledge_points": [
        {{
            "title": "知识点标题（2-15字）",
            "type": "概念",
            "content": "知识点的详细内容",
            "keywords": ["关键词1", "关键词2", "关键词3"]
        }}
    ]
}}

要求：
1. title必须是简洁的术语或概念名称
2. type只能是：概念、分类、关系、流程 之一
3. content要包含完整的定义或说明
4. keywords提取3-5个最重要的关键词
5. 不要提取计算公式、图表说明
6. 每个知识点要有实际的内容价值

只返回JSON，不要有其他内容。"""

        try:
            response = asyncio.run(self.llm_service.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            ))

            result_text = response["choices"][0]["message"]["content"]
            result = json.loads(result_text)

            points = []
            for item in result.get("knowledge_points", []):
                point = KnowledgePoint(
                    source_file=str(md_file),
                    session_id=session_id,
                    type=self._map_type(item.get("type", "概念")),
                    category="",  # 后续可以填充
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    keywords=item.get("keywords", []),
                    difficulty=0.5,
                )

                # 验证有效性
                if self._is_valid_point(point):
                    points.append(point)

            return points

        except Exception as e:
            print(f"    提取失败: {e}")
            return []

    def _map_type(self, type_str: str) -> KnowledgeType:
        """映射类型"""
        type_map = {
            "概念": KnowledgeType.CONCEPT,
            "分类": KnowledgeType.CLASSIFICATION,
            "关系": KnowledgeType.RELATIONSHIP,
            "流程": KnowledgeType.PROCESS,
        }
        return type_map.get(type_str, KnowledgeType.CONCEPT)

    def _is_valid_point(self, point: KnowledgePoint) -> bool:
        """验证知识点是否有效"""
        # 标题长度检查
        if len(point.title) < 2 or len(point.title) > 30:
            return False

        # 内容长度检查
        if len(point.content) < 20 or len(point.content) > 500:
            return False

        # 无效标题检查
        invalid_prefixes = ["例", "如图", "说明", "其他", "包括"]
        if any(point.title.startswith(p) for p in invalid_prefixes):
            return False

        # 无效内容检查
        if "计算" in point.content[:50] and "公式" in point.content[:50]:
            return False

        return True
