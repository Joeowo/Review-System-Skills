"""
题目生成模块 - 简化版
支持dict和KnowledgePoint对象
"""
import re
from typing import List, Union, Dict
from models import Question, QuestionType, KnowledgePoint, KnowledgeType


class QuestionGenerator:
    """题目生成器"""

    def __init__(self):
        """初始化生成器"""

    def generate_from_knowledge(self, knowledge: Union[KnowledgePoint, Dict]) -> List[Question]:
        """从单个知识点生成题目"""
        questions = []

        # 处理dict对象
        if isinstance(knowledge, dict):
            point_type = self._map_type(knowledge.get("type", "概念"))
            title = knowledge.get("title", "")
            content = knowledge.get("content", "")
            point_id = knowledge.get("id", "")
            session_id = knowledge.get("session_id", "")
            difficulty = knowledge.get("difficulty", 0.5)
            category = knowledge.get("category", "")
        else:
            point_type = knowledge.type
            title = knowledge.title
            content = knowledge.content
            point_id = knowledge.id
            session_id = knowledge.session_id
            difficulty = knowledge.difficulty
            category = knowledge.category

        # 提取核心术语
        term = self._extract_term(title)
        if not term or len(term) < 2:
            return questions

        # 只为概念类生成定义题
        if point_type == KnowledgeType.CONCEPT:
            question = self._create_definition_question(
                term, content, point_id, session_id, category, difficulty
            )
            if question:
                questions.append(question)

        return questions

    def generate_batch(self, knowledge_list: List) -> List[Question]:
        """批量生成题目"""
        questions = []
        for knowledge in knowledge_list:
            questions.extend(self.generate_from_knowledge(knowledge))
        return questions

    def _map_type(self, type_str: str) -> KnowledgeType:
        """映射类型字符串到KnowledgeType枚举"""
        type_map = {
            "概念": KnowledgeType.CONCEPT,
            "分类": KnowledgeType.CLASSIFICATION,
            "关系": KnowledgeType.RELATIONSHIP,
            "流程": KnowledgeType.PROCESS,
        }
        return type_map.get(type_str, KnowledgeType.CONCEPT)

    def _extract_term(self, title: str) -> str:
        """提取核心术语"""
        title = title.strip()

        # 清理括号内容
        for bracket in ["(", "（"]:
            if bracket in title:
                title = title.split(bracket)[0].strip()

        # 验证术语质量
        if 2 <= len(title) <= 15:
            # 过滤无效术语
            invalid = ["其他", "包括", "具有", "表示", "分为", "因素", "原理", "包括", "定义"]
            if title not in invalid and not title.endswith(("等", "等")):
                return title

        return ""

    def _create_definition_question(
        self, term: str, content: str, point_id: str, session_id: str, category: str, difficulty: float
    ) -> Question:
        """创建定义题"""
        # 提取答案
        answer = self._extract_answer(content)
        if not answer or len(answer) < 10:
            return None

        return Question(
            knowledge_point_id=point_id,
            session_id=session_id,
            type=QuestionType.DEFINITION,
            content=f"什么是{term}？",
            correct_answer=answer,
            explanation=content,
            difficulty=difficulty,
            tags=[category],
        )

    def _extract_answer(self, content: str) -> str:
        """提取答案"""
        # 查找"是指"后的定义
        match = re.search(r'是指(.{10,200})', content)
        if match:
            answer = match.group(1).strip()
            # 清理标点
            answer = re.sub(r'[，；：].*$', '', answer)
            return answer

        # 查找"："后的内容
        match = re.search(r'：(.{10,200})', content)
        if match:
            return match.group(1).strip()

        # 查找"is"后的内容
        match = re.search(r' is (.{10,200})', content)
        if match:
            return match.group(1).strip()

        return None
