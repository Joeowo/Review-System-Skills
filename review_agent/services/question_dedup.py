"""
题目去重服务
基于内容相似度和关键词匹配进行题目去重
"""
import re
from typing import List, Set
from difflib import SequenceMatcher
from models import Question


class QuestionDeduplicator:
    """题目去重器"""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        初始化去重器

        Args:
            similarity_threshold: 相似度阈值，超过此值认为是重复题目
        """
        self.similarity_threshold = similarity_threshold
        self.existing_questions: List[Question] = []

    def set_existing(self, questions: List[Question]):
        """设置已存在的题目集合"""
        self.existing_questions = questions

    def deduplicate(self, new_questions: List[Question]) -> List[Question]:
        """
        从新题目中去除与已有题目重复的题目

        Args:
            new_questions: 新提取的题目列表

        Returns:
            去重后的题目列表
        """
        unique_questions = []

        for new_q in new_questions:
            is_duplicate = False

            # 检查是否与已有题目重复
            for existing_q in self.existing_questions:
                if self._are_similar(new_q, existing_q):
                    is_duplicate = True
                    break

            # 检查是否与新题目列表中的题目重复
            if not is_duplicate:
                for unique_q in unique_questions:
                    if self._are_similar(new_q, unique_q):
                        is_duplicate = True
                        break

            if not is_duplicate:
                unique_questions.append(new_q)

        return unique_questions

    def _are_similar(self, q1: Question, q2: Question) -> bool:
        """
        判断两个题目是否相似

        Args:
            q1, q2: 要比较的题目

        Returns:
            True表示相似，应该去重
        """
        # 1. 完全匹配检查（标准化后）
        if self._normalize(q1.content) == self._normalize(q2.content):
            return True

        # 2. 内容相似度检查
        content_similarity = self._text_similarity(q1.content, q2.content)
        if content_similarity >= self.similarity_threshold:
            return True

        # 3. 关键词重叠检查
        if self._keyword_overlap(q1.content, q2.content) >= 0.8:
            # 进一步检查答案相似度
            if self._text_similarity(q1.correct_answer, q2.correct_answer) >= 0.7:
                return True

        # 4. 特殊模式：选择题选项匹配
        if self._is_multiple_choice_match(q1, q2):
            return True

        return False

    def _normalize(self, text: str) -> str:
        """标准化文本"""
        # 移除空格和标点
        text = re.sub(r'\s+', '', text)
        # 移除中英文标点符号
        for char in ['，', '。', '、', '；', '：', '？', '！', '"', '"', ''', ''', '（', '）', '[', ']', '《', '》', '【', '】']:
            text = text.replace(char, '')
        return text.lower().strip()

    def _text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（使用difflib）"""
        norm1 = self._normalize(text1)
        norm2 = self._normalize(text2)

        if not norm1 or not norm2:
            return 0.0

        return SequenceMatcher(None, norm1, norm2).ratio()

    def _keyword_overlap(self, text1: str, text2: str) -> float:
        """计算关键词重叠度"""
        # 简单分词（按字符）
        words1 = set(self._normalize(text1))
        words2 = set(self._normalize(text2))

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _is_multiple_choice_match(self, q1: Question, q2: Question) -> bool:
        """检查是否是同一道选择题"""
        # 检查是否都包含选项标记
        has_options1 = re.search(r'[A-D][．.、\s]', q1.content) or re.search(r'\([A-D]\)', q1.content)
        has_options2 = re.search(r'[A-D][．.、\s]', q2.content) or re.search(r'\([A-D]\)', q2.content)

        if not (has_options1 and has_options2):
            return False

        # 提取题干（去除选项）
        stem1 = self._extract_choice_stem(q1.content)
        stem2 = self._extract_choice_stem(q2.content)

        # 比较题干相似度
        return self._text_similarity(stem1, stem2) >= self.similarity_threshold

    def _extract_choice_stem(self, content: str) -> str:
        """提取选择题的题干"""
        # 查找第一个选项出现的位置
        match = re.search(r'[A-D][．.、\s]|\([A-D]\)', content)
        if match:
            return content[:match.start()].strip()
        return content

    def get_duplicate_report(self, new_questions: List[Question]) -> dict:
        """
        生成去重报告

        Args:
            new_questions: 新提取的题目列表

        Returns:
            去重统计报告
        """
        original_count = len(new_questions)
        unique_count = len(self.deduplicate(new_questions))
        duplicate_count = original_count - unique_count

        return {
            "original_count": original_count,
            "unique_count": unique_count,
            "duplicate_count": duplicate_count,
            "duplicate_rate": duplicate_count / original_count if original_count > 0 else 0,
        }
