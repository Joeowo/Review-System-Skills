"""
基于Agent的题目提取模块
使用LLM从复习资料和历年试题中智能提取题目
"""
import json
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from models import Question, QuestionType
from services.llm_service import DeepSeekService
from utils.file_reader import FileReader


class QuestionSource:
    """题目来源配置"""
    PAST_EXAMS = "往届期末试题"
    REVIEW_MATERIALS = "复习资料"
    AUTO_GENERATED = "自动生成"


class AgentQuestionExtractor:
    """基于Agent的题目提取器"""

    def __init__(self):
        """初始化提取器"""
        self.llm_service = DeepSeekService()
        self.file_reader = FileReader()
        self.existing_questions: set = set()  # 用于去重

    def set_existing_questions(self, questions: List[Question]):
        """设置已存在的题目集合，用于去重"""
        self.existing_questions = {
            self._normalize_content(q.content) for q in questions
        }

    def extract_from_source(
        self,
        source_dir: Path,
        source_name: str,
        priority: int = 1
    ) -> List[Question]:
        """
        从指定目录提取题目

        Args:
            source_dir: 源文件目录
            source_name: 来源名称
            priority: 优先级（2=历年试题, 1=复习资料, 0=自动生成）

        Returns:
            提取的题目列表
        """
        if not source_dir.exists():
            print(f"  跳过（目录不存在）: {source_dir}")
            return []

        questions = []
        files = sorted(source_dir.glob("*"))

        print(f"\n正在处理: {source_name}")
        print(f"  找到 {len(files)} 个文件")

        for file_path in files:
            if file_path.is_dir():
                continue

            if not self.file_reader.is_supported(file_path):
                print(f"  跳过（不支持的格式）: {file_path.name}")
                continue

            print(f"  处理: {file_path.name}")
            file_questions = self._extract_from_file(
                file_path, source_name, priority
            )
            print(f"    提取 {len(file_questions)} 道题目")
            questions.extend(file_questions)

        print(f"  ✓ {source_name}共提取 {len(questions)} 道题目")
        return questions

    def _extract_from_file(
        self,
        file_path: Path,
        source_name: str,
        priority: int
    ) -> List[Question]:
        """从单个文件提取题目"""
        content = self.file_reader.read(file_path)
        if not content or len(content.strip()) < 50:
            return []

        # 将内容分段处理
        chunks = self._split_content(content)

        all_questions = []
        for chunk in chunks:
            questions = self._extract_from_chunk(
                chunk, file_path.name, source_name, priority
            )
            all_questions.extend(questions)

        return all_questions

    def _split_content(self, content: str, max_length: int = 3000) -> List[str]:
        """将内容分成适合LLM处理的块"""
        chunks = []
        lines = content.split("\n")
        current_chunk = []

        for line in lines:
            current_chunk.append(line)
            current_length = sum(len(l) for l in current_chunk)

            # 检测题目分隔符
            stripped = line.strip()
            is_question_start = (
                re.match(r'^\d+[．.、\s]', stripped) or
                re.match(r'^\([一二三四五六]+\)', stripped) or
                re.match(r'^[（\[]*\d+[）\]]*[\s.、]', stripped) or
                stripped.startswith("题目") or
                stripped.startswith("问题") or
                (len(stripped) < 50 and stripped.endswith("?") and "?" in stripped)
            )

            # 当检测到新题目或当前块太长时，分块
            if (is_question_start and len(current_chunk) > 3) or current_length > max_length:
                chunk_text = "\n".join(current_chunk)
                if len(chunk_text.strip()) > 100:
                    chunks.append(chunk_text)
                current_chunk = [line]

        # 保存剩余内容
        if current_chunk:
            chunk_text = "\n".join(current_chunk)
            if len(chunk_text.strip()) > 100:
                chunks.append(chunk_text)

        return chunks

    def _extract_from_chunk(
        self,
        chunk: str,
        filename: str,
        source_name: str,
        priority: int
    ) -> List[Question]:
        """从内容块中提取题目"""
        prompt = f"""请从以下考试材料中提取完整的题目和答案。

考试材料：
```
{chunk[:3000]}
```

请返回JSON格式，必须严格按照以下结构：
{{
    "questions": [
        {{
            "type": "题型",
            "content": "题目内容",
            "correct_answer": "正确答案",
            "explanation": "详细解析（如果材料中没有，可以省略）",
            "difficulty": 0.5
        }}
    ]
}}

题型类型：选择题、填空题、判断题、简答题、计算题、定义题、应用题

要求：
1. content必须是完整的题目内容
2. correct_answer必须是完整的答案（对于选择题，要包含选项字母和内容）
3. 只提取有明确答案的题目
4. 不要提取没有答案的题目
5. difficulty范围0.0-1.0，概念题0.3，计算题0.7
6. 如果选择题有多个选项，请将选项内容包含在correct_answer中

只返回JSON，不要有其他内容。"""

        try:
            response = asyncio.run(self.llm_service.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100000  # 大幅增加token限制
            ))

            result_text = response["choices"][0]["message"]["content"]

            # 检查空响应
            if not result_text or not result_text.strip():
                print(f"    跳过：LLM返回空响应")
                return []

            # 清理可能的markdown代码块标记
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # 尝试解析JSON
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试提取和修复JSON
                print(f"    JSON解析失败，尝试修复: {str(e)[:80]}")

                # 尝试修复截断的JSON
                start = result_text.find('{')
                if start >= 0:
                    # 查找最后一个完整的question对象
                    last_question_end = result_text.rfind('}')
                    if last_question_end > start:
                        # 尝试构建有效的JSON（可能缺少最后的括号）
                        try:
                            # 尝试直接解析
                            result_text = result_text[start:]
                            result = json.loads(result_text)
                        except:
                            # 如果失败，尝试补全JSON结构
                            try:
                                # 找到最后一个完整的question对象
                                questions_end = result_text.rfind('}]')
                                if questions_end > 0:
                                    result_text = result_text[:questions_end+2] + '}'
                                    result = json.loads(result_text)
                                else:
                                    # 单个question对象
                                    result_text = result_text[:result_text.rfind('}')+1] + '}'
                                    temp = json.loads(result_text)
                                    result = {"questions": [temp] if "questions" not in result_text else temp}
                            except:
                                print(f"    无法修复，跳过此文件")
                                return []
                else:
                    print(f"    无法找到JSON起始位置，跳过此文件")
                    return []

            questions = []
            for item in result.get("questions", []):
                # 去重检查
                normalized_content = self._normalize_content(item.get("content", ""))
                if normalized_content in self.existing_questions:
                    continue

                question = Question(
                    source=f"{source_name}/{filename}",
                    source_priority=priority,
                    type=self._map_type(item.get("type", "定义题")),
                    content=item.get("content", ""),
                    correct_answer=item.get("correct_answer", ""),
                    explanation=item.get("explanation", ""),
                    difficulty=item.get("difficulty", 0.5),
                    tags=[source_name],
                )

                # 验证有效性
                if self._is_valid_question(question):
                    questions.append(question)
                    self.existing_questions.add(normalized_content)

            return questions

        except Exception as e:
            print(f"    提取失败: {e}")
            return []

    def _map_type(self, type_str: str) -> QuestionType:
        """映射题型"""
        type_map = {
            "选择题": QuestionType.APPLICATION,
            "填空题": QuestionType.DEFINITION,
            "判断题": QuestionType.RELATIONSHIP,
            "简答题": QuestionType.DEFINITION,
            "计算题": QuestionType.FORMULA,
            "定义题": QuestionType.DEFINITION,
            "应用题": QuestionType.APPLICATION,
            "分类题": QuestionType.CLASSIFICATION,
            "关系题": QuestionType.RELATIONSHIP,
            "公式题": QuestionType.FORMULA,
        }
        return type_map.get(type_str, QuestionType.DEFINITION)

    def _normalize_content(self, content: str) -> str:
        """标准化题目内容，用于去重"""
        # 移除空格和标点
        normalized = re.sub(r'\s+', '', content)
        # 移除中英文标点符号
        for char in ['，', '。', '、', '；', '：', '？', '！', '"', '"', ''', ''', '（', '）', '[', ']', '《', '》']:
            normalized = normalized.replace(char, '')
        return normalized.lower()

    def _is_valid_question(self, question: Question) -> bool:
        """验证题目是否有效"""
        # 题目长度检查
        if len(question.content) < 5 or len(question.content) > 500:
            return False

        # 答案长度检查
        if len(question.correct_answer) < 2:
            return False

        # 无效题目检查
        invalid_patterns = [
            r'^详见',
            r'^参考',
            r'^答案略',
            r'^见教材',
            r'^略$',
        ]
        for pattern in invalid_patterns:
            if re.match(pattern, question.correct_answer.strip()):
                return False

        return True
