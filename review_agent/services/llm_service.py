"""
DeepSeek API 服务
提供LLM调用功能
"""
import asyncio
import aiohttp
import json
from typing import Dict, Optional, Any, List
from datetime import datetime

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


class DeepSeekService:
    """DeepSeek API服务"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化服务

        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.model = DEEPSEEK_MODEL

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY未设置")

    async def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式 ("json" 或 None)

        Returns:
            API响应
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # 如果需要JSON格式响应
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API请求失败: {response.status} - {error_text}")

                return await response.json()

    async def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str
    ) -> Dict[str, Any]:
        """
        评估用户答案

        Args:
            question: 题目
            user_answer: 用户答案
            correct_answer: 正确答案

        Returns:
            评估结果字典
        """
        messages = [
            {
                "role": "system",
                "content": """你是一个专业且宽容的答案评估助手。你的目标是评估学生是否真正理解了核心概念，而不是纠结于细枝末节。

评估原则（重要）：
1. 笔误宽容：数字单位简写（300w、300万、300万元）视为相同；错别字不影响理解时忽略
2. 逻辑优先：关注核心概念、计算逻辑、推理过程是否正确，而非文字表述完全一致
3. 顺序无关：要点顺序不同但内容正确应认可，如先列公式再代入数字和先代入数字再列公式都正确
4. 同义词宽容：使用同义词、不同表述方式但意思相同应认可
5. 计算过程：数值计算结果正确即可，中间步骤顺序不影响

严格评估的例外：
只有当错误影响核心概念理解、导致结果错误、或遗漏关键步骤时才扣分。"""
            },
            {
                "role": "user",
                "content": f"""请评估以下答案：

题目：{question}

正确答案：{correct_answer}

学生答案：{user_answer}

请返回JSON格式（必须严格按照以下格式）：
{{
    "is_correct": true/false,
    "score": 0.0-1.0之间的分数,
    "feedback": "具体的反馈意见",
    "missing_points": ["学生遗漏的关键点1", "关键点2"],
    "strengths": ["学生回答好的地方1", "地方2"]
}}

评分标准：
- 完全正确（核心概念准确，表述清晰）：score >= 0.9, is_correct = true
- 基本正确（理解到位，有轻微笔误或表述不同）：0.7 <= score < 0.9, is_correct = true
- 部分正确（理解部分内容，有遗漏）：0.4 <= score < 0.7, is_correct = false
- 基本错误（核心概念错误或完全偏离）：score < 0.4, is_correct = false

特别注意：
- 学生写"300w元"与"300万元"视为相同，不扣分
- 计算步骤顺序不同但结果正确，不扣分
- 使用同义表述但意思正确，不扣分

请只返回JSON，不要有其他内容。"""
            }
        ]

        try:
            response = await self.chat(
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
                response_format="json"
            )

            content = response["choices"][0]["message"]["content"]

            # 解析JSON
            result = json.loads(content)

            # 确保字段完整
            if "is_correct" not in result:
                result["is_correct"] = result.get("score", 0) >= 0.6

            return result

        except Exception as e:
            # 降级处理：返回简单评估
            return self._simple_evaluate(user_answer, correct_answer)

    def _simple_evaluate(self, user_answer: str, correct_answer: str) -> Dict[str, Any]:
        """简单答案评估（降级方案）"""
        # 简单的关键词匹配
        user_lower = user_answer.lower()
        correct_lower = correct_answer.lower()

        # 提取正确答案中的关键词
        correct_keywords = [w for w in correct_lower.split() if len(w) >= 2]

        # 计算匹配度
        matches = sum(1 for kw in correct_keywords if kw in user_lower)
        score = min(matches / max(len(correct_keywords), 1), 1.0)

        return {
            "is_correct": score >= 0.6,
            "score": score,
            "feedback": "基于关键词匹配的简单评估",
            "missing_points": [],
            "strengths": [],
        }

    async def extract_knowledge_points(
        self,
        content: str,
        category: str = ""
    ) -> Dict[str, Any]:
        """
        从文本中提取知识点

        Args:
            content: 文本内容
            category: 类别

        Returns:
            提取的知识点字典
        """
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的知识点提取助手。请从文本中提取结构化的知识点。"
            },
            {
                "role": "user",
                "content": f"""请从以下文本中提取知识点：

类别：{category}

文本内容：
{content[:2000]}

请返回JSON格式：
{{
    "knowledge_points": [
        {{
            "title": "知识点标题",
            "type": "概念/公式/分类/流程/关系",
            "content": "详细内容",
            "keywords": ["关键词1", "关键词2"]
        }}
    ]
}}

只返回JSON，不要有其他内容。"""
            }
        ]

        try:
            response = await self.chat(
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                response_format="json"
            )

            content = response["choices"][0]["message"]["content"]
            return json.loads(content)

        except Exception as e:
            return {"knowledge_points": []}


# 异步服务（支持并发）
class AsyncDeepSeekService:
    """支持并发的异步DeepSeek服务"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化异步服务

        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self._service = DeepSeekService(api_key, base_url)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """关闭HTTP会话"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def evaluate_answers_batch(
        self,
        questions: List[str],
        user_answers: List[str],
        correct_answers: List[str]
    ) -> List[Dict[str, Any]]:
        """
        批量评估答案（并发）

        Args:
            questions: 题目列表
            user_answers: 用户答案列表
            correct_answers: 正确答案列表

        Returns:
            评估结果列表
        """
        if len(questions) != len(user_answers) or len(questions) != len(correct_answers):
            raise ValueError("题目、用户答案和正确答案数量不匹配")

        # 创建所有评估任务
        tasks = [
            self._service.evaluate_answer(q, ua, ca)
            for q, ua, ca in zip(questions, user_answers, correct_answers)
        ]

        # 并发执行所有评估
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        evaluations = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 单个评估失败，使用降级方案
                evaluations.append(self._service._simple_evaluate(
                    user_answers[i],
                    correct_answers[i]
                ))
            else:
                evaluations.append(result)

        return evaluations

    async def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str
    ) -> Dict[str, Any]:
        """评估单个答案"""
        return await self._service.evaluate_answer(question, user_answer, correct_answer)


# 同步封装
class SyncDeepSeekService:
    """同步版本的DeepSeek服务"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self._async_service = DeepSeekService(api_key, base_url)

    def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str
    ) -> Dict[str, Any]:
        """同步评估答案"""
        return asyncio.run(self._async_service.evaluate_answer(
            question, user_answer, correct_answer
        ))

    def extract_knowledge_points(
        self,
        content: str,
        category: str = ""
    ) -> Dict[str, Any]:
        """同步提取知识点"""
        return asyncio.run(self._async_service.extract_knowledge_points(content, category))


# 测试代码
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # 测试API
    service = SyncDeepSeekService()

    # 测试答案评估
    result = service.evaluate_answer(
        question="什么是机会成本？",
        user_answer="机会成本是指选择一个选项后放弃的其他选项的最大收益。",
        correct_answer="机会成本是指资源用于某一用途后放弃的其他用途所能获得的最大收益。"
    )

    print("评估结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
