"""
核心研究模块 (V2)
使用 DeepSeek API 进行自动化研究，强化来源追踪和置信度
"""
import requests
import json
import time
import re
from typing import Dict, List, Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urlparse

from .config import Config


@dataclass
class Source:
    """信息来源"""
    title: str
    url: str
    type: str  # paper, arxiv, github, blog, docs, other
    confidence: str  # high, medium, low
    date: str = ""
    authors: str = ""
    arxiv_id: str = ""

    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        md = f"- [{self.title}]({self.url})"
        if self.arxiv_id:
            md += f" (arXiv:{self.arxiv_id})"
        if self.authors:
            md += f" - {self.authors}"
        if self.date:
            md += f" ({self.date})"
        return md


@dataclass
class SearchQuery:
    """搜索查询"""
    query: str
    context: str = ""
    depth: str = "comprehensive"  # basic, standard, comprehensive
    require_sources: bool = True  # 是否要求提供来源


@dataclass
class ResearchResult:
    """研究结果"""
    topic: str
    content: str
    reasoning: str = ""
    sources: List[Source] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    token_usage: Dict = field(default_factory=dict)
    web_search_used: bool = False

    def add_source(self, source: Source):
        """添加来源"""
        self.sources.append(source)

    def get_sources_by_type(self, source_type: str) -> List[Source]:
        """按类型获取来源"""
        return [s for s in self.sources if s.type == source_type]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "topic": self.topic,
            "content": self.content,
            "reasoning": self.reasoning,
            "sources": [s.to_markdown() for s in self.sources],
            "timestamp": self.timestamp,
            "token_usage": self.token_usage,
            "web_search_used": self.web_search_used,
        }


class SourceExtractor:
    """来源提取器 - 从文本中提取引用信息"""

    @staticmethod
    def extract_arxiv_id(text: str) -> Optional[str]:
        """提取 arXiv ID"""
        patterns = [
            r'arXiv:(\d{4}\.\d+)',
            r'arxiv\.org/abs/(\d{4}\.\d+)',
            r'arxiv\.org/html/(\d{4}\.\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """提取 URL"""
        url_pattern = r'https?://[^\s\)\],}]+(?:\([^\s]*\))?[^\s\)\],}]*'
        urls = re.findall(url_pattern, text)
        # 去重并过滤
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        return unique_urls

    @staticmethod
    def classify_url(url: str) -> str:
        """对 URL 进行分类"""
        domain = urlparse(url).netloc.lower()

        if 'arxiv.org' in domain:
            return 'arxiv'
        elif 'github.com' in domain:
            return 'github'
        elif 'docs.' in domain or 'documentation' in url.lower():
            return 'docs'
        elif 'blog.' in domain or '/blog/' in url.lower():
            return 'blog'
        elif 'papers.' in domain or 'publications' in url.lower():
            return 'paper'
        else:
            return 'other'

    @staticmethod
    def extract_sources_from_content(content: str) -> List[Source]:
        """从内容中提取来源"""
        sources = []
        urls = SourceExtractor.extract_urls(content)

        for url in urls:
            source_type = SourceExtractor.classify_url(url)
            arxiv_id = SourceExtractor.extract_arxiv_id(url) if source_type == 'arxiv' else ""

            # 简单的标题提取（可以改进）
            # 查找 URL 前面的文本作为标题
            url_escaped = re.escape(url)
            title_match = re.search(r'\[([^\]]+)\]\(' + url_escaped, content)
            title = title_match.group(1) if title_match else url

            source = Source(
                title=title,
                url=url,
                type=source_type,
                confidence='high' if source_type in ['arxiv', 'github', 'docs'] else 'medium',
                arxiv_id=arxiv_id
            )
            sources.append(source)

        return sources


class DeepSeekResearcher:
    """DeepSeek 研究器 (V2 - 增强版)"""

    def __init__(self, config: Config = None):
        self.config = config or Config
        self.api_key = self.config.API_KEY
        self.base_url = self.config.BASE_URL
        self.model = self.config.MODEL
        self.endpoint = f"{self.base_url}/chat/completions"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        self.source_extractor = SourceExtractor()

    def _make_request(
        self,
        messages: List[Dict],
        web_search: bool = True,
        max_tokens: int = None,
        **kwargs
    ) -> Dict:
        """发起 API 请求"""
        payload = {
            "model": self.model,
            "messages": messages,
            "web_search": web_search,
            **kwargs
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        for attempt in range(Config.MAX_RETRIES):
            try:
                response = requests.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=Config.TIMEOUT
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                print(f"请求超时，重试 {attempt + 1}/{Config.MAX_RETRIES}...")
                time.sleep(2 ** attempt)

            except requests.exceptions.RequestException as e:
                if attempt == Config.MAX_RETRIES - 1:
                    raise Exception(f"API 请求失败: {e}")
                print(f"请求失败，重试 {attempt + 1}/{Config.MAX_RETRIES}...")
                time.sleep(2 ** attempt)

        return {}

    def search(self, query: SearchQuery) -> ResearchResult:
        """执行单次搜索"""
        print(f"\n🔍 搜索: {query.query}")

        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(query.depth, query.require_sources)
            },
            {
                "role": "user",
                "content": self._format_user_query(query)
            }
        ]

        result = self._make_request(messages, web_search=Config.WEB_SEARCH_ENABLED)

        return self._parse_result(query.query, result, web_search=Config.WEB_SEARCH_ENABLED)

    def research_deep(
        self,
        topic: str,
        aspects: List[str],
        depth: str = "comprehensive"
    ) -> List[ResearchResult]:
        """深度研究：分多个维度进行研究"""
        print(f"\n📚 开始深度研究: {topic}")
        print(f"研究维度: {', '.join(aspects)}")

        results = []

        for i, aspect in enumerate(aspects, 1):
            print(f"\n{'='*60}")
            print(f"维度 {i}/{len(aspects)}: {aspect}")
            print(f"{'='*60}")

            query = SearchQuery(
                query=f"{topic} - {aspect}",
                context=f"专注于 {aspect} 方面的研究",
                depth=depth,
                require_sources=True
            )

            result = self.search(query)
            results.append(result)

        return results

    def research_iterative(
        self,
        topic: str,
        questions: List[str],
        previous_context: str = ""
    ) -> Generator[ResearchResult, None, None]:
        """迭代研究：基于上下文逐步深入研究"""
        context = previous_context

        for i, question in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"问题 {i}/{len(questions)}: {question}")
            print(f"{'='*60}")

            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的研究助手，擅长深入分析问题并提供详尽的答案。"
                },
            ]

            if context:
                messages.append({
                    "role": "assistant",
                    "content": f"之前的研究结果：\n\n{context}\n\n请基于这些信息继续研究。"
                })

            messages.append({
                "role": "user",
                "content": question
            })

            result_dict = self._make_request(messages, web_search=True)
            result = self._parse_result(question, result_dict, web_search=True)

            context += f"\n\n## {question}\n\n{result.content}"
            yield result

    def generate_research_questions(
        self,
        topic: str,
        research_type: str = "通用"
    ) -> List[str]:
        """生成研究问题列表"""
        print(f"\n🤔 为 '{topic}' 生成研究问题...")

        template = Config.RESEARCH_TEMPLATES.get(research_type, Config.RESEARCH_TEMPLATES["通用"])

        prompt = f"""请为主题 "{topic}" 生成一组深度研究问题。

研究类型: {research_type}
研究描述: {template['description']}
重点关注: {', '.join(template['focus_areas'])}

请生成 5-8 个具体的研究问题，这些问题应该：
1. 覆盖主题的各个重要方面
2. 从基础到深入，循序渐进
3. 具有实际的研究价值
4. 便于通过搜索获得答案

只返回问题列表，每行一个问题，以数字编号。"""

        messages = [
            {"role": "system", "content": "你是一个专业的研究策划专家。"},
            {"role": "user", "content": prompt}
        ]

        result = self._make_request(messages, web_search=True, max_tokens=1000)

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # 解析问题列表
        questions = []
        for line in content.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                # 移除编号和符号
                q = line.lstrip("0123456789.-.) ] ")
                if q:
                    questions.append(q)

        return questions if questions else [
            f"什么是 {topic}？",
            f"{topic} 的核心原理是什么？",
            f"{topic} 有哪些主要应用场景？",
            f"{topic} 的最新发展趋势是什么？",
            f"如何选择合适的 {topic} 方案？"
        ]

    def _get_system_prompt(self, depth: str, require_sources: bool = True) -> str:
        """获取系统提示词"""
        base = """你是一个专业的研究助手，擅长搜集、整理和分析信息。

## 核心任务
1. 搜索并收集准确、最新的信息
2. 分析信息的可靠性和相关性
3. 整理成清晰、结构化的回答
4. **重要**: 引用可靠的信息来源

## 回答格式要求

### 结构要求
- 使用清晰的层级标题 (##, ###)
- 使用列表、表格等格式化信息
- 对比分析使用表格
- 时间线使用代码块图表

### 来源引用要求
"""

        if require_sources:
            base += """
**每篇论文必须包含：**
- 论文标题
- arXiv 编号或 DOI
- 第一作者
- 发表年份
- 链接

**格式示例：**
```
#### 论文标题
- **来源**: arXiv:XXXX.XXXXX (年份)
- **作者**: First Author et al.
- **链接**: https://arxiv.org/abs/XXXX.XXXXX
- **核心贡献**: 简要描述
```

**每个框架/工具必须包含：**
- 框架名称
- 官方文档链接
- GitHub 仓库链接（如有）
- 核心特性
"""

        base += """

### 内容质量要求
- 提供具体的数据和事实
- 标注信息来源和时间
- 区分事实和观点
- 保持客观中立
"""

        depth_instructions = {
            "basic": "\n**深度要求**: 提供简洁的概述，重点突出核心信息。",
            "standard": "\n**深度要求**: 提供详细的说明，涵盖主要方面和细节。",
            "comprehensive": "\n**深度要求**: 提供全面深入的分析，包括背景、细节、对比、趋势等多个维度。"
        }

        return base + depth_instructions.get(depth, depth_instructions["standard"])

    def _format_user_query(self, query: SearchQuery) -> str:
        """格式化用户查询"""
        content = f"请帮我研究以下主题：{query.query}"

        if query.context:
            content += f"\n\n研究背景：{query.context}"

        content += f"\n\n请提供深度 {query.depth} 的研究结果。"

        if query.require_sources:
            content += "\n\n**重要**: 请确保每个重要观点都有可靠的来源引用，包括论文的 arXiv 编号和链接。"

        return content

    def _parse_result(self, query: str, result: Dict, web_search: bool = False) -> ResearchResult:
        """解析 API 结果，提取来源"""
        if not result or "choices" not in result:
            return ResearchResult(
                topic=query,
                content="无法获取研究结果",
                sources=[]
            )

        choice = result["choices"][0]
        message = choice["message"]

        content = message.get("content", "")
        reasoning = message.get("reasoning_content", "")

        # 提取 token 使用情况
        usage = result.get("usage", {})

        # 从内容中提取来源
        sources = self.source_extractor.extract_sources_from_content(content)

        # 检查 API 返回的 web_search 信息
        web_search_info = usage.get("web_search", {}) if isinstance(usage, dict) else {}

        return ResearchResult(
            topic=query,
            content=content,
            reasoning=reasoning,
            sources=sources,
            token_usage=usage,
            web_search_used=web_search
        )

    def collect_all_sources(self, results: List[ResearchResult]) -> List[Source]:
        """收集所有研究结果的来源，去重"""
        all_sources = {}
        for result in results:
            for source in result.sources:
                # 使用 URL 作为唯一标识
                if source.url and source.url not in all_sources:
                    all_sources[source.url] = source
        return list(all_sources.values())
