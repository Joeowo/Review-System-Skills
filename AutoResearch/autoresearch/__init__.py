"""
AutoResearch - 强化置信度的自动化研究工具
基于 DeepSeek V4-Pro + WebSearch + 学术规范化
"""

from .config import Config, RESEARCH_TEMPLATES
from .researcher import DeepSeekResearcher, SearchQuery, ResearchResult, Source, SourceExtractor
from .reporter import ReportGenerator, ReferenceFormatter
from .planner import TaskPlanner, ResearchPlan

__version__ = "2.0.0"
__author__ = "AutoResearch"

__all__ = [
    # 配置
    "Config",
    "RESEARCH_TEMPLATES",
    # 研究器
    "DeepSeekResearcher",
    "SearchQuery",
    "ResearchResult",
    "Source",
    "SourceExtractor",
    # 报告生成
    "ReportGenerator",
    "ReferenceFormatter",
    # 规划器
    "TaskPlanner",
    "ResearchPlan",
]
