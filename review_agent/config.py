"""
Review Agent Configuration
加载和管理应用配置
"""
from pathlib import Path
from dotenv import load_dotenv
import os

# 项目根目录
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
QUESTION_BANK_DIR = DATA_DIR / "question_bank"
USER_STATS_DIR = DATA_DIR / "user_stats"

# 数据源目录（review会话目录）
REVIEW_SOURCES = [
    BASE_DIR.parent / "review-20250619-经济管理",
    BASE_DIR.parent / "review-20250622-生产管理",
    BASE_DIR.parent / "review-20250623-经济管理",
    BASE_DIR.parent / "review-20250624-经济管理",
    BASE_DIR.parent / "review-20260620-经济管理",
]

# 题目源目录（按优先级排序）
QUESTION_SOURCES = [
    (BASE_DIR.parent / "往届期末试题", 2),  # 优先级最高
    (BASE_DIR.parent / "复习资料", 1),       # 优先级中等
]

# 加载.env配置
load_dotenv(BASE_DIR / ".env")

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# SuperMemo-2 算法参数
SM2_INITIAL_EF = 2.5  # 初始易记因子
SM2_INITIAL_INTERVAL = 1  # 初始间隔（天）
SM2_MINIMUM_EF = 1.3  # 最小易记因子

# 刷题配置
QUESTIONS_PER_ROUND = 5  # 每轮题目数量

# 并发评估配置
MAX_CONCURRENT_EVALUATIONS = 5  # 最大并发评估数
EVALUATION_TIMEOUT = 30  # 单个评估超时时间(秒)
SHOW_EVALUATION_PROGRESS = True  # 是否显示评估进度

# 题目类型
QUESTION_TYPES = {
    "DEFINITION": "定义题",
    "FORMULA": "公式题",
    "CLASSIFICATION": "分类题",
    "RELATIONSHIP": "关系题",
    "APPLICATION": "应用题",
}

# 知识点类型
KNOWLEDGE_TYPES = {
    "CONCEPT": "概念",
    "FORMULA": "公式",
    "CLASSIFICATION": "分类",
    "PROCESS": "流程",
    "RELATIONSHIP": "关系",
}


def ensure_data_dirs():
    """确保数据目录存在"""
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    QUESTION_BANK_DIR.mkdir(parents=True, exist_ok=True)
    USER_STATS_DIR.mkdir(parents=True, exist_ok=True)
