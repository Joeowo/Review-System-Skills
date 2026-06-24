"""
用户统计数据存储
"""
import json
from pathlib import Path
from typing import Dict
from datetime import datetime

from models import Progress, UserAnswer
from config import USER_STATS_DIR


class StatsRepository:
    """用户统计数据存储库"""

    def __init__(self):
        """初始化存储库"""
        self._cache: Progress = None
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        USER_STATS_DIR.mkdir(parents=True, exist_ok=True)

    def load_progress(self, user_id: str = "default") -> Progress:
        """
        加载用户进度

        Args:
            user_id: 用户ID

        Returns:
            进度对象
        """
        if self._cache and self._cache.user_id == user_id:
            return self._cache

        stats_file = USER_STATS_DIR / f"{user_id}.json"

        if stats_file.exists():
            data = json.loads(stats_file.read_text(encoding="utf-8"))
            self._cache = Progress.from_dict(data)
        else:
            self._cache = Progress(user_id=user_id)

        return self._cache

    def save_progress(self, progress: Progress) -> None:
        """
        保存用户进度

        Args:
            progress: 进度对象
        """
        stats_file = USER_STATS_DIR / f"{progress.user_id}.json"
        data = progress.to_dict()
        stats_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        self._cache = progress

    def save_answer(self, answer: UserAnswer, user_id: str = "default") -> None:
        """
        保存答题记录

        Args:
            answer: 答题记录
            user_id: 用户ID
        """
        progress = self.load_progress(user_id)

        # 更新进度统计
        progress.total_answers += 1
        progress.total_study_time += answer.time_spent_seconds
        if answer.is_correct:
            progress.correct_answers += 1
        else:
            # 从题目ID获取类别信息（简化处理）
            progress.weak_areas["未分类"] = progress.weak_areas.get("未分类", 0) + 1

        progress.last_study_date = datetime.now()

        self.save_progress(progress)

    def get_answer_history(self, user_id: str = "default", limit: int = 50) -> list:
        """
        获取答题历史

        Args:
            user_id: 用户ID
            limit: 最大返回数量

        Returns:
            答题记录列表
        """
        # TODO: 实现答题历史记录存储
        return []
