"""
题目提取服务
整合题目提取、去重和存储功能
"""
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from models import Question
from core.question_extractor import AgentQuestionExtractor, QuestionSource
from services.question_dedup import QuestionDeduplicator
from config import QUESTION_SOURCES, QUESTION_BANK_DIR


class QuestionExtractionService:
    """题目提取服务"""

    def __init__(self):
        """初始化服务"""
        self.extractor = AgentQuestionExtractor()
        self.deduplicator = QuestionDeduplicator()
        self._load_existing_questions()

    def _load_existing_questions(self):
        """加载已存在的题目"""
        existing_questions = []

        for json_file in QUESTION_BANK_DIR.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        question = Question.from_dict(item)
                        existing_questions.append(question)
            except Exception as e:
                print(f"  警告：无法读取 {json_file.name}: {e}")

        # 设置到提取器和去重器
        self.extractor.set_existing_questions(existing_questions)
        self.deduplicator.set_existing(existing_questions)

        print(f"  已加载 {len(existing_questions)} 道现有题目")

    def extract_all(self, source_type: str = "all") -> Dict[str, List[Question]]:
        """
        从所有源提取题目

        Args:
            source_type: 提取源类型（"all", "exams", "materials"）

        Returns:
            按来源分组的题目字典
        """
        results = {}

        # 按优先级从高到低处理
        for source_dir, priority in sorted(QUESTION_SOURCES, key=lambda x: -x[1]):
            source_name = source_dir.name

            # 过滤源类型
            if source_type == "exams" and "试题" not in str(source_dir):
                continue
            if source_type == "materials" and "复习资料" not in str(source_dir):
                continue

            questions = self.extractor.extract_from_source(
                source_dir, source_name, priority
            )

            if questions:
                results[source_name] = questions

        return results

    def process_and_save(
        self,
        source_type: str = "all",
        output_file: str = None
    ) -> Dict:
        """
        提取、去重并保存题目

        Args:
            source_type: 提取源类型
            output_file: 输出文件名（不指定则自动生成）

        Returns:
            处理统计报告
        """
        print(f"\n{'='*50}")
        print(f"开始提取题目（源类型: {source_type}）")
        print(f"{'='*50}")

        # 1. 提取题目
        raw_results = self.extract_all(source_type)
        all_questions = []
        for source_name, questions in raw_results.items():
            all_questions.extend(questions)

        print(f"\n原始提取: {len(all_questions)} 道题目")

        # 2. 去重
        print("\n正在去重...")
        unique_questions = self.deduplicator.deduplicate(all_questions)
        print(f"去重后: {len(unique_questions)} 道题目")

        # 3. 生成报告
        report = {
            "source_type": source_type,
            "raw_count": len(all_questions),
            "unique_count": len(unique_questions),
            "duplicate_count": len(all_questions) - len(unique_questions),
            "by_source": {
                name: len(questions) for name, questions in raw_results.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

        # 4. 保存
        if unique_questions:
            if output_file is None:
                output_file = f"question_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            output_path = QUESTION_BANK_DIR / output_file
            self._save_questions(unique_questions, output_path)
            report["saved_to"] = str(output_path)
            print(f"\n题目已保存到: {output_path}")

        return report

    def _save_questions(self, questions: List[Question], output_path: Path):
        """保存题目到JSON文件"""
        data = [q.to_dict() for q in questions]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_statistics(self) -> Dict:
        """获取题库统计信息"""
        all_questions = []

        for json_file in QUESTION_BANK_DIR.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    all_questions.extend(data)
            except Exception:
                pass

        # 按来源统计
        by_source = {}
        by_priority = {0: 0, 1: 0, 2: 0}

        for q in all_questions:
            source = q.get("source", "未知")
            by_source[source] = by_source.get(source, 0) + 1
            priority = q.get("source_priority", 0)
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            "total_questions": len(all_questions),
            "files": len(list(QUESTION_BANK_DIR.glob("*.json"))),
            "by_source": by_source,
            "by_priority": {
                "历年试题": by_priority.get(2, 0),
                "复习资料": by_priority.get(1, 0),
                "自动生成": by_priority.get(0, 0),
            },
        }
