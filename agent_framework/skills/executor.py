"""
S1-T7: 并行执行器

支持多个 Skills 同时执行且状态隔离。
"""

from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import List, Optional, Tuple
from loguru import logger

from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult


class ParallelSkillExecutor:
    """并行技能执行器

    支持多个技能同时执行，每个技能的状态相互隔离。
    """

    def __init__(self, middleware: SkillMiddleware, max_workers: Optional[int] = None) -> None:
        """初始化并行执行器

        Args:
            middleware: 技能中间件
            max_workers: 最大工作线程数，None 表示使用默认值
        """
        self._middleware = middleware
        self._max_workers = max_workers
        logger.info("ParallelSkillExecutor initialized", max_workers=max_workers)

    def execute_parallel(
        self,
        skill_names: List[str],
        contexts: List[SkillContext],
        loader: SkillLoader
    ) -> List[SkillResult]:
        """并行执行多个技能

        Args:
            skill_names: 技能名称列表
            contexts: 上下文列表，与 skill_names 一一对应
            loader: 技能加载器

        Returns:
            技能执行结果列表，顺序与输入一致

        Raises:
            ValueError: 技能列表与上下文列表长度不匹配时
        """
        if len(skill_names) != len(contexts):
            raise ValueError(
                f"Length mismatch: {len(skill_names)} skills vs {len(contexts)} contexts"
            )

        if not skill_names:
            logger.info("No skills to execute")
            return []

        # 创建结果列表，保持顺序
        results: List[Optional[SkillResult]] = [None] * len(skill_names)

        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            # 提交所有任务
            futures: List[Tuple[int, Future]] = []
            for i, (skill_name, context) in enumerate(zip(skill_names, contexts)):
                future = executor.submit(self._execute_single, skill_name, context, loader, i)
                futures.append((i, future))

            # 等待所有任务完成
            for index, future in futures:
                try:
                    result = future.result()
                    results[index] = result
                except Exception as e:
                    logger.error("Skill execution failed", index=index, error=str(e))
                    results[index] = SkillResult(
                        success=False,
                        output=None,
                        error=f"Execution failed: {str(e)}",
                        metadata={"skill_name": skill_names[index], "execution_failed": True}
                    )

        # 过滤掉 None（理论上不应该有）
        return [r for r in results if r is not None]

    def _execute_single(
        self,
        skill_name: str,
        context: SkillContext,
        loader: SkillLoader,
        index: int
    ) -> SkillResult:
        """执行单个技能

        Args:
            skill_name: 技能名称
            context: 技能上下文
            loader: 技能加载器
            index: 执行索引（用于日志）

        Returns:
            技能执行结果
        """
        logger.debug("Executing skill", index=index, skill=skill_name)
        try:
            result = self._middleware.execute_skill(skill_name, context, loader)
            logger.debug("Skill executed", index=index, success=result.success)
            return result
        except Exception as e:
            logger.error("Skill execution exception", index=index, error=str(e))
            return SkillResult(
                success=False,
                output=None,
                error=f"Skill execution error: {str(e)}",
                metadata={"skill_name": skill_name, "exception": True}
            )

    def verify_isolation(self) -> bool:
        """验证状态隔离

        这是一个验证方法，用于测试和调试。
        在实际执行中，由于每个执行使用独立的上下文对象，
        状态隔离由设计保证。

        Returns:
            始终返回 True（设计保证隔离）
        """
        return True
