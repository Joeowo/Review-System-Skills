"""
后台任务管理器
支持异步并行任务执行和状态跟踪
"""
import asyncio
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class Task:
    """后台任务"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    progress: float = 0.0  # 0.0 - 1.0
    total_steps: int = 0
    completed_steps: int = 0


class AsyncTaskManager:
    """异步任务管理器"""

    def __init__(self, max_concurrent: int = 5):
        """
        初始化任务管理器

        Args:
            max_concurrent: 最大并发任务数
        """
        self.max_concurrent = max_concurrent
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: int = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def submit_task(
        self,
        coro,
        task_id: Optional[str] = None,
        total_steps: int = 1
    ) -> str:
        """
        提交异步任务

        Args:
            coro: 协程对象
            task_id: 可选的任务ID
            total_steps: 任务总步数（用于进度计算）

        Returns:
            任务ID
        """
        if task_id is None:
            task_id = str(uuid.uuid4())

        task = Task(id=task_id, total_steps=total_steps)
        self.tasks[task_id] = task

        # 在后台执行任务
        asyncio.create_task(self._execute_task(coro, task))

        return task_id

    async def _execute_task(self, coro, task: Task):
        """执行任务"""
        async with self.semaphore:
            try:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                self.running_tasks += 1

                # 执行任务
                result = await coro

                task.result = result
                task.status = TaskStatus.COMPLETED
                task.progress = 1.0

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)

            finally:
                task.completed_at = datetime.now()
                self.running_tasks -= 1

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态，如果任务不存在返回None
        """
        task = self.tasks.get(task_id)
        return task.status if task else None

    def get_task_progress(self, task_id: str) -> Optional[float]:
        """
        获取任务进度

        Args:
            task_id: 任务ID

        Returns:
            进度值 (0.0 - 1.0)，如果任务不存在返回None
        """
        task = self.tasks.get(task_id)
        return task.progress if task else None

    def update_task_progress(self, task_id: str, completed_steps: int):
        """
        更新任务进度

        Args:
            task_id: 任务ID
            completed_steps: 已完成步数
        """
        task = self.tasks.get(task_id)
        if task and task.total_steps > 0:
            task.completed_steps = completed_steps
            task.progress = min(completed_steps / task.total_steps, 1.0)

    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        获取任务结果（等待完成）

        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）

        Returns:
            任务结果

        Raises:
            TimeoutError: 超时
            ValueError: 任务不存在
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        # 等待任务完成
        start_time = datetime.now()
        while task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            await asyncio.sleep(0.1)

            # 检查超时
            if timeout is not None:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= timeout:
                    raise TimeoutError(f"任务超时: {task_id}")

        if task.status == TaskStatus.FAILED:
            raise RuntimeError(f"任务失败: {task.error}")

        return task.result

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            return True
        return False

    def clean_completed_tasks(self, older_than_seconds: int = 3600):
        """
        清理已完成的旧任务

        Args:
            older_than_seconds: 清理多少秒之前的任务
        """
        now = datetime.now()
        to_remove = []

        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.completed_at and
                (now - task.completed_at).total_seconds() > older_than_seconds):
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.tasks[task_id]

    def get_all_tasks(self) -> Dict[str, Task]:
        """获取所有任务"""
        return self.tasks.copy()

    def get_running_tasks(self) -> List[str]:
        """获取正在运行的任务ID列表"""
        return [
            task_id for task_id, task in self.tasks.items()
            if task.status == TaskStatus.RUNNING
        ]


# 全局任务管理器实例
_global_manager: Optional[AsyncTaskManager] = None


def get_global_manager() -> AsyncTaskManager:
    """获取全局任务管理器实例"""
    global _global_manager
    if _global_manager is None:
        _global_manager = AsyncTaskManager()
    return _global_manager
