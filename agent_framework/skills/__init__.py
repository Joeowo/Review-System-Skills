"""
S1: 技能注册表与中间件调度层

提供技能发现、注册、路由和执行功能。
"""

from agent_framework.skills.registry import (
    SkillRegistry,
    DuplicateSkillError,
    SkillNotFoundError,
)
from agent_framework.skills.loader import SkillLoader, SkillLoadError
from agent_framework.skills.middleware import (
    Interceptor,
    InterceptorChain,
    LoggingInterceptor,
    StopExecution,
    SkillMiddleware,
    RouteNotFoundError,
)
from agent_framework.skills.executor import ParallelSkillExecutor
from agent_framework.skills.models import (
    SkillMetadata,
    SkillContext,
    SkillResult,
)

__all__ = [
    # Registry
    "SkillRegistry",
    "DuplicateSkillError",
    "SkillNotFoundError",
    # Loader
    "SkillLoader",
    "SkillLoadError",
    # Middleware
    "Interceptor",
    "InterceptorChain",
    "LoggingInterceptor",
    "StopExecution",
    "SkillMiddleware",
    "RouteNotFoundError",
    # Executor
    "ParallelSkillExecutor",
    # Models
    "SkillMetadata",
    "SkillContext",
    "SkillResult",
]
