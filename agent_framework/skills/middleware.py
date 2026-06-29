"""
S1-T4/T5: Middleware 调度层 - Interceptor 接口与路由功能

定义拦截器接口和拦截器链，支持在技能执行前后拦截。
实现技能路由功能，根据状态路由到合适的技能。
"""

from typing import Protocol, List, Any, Dict, Optional
from loguru import logger

from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult
from agent_framework.skills.registry import SkillRegistry


class Interceptor(Protocol):
    """拦截器接口

    定义在技能执行前后进行拦截的接口。
    """

    def before(self, skill_name: str, context: SkillContext) -> SkillContext:
        """执行前拦截

        在技能执行前调用，可以修改上下文。

        Args:
            skill_name: 技能名称
            context: 技能上下文

        Returns:
            修改后的上下文

        Raises:
            StopExecution: 如果希望阻止技能执行
        """
        ...

    def after(self, skill_name: str, result: SkillResult) -> SkillResult:
        """执行后拦截

        在技能执行后调用，可以修改结果。

        Args:
            skill_name: 技能名称
            result: 技能执行结果

        Returns:
            修改后的结果
        """
        ...


class StopExecution(Exception):
    """停止执行异常

    拦截器可以抛出此异常来阻止技能执行。
    """

    pass


class InterceptorChain:
    """拦截器链

    管理多个拦截器，按顺序执行 before，逆序执行 after。
    """

    def __init__(self) -> None:
        """初始化拦截器链"""
        self._interceptors: List[Interceptor] = []
        logger.info("InterceptorChain initialized")

    @property
    def interceptors(self) -> List[Interceptor]:
        """获取拦截器列表"""
        return self._interceptors

    def add(self, interceptor: Interceptor) -> None:
        """添加拦截器到链

        Args:
            interceptor: 拦截器实例
        """
        self._interceptors.append(interceptor)
        logger.info("Interceptor added to chain")

    def before(self, skill_name: str, context: SkillContext) -> SkillContext:
        """按顺序执行所有 before 拦截器

        Args:
            skill_name: 技能名称
            context: 技能上下文

        Returns:
            经过所有拦截器处理后的上下文
        """
        current_context = context
        for interceptor in self._interceptors:
            current_context = interceptor.before(skill_name, current_context)
        return current_context

    def after(self, skill_name: str, result: SkillResult) -> SkillResult:
        """按逆序执行所有 after 拦截器

        Args:
            skill_name: 技能名称
            result: 技能执行结果

        Returns:
            经过所有拦截器处理后的结果
        """
        current_result = result
        for interceptor in reversed(self._interceptors):
            current_result = interceptor.after(skill_name, current_result)
        return current_result

    def clear(self) -> None:
        """清除所有拦截器"""
        self._interceptors.clear()
        logger.info("Interceptor chain cleared")


class LoggingInterceptor:
    """日志拦截器

    记录技能执行前后的日志。
    """

    def before(self, skill_name: str, context: SkillContext) -> SkillContext:
        """记录执行前日志"""
        logger.info(
            "Executing skill",
            skill=skill_name,
            session_path=str(context.session_path)
        )
        return context

    def after(self, skill_name: str, result: SkillResult) -> SkillResult:
        """记录执行后日志"""
        if result.success:
            logger.info("Skill executed successfully", skill=skill_name)
        else:
            logger.error("Skill execution failed", skill=skill_name, error=result.error)
        return result


class RouteNotFoundError(Exception):
    """路由未找到异常

    当无法根据状态找到合适的技能时抛出。
    """

    pass


class SkillMiddleware:
    """技能中间件

    提供技能路由、拦截器管理和技能执行功能。
    """

    # 默认路由映射：task_type -> skill_name
    DEFAULT_ROUTE_MAPPING: Dict[str, str] = {
        "grilling": "grill-me",
        "qa": "grill-you",
        "advance": "advance-task",
        "continue": "continue-task",
        "review": "review-session",
    }

    # 关键词映射：keyword -> skill_name
    KEYWORD_MAPPING: Dict[str, str] = {
        "grill": "grill-me",
        "advance": "advance-task",
        "continue": "continue-task",
        "review": "review-session",
        "help": "review-system",
    }

    def __init__(
        self,
        registry: SkillRegistry,
        default_route: Optional[str] = None,
        route_mapping: Optional[Dict[str, str]] = None
    ) -> None:
        """初始化技能中间件

        Args:
            registry: 技能注册表
            default_route: 默认路由，当无匹配时使用
            route_mapping: 自定义路由映射
        """
        self._registry = registry
        self._default_route = default_route
        self._route_mapping = route_mapping or {}
        self._interceptor_chain = InterceptorChain()
        logger.info("SkillMiddleware initialized", default_route=default_route)

    def add_route(self, key: str, skill_name: str) -> None:
        """添加自定义路由

        Args:
            key: 路由键（task_type 或 keyword）
            skill_name: 目标技能名称
        """
        self._route_mapping[key] = skill_name
        logger.info("Route added", key=key, skill=skill_name)

    def route(self, state: Dict[str, Any]) -> str:
        """根据状态路由到合适的技能

        路由优先级：
        1. 自定义路由映射
        2. task_type 匹配
        3. user_query 关键词匹配
        4. 默认路由

        Args:
            state: 执行状态，可能包含 task_type 和 user_query

        Returns:
            技能名称

        Raises:
            RouteNotFoundError: 无法找到匹配的技能时
        """
        # 1. 检查自定义路由
        if "task_type" in state and state["task_type"] in self._route_mapping:
            skill_name = self._route_mapping[state["task_type"]]
            if self._validate_skill_exists(skill_name):
                return skill_name

        # 2. 检查 task_type 默认映射
        if "task_type" in state:
            task_type = state["task_type"]
            if task_type in self.DEFAULT_ROUTE_MAPPING:
                skill_name = self.DEFAULT_ROUTE_MAPPING[task_type]
                if self._validate_skill_exists(skill_name):
                    return skill_name

        # 3. 检查 user_query 关键词
        if "user_query" in state:
            query = state["user_query"].lower()
            for keyword, skill_name in self.KEYWORD_MAPPING.items():
                if keyword in query:
                    if self._validate_skill_exists(skill_name):
                        return skill_name

            # 检查自定义关键词映射
            for key, skill_name in self._route_mapping.items():
                if key in query:
                    if self._validate_skill_exists(skill_name):
                        return skill_name

        # 4. 检查默认路由
        if self._default_route:
            if self._validate_skill_exists(self._default_route):
                return self._default_route

        raise RouteNotFoundError(f"No route found for state: {state}")

    def _validate_skill_exists(self, skill_name: str) -> bool:
        """验证技能是否存在

        Args:
            skill_name: 技能名称

        Returns:
            技能是否存在
        """
        try:
            self._registry.get(skill_name)
            return True
        except Exception:
            return False

    def add_interceptor(self, interceptor: Interceptor) -> None:
        """添加拦截器

        Args:
            interceptor: 拦截器实例
        """
        self._interceptor_chain.add(interceptor)

    @property
    def interceptor_chain(self) -> InterceptorChain:
        """获取拦截器链"""
        return self._interceptor_chain

    def execute_skill(
        self,
        skill_name: str,
        context: SkillContext,
        loader: "SkillLoader"
    ) -> SkillResult:
        """执行技能

        应用拦截器链，加载技能内容，返回执行结果。

        Args:
            skill_name: 技能名称
            context: 技能上下文
            loader: 技能加载器

        Returns:
            技能执行结果

        Raises:
            Exception: 技能不存在或加载失败时
        """
        # 1. 验证技能存在
        try:
            self._registry.get(skill_name)
        except Exception as e:
            raise Exception(f"Skill '{skill_name}' not found in registry") from e

        # 2. 应用 before 拦截器
        try:
            modified_context = self._interceptor_chain.before(skill_name, context)
        except StopExecution as e:
            # 拦截器阻止执行
            return SkillResult(
                success=False,
                output=None,
                error=f"Execution stopped: {str(e)}",
                metadata={"skill_name": skill_name, "stopped_by_interceptor": True}
            )
        except Exception as e:
            # before 拦截器错误
            return SkillResult(
                success=False,
                output=None,
                error=f"Before interceptor error: {str(e)}",
                metadata={"skill_name": skill_name}
            )

        # 3. 加载并执行技能
        try:
            content = loader.load_skill(skill_name)
            # 这里只是加载内容，实际执行由调用方处理
            # 返回加载的内容作为 output
            result = SkillResult(
                success=True,
                output=content,
                metadata={"skill_name": skill_name, "loaded": True}
            )
        except Exception as e:
            result = SkillResult(
                success=False,
                output=None,
                error=f"Failed to load skill: {str(e)}",
                metadata={"skill_name": skill_name}
            )

        # 4. 应用 after 拦截器
        try:
            final_result = self._interceptor_chain.after(skill_name, result)
        except Exception as e:
            # after 拦截器错误，返回原始结果
            logger.warning("After interceptor failed, using original result", error=str(e))
            final_result = result

        return final_result
