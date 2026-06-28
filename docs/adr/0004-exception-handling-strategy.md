# ADR 0004: 异常处理与降级策略

**状态**: 已采纳
**日期**: 2026-06-28
**决策者**: Agent 框架设计团队

---

## 上下文

Agent 框架调用外部服务（LLM API、WebSearch）和本地模块，可能遇到各种异常情况：

| 异常类型 | 示例 |
|---------|------|
| **API 失败** | LLM API 超时、限流、服务不可用 |
| **数据不足** | 研究报告内容过少、概念提取失败 |
| **资源冲突** | 会话目录已存在、文件权限问题 |
| **用户输入** | 无效的研究主题、空输入 |

需要统一的异常处理策略。

---

## 决策

采用**分层异常处理 + 降级策略**：

### 层级定义

| 层级 | 处理方式 | 示例 |
|------|---------|------|
| **L1: 重试** | 瞬时错误，自动重试 | API 超时、网络抖动 |
| **L2: 降级** | 降低服务质量，继续执行 | 深度研究 → 浅度研究 |
| **L3: 跳过** | 跳过当前步骤，标记警告 | 非关键功能失败 |
| **L4: 终止** | 无法继续，终止流程 | 核心依赖不可用 |

---

## 理由

### 分层处理的论据

1. **用户体验**: 避免因小问题导致整个流程失败
2. **弹性**: 大部分场景下可以继续完成核心功能
3. **可观测性**: 不同层级记录不同级别的日志

### 降级策略的论据

1. **核心价值保证**: 深度失败可降级到浅度，仍能产出价值
2. **用户选择**: 关键节点让用户确认是否继续

---

## 后果

### 正面影响

- 提高系统可用性
- 更好的用户体验
- 可预测的行为

### 负面影响

- 增加逻辑复杂度
- 可能掩盖部分错误
- 降级后的结果质量可能不满足期望

### 缓解措施

- **明确日志**: 记录降级原因和层级
- **用户通知**: 关键降级需通知用户
- **质量指标**: 跟踪降级率，优化上游服务

---

## 实施细节

### 异常分类

```python
# core/exceptions.py

class AgentException(Exception):
    """Agent 框架异常基类"""
    level: str = "terminate"  # retry, degrade, skip, terminate

class RetryableError(AgentException):
    """可重试错误"""
    level = "retry"
    max_retries: int = 2

class DegradableError(AgentException):
    """可降级错误"""
    level = "degrade"

class SkippableError(AgentException):
    """可跳过错误"""
    level = "skip"

class TerminalError(AgentException):
    """终止错误"""
    level = "terminate"
```

### 处理器实现

```python
# core/exception_handler.py

class ExceptionHandler:
    """异常处理器"""
    
    def handle(self, error: Exception, context: dict) -> dict:
        """处理异常，返回下一步动作"""
        if isinstance(error, RetryableError):
            return self._retry(error, context)
        elif isinstance(error, DegradableError):
            return self._degrade(error, context)
        elif isinstance(error, SkippableError):
            return self._skip(error, context)
        else:
            return self._terminate(error, context)
    
    def _retry(self, error: RetryableError, context: dict) -> dict:
        retry_count = context.get("retry_count", 0)
        if retry_count < error.max_retries:
            return {
                "next_action": "retry",
                "retry_count": retry_count + 1,
                "message": f"重试 {retry_count + 1}/{error.max_retries}"
            }
        return self._degrade(error, context)
    
    def _degrade(self, error: DegradableError, context: dict) -> dict:
        return {
            "next_action": "degrade",
            "fallback": error.fallback,
            "message": f"降级: {error.message}"
        }
    
    def _skip(self, error: SkippableError, context: dict) -> dict:
        return {
            "next_action": "skip",
            "message": f"跳过: {error.message}"
        }
    
    def _terminate(self, error: Exception, context: dict) -> dict:
        return {
            "next_action": "terminate",
            "error": str(error),
            "message": f"终止: {error.message}"
        }
```

### 具体异常定义

```python
# AutoResearch 相关异常

class ResearchTimeoutError(RetryableError):
    """研究超时"""
    max_retries = 2

class ResearchInsufficientError(DegradableError):
    """研究内容不足"""
    fallback = "use_summary"  # 使用摘要继续

class ConceptExtractionFailedError(DegradableError):
    """概念提取失败"""
    fallback = "use_topic_as_concept"  # 用主题作为概念

class SessionExistsError(DegradableError):
    """会话已存在"""
    fallback = "create_new_session"  # 创建新会话

class LLMAPIError(RetryableError):
    """LLM API 错误"""
    max_retries = 3
```

---

## 相关决策

- [ADR 0001: 双状态并行管理策略](0001-dual-state-management.md)

---

**文档版本**: 1.0
