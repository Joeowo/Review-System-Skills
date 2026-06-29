# Sub-Spec S2: 工具适配层

**父文档**: [01-master-spec.md](01-master-spec.md)
**预估 LOC**: ~1,150
**依赖**: S1 (异常处理)

---

## 目标 (Objective)

封装现有模块（AutoResearch、review_agent、skills）为 LangChain Tools，提供统一的调用接口。

---

## 组件分解 (Component Breakdown)

### T1: AutoResearch Tools (~300 LOC)

**目标**: 封装 AutoResearch 模块为 LangChain Tools

**源模块接口**:

```python
# AutoResearch/autoresearch/main.py
def research_single(topic: str, research_type: str = "通用", depth: str = "comprehensive") -> str:
    """单次研究模式

    Args:
        topic: 研究主题
        research_type: 研究类型（技术/学术/通用）
        depth: 研究深度（comprehensive/deep/survey）

    Returns:
        报告文件路径
    """
    pass

def research_deep(topic: str, research_type: str = "通用") -> str:
    """深度研究模式

    Args:
        topic: 研究主题
        research_type: 研究类型

    Returns:
        报告文件路径
    """
    pass
```

**Tool 封装**:

```python
# tools/autoresearch_tools.py
from langchain_core.tools import tool
from AutoResearch.autoresearch.main import research_single, research_deep

@tool
def research_single_tool(
    topic: str,
    research_type: str = "通用",
    depth: str = "comprehensive"
) -> str:
    """单次研究模式

    执行针对指定主题的综合研究，生成结构化报告。

    Args:
        topic: 研究主题，例如 "RAG 技术调研"
        research_type: 研究类型（技术/学术/通用）
        depth: 研究深度
            - comprehensive: 综合研究，覆盖多个维度
            - deep: 深度研究，聚焦核心问题
            - survey: 快速调研，概览性质

    Returns:
        报告文件路径，例如 "output/reports/topic_20250628.md"

    Raises:
        ResearchTimeoutError: 研究超时
        ResearchInsufficientError: 研究内容不足
    """
    try:
        return research_single(topic, research_type, depth)
    except TimeoutError as e:
        raise ResearchTimeoutError(f"研究超时: {e}")
    except ValueError as e:
        raise ResearchInsufficientError(f"研究内容不足: {e}")

@tool
def research_deep_tool(topic: str, research_type: str = "通用") -> str:
    """深度研究模式

    执行多维度深度研究，自动生成研究计划并执行。

    Args:
        topic: 研究主题
        research_type: 研究类型（技术/学术/通用）

    Returns:
        报告文件路径
    """
    try:
        return research_deep(topic, research_type)
    except Exception as e:
        raise DegradableError(f"深度研究失败，降级到单次研究: {e}", fallback="single_research")
```

**成功标准**:
- Tool 可正确调用 AutoResearch 模块
- 异常正确转换为框架异常类型
- 返回值路径可被后续节点使用

---

### T2: review_agent Tools (~250 LOC)

**目标**: 封装 review_agent 核心功能为 Tools

**源模块接口**:

```python
# review_agent/services/qa_assistant.py
class QAAssistant:
    def generate_question(self, topic: str, difficulty: str = "medium") -> str:
        """生成问题"""
        pass

    def evaluate_answer(self, question: str, answer: str) -> dict:
        """评估答案"""
        pass
```

**Tool 封装**:

```python
# tools/review_agent_tools.py
from langchain_core.tools import tool
from review_agent.services.qa_assistant import QAAssistant

@tool
def generate_question_tool(topic: str, difficulty: str = "medium") -> str:
    """生成学习问题

    基于指定主题生成难度适中的问题。

    Args:
        topic: 学习主题
        difficulty: 难度级别 (easy/medium/hard)

    Returns:
        生成的问题文本
    """
    assistant = QAAssistant()
    return assistant.generate_question(topic, difficulty)

@tool
def evaluate_answer_tool(question: str, answer: str) -> dict:
    """评估答案质量

    评估用户对问题的回答质量。

    Args:
        question: 问题文本
        answer: 用户回答

    Returns:
        评估结果字典: {"score": 0-100, "feedback": "..."}
    """
    assistant = QAAssistant()
    return assistant.evaluate_answer(question, answer)
```

**成功标准**:
- 问题生成功能正常
- 答案评估返回结构化结果

---

### T3: Skills 适配器 (~600 LOC)

**目标**: 适配现有 skills 为可调用的 Tool/节点

**适配策略**:

由于现有 skills 基于 Claude Code skill 调用机制，需要创建适配器层：

```python
# tools/skills_adapters.py
from typing import Dict, Any
from pathlib import Path

class SkillsAdapter:
    """Skills 适配器基类"""

    def __init__(self, session_path: str):
        """初始化适配器

        Args:
            session_path: 会话目录路径
        """
        self.session_path = Path(session_path)

    def load_context(self) -> Dict[str, str]:
        """加载 CONTEXT.md"""
        pass

    def update_context(self, key: str, value: str) -> None:
        """更新 CONTEXT.md"""
        pass

    def load_task_progress(self) -> Dict[str, Any]:
        """加载 Task.md"""
        pass

    def update_task_progress(self, task_id: str, status: str) -> None:
        """更新 Task.md"""
        pass

class GrillMeAdapter(SkillsAdapter):
    """grill-me skill 适配器"""

    def generate_questions(self, task_id: str, count: int = 5) -> list:
        """生成 grill-me 问题"""
        context = self.load_context()
        task = self.load_task_progress().get(task_id, {})

        # 模拟 grill-me 逻辑
        questions = []
        for i in range(count):
            questions.append({
                "question": f"关于 {task.get('topic', '')} 的第 {i+1} 个问题",
                "expected": "...",
                "difficulty": "medium"
            })
        return questions

    def evaluate_answers(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """评估答案并更新 CONTEXT.md"""
        results = {}
        for q_id, answer in answers.items():
            results[q_id] = {
                "correct": True,  # 简化示例
                "feedback": "回答准确"
            }

        # 更新 CONTEXT.md
        self.update_context("last_grill_results", str(results))
        return results

class GrillYouAdapter(SkillsAdapter):
    """grill-you skill 适配器"""

    def suggest_questions(self, topic: str, count: int = 3) -> list:
        """建议用户可以问的问题"""
        return [
            f"请解释 {topic} 的核心原理",
            f"{topic} 与相关概念有什么区别",
            f"{topic} 的典型应用场景是什么"
        ]

class AdvanceTaskAdapter(SkillsAdapter):
    """advance-task skill 适配器"""

    def complete_task(self, task_id: str, notes: str = "") -> None:
        """完成任务，更新状态"""
        self.update_task_progress(task_id, "completed")

        # 生成 handoff.md
        handoff_path = self.session_path / "handoff.md"
        handoff_content = f"""# 会话交接

## 当前状态
- 完成任务: {task_id}
- 时间: {datetime.now().isoformat()}

## 备注
{notes}

## 下一步
"""
        handoff_path.write_text(handoff_content, encoding="utf-8")
```

**Tool 封装**:

```python
@tool
def grill_me_tool(session_path: str, task_id: str, count: int = 5) -> dict:
    """执行 grill-me 流程

    Args:
        session_path: 会话目录
        task_id: 任务 ID
        count: 生成问题数量

    Returns:
        问题列表和评估结果
    """
    adapter = GrillMeAdapter(session_path)
    questions = adapter.generate_questions(task_id, count)
    return {"questions": questions}
```

**成功标准**:
- 可正确加载和更新 CONTEXT.md/Task.md
- 适配器行为与原 skill 一致
- handoff.md 生成正确

---

## 适配器层 (Adapters Layer)

```python
# tools/adapters/autoresearch_adapter.py
class AutoResearchAdapter:
    """AutoResearch 适配器，提供结构化接口"""

    @staticmethod
    def single(topic: str, research_type: str = "通用", depth: str = "comprehensive") -> dict:
        """单次研究，返回结构化结果"""
        from AutoResearch.autoresearch.main import research_single

        filepath = research_single(topic, research_type, depth)

        # 解析报告文件
        return {
            "status": "success",
            "filepath": filepath,
            "topic": topic,
            "type": research_type
        }
```

---

## 测试策略

### 单元测试

| 组件 | 测试重点 |
|------|----------|
| AutoResearch Tools | 调用成功、异常转换 |
| review_agent Tools | 问题生成、答案评估 |
| Skills 适配器 | 文件读写、状态更新 |

### 集成测试

- Tool 通过 LangChain 正确调用
- 适配器与文件系统交互正确

### Mock 测试

```python
# tests/tools/test_autoresearch_tools.py
from unittest.mock import patch

@patch('AutoResearch.autoresearch.main.research_single')
def test_research_single_tool(mock_research):
    mock_research.return_value = "output/test.md"
    result = research_single_tool.invoke({"topic": "测试"})
    assert result == "output/test.md"
```

---

## 边界规则

### Always Do
- 所有 Tool 调用必须通过异常处理器
- 适配器更新文件前验证内容
- 返回值必须有明确类型

### Ask First
- 新增 Tool 封装
- 修改适配器接口

### Never Do
- 在 Tool 中直接修改持久层文件
- 忽略源模块的异常

---

## 成功标准

- [ ] AutoResearch 调用成功率 ≥ 95%
- [ ] review_agent 功能正常
- [ ] Skills 适配器与原行为一致
- [ ] 所有测试通过

---

## 依赖项

```toml
[tool.poetry.dependencies]
AutoResearch = {path = "../AutoResearch"}
review_agent = {path = "../review_agent"}
langchain-core = "*"
```

---

**下一步**: S3 Workflow - 学习研究
