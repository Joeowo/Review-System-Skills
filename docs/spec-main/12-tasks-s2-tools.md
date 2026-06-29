# Tasks: Sub-Spec S2 - 工具适配层

**父文档**: [10-master-plan.md](10-master-plan.md)
**预估总 LOC**: ~1,150

---

## Task 1: 实现 AutoResearch Tools (~200 LOC)

**描述**: 封装 AutoResearch 模块为 LangChain Tools

**验收标准**:
- [ ] research_single_tool 可调用
- [ ] research_deep_tool 可调用
- [ ] 异常正确转换为框架类型
- [ ] 返回值格式统一

**实现要点**:
```python
# tools/autoresearch_tools.py
from langchain_core.tools import tool
from AutoResearch.autoresearch.main import research_single, research_deep
from core.exceptions import ResearchTimeoutError, ResearchInsufficientError

@tool
def research_single_tool(topic: str, research_type: str = "通用",
                          depth: str = "comprehensive") -> str:
    """单次研究模式"""
    try:
        return research_single(topic, research_type, depth)
    except TimeoutError as e:
        raise ResearchTimeoutError(f"研究超时: {e}")
    except ValueError as e:
        raise ResearchInsufficientError(f"研究内容不足: {e}")
```

**测试**:
- 正常调用测试
- 异常转换测试
- 返回值验证

**依赖**: S1 (异常处理)

**预计时间**: 5 小时

---

## Task 2: 实现 AutoResearch 适配器 (~100 LOC)

**描述**: 提供结构化接口的适配器

**验收标准**:
- [ ] 适配器返回结构化数据
- [ ] 报告文件解析正确
- [ ] 错误处理完善

**实现要点**:
```python
# tools/adapters/autoresearch_adapter.py
class AutoResearchAdapter:
    @staticmethod
    def single(topic: str, research_type: str, depth: str) -> dict:
        filepath = research_single(topic, research_type, depth)
        return {
            "status": "success",
            "filepath": filepath,
            "topic": topic
        }
```

**测试**:
- 适配器调用测试
- 错误处理测试

**依赖**: Task 1

**预计时间**: 3 小时

---

## Task 3: 实现 review_agent Tools (~150 LOC)

**描述**: 封装 review_agent 核心功能

**验收标准**:
- [ ] generate_question_tool 可调用
- [ ] evaluate_answer_tool 可调用
- [ ] 返回值格式统一

**实现要点**:
```python
# tools/review_agent_tools.py
from langchain_core.tools import tool
from review_agent.services.qa_assistant import QAAssistant

@tool
def generate_question_tool(topic: str, difficulty: str = "medium") -> str:
    """生成学习问题"""
    assistant = QAAssistant()
    return assistant.generate_question(topic, difficulty)
```

**测试**:
- 问题生成测试
- 答案评估测试

**依赖**: S1 (异常处理)

**预计时间**: 4 小时

---

## Task 4: 实现 Skills 适配器基类 (~150 LOC)

**描述**: 实现 Skills 适配器基础功能

**验收标准**:
- [ ] 可加载 CONTEXT.md
- [ ] 可更新 CONTEXT.md
- [ ] 可加载 Task.md
- [ ] 可更新 Task.md

**实现要点**:
```python
# tools/skills_adapters.py
class SkillsAdapter:
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)

    def load_context(self) -> Dict[str, str]:
        # 加载 CONTEXT.md
        pass

    def update_context(self, key: str, value: str) -> None:
        # 更新 CONTEXT.md
        pass
```

**测试**:
- 文件加载测试
- 文件更新测试
- 原子性测试

**依赖**: S1 (State 同步)

**预计时间**: 5 小时

---

## Task 5: 实现 GrillMeAdapter (~150 LOC)

**描述**: 实现 grill-me skill 适配

**验收标准**:
- [ ] 可生成 grill-me 问题
- [ ] 可评估答案
- [ ] 可更新 CONTEXT.md

**实现要点**:
```python
class GrillMeAdapter(SkillsAdapter):
    def generate_questions(self, task_id: str, count: int = 5) -> list:
        context = self.load_context()
        # 生成问题
        pass

    def evaluate_answers(self, answers: Dict[str, str]) -> Dict:
        # 评估并更新
        pass
```

**测试**:
- 问题生成测试
- 答案评估测试
- 状态更新测试

**依赖**: Task 4

**预计时间**: 5 小时

---

## Task 6: 实现 GrillYouAdapter (~100 LOC)

**描述**: 实现 grill-you skill 适配

**验收标准**:
- [ ] 可建议用户问题
- [ ] 问题质量合理

**实现要点**:
```python
class GrillYouAdapter(SkillsAdapter):
    def suggest_questions(self, topic: str, count: int = 3) -> list:
        return [
            f"请解释 {topic} 的核心原理",
            # ...
        ]
```

**测试**:
- 问题建议测试

**依赖**: Task 4

**预计时间**: 3 小时

---

## Task 7: 实现 AdvanceTaskAdapter (~100 LOC)

**描述**: 实现 advance-task skill 适配

**验收标准**:
- [ ] 可完成任务
- [ ] 可生成 handoff.md
- [ ] handoff.md 格式正确

**实现要点**:
```python
class AdvanceTaskAdapter(SkillsAdapter):
    def complete_task(self, task_id: str, notes: str = "") -> None:
        self.update_task_progress(task_id, "completed")
        # 生成 handoff.md
        pass
```

**测试**:
- 任务完成测试
- handoff.md 生成测试

**依赖**: Task 4

**预计时间**: 3 小时

---

## Task 8: 集成测试 (~200 LOC)

**描述**: S2 集成测试

**验收标准**:
- [ ] AutoResearch Tool 集成测试通过
- [ ] review_agent Tool 集成测试通过
- [ ] Skills 适配器集成测试通过
- [ ] 跨适配器集成测试通过

**测试**:
```python
# tests/integration/test_s2_integration.py
def test_autoresearch_integration():
    # 完整调用流程
    pass

def test_skills_adapter_integration():
    # 适配器端到端测试
    pass
```

**依赖**: 所有前置任务

**预计时间**: 5 小时

---

## Summary

- **总任务数**: 8
- **总预估 LOC**: ~1,150
- **关键路径**: Task 4 → Task 5/6/7 → Task 8
- **并行机会**: Task 1/3 可并行，Task 5/6/7 可并行

→ **Human**: 审查任务列表，批准后开始实施
