# Sub-Spec S3: Workflow - 学习研究

**父文档**: [01-master-spec.md](01-master-spec.md)
**预估 LOC**: ~850
**依赖**: S1 (核心框架), S2 (工具适配)

---

## 目标 (Objective)

实现学习研究相关的业务流程：
1. **F1: 学习研究一体化** - AutoResearch + 概念提取 + grilling 循环
2. **F2: 知识问答增强** - review_agent 深度集成

---

## 组件分解 (Component Breakdown)

### W1: F1 学习研究一体化 (~500 LOC)

**目标**: 端到端执行从研究到掌握的学习流程

**流程图**:

```
┌─────────────┐
│    Start    │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  研究阶段 (Research)                                      │
│  ├─ 调用 AutoResearch                                   │
│  ├─ 生成研究报告                                         │
│  └─ 提取关键概念                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  确认节点 (Confirmation)                                 │
│  ├─ 展示研究摘要                                         │
│  └─ 用户确认是否继续                                     │
└──────────────────┬──────────────────────────────────────┘
                   │ 继续研究
                   ├──────────────┐
                   │              │
                   ↓              ↓
┌─────────────────────────┐  ┌─────────────┐
│  概念提取 (Extract)      │  │ 重新研究     │
│  ├─ 解析报告            │  │              │
│  └─ 生成概念列表        │  └──────┬──────┘
└──────────┬──────────────┘         │
           │                        │
           │ 继续学习               │ 重新开始
           ↓                        │
┌─────────────────────────────────────────────────────────┐
│  任务分解 (Breakdown)                                     │
│  ├─ 按概念分解学习任务                                   │
│  └─ 初始化 Task.md                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  Grilling 循环                                            │
│  ┌─────────────┐    ┌─────────────┐                    │
│  │  grill-me   │ ←→ │  grill-you  │ ←──┐               │
│  │ (AI考你)    │    │ (你考AI)    │    │               │
│  └─────────────┘    └─────────────┘    │ 循环直到      │
│         │                  │          │ 掌握           │
│         └─────────→ 评估 ←─────────────┘                │
│                    │                                     │
│              掌握? ─No─→ 返回                            │
│                   │                                      │
│              Yes ↓                                       │
└──────────────────┼──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  保存进度 (Save)                                          │
│  ├─ 更新 Task.md                                          │
│  ├─ 更新 CONTEXT.md                                       │
│  └─ 生成 handoff.md                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
              ┌─────────┐
              │  End    │
              └─────────┘
```

**Workflow 定义**:

```python
# workflows/f1_learning_research.py
from langgraph.graph import StateGraph, END
from core.state import AgentState
from core.checkpoint import CheckpointManager
from tools.autoresearch_tools import research_single_tool
from tools.skills_adapters import GrillMeAdapter, GrillYouAdapter

def create_f1_workflow() -> StateGraph:
    """创建 F1 学习研究一体化 Workflow"""

    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("research", research_node)
    workflow.add_node("extract_concepts", extract_concepts_node)
    workflow.add_node("breakdown_tasks", breakdown_tasks_node)
    workflow.add_node("grill_me", grill_me_node)
    workflow.add_node("grill_you", grill_you_node)
    workflow.add_node("evaluate_mastery", evaluate_mastery_node)
    workflow.add_node("save_progress", save_progress_node)

    # 确认节点
    workflow.add_node("research_confirmation", research_confirmation_node)

    # 设置入口
    workflow.set_entry_point("research")

    # 添加边
    workflow.add_edge("research", "research_confirmation")
    workflow.add_conditional_edges(
        "research_confirmation",
        should_continue_research,
        {
            "continue": "extract_concepts",
            "rethink": "research"
        }
    )

    workflow.add_edge("extract_concepts", "breakdown_tasks")
    workflow.add_edge("breakdown_tasks", "grill_me")

    # Grilling 循环
    workflow.add_edge("grill_me", "evaluate_mastery")
    workflow.add_conditional_edges(
        "evaluate_mastery",
        check_mastery,
        {
            "continue": "grill_you",
            "completed": "save_progress"
        }
    )

    workflow.add_edge("grill_you", "grill_me")

    workflow.add_edge("save_progress", END)

    return workflow
```

**节点实现**:

```python
def research_node(state: AgentState) -> Dict[str, Any]:
    """研究节点"""
    try:
        result = research_single_tool.invoke({
            "topic": state["topic"],
            "research_type": "技术",
            "depth": "comprehensive"
        })

        return {
            "report_path": result,
            "current_step": "research_complete",
            "error_message": None
        }
    except Exception as e:
        return {
            "error_message": str(e),
            "current_step": "research_failed"
        }

def research_confirmation_node(state: AgentState) -> Dict[str, Any]:
    """研究完成确认节点"""
    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": f"""
研究已完成！

主题: {state['topic']}
报告: {state['report_path']}

是否继续基于此报告学习？
回复 '继续' 或 '重新研究'
        """
    }

def extract_concepts_node(state: AgentState) -> Dict[str, Any]:
    """概念提取节点"""
    # 解析报告文件，提取关键概念
    concepts = extract_concepts_from_report(state["report_path"])

    return {
        "key_concepts": concepts,
        "current_step": "concepts_extracted"
    }

def breakdown_tasks_node(state: AgentState) -> Dict[str, Any]:
    """任务分解节点"""
    # 按概念分解学习任务
    tasks = []
    for concept in state["key_concepts"]:
        tasks.append({
            "id": f"task_{len(tasks)+1}",
            "concept": concept,
            "status": "pending",
            "round": 0
        })

    # 初始化 Task.md
    initialize_task_md(state["session_path"], tasks)

    return {
        "tasks": tasks,
        "current_task_id": tasks[0]["id"] if tasks else None,
        "current_step": "tasks_breakdown"
    }

def grill_me_node(state: AgentState) -> Dict[str, Any]:
    """grill-me 节点"""
    adapter = GrillMeAdapter(state["session_path"])
    questions = adapter.generate_questions(
        state["current_task_id"],
        count=3
    )

    return {
        "current_questions": questions,
        "current_step": "grilling_me"
    }

def grill_you_node(state: AgentState) -> Dict[str, Any]:
    """grill-you 节点"""
    adapter = GrillYouAdapter(state["session_path"])
    suggestions = adapter.suggest_questions(
        state["topic"],
        count=3
    )

    return {
        "user_question_suggestions": suggestions,
        "current_step": "grilling_you"
    }

def evaluate_mastery_node(state: AgentState) -> Dict[str, Any]:
    """评估掌握程度节点"""
    # 基于问答结果评估
    # 这里简化处理
    mastered = len(state.get("answers", [])) >= 2

    return {
        "mastery_level": "completed" if mastered else "continuing",
        "current_step": "mastery_evaluated"
    }

def save_progress_node(state: AgentState) -> Dict[str, Any]:
    """保存进度节点"""
    adapter = AdvanceTaskAdapter(state["session_path"])
    adapter.complete_task(
        state["current_task_id"],
        notes=f"完成 {state['round']} 轮学习"
    )

    return {
        "current_step": "progress_saved"
    }
```

**成功标准**:
- Workflow 可端到端执行
- 确认节点正确暂停
- Grilling 循环可正确退出
- 进度正确保存

---

### W2: F2 知识问答增强 (~350 LOC)

**目标**: 深度集成 review_agent，提供增强的知识问答

**流程图**:

```
┌─────────────┐
│    Start    │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  加载知识库 (Load Knowledge)                              │
│  ├─ 读取 CONTEXT.md                                      │
│  └─ 读取 sources/ 目录                                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  接收问题 (Receive Question)                              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  知识查询 (Query)                                         │
│  ├─ 检索本地知识库                                       │
│  ├─ 调用 review_agent                                    │
│  └─ 必要时进行网络搜索                                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  生成回答 (Generate Answer)                              │
│  └─ 综合信息生成结构化回答                               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
              ┌─────────┐
              │  End    │
              └─────────┘
```

**Workflow 定义**:

```python
# workflows/f2_qa_enhanced.py
def create_f2_workflow() -> StateGraph:
    """创建 F2 知识问答增强 Workflow"""

    workflow = StateGraph(AgentState)

    workflow.add_node("load_knowledge", load_knowledge_node)
    workflow.add_node("query_knowledge", query_knowledge_node)
    workflow.add_node("generate_answer", generate_answer_node)

    workflow.set_entry_point("load_knowledge")
    workflow.add_edge("load_knowledge", "query_knowledge")
    workflow.add_edge("query_knowledge", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow
```

**成功标准**:
- 可正确加载知识库
- 答案基于知识库内容
- 支持追问和澄清

---

## 测试策略

### 单元测试

| 组件 | 测试重点 |
|------|----------|
| F1 节点 | 各节点状态转换 |
| F2 节点 | 知识库加载、查询 |

### 集成测试

- F1 端到端流程测试
- F2 端到端流程测试
- 确认节点暂停/恢复测试

### E2E 测试

```python
# tests/e2e/test_f1_workflow.py
def test_f1_full_workflow():
    """测试 F1 完整流程"""
    workflow = create_f1_workflow()
    checkpointer = CheckpointManager().get_checkpointer()

    app = workflow.compile(checkpointer=checkpointer)

    # 执行流程
    config = {"configurable": {"thread_id": "test_f1"}}
    result = app.invoke({
        "topic": "测试主题",
        "session_path": "/tmp/test_session"
    }, config=config)

    assert result["current_step"] == "progress_saved"
```

---

## 边界规则

### Always Do
- Workflow 入口验证必要参数
- 关键节点记录日志
- 异常通过异常处理器处理

### Ask First
- 修改 Workflow 结构
- 新增/删除节点

### Never Do
- 硬编码节点顺序
- 跳过确认节点（除非配置）

---

## 成功标准

- [ ] F1 Workflow 端到端成功率 ≥ 90%
- [ ] F2 Workflow 端到端成功率 ≥ 90%
- [ ] Checkpoint 恢复正确
- [ ] 所有测试通过

---

## 依赖项

```toml
[tool.poetry.dependencies]
langgraph = "*"
langchain-core = "*"
```

---

**下一步**: S4 Workflow - 学术写作复习
