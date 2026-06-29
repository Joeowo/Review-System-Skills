# Sub-Spec S4: Workflow - 学术写作复习

**父文档**: [01-master-spec.md](01-master-spec.md)
**预估 LOC**: ~950
**依赖**: S1 (核心框架), S2 (工具适配)

---

## 目标 (Objective)

实现学术写作和复习计划相关的业务流程：
1. **F3: 学术写作全流程** - 研究 → 写作 → Review 循环
2. **F4: 复习计划生成** - SM2 调度器集成

---

## 组件分解 (Component Breakdown)

### W3: F3 学术写作全流程 (~550 LOC)

**目标**: 实现人机协同学术写作完整流程

**流程图**:

```
┌─────────────┐
│    Start    │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  阶段1: 澄清 (Clarification)                             │
│  ├─ 确定研究方向                                         │
│  ├─ 明确核心论点                                         │
│  ├─ 识别关键问题                                         │
│  └─ 用户确认                                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  阶段2: 研究 (Research)                                   │
│  ┌─────────────────────────────────────────────────┐    │
│  │  调用 AutoResearch 进行文献调研                   │    │
│  │  ├─ 生成研究计划                                  │    │
│  │  ├─ 执行多维度研究                                │    │
│  │  └─ 生成结构化报告                                │    │
│  └─────────────────────────────────────────────────┘    │
│                        │                                  │
│                        ↓                                  │
│  ┌─────────────────────────────────────────────────┐    │
│  │  研究确认 (Confirmation)                         │    │
│  └────────────────────┬────────────────────────────┘    │
│                        │                                  │
│          ┌────────────┴────────────┐                   │
│          │                         │                   │
│          ↓ 继续写作              ↓ 补充研究              │
└──────────────────────┐    ┌─────────────────────┐       │
                       │    │                     │       │
                       ↓    │                     ↓       │
┌─────────────────────────────────────────────────────────┐
│  阶段3: 写作 (Writing)                                    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  3.1 大纲生成 (Outline)                           │    │
│  │      ├─ 基于研究生成结构化大纲                    │    │
│  │      ├─ 用户审查和调整                            │    │
│  │      └─ 确认大纲                                  │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  3.2 分段写作 (Draft)                             │    │
│  │      ├─ Introduction → Literature Review          │    │
│  │      ├─ Methods → Results → Discussion            │    │
│  │      └─ Conclusion                                │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  3.3 表达优化 (Refine)                            │    │
│  │      ├─ 学术语气调整                              │    │
│  │      ├─ 逻辑流畅性                                │    │
│  │      └─ 语言精炼                                  │    │
│  └─────────────────────────────────────────────────┘    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  阶段4: Review 循环                                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │  4.1 自我审查 (Self-Review)                       │    │
│  │      ├─ 论点一致性检查                            │    │
│  │      ├─ 证据充分性检查                            │    │
│  │      └─ 逻辑结构检查                              │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  4.2 用户审查 (User Review)                       │    │
│  │      └─ 用户确认或提出修改建议                    │    │
│  ├──────────────────────────────────────────────────┤    │
│  │  4.3 迭代改进 (Iterate)                           │    │
│  │      └─ 根据反馈修改 → 返回审查                   │    │
│  └─────────────────────────────────────────────────┘    │
│                        │                                  │
│                        ↓ 满意                            │
│                   ┌─────────┐                           │
│                   │ 完成    │                           │
│                   └────┬────┘                           │
└──────────────────────┼──────────────────────────────────┘
                       │
                       ↓
                  ┌─────────┐
                  │  End    │
                  └─────────┘
```

**Workflow 定义**:

```python
# workflows/f3_academic_writing.py
from langgraph.graph import StateGraph, END
from enum import Enum

class WritingPhase(Enum):
    """写作阶段"""
    CLARIFICATION = "clarification"
    RESEARCH = "research"
    WRITING = "writing"
    REVIEW = "review"
    COMPLETED = "completed"

def create_f3_workflow() -> StateGraph:
    """创建 F3 学术写作全流程 Workflow"""

    workflow = StateGraph(AgentState)

    # 澄清阶段
    workflow.add_node("clarify_topic", clarify_topic_node)
    workflow.add_node("clarify_confirmation", clarify_confirmation_node)

    # 研究阶段
    workflow.add_node("plan_research", plan_research_node)
    workflow.add_node("execute_research", execute_research_node)
    workflow.add_node("research_confirmation", research_confirmation_node)

    # 写作阶段
    workflow.add_node("generate_outline", generate_outline_node)
    workflow.add_node("outline_confirmation", outline_confirmation_node)
    workflow.add_node("draft_section", draft_section_node)
    workflow.add_node("refine_section", refine_section_node)

    # Review 阶段
    workflow.add_node("self_review", self_review_node)
    workflow.add_node("user_review", user_review_node)
    workflow.add_node("iterate_section", iterate_section_node)

    # 完成
    workflow.add_node("finalize_paper", finalize_paper_node)

    # 设置入口
    workflow.set_entry_point("clarify_topic")

    # 澄清阶段边
    workflow.add_edge("clarify_topic", "clarify_confirmation")
    workflow.add_conditional_edges(
        "clarify_confirmation",
        lambda s: "continue" if s.get("clarification_approved") else "clarify_topic",
        {
            "continue": "plan_research",
            "clarify_topic": "clarify_topic"
        }
    )

    # 研究阶段边
    workflow.add_edge("plan_research", "execute_research")
    workflow.add_edge("execute_research", "research_confirmation")
    workflow.add_conditional_edges(
        "research_confirmation",
        lambda s: "writing" if s.get("research_approved") else "plan_research",
        {
            "writing": "generate_outline",
            "plan_research": "plan_research"
        }
    )

    # 写作阶段边
    workflow.add_edge("generate_outline", "outline_confirmation")
    workflow.add_conditional_edges(
        "outline_confirmation",
        lambda s: "draft" if s.get("outline_approved") else "generate_outline",
        {
            "draft": "draft_section",
            "generate_outline": "generate_outline"
        }
    )

    workflow.add_edge("draft_section", "refine_section")
    workflow.add_conditional_edges(
        "refine_section",
        check_section_complete,
        {
            "next_section": "draft_section",
            "review": "self_review"
        }
    )

    # Review 循环边
    workflow.add_edge("self_review", "user_review")
    workflow.add_conditional_edges(
        "user_review",
        lambda s: "finalize" if s.get("review_approved") else "iterate",
        {
            "finalize": "finalize_paper",
            "iterate": "iterate_section"
        }
    )

    workflow.add_edge("iterate_section", "refine_section")
    workflow.add_edge("finalize_paper", END)

    return workflow
```

**关键节点实现**:

```python
def clarify_topic_node(state: AgentState) -> Dict[str, Any]:
    """澄清研究主题节点"""
    topic = state.get("topic", "")

    # 生成澄清问题
    questions = [
        f"关于 '{topic}'，你的核心论点是什么？",
        f"这项研究的主要创新点在哪里？",
        f"目标读者是谁？",
        f"是否有特定的研究方法要求？"
    ]

    return {
        "clarification_questions": questions,
        "current_step": "clarification",
        "writing_phase": WritingPhase.CLARIFICATION.value
    }

def plan_research_node(state: AgentState) -> Dict[str, Any]:
    """规划研究节点"""
    topic = state["topic"]
    core_argument = state.get("core_argument", "")

    # 基于澄清信息生成研究计划
    research_plan = {
        "main_topics": [
            f"{topic} 理论基础",
            f"{topic} 现有研究综述",
            f"{topic} 方法论",
            f"{topic} 实证研究"
        ],
        "search_queries": [
            topic,
            core_argument,
            f"{topic} review",
            f"{topic} methodology"
        ],
        "estimated_papers": 20
    }

    return {
        "research_plan": research_plan,
        "current_step": "research_planned",
        "writing_phase": WritingPhase.RESEARCH.value
    }

def generate_outline_node(state: AgentState) -> Dict[str, Any]:
    """生成大纲节点"""
    research_report = state.get("research_report_path", "")
    core_argument = state.get("core_argument", "")

    # 基于研究生成大纲
    outline = {
        "title": state["topic"],
        "sections": [
            {
                "name": "Introduction",
                "subsections": [
                    "背景介绍",
                    "研究问题",
                    "核心论点",
                    "论文结构"
                ]
            },
            {
                "name": "Literature Review",
                "subsections": [
                    "理论基础",
                    "现有研究综述",
                    "研究空白"
                ]
            },
            {
                "name": "Methods",
                "subsections": [
                    "研究设计",
                    "数据来源",
                    "分析方法"
                ]
            },
            {
                "name": "Results",
                "subsections": [
                    "主要发现",
                    "数据分析"
                ]
            },
            {
                "name": "Discussion",
                "subsections": [
                    "结果解释",
                    "理论贡献",
                    "实践意义"
                ]
            },
            {
                "name": "Conclusion",
                "subsections": [
                    "研究总结",
                    "局限性",
                    "未来研究方向"
                ]
            }
        ]
    }

    return {
        "outline": outline,
        "current_step": "outline_generated",
        "writing_phase": WritingPhase.WRITING.value
    }

def draft_section_node(state: AgentState) -> Dict[str, Any]:
    """起草章节节点"""
    outline = state.get("outline", {})
    current_section_idx = state.get("current_section_index", 0)

    if current_section_idx >= len(outline["sections"]):
        return {
            "current_step": "all_sections_draft",
            "drafting_complete": True
        }

    section = outline["sections"][current_section_idx]
    section_name = section["name"]

    # 调用写作助手生成章节草稿
    draft_content = f"""
# {section_name}

本节主要讨论...（基于研究内容生成）

"""

    # 保存草稿
    draft_path = f"{state['session_path']}/draft/{section_name.lower()}.md"
    save_draft(draft_path, draft_content)

    return {
        "current_section_index": current_section_idx + 1,
        "current_section_name": section_name,
        "draft_paths": state.get("draft_paths", []) + [draft_path],
        "current_step": "section_drafted"
    }

def self_review_node(state: AgentState) -> Dict[str, Any]:
    """自我审查节点"""
    draft_paths = state.get("draft_paths", [])

    review_results = []
    for path in draft_paths:
        # 读取草稿
        content = read_draft(path)

        # 执行审查检查
        review = {
            "path": path,
            "checks": {
                "argument_consistency": check_argument_consistency(content),
                "evidence_adequacy": check_evidence_adequacy(content),
                "logical_flow": check_logical_flow(content),
                "academic_tone": check_academic_tone(content)
            }
        }
        review_results.append(review)

    # 计算总体质量分
    total_score = calculate_review_score(review_results)

    return {
        "review_results": review_results,
        "review_score": total_score,
        "current_step": "self_review_completed",
        "writing_phase": WritingPhase.REVIEW.value
    }
```

**成功标准**:
- Workflow 可完整执行所有阶段
- 确认节点正确工作
- Review 循环可正确迭代
- 最终论文结构完整

---

### W4: F4 复习计划生成 (~400 LOC)

**目标**: 基于 SM2 算法生成复习计划

**流程图**:

```
┌─────────────┐
│    Start    │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  知识提取 (Extract)                                        │
│  ├─ 读取学习资料                                         │
│  ├─ 提取知识点                                           │
│  └─ 生成问题池                                           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  SM2 调度 (Schedule)                                      │
│  ├─ 计算初始复习间隔                                      │
│  ├─ 生成复习日期表                                        │
│  └─ 创建复习任务                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│  计划输出 (Output)                                        │
│  ├─ 生成复习计划文档                                      │
│  ├─ 同步到日历系统                                        │
│  └─ 设置提醒                                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
              ┌─────────┐
              │  End    │
              └─────────┘
```

**Workflow 定义**:

```python
# workflows/f4_review_planning.py
from review_agent.core.sm2_scheduler import SM2Scheduler

def create_f4_workflow() -> StateGraph:
    """创建 F4 复习计划生成 Workflow"""

    workflow = StateGraph(AgentState)

    workflow.add_node("extract_knowledge", extract_knowledge_node)
    workflow.add_node("sm2_schedule", sm2_schedule_node)
    workflow.add_node("generate_plan", generate_plan_node)
    workflow.add_node("sync_calendar", sync_calendar_node)

    workflow.set_entry_point("extract_knowledge")
    workflow.add_edge("extract_knowledge", "sm2_schedule")
    workflow.add_edge("sm2_schedule", "generate_plan")
    workflow.add_edge("generate_plan", "sync_calendar")
    workflow.add_edge("sync_calendar", END)

    return workflow

def sm2_schedule_node(state: AgentState) -> Dict[str, Any]:
    """SM2 调度节点"""
    knowledge_points = state.get("knowledge_points", [])

    scheduler = SM2Scheduler()
    schedule_items = []

    for kp in knowledge_points:
        # 计算初始复习间隔
        item = scheduler.create_item(
            question=kp["question"],
            answer=kp["answer"],
            ease_factor=2.5  # 默认难度因子
        )
        schedule_items.append(item)

    return {
        "schedule_items": schedule_items,
        "current_step": "sm2_scheduled"
    }
```

**成功标准**:
- 知识提取完整
- SM2 调度正确
- 复习计划可执行

---

## 测试策略

### 单元测试

| 组件 | 测试重点 |
|------|----------|
| F3 节点 | 各阶段状态转换 |
| F4 节点 | SM2 调度逻辑 |

### 集成测试

- F3 端到端流程测试
- F4 端到端流程测试

### E2E 测试

```python
# tests/e2e/test_f3_workflow.py
def test_f3_full_workflow():
    """测试 F3 完整流程"""
    workflow = create_f3_workflow()

    app = workflow.compile()

    result = app.invoke({
        "topic": "AI在教育中的应用",
        "session_path": "/tmp/test_writing"
    })

    assert result["writing_phase"] == "completed"
```

---

## 边界规则

### Always Do
- 每个阶段开始前验证前置条件
- 关键节点记录详细日志
- 用户输入必须验证

### Ask First
- 修改阶段顺序
- 新增/删除节点

### Never Do
- 跳过用户确认
- 自动修改用户内容

---

## 成功标准

- [ ] F3 Workflow 端到端成功率 ≥ 85%
- [ ] F4 Workflow 端到端成功率 ≥ 90%
- [ ] 生成的论文结构完整
- [ ] 复习计划可执行

---

## 依赖项

```toml
[tool.poetry.dependencies]
langgraph = "*"
review_agent = {path = "../review_agent"}
```

---

**下一步**: S5 基础设施层
