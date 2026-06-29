# Tasks: Sub-Spec S3 & S4 - Workflow 编排层

**父文档**: [10-master-plan.md](10-master-plan.md)
**S3 预估 LOC**: ~850
**S4 预估 LOC**: ~950
**总计**: ~1,800

---

## S3: 学习研究 Workflow

### Task 1: 实现 F1 研究节点 (~80 LOC)

**描述**: 实现研究阶段节点

**验收标准**:
- [ ] 可调用 AutoResearch
- [ ] 状态更新正确
- [ ] 异常处理完善

**实现要点**:
```python
def research_node(state: AgentState) -> Dict[str, Any]:
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
```

**依赖**: S1, S2

**预计时间**: 3 小时

---

### Task 2: 实现 F1 确认节点 (~60 LOC)

**描述**: 实现研究完成确认节点

**验收标准**:
- [ ] 确认提示清晰
- [ ] 可正确暂停/恢复
- [ ] 用户输入处理正确

**依赖**: S1 (确认机制)

**预计时间**: 2 小时

---

### Task 3: 实现 F1 概念提取节点 (~80 LOC)

**描述**: 实现概念提取节点

**验收标准**:
- [ ] 可解析报告文件
- [ ] 概念提取准确
- [ ] 状态更新正确

**依赖**: Task 1

**预计时间**: 3 小时

---

### Task 4: 实现 F1 任务分解节点 (~80 LOC)

**描述**: 实现任务分解节点

**验收标准**:
- [ ] 可初始化 Task.md
- [ ] 任务分解合理
- [ ] 格式正确

**依赖**: Task 3

**预计时间**: 3 小时

---

### Task 5: 实现 F1 Grilling 循环节点 (~120 LOC)

**描述**: 实现 grill-me、grill-you、评估节点

**验收标准**:
- [ ] grill-me 节点可生成问题
- [ ] grill-you 节点可建议问题
- [ ] 评估节点可判断掌握程度
- [ ] 循环可正确退出

**依赖**: S2 (Skills 适配器)

**预计时间**: 5 小时

---

### Task 6: 实现 F1 保存进度节点 (~60 LOC)

**描述**: 实现进度保存节点

**验收标准**:
- [ ] 可更新 Task.md
- [ ] 可生成 handoff.md
- [ ] 格式正确

**依赖**: S2 (AdvanceTaskAdapter)

**预计时间**: 2 小时

---

### Task 7: 组装 F1 Workflow (~100 LOC)

**描述**: 组装完整 F1 Workflow

**验收标准**:
- [ ] 所有节点正确连接
- [ ] 条件边正确
- [ ] 入口/出口正确

**实现要点**:
```python
def create_f1_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)
    # 添加节点
    # 添加边
    return workflow
```

**依赖**: 所有前置任务

**预计时间**: 4 小时

---

### Task 8: 实现 F2 Workflow (~150 LOC)

**描述**: 实现 F2 知识问答增强 Workflow

**验收标准**:
- [ ] 可加载知识库
- [ ] 可查询知识
- [ ] 可生成答案

**依赖**: S1, S2

**预计时间**: 5 小时

---

### Task 9: S3 集成测试 (~200 LOC)

**描述**: S3 端到端测试

**验收标准**:
- [ ] F1 E2E 测试通过
- [ ] F2 E2E 测试通过
- [ ] Checkpoint 恢复测试通过

**依赖**: 所有前置任务

**预计时间**: 6 小时

---

## S4: 学术写作复习 Workflow

### Task 10: 实现 F3 澄清阶段节点 (~100 LOC)

**描述**: 实现主题澄清相关节点

**验收标准**:
- [ ] clarify_topic 节点可生成澄清问题
- [ ] clarify_confirmation 可确认澄清结果

**依赖**: S1

**预计时间**: 4 小时

---

### Task 11: 实现 F3 研究阶段节点 (~100 LOC)

**描述**: 实现研究计划、执行、确认节点

**验收标准**:
- [ ] plan_research 可生成研究计划
- [ ] execute_research 可执行研究
- [ ] research_confirmation 可确认结果

**依赖**: S2 (AutoResearch Tools)

**预计时间**: 4 小时

---

### Task 12: 实现 F3 写作阶段节点 (~150 LOC)

**描述**: 实现大纲生成、起草、优化节点

**验收标准**:
- [ ] generate_outline 可生成大纲
- [ ] draft_section 可起草章节
- [ ] refine_section 可优化内容
- [ ] 章节切换逻辑正确

**依赖**: S1, S2

**预计时间**: 6 小时

---

### Task 13: 实现 F3 Review 循环节点 (~100 LOC)

**描述**: 实现自我审查、用户审查、迭代节点

**验收标准**:
- [ ] self_review 可执行审查
- [ ] user_review 可等待用户输入
- [ ] iterate_section 可迭代改进
- [ ] 循环可正确退出

**依赖**: Task 12

**预计时间**: 4 小时

---

### Task 14: 组装 F3 Workflow (~100 LOC)

**描述**: 组装完整 F3 Workflow

**验收标准**:
- [ ] 所有阶段正确连接
- [ ] 确认节点正确
- [ ] Review 循环正确

**依赖**: 所有前置任务

**预计时间**: 4 小时

---

### Task 15: 实现 F4 Workflow (~150 LOC)

**描述**: 实现 F4 复习计划生成

**验收标准**:
- [ ] extract_knowledge 可提取知识点
- [ ] sm2_schedule 可计算复习间隔
- [ ] generate_plan 可生成计划文档

**依赖**: S2 (review_agent Tools)

**预计时间**: 5 小时

---

### Task 16: Workflow E2E 测试 (~200 LOC)

**描述**: 完整 Workflow 端到端测试

**验收标准**:
- [ ] F1 完整流程测试通过
- [ ] F3 完整流程测试通过
- [ ] F4 完整流程测试通过
- [ ] 跨会话恢复测试通过

**依赖**: 所有前置任务

**预计时间**: 6 小时

---

## Summary

### S3 Summary
- **任务数**: 9
- **预估 LOC**: ~850
- **关键路径**: Task 1 → Task 3 → Task 4 → Task 5 → Task 7 → Task 9

### S4 Summary
- **任务数**: 7
- **预估 LOC**: ~950
- **关键路径**: Task 10 → Task 11 → Task 12 → Task 13 → Task 14 → Task 16

### 总体
- **总任务数**: 16
- **总预估 LOC**: ~1,800
- **并行机会**: S3 和 S4 可部分并行开发

→ **Human**: 审查任务列表，批准后开始实施
