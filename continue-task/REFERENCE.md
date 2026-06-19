# Reference: Continue Task

## 进度推断规则

当 handoff.md、Task.md、CONTEXT.md 不一致时：

| handoff.md | Task.md | CONTEXT.md | 决策 |
|------------|---------|------------|------|
| Task 2, 轮次3 | Task 2, 轮次2 | Task 2, 轮次3 | 相信 handoff |
| Task 2, 轮次3 | Task 3, pending | 无 Task 2 记录 | 继续 Task 2，第3轮 |
| 无文件 | Task 2, in_progress | 无 Task 1 完成 | 从 Task 2 开始 |

**原则**：handoff.md 最可靠（每次 Q&A 循环后更新），Task.md 次之，CONTEXT.md 辅助验证。

## 学前问卷设计原则

1. **引导性**：问题本身应包含学习线索或方向
   - 好的：货币政策工具中，利率和存款准备金率对经济的影响有什么不同？
   - 差的：什么是货币政策？

2. **层次递进**：从概念理解 → 应用场景 → 深层原理
   - Q1: 基本概念（记忆）
   - Q2: 应用场景（理解）
   - Q3: 比较分析（分析）

3. **数量控制**：3-5题为宜，避免信息过载

## 多源资料映射

当资料分散在多个文件时：

```python
# 假设 Task 3 涉及以下资料
task_sources = {
    "Task 3: 货币政策": [
        "sources/chapter-05.md",  # 定义
        "sources/chapter-07.md",  # 工具
        "sources/case-01.md"      # 案例
    ]
}
```

Agent 应：
1. 识别与任务相关的所有 source
2. 先读主章节，再看案例补充
3. 生成跨资料的综合性问题

## CONTEXT.md 更新格式

```markdown
## Task 3: 货币政策

### 学前问卷

1. **Q1**: 利率和存款准备金率对经济的影响有什么不同？
   **学习线索**: 关注传导机制和时效性

2. **Q2**: 央行在什么情况下会选择降息而非降准？
   **学习线索**: 考虑政策目标和经济背景

3. **Q3**: 为什么说货币政策是"总量调节"工具？
   **学习线索**: 与财政政策对比思考

### 答案记录

- [ ] Q1:
- [ ] Q2:
- [ ] Q3:
```

## 与 grill-me/grill-you 的配合

**标准循环**：

1. `/continue-task` → 生成学前问卷 → 提示用户 `/grill-me`
2. 用户学习并完成问卷 → `/grill-me` "检查我的理解"
3. Agent 点评 → 若需深化 → `/grill-you` "再考我几个"
4. 完成一轮 → 更新 Task.md + handoff.md
5. 重复 2-4

**进度同步点**：每轮 Q&A 后更新 handoff.md，确保断点可恢复。