---
name: review-system
description: Orchestrate a complete review session workflow using review-session, continue-task, advance-task, grill-me, and grill-you skills. Use when starting a new course review, preparing for exams, or managing multi-session study plans.
---

# Review System

基于skills的agent协助复习系统，通过多阶段工作流实现系统化学习。

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Review System                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  初始化阶段 ─────────────────────────────────────────────   │
│  ┌─────────────────┐    ┌─────────────────┐               │
│  │  review-session │ →  │ 文档转换+任务分解 │               │
│  └─────────────────┘    └─────────────────┘               │
│                                                             │
│  学习循环阶段（每task独立窗口）────────────────────────     │
│  ┌───────────────┐    ┌──────────────────────────────┐   │
│  │ continue-task │ →  │ 学前问卷 → /grill-me         │   │
│  └───────────────┘    └──────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Q&A 循环: /grill-me ↔ /grill-you                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌───────────────┐    ┌──────────────────────────────┐   │
│  │  advance-task │ →  │ 更新 Task.md + handoff.md    │   │
│  └───────────────┘    └──────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 完整工作流

### Phase 1: 初始化

```
/review-session 复习经济管理，资料在 d:\学习\21CoreDocs\经管\复习资料
```

执行：
1. 创建 `review-YYYYMMDD-主题/` 文件夹
2. 初始化 CONTEXT.md、Task.md、README.md
3. 转换 PDF/DOCX → sources/*.md
4. 按章节分解任务到 Task.md
5. 生成 handoff.md

### Phase 2: 开始学习

**新窗口 A**:
```
/continue-task review-20250619-经济管理
```

执行：
1. 恢复上下文（handoff、CONTEXT、Task）
2. 生成当前task的学前问卷
3. 写入 CONTEXT.md
4. 提示用户完成问卷

### Phase 3: Q&A 循环

```
/grill-me Task 3 关于货币政策
```

用户回答后：

```
/grill-you 再考我几个货币传导机制的问题
```

### Phase 4: 保存进度

```
/advance-task Task 3 已完成第2轮，理解良好
```

执行：
1. 更新 Task.md 轮次
2. 更新 handoff.md
3. 若完成，进入下一task

### Phase 5: 继续或结束

**继续学习**：
- 打开新窗口 → `/continue-task` → 循环 Phase 3-4

**结束Session**：
- 所有 tasks 标记 completed
- 生成最终总结

## 常见场景

| 场景 | 命令 |
|------|------|
| 开始新课程复习 | `/review-session` |
| 恢复昨日学习 | `/continue-task` |
| 练习巩固 | `/grill-me` |
| 深度提问 | `/grill-you` |
| 保存当前进度 | `/advance-task` |

## Advanced features

See [REFERENCE.md](REFERENCE.md) for:
- Multi-session coordination
- Recovery after context loss
- Integration with future question bank

## 依赖skills

- `/review-session` - 初始化和文档处理
- `/continue-task` - 恢复和学前问卷
- `/advance-task` - 进度保存
- `/grill-me` - 主动练习
- `/grill-you` - 深度考核