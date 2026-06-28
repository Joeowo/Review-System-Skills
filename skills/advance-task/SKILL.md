---
name: advance-task
description: Update session state after each Q&A round by recording progress to Task.md and handoff.md. Use after completing a /grill-me or /grill-you round to save progress.
---

# Advance Task

记录一轮Q&A后的进度，更新Task.md和handoff.md。

## Quick start

```
/advance-task Task 3 已完成第2轮，对货币政策工具理解较好
```

## Workflows

### 1. 更新 Task.md

- [ ] 更新当前task的Q&A轮次
- [ ] 添加本轮学习要点摘要
- [ ] 若用户掌握良好，标记为 `completed`

### 2. 更新 handoff.md

- [ ] 记录当前task和轮次
- [ ] 写入本轮问答摘要
- [ ] 列出待解决问题（如有）

### 3. 更新 CONTEXT.md

- [ ] 补充本轮涉及的新术语
- [ ] 更新学前问卷答案记录

### 4. 准备下一轮

- [ ] 若当前task完成，提示用户进入下一个
- [ ] 若需继续，提示用户使用 `/grill-me` 继续

## Advanced features

See [REFERENCE.md](REFERENCE.md) for:
- Handoff template
- Completion criteria
- Progress snapshot format