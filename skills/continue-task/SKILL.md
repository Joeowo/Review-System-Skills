---
name: continue-task
description: Resume a review session by reading handoff.md, CONTEXT.md, and Task.md, then generate pre-study questionnaire for the current task. Use when continuing a session in a new window or after context loss.
---

# Continue Task

恢复复习会话，读取状态并为当前任务生成学前问卷。

## Quick start

```
/continue-task review-20250619-经济管理
```

## Workflows

### 1. 恢复上下文

- [ ] 读取 `handoff.md` 获取上次状态
- [ ] 读取 `CONTEXT.md` 恢复术语定义
- [ ] 读取 `Task.md` 确认当前任务

### 2. 确定继续位置

- [ ] 根据三文件综合判断当前进度
- [ ] 优先从上次未完成的 task 继续
- [ ] 若上次 task 已完成，进入下一个

### 3. 生成学前问卷

- [ ] 阅读 `sources/` 中当前任务对应的资料
- [ ] 生成3-5个引导型问题（含学习线索）
- [ ] 问题写入 `CONTEXT.md` → `Task X: 学前问卷`
- [ ] 更新 `Task.md` 状态为 `in_progress`

### 4. 开始循环

- [ ] 提示用户使用 `/grill-me` 开始问答

## ⚠️ 核心原则：一次只问一个问题

当配合 `/grill-me` 使用时，必须严格遵循：
- **一次只问一个问题**
- 等待用户回答后，再问下一个问题
- 绝不要一次性抛出多个问题造成信息过载

用户的反馈表明：多问题堆叠会导致认知负担，无法有效学习。

## Advanced features

See [REFERENCE.md](REFERENCE.md) for:
- Progress inference rules
- Questionnaire design principles
- Multi-source mapping strategy