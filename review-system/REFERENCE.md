# Reference: Review System

## Session 文件映射

```
review-YYYYMMDD-主题/
├── CONTEXT.md       ← continue-task 恢复术语 / advance-task 扩展
├── README.md        ← review-session 初始化
├── Task.md          ← review-session 生成 / advance-task 更新
├── handoff.md       ← review-session 生成 / advance-task 更新
└── sources/
    └── *.md         ← review-session 转换
```

**写入责任矩阵**:

| 文件 | review-session | continue-task | advance-task |
|------|----------------|---------------|--------------|
| CONTEXT.md | 初始化模板 | 写入学前问卷 | 补充术语/答案 |
| Task.md | 初始化列表 | 更新状态为 in_progress | 更新轮次/完成 |
| handoff.md | 初始化 | - | 完全重写 |
| sources/ | 转换写入 | 读取 | - |

## 多Session协调

同一课程的跨天学习：

```
Day 1:
├── review-20250619-经济管理/ (Task 1-3 完成)
│
Day 2:
├── review-20250619-经济管理/ (继续，Task 4 开始)
│
Day 3:
├── review-20250619-经济管理/ (最终，Task 5-6 完成)
```

**原则**：
- 同一课程用同一session文件夹
- 通过 handoff.md 断点恢复
- 避免创建多个 session 造成分散

## 上下文丢失后的恢复

当对话窗口关闭后：

1. 用户打开新窗口
2. 调用 `/continue-task <session-path>`
3. Agent 读取三文件 → 推断位置 → 恢复状态

**推断优先级**：
1. handoff.md 的记录（最可靠，每次 Q&A 后更新）
2. Task.md 的状态（次可靠）
3. CONTEXT.md 的轮次（辅助验证）

## 完成标准

整个 Session 标记为完成：

```markdown
# Session 完成摘要

**完成日期**: 2025-06-21
**总 Task 数**: 6
**完成 Task 数**: 6
**总 Q&A 轮次**: 12

## 完成的 Tasks

- ✅ Task 1: 绪论 (2 轮)
- ✅ Task 2: 市场机制 (3 轮)
- ...

## 薄弱环节

- 财政政策工具的应用场景需加强
```

## 与未来题库系统的集成

当前系统专注于交互式学习。未来题库功能可按以下方式扩展：

1. **搜索**：在 `sources/` 中 RAG 搜索相关内容
2. **出题**：基于章节生成选择题、计算题
3. **判题**：自动评分并给出解析

**扩展技能**（待实现）：
- `/question-bank-search` - 搜索往届试题
- `/question-bank-generate` - 基于资料生成新题
- `/question-bank-grade` - 自动评分

## 故障恢复指南

| 症状 | 原因 | 解决 |
|------|------|------|
| Task.md 为空 | 转换失败 | 重新 `/review-session` |
| handoff.md 缺失 | 用户未调用 `/advance-task` | 读取 Task.md 推断 |
| sources/ 为空 | 转换脚本未运行 | 检查 pypdf/python-docx 安装 |
| CONTEXT.md 丢失 | 意外删除 | 从 handoff.md 重建 |

## 性能优化建议

1. **限制并发窗口**：最多 2 个学习窗口，避免任务混乱
2. **轮次控制**：每task 2-4 轮为宜，避免无效重复
3. **资料分段**：若单文件 >100 页，建议分多个task处理