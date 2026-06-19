---
name: review-session
description: Create and initialize a review session by setting up folder structure, converting PDF/DOCX to markdown, and generating learning tasks. Use when starting a new review session, preparing for exams, or setting up course study materials.
---

# Review Session

初始化复习会话，创建学习任务，准备交互式问答学习环境。

## Quick start

```
/review-session 复习经济管理，资料在 d:\学习\21CoreDocs\经管\复习资料
```

## Workflows

### 1. 初始化新Session

- [ ] 确认任务目标和资料路径
- [ ] 创建Session文件夹（格式：`review-YYYYMMDD-主题`）
- [ ] 初始化 `CONTEXT.md`（复制模板）
- [ ] 初始化 `Task.md`（空任务列表）
- [ ] 初始化 `README.md`（会话概要）

### 2. 文档转换

- [ ] 扫描资料目录下的 `.pdf` 和 `.docx` 文件
- [ ] 使用 `pypdf` 或 `python-docx` 转换为 `.md`
- [ ] 存储到 `sources/` 目录

### 3. 任务分解

- [ ] 阅读所有转换后的 `.md` 文件
- [ ] 按章节/主题分解学习任务
- [ ] 为每个task生成简短描述
- [ ] 写入 `Task.md`，初始状态均为 `pending`

### 4. 交接准备

- [ ] 生成 `handoff.md`，记录当前状态
- [ ] 指导用户用新窗口开始学习循环

## Advanced features

See [REFERENCE.md](REFERENCE.md) for:
- Task decomposition strategies
- handoff.md format specification
- Integration with `/grill-me` and `/grill-you`