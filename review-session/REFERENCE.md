# Reference: Review Session Internal Structure

## 文件夹结构

```
review-YYYYMMDD-主题/
├── CONTEXT.md          # 共享概念上下文（术语定义）
├── README.md           # 会话概要和快速导航
├── Task.md             # 学习任务列表和进度
├── handoff.md          # 会话交接文件（动态生成）
├── current_task.md     # 当前聚焦任务（可选）
└── sources/            # 转换后的学习资料
    ├── chapter-01.md
    ├── chapter-02.md
    └── ...
```

## Task.md 格式

```markdown
# 学习任务

## Task 1: [章节标题]

**状态**: pending | in_progress | completed
**来源**: sources/chapter-01.md
**学前问卷**: 见 CONTEXT.md § Task 1
**Q&A 轮次**: 3
**备注**: [可选]

---

## Task 2: [章节标题]
...
```

## handoff.md 格式

```markdown
# Session Handoff

## 当前状态

- **Task**: Task 3 - 货币政策
- **Q&A 轮次**: 第2轮
- **上次问答摘要**: [用户对...的理解基本正确，但在...方面需要加强]

## 继续步骤

1. 读取 CONTEXT.md 恢复术语上下文
2. 读取 Task.md 确认当前任务状态
3. 使用 `/grill-me` 下一轮练习
4. 完成后更新 Task.md 和 handoff.md

## 待解决问题

- [ ] 用户对...概念仍有疑问
- [ ] ...需要更多例题练习
```

## 任务分解策略

1. **按章节分解**：最常见方式，每章一个task
2. **按主题分解**：跨章节相关概念合并
3. **按难度分解**：基础概念、进阶应用、综合案例

**原则**：每个task 应能在2-4轮 Q&A 中完成，避免过大。

## 集成 gril-me/grill-you

**学习循环**：

1. **前置**：生成学前问卷 → 写入 CONTEXT.md
2. **Q&A**：`/grill-me` 提问 → 用户回答 → `/grill-you` 点评
3. **后置**：更新 Task.md、生成 handoff.md
4. **循环**：重复直到 task 完成

## 文档转换脚本

使用 Python：

```python
# PDF → MD
import pypdf
def pdf_to_md(path, output):
    reader = pypdf.PdfReader(path)
    text = ''.join(page.extract_text() for page in reader.pages)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(text)

# DOCX → MD
from docx import Document
def docx_to_md(path, output):
    doc = Document(path)
    text = '\n'.join(p.text for p in doc.paragraphs)
    with open(output, 'w', encoding='utf-8') as f:
        f.write(text)
```