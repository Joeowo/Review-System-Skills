# 经济管理复习系统

一套基于skills的agent协助复习系统，用于帮助用户系统化地学习课程资料并通过交互式问答巩固理解。

## Language

**Session**:
一个文件系统文件夹，用于存放一次复习的所有文件（CONTEXT.md、Task.md、README.md、handoff.md、sources/等）。
_Avoid_: 对话窗口、学习阶段、会话记录

**Task**:
学习任务单元，通常按章节划分。每个task代表一章或一组相关章节的学习内容。
_Avoid_: 学习目标、知识点、学习活动

**学前问卷**:
Agent生成的引导型问题，带着学习线索，用户在寻找答案的过程中自然完成学习。
_Avoid_: 诊断测试、摸底题、预习作业

**Q&A 循环**:
用户主导的问答来回模式，在 `/grill-me` 和 `/grill-you` 两个skills之间切换。每轮问题数量由用户自行控制。
_Avoid_: 对话、交互、轮询

**CONTEXT.md**:
Agent与用户共享的概念上下文，确保双方语言一致、术语定义清晰。
_Avoid_: 学习笔记、对话摘要、知识总结

**handoff.md**:
会话交接文件，总结当前状态，帮助新窗口/subagent快速恢复上下文。
_Avoid_: 交接记录、状态快照、摘要

**sources/**:
Session文件夹下的子目录，存放从PDF/DOCX转换后的.md文件。
_Avoid_: materials/、resources/、content/

**任务设置**:
用户通过自然语言描述复习目标（如"复习经济管理概论，准备期末考，重点关注计算题"）。
_Avoid_: 任务模板、复习模式、配置表

**进度恢复**:
用户继续同一Session时，通过Task.md完成状态、CONTEXT.md最后状态、handoff.md推断共同确定继续位置。
_Avoid_: 断点续传、上次进度、继续学习

## Relationships

- 一个 **Session** 包含一个 CONTEXT.md、一个 README.md、一个 Task.md、零个或多个 handoff.md、一个 sources/ 目录
- 一个 **Task** 对应一个章节的学习内容
- **学前问卷** 的答案被记录在 CONTEXT.md 中
- 每轮 **Q&A 循环** 后更新 Task.md 和 README.md
- 当新窗口触发时，生成 **handoff.md** 并继续同一个 Session

## Example dialogue

> **Dev**: "当用户开始复习时，我们怎么确定从哪个章节开始？"
> **Domain expert**: "读取 Task.md 找到第一个未完成的 task，同时看 CONTEXT.md 和 handoff.md 确定上次停留的位置，三者综合判断。"

## Flagged ambiguities

无