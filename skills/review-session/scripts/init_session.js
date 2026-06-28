#!/usr/bin/env node

/**
 * Initialize a new review session
 * Usage: node scripts/init_session.js <session-name> <source-path>
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function formatDate(date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `${yyyy}${mm}${dd}`;
}

function createSession(sessionName, sourcePath) {
  const date = formatDate(new Date());
  const sessionDir = `review-${date}-${sessionName}`;

  // Create directory structure
  fs.mkdirSync(sessionDir, { recursive: true });
  fs.mkdirSync(path.join(sessionDir, 'sources'), { recursive: true });

  // Create CONTEXT.md template
  const contextContent = `# ${sessionName}

## Language

**Session**:
...

**Task**:
...

**学前问卷**:
...

**Q&A 循环**:
...

**CONTEXT.md**:
...

**handoff.md**:
...

**sources/**:
...

**任务设置**:
...

**进度恢复**:
...

## Relationships

...

## Example dialogue

...

## Flagged ambiguities

无
`;

  // Create empty Task.md
  const taskContent = `# 学习任务

任务列表将在文档转换后自动生成。
`;

  // Create README.md
  const readmeContent = `# ${sessionName} - 复习Session

**创建日期**: ${new Date().toLocaleDateString('zh-CN')}
**资料来源**: \`${sourcePath}\`

## 快速开始

1. 读取 \`CONTEXT.md\` 了解术语定义
2. 查看 \`Task.md\` 获取任务列表
3. 使用 \`/grill-me\` 开始学习循环

## 文件说明

- \`CONTEXT.md\` - 共享概念上下文
- \`Task.md\` - 学习任务列表和进度
- \`handoff.md\` - 会话交接文件
- \`sources/\` - 学习资料（已转换为MD）
`;

  fs.writeFileSync(path.join(sessionDir, 'CONTEXT.md'), contextContent, 'utf8');
  fs.writeFileSync(path.join(sessionDir, 'Task.md'), taskContent, 'utf8');
  fs.writeFileSync(path.join(sessionDir, 'README.md'), readmeContent, 'utf8');

  console.log(`✓ Session created: ${sessionDir}`);
  console.log(`✓ Ready for document conversion from: ${sourcePath}`);

  return sessionDir;
}

// Main
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node init_session.js <session-name> <source-path>');
  process.exit(1);
}

createSession(args[0], args[1]);