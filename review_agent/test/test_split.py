"""测试内容分块 - 显示详细内容"""
from pathlib import Path
import re

def split_content(content: str, max_length: int = 1500):
    """将内容分成适合LLM处理的块"""
    chunks = []
    current_chunk = ""

    lines = content.split("\n")

    for line in lines:
        stripped = line.strip()

        # 检测章节标题 - 新章节开始
        if re.match(r'^第\d+章[：:]', stripped) or re.match(r'^\d+[-\s]*第.*章', stripped):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = stripped + "\n"
            continue

        # 检测大知识点标题
        if re.match(r'^\d+．\s*[^\d]', stripped) and len(current_chunk) > max_length // 2:
            chunks.append(current_chunk)
            current_chunk = stripped + "\n"
            continue

        current_chunk += line + "\n"

        if len(current_chunk) >= max_length:
            chunks.append(current_chunk)
            current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk)

    return [c for c in chunks if len(c.strip()) > 100]

# 测试文件
md_file = Path(r'D:\CODE\review_system_skills\review-20250619-经济管理\sources\01-经济问题与经济学.md')

if md_file.exists():
    content = md_file.read_text(encoding='utf-8')
    chunks = split_content(content)

    print(f'=== 分块详细内容 ===')
    print(f'文件: {md_file.name}')
    print(f'总长度: {len(content)} 字符')
    print(f'分块数量: {len(chunks)}')
    print()

    # 显示前6块的完整内容
    for i in range(min(6, len(chunks))):
        chunk = chunks[i]
        print(f'{"="*60}')
        print(f'--- 块 {i+1} ({len(chunk)} 字符) ---')
        print(f'{"="*60}')
        print(chunk[:800])  # 显示前800字符
        if len(chunk) > 800:
            print(f'\n... (还有 {len(chunk)-800} 字符)')
        print()
else:
    print(f'文件不存在: {md_file}')
