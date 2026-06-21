import pypdf
import os
from pathlib import Path

# PDF文件列表
pdf_files = [
    ("d:/学习/21CoreDocs/经管/书/04-宏观经济分析.pdf", "04-宏观经济分析"),
    ("d:/学习/21CoreDocs/经管/书/05-管理学概述.pdf", "05-管理学概述"),
    ("d:/学习/21CoreDocs/经管/书/06-管理的职能.pdf", "06-管理的职能"),
    ("d:/学习/21CoreDocs/经管/书/07-企业与管理.pdf", "07-企业与管理")
]

output_dir = "D:/学习/21CoreDocs/经管/review-20260620-经济管理/sources"

for pdf_path, name in pdf_files:
    # 读取PDF
    reader = pypdf.PdfReader(pdf_path)

    # 提取文本
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text())

    full_text = '\n\n'.join(text_parts)

    # 写入Markdown文件
    output_path = os.path.join(output_dir, f"{name}.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {name}\n\n")
        f.write("---\n\n")
        f.write(full_text)

    print(f"已转换: {name}.md ({len(reader.pages)} 页)")