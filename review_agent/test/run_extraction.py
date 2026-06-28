"""运行提取并保存结果"""
from core.knowledge_extractor import AgentKnowledgeExtractor
from pathlib import Path
import sys

try:
    extractor = AgentKnowledgeExtractor()
    md_file = Path(r'../review-20250619-经济管理/sources/01-经济问题与经济学.md').resolve()

    print('完整文件提取...')
    points = extractor._extract_from_file(md_file, '20250619')

    print(f'提取了 {len(points)} 个知识点\n')
    for i, p in enumerate(points, 1):
        print(f'{i:2d}. [{p.type.value}] {p.title}')

    print(f'\n成功！共提取 {len(points)} 个知识点')
    sys.exit(0)

except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
