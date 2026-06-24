"""测试agent提取功能"""
from core.knowledge_extractor import AgentKnowledgeExtractor
from pathlib import Path
import json

extractor = AgentKnowledgeExtractor()
md_file = Path('../review-20250624-经济管理/sources/01_经济管理概论复习纲要.md').resolve()

print('=== Agent提取测试 ===')
print(f'文件: {md_file.name}')
print('开始提取...')

points = extractor._extract_from_file(md_file, 'test')

print(f'\n✓ 提取了 {len(points)} 个知识点\n')

print('知识点列表:')
for i, point in enumerate(points[:15], 1):
    print(f'{i:2d}. [{point.type.value}] {point.title}')

# 保存结果
output_file = Path('test_extraction_result.json')
output_file.write_text(json.dumps([p.to_dict() for p in points], ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\n结果已保存到: {output_file}')
