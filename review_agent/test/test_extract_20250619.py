"""测试review-20250619提取"""
from core.knowledge_extractor import AgentKnowledgeExtractor
from pathlib import Path
import json

extractor = AgentKnowledgeExtractor()
session_path = Path(r'D:\CODE\review_system_skills\review-20250619-经济管理')

print('=== 测试 review-20250619-经济管理 ===')
print('开始提取...\n')

points = extractor.extract_from_session(session_path)

print(f'\n✓ 提取了 {len(points)} 个知识点\n')

print('前20个知识点:')
for i, point in enumerate(points[:20], 1):
    print(f'{i:2d}. [{point.type.value}] {point.title}')

# 保存结果
output_file = Path('test_20250619_result.json')
output_file.write_text(json.dumps([p.to_dict() for p in points], ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\n结果已保存到: {output_file}')
