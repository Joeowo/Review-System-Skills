"""运行完整agent提取 - review-20250619-经济管理"""
import sys
sys.path.insert(0, '.')

from core.knowledge_extractor import AgentKnowledgeExtractor
from repositories.knowledge_repo import KnowledgeRepository
from pathlib import Path

# 清空并重新提取
print('=== Agent提取: review-20250619-经济管理 ===\n')

extractor = AgentKnowledgeExtractor()
session_path = Path(r'../review-20250619-经济管理')

print('开始提取...\n')
points = extractor.extract_from_session(session_path)

print(f'\n✓ 提取了 {len(points)} 个知识点\n')

# 显示结果
for i, p in enumerate(points[:25], 1):
    print(f'{i:2d}. [{p.type.value}] {p.title}')

# 保存
repo = KnowledgeRepository()
repo.save_session('review-20250619-经济管理', points)

print(f'\n已保存到 data/knowledge_base/review-20250619-经济管理.json')
