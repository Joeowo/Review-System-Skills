"""单独提取 review-20260620-经济管理"""
import sys
sys.path.insert(0, '.')

from core.knowledge_extractor import AgentKnowledgeExtractor
from repositories.knowledge_repo import KnowledgeRepository
from pathlib import Path

print('=== 提取 review-20260620-经济管理 ===\n')

extractor = AgentKnowledgeExtractor()
session_path = Path(r'../review-20260620-经济管理')

print('开始提取...\n')
points = extractor.extract_from_session(session_path)

print(f'\n✓ 提取了 {len(points)} 个知识点\n')

# 保存
repo = KnowledgeRepository()
repo.save_session('review-20260620-经济管理', points)

print(f'已保存')
