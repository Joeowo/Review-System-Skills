"""提取所有会话的知识点"""
import sys
sys.path.insert(0, '.')

from core.knowledge_extractor import AgentKnowledgeExtractor
from repositories.knowledge_repo import KnowledgeRepository
from pathlib import Path
from config import REVIEW_SOURCES

print('=== Agent提取所有会话 ===\n')

extractor = AgentKnowledgeExtractor()
repo = KnowledgeRepository()

all_results = {}

for session_path in REVIEW_SOURCES:
    if not session_path.exists():
        continue

    session_id = session_path.name
    print(f'--- {session_id} ---')
    print('开始提取...\n')

    points = extractor.extract_from_session(session_path)
    all_results[session_id] = points

    # 保存
    repo.save_session(session_id, points)

    print(f'✓ 提取了 {len(points)} 个知识点\n')

# 统计
print('='*50)
print('=== 总体统计 ===')
total = sum(len(points) for points in all_results.values())
print(f'总会话数: {len(all_results)}')
print(f'总知识点数: {total}')

for session_id, points in all_results.items():
    print(f'  {session_id}: {len(points)} 个')
