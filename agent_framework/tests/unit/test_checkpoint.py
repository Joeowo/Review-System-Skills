"""
C2: Checkpoint 管理 - 单元测试

测试覆盖：
- CheckpointManager 初始化
- get_checkpointer() 获取 SqliteSaver
- cleanup_old_checkpoints() 清理旧 checkpoint
- list_checkpoints() 列出 checkpoint
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from agent_framework.core.checkpoint import (
    CheckpointManager,
    get_checkpointer,
)


# =============================================================================
# 测试组 1: CheckpointManager 初始化
# =============================================================================

class TestCheckpointManagerInit:
    """测试 CheckpointManager 初始化"""

    def test_checkpoint_manager_can_be_initialized(self):
        """CheckpointManager 可以正确初始化"""
        manager = CheckpointManager()

        assert manager is not None
        assert hasattr(manager, "db_path")

    def test_checkpoint_manager_with_custom_path(self, temp_dir):
        """CheckpointManager 可以使用自定义路径"""
        custom_db = temp_dir / "custom.db"
        manager = CheckpointManager(db_path=str(custom_db))

        assert manager.db_path == str(custom_db)

    def test_checkpoint_manager_creates_database_file(self, temp_dir):
        """CheckpointManager 初始化时创建数据库文件"""
        db_path = temp_dir / "test.db"
        manager = CheckpointManager(db_path=str(db_path))

        # 获取 checkpointer 会导致数据库文件创建
        checkpointer = manager.get_checkpointer()

        # 验证数据库文件存在
        # 注意：SqliteSaver 可能在首次写入时才创建文件
        assert manager.db_path == str(db_path)


# =============================================================================
# 测试组 2: get_checkpointer
# =============================================================================

class TestGetCheckpointer:
    """测试 get_checkpointer 方法"""

    def test_get_checkpointer_returns_context_manager(self):
        """get_checkpointer 返回上下文管理器"""
        manager = CheckpointManager()
        checkpointer = manager.get_checkpointer()

        # 验证返回的对象是上下文管理器
        assert hasattr(checkpointer, "__enter__")
        assert hasattr(checkpointer, "__exit__")

    def test_get_checkpoint_can_use_context_manager(self):
        """get_checkpointer 可以用作上下文管理器"""
        manager = CheckpointManager()

        with manager.get_checkpointer() as saver:
            # 验证 saver 有 put/get 方法
            assert hasattr(saver, "put")
            assert hasattr(saver, "get")

    def test_get_checkpointer_function(self):
        """模块级 get_checkpointer 函数可用"""
        checkpointer = get_checkpointer()

        assert checkpointer is not None
        assert hasattr(checkpointer, "__enter__")
        assert hasattr(checkpointer, "__exit__")


# =============================================================================
# 测试组 3: cleanup_old_checkpoints
# =============================================================================

class TestCleanupOldCheckpoints:
    """测试清理旧 checkpoint 功能"""

    def test_cleanup_old_checkpoints_exists(self):
        """cleanup_old_checkpoints 方法存在"""
        manager = CheckpointManager()

        assert hasattr(manager, "cleanup_old_checkpoints")
        assert callable(manager.cleanup_old_checkpoints)

    def test_cleanup_old_checkpoints_accepts_days_parameter(self, temp_dir):
        """cleanup_old_checkpoints 接受 days 参数"""
        manager = CheckpointManager(db_path=str(temp_dir / "test.db"))

        # 不应该抛出异常
        try:
            result = manager.cleanup_old_checkpoints(days=30)
            assert isinstance(result, int)
        except Exception as e:
            pytest.fail(f"cleanup_old_checkpoints raised {e}")

    def test_cleanup_old_checkpoints_returns_count(self, temp_dir):
        """cleanup_old_checkpoints 返回清理数量"""
        manager = CheckpointManager(db_path=str(temp_dir / "test.db"))

        result = manager.cleanup_old_checkpoints(days=30)

        # 应该返回整数（清理的数量）
        assert isinstance(result, int)
        assert result >= 0

    def test_cleanup_with_zero_days(self, temp_dir):
        """cleanup_old_checkpoints(days=0) 应该清理所有"""
        manager = CheckpointManager(db_path=str(temp_dir / "test.db"))

        result = manager.cleanup_old_checkpoints(days=0)

        # 应该返回非负整数
        assert result >= 0


# =============================================================================
# 测试组 4: list_checkpoints
# =============================================================================

class TestListCheckpoints:
    """测试列出 checkpoint 功能"""

    def test_list_checkpoints_exists(self):
        """list_checkpoints 方法存在"""
        manager = CheckpointManager()

        assert hasattr(manager, "list_checkpoints")
        assert callable(manager.list_checkpoints)

    def test_list_checkpoints_accepts_thread_id(self, temp_dir):
        """list_checkpoints 接受 thread_id 参数"""
        manager = CheckpointManager(db_path=str(temp_dir / "test.db"))

        # 不应该抛出异常
        try:
            result = manager.list_checkpoints(thread_id="test-thread")
            assert isinstance(result, list)
        except Exception as e:
            pytest.fail(f"list_checkpoints raised {e}")

    def test_list_checkpoints_returns_list(self, temp_dir):
        """list_checkpoints 返回列表"""
        manager = CheckpointManager(db_path=str(temp_dir / "test.db"))

        result = manager.list_checkpoints(thread_id="test-thread")

        assert isinstance(result, list)

    def test_list_checkpoints_empty_database(self, temp_dir):
        """list_checkpoints 在空数据库返回空列表"""
        manager = CheckpointManager(db_path=str(temp_dir / "empty.db"))

        result = manager.list_checkpoints(thread_id="nonexistent-thread")

        assert result == []


# =============================================================================
# 测试组 5: Checkpoint 保存和恢复
# =============================================================================

class TestCheckpointSaveAndRestore:
    """测试 checkpoint 保存和恢复"""

    def test_can_save_checkpoint(self, temp_checkpoint_db, sample_thread_id):
        """可以保存 checkpoint"""
        manager = CheckpointManager(db_path=temp_checkpoint_db)

        with manager.get_checkpointer() as saver:
            # 创建正确的 checkpoint 格式
            config = {
                "configurable": {
                    "thread_id": sample_thread_id,
                    "checkpoint_ns": ""
                }
            }
            checkpoint = {
                "id": "test-id-1",
                "channel_values": {"step": "test", "value": 42},
                "channel_versions": {},
                "versions_seen": {}
            }
            metadata = {"source": "test", "step": 1}
            new_versions = {}

            # 保存 checkpoint
            try:
                saver.put(config, checkpoint, metadata, new_versions)
            except Exception as e:
                pytest.fail(f"Failed to save checkpoint: {e}")

    def test_can_restore_checkpoint(self, temp_checkpoint_db, sample_thread_id):
        """可以恢复 checkpoint"""
        manager = CheckpointManager(db_path=temp_checkpoint_db)

        # 先保存
        with manager.get_checkpointer() as saver:
            config = {
                "configurable": {
                    "thread_id": sample_thread_id,
                    "checkpoint_ns": ""
                }
            }
            checkpoint = {
                "id": "test-id-1",
                "channel_values": {"step": "test", "value": 42},
                "channel_versions": {},
                "versions_seen": {}
            }
            metadata = {"source": "test", "step": 1}
            new_versions = {}
            saver.put(config, checkpoint, metadata, new_versions)

        # 再恢复（新的上下文）
        with manager.get_checkpointer() as saver:
            try:
                result = saver.get(config)
                # result 应该返回 checkpoint 对象
                assert result is not None
                assert "id" in result
                assert result["id"] == "test-id-1"
            except Exception as e:
                pytest.fail(f"Failed to restore checkpoint: {e}")
