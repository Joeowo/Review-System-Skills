"""
Review Agent - 经济管理复习系统
主入口文件
"""
import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from config import ensure_data_dirs
from ui.menu import MainMenu
from dotenv import load_dotenv
from utils.config_setup import ensure_api_config


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 确保数据目录存在
    ensure_data_dirs()

    # 检查并配置API Key（首次使用）
    ensure_api_config()

    # 显示启动信息
    print("=" * 50)
    print("  Review Agent - 经济管理复习系统")
    print("  版本: 1.0.0")
    print("=" * 50)
    print()

    try:
        # 启动主菜单
        menu = MainMenu()
        menu.show()

    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出。")
    except Exception as e:
        print(f"\n\n程序出错: {e}")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
