"""
Agent Framework - ComindFlow 核心编排引擎
主入口文件
"""
import sys
import traceback
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from ui.menu import MainMenu


def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()

    # 显示启动信息
    print("=" * 60)
    print("  Agent Framework - ComindFlow 核心编排引擎")
    print("  版本: 0.1.0")
    print("=" * 60)
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
