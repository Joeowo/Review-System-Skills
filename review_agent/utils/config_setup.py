"""
首次使用配置工具
检查并配置API Key
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from config import BASE_DIR, DEEPSEEK_API_KEY


def check_api_config() -> bool:
    """
    检查API配置是否完整

    Returns:
        True表示配置完整，False表示需要配置
    """
    return bool(DEEPSEEK_API_KEY and DEEPSEEK_API_KEY.startswith('sk-'))


def setup_api_key():
    """
    交互式配置API Key

    Returns:
        配置是否成功
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt

    console = Console()

    console.clear()
    console.print()

    console.print(Panel(
        "[bold cyan]🔧 首次使用配置[/bold cyan]\n\n"
        "欢迎使用经济管理复习系统！\n"
        "为了使用AI功能，需要配置DeepSeek API Key。\n\n"
        "[dim]获取API Key：[/dim]\n"
        "1. 访问 https://platform.deepseek.com/\n"
        "2. 注册/登录账号\n"
        "3. 在 API Keys 页面创建新的密钥\n\n"
        "[bold yellow]⚠️  请妥善保管您的API Key，不要泄露给他人！[/bold yellow]",
        title="配置向导",
        border_style="cyan"
    ))

    console.print()

    # 输入API Key
    api_key = Prompt.ask(
        "[bold cyan]请输入您的DeepSeek API Key[/bold cyan]",
        console=console
    )

    # 验证API Key格式
    if not api_key.startswith('sk-'):
        console.print()
        console.print("[red]✗ API Key格式不正确，应以'sk-'开头[/red]")
        console.print()
        input("按 Enter 重试...")
        return False

    if len(api_key) < 20:
        console.print()
        console.print("[red]✗ API Key长度不正确[/red]")
        console.print()
        input("按 Enter 重试...")
        return False

    # 询问是否需要配置base_url（可选）
    console.print()
    base_url = Prompt.ask(
        "[dim]API Base URL（可选，直接Enter使用默认值）[/dim]",
        default="https://api.deepseek.com",
        console=console
    )

    # 保存到.env文件
    env_file = BASE_DIR / ".env"

    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"DEEPSEEK_API_KEY={api_key}\n")
            f.write(f"DEEPSEEK_BASE_URL={base_url}\n")
            f.write("DEEPSEEK_MODEL=deepseek-chat\n")

        console.print()
        console.print("[green]✓ 配置已保存！[/green]")
        console.print()
        console.print("[yellow]程序将重启以加载新配置...[/yellow]")
        console.print()

        input("按 Enter 重启...")

        # 重启程序
        import sys
        import os
        python = sys.executable
        os.execl(python, python, *sys.argv)

        return True

    except Exception as e:
        console.print()
        console.print(f"[red]✗ 保存配置失败: {e}[/red]")
        console.print()
        input("按 Enter 重试...")
        return False


def ensure_api_config():
    """
    确保API配置存在

    如果配置不存在或无效，会启动配置流程
    """
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts and not check_api_config():
        attempts += 1
        if not setup_api_key():
            continue

        # 重新加载配置
        load_dotenv(BASE_DIR / ".env")

    if not check_api_config():
        from rich.console import Console
        console = Console()
        console.print()
        console.print("[red]✗ API配置失败，程序无法正常运行[/red]")
        console.print()
        exit(1)
