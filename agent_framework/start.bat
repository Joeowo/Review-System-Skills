@echo off
REM Agent Framework 启动脚本 (Windows)

cd /d "%~dp0"

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)

REM 检查是否安装了 rich
python -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo 安装依赖中...
    pip install rich
)

REM 启动主程序
python main.py %*

pause
