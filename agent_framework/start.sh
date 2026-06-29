#!/bin/bash
# Agent Framework 启动脚本

cd "$(dirname "$0")"

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python"
    exit 1
fi

# 检查是否安装了 rich
python -c "import rich" 2>/dev/null || {
    echo "安装依赖中..."
    pip install rich
}

# 启动主程序
python main.py "$@"
