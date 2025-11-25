#!/bin/bash
# 招标信息爬虫系统 - Linux/Mac 运行脚本

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.9+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "提示: 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "错误: 创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否已安装
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "安装依赖包..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/.dependencies_installed
        echo "✓ 依赖安装完成"
    else
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

# 运行主程序
echo "启动爬虫系统..."
python -m src.main "$@"

# 保存退出码
exit_code=$?

# 退出
deactivate
exit $exit_code
