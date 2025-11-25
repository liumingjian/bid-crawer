@echo off
REM 招标信息爬虫系统 - Windows 运行脚本

cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 python，请先安装 Python 3.9+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\" (
    echo 提示: 虚拟环境不存在，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖是否已安装
if not exist "venv\.dependencies_installed" (
    echo 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 0 (
        echo. > venv\.dependencies_installed
        echo ✓ 依赖安装完成
    ) else (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

REM 运行主程序
echo 启动爬虫系统...
python -m src.main %*

REM 退出
call venv\Scripts\deactivate.bat
pause
