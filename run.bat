@echo off
chcp 65001 >nul
echo ==========================================
echo   Dynamic Island for Windows 11
echo ==========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

:: 检查虚拟环境
if not exist .venv (
    echo [信息] 创建虚拟环境...
    python -m venv .venv
)

:: 激活虚拟环境
call .venv\Scripts\activate

:: 安装依赖
echo [信息] 检查依赖...
pip install -q PyQt6 pycaw comtypes psutil pywin32 pystray

:: 运行应用
echo [信息] 启动灵动岛...
echo.
python -m src.main

:: 如果出错暂停
if errorlevel 1 (
    echo.
    echo [错误] 应用运行失败，请检查错误信息
    pause
)

:: 退出虚拟环境
deactivate
