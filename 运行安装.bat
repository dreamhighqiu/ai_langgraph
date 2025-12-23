@echo off
chcp 65001 >nul
echo ========================================
echo  AI LangGraph 环境安装
echo ========================================
echo.

echo [1/3] 设置执行策略...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force"

echo [2/3] 开始安装...
powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

echo.
echo [3/3] 完成！
echo.
pause

