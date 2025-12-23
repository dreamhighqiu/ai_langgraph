@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo   AI LangGraph 环境安装
echo ========================================
echo.
echo 正在安装，请稍候...
echo.

REM 使用 -NoProfile 参数避免加载有问题的 profile
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   安装完成！
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo   安装过程中出现错误
    echo ========================================
    echo.
)

pause



