@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   完全重置 MySQL（会删除所有数据）
echo ========================================
echo.
echo 警告：此操作会删除 MySQL 的所有数据！
echo.
set /p confirm="确认要继续吗？(输入 yes 继续): "

if /i not "%confirm%"=="yes" (
    echo 操作已取消
    pause
    exit /b
)

cd /d "%~dp0"

echo.
echo [1/4] 停止 MySQL 容器...
docker-compose stop mysql

echo.
echo [2/4] 删除 MySQL 容器...
docker-compose rm -f mysql

echo.
echo [3/4] 删除 MySQL 数据卷...
docker volume rm yml_mysql_data 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 尝试使用完整卷名...
    docker volume rm ai_langgraph_mysql_data 2>nul
)

echo.
echo [4/4] 重新创建 MySQL...
docker-compose up -d mysql

echo.
echo ========================================
echo   等待 MySQL 初始化（约 30 秒）...
echo ========================================
timeout /t 30 /nobreak

echo.
echo 查看启动日志...
docker-compose logs --tail=50 mysql

echo.
echo ========================================
echo   完成！
echo ========================================
echo.
pause

