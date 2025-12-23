@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   重启 MySQL 服务
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 停止 MySQL 容器...
docker-compose stop mysql

echo.
echo [2/3] 删除 MySQL 容器（保留数据）...
docker-compose rm -f mysql

echo.
echo [3/3] 重新创建并启动 MySQL...
docker-compose up -d mysql

echo.
echo ========================================
echo   完成！查看日志...
echo ========================================
echo.

timeout /t 3 >nul
docker-compose logs --tail=50 mysql

echo.
echo 按任意键退出...
pause >nul

