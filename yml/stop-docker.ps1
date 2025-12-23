# Docker Compose 停止脚本 (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI LangGraph Docker 服务停止脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "停止所有服务..." -ForegroundColor Yellow
docker-compose stop

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 所有服务已停止" -ForegroundColor Green
} else {
    Write-Host "错误: 停止服务失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "是否要删除容器? (数据卷将保留) (y/n): " -NoNewline -ForegroundColor Yellow
$remove = Read-Host

if ($remove -eq 'y' -or $remove -eq 'Y') {
    Write-Host "删除容器..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✓ 容器已删除" -ForegroundColor Green
}

Write-Host ""
Write-Host "完成！" -ForegroundColor Green

