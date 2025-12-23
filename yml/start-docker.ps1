# Docker Compose 启动脚本 (PowerShell)
# 用于快速启动所有服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI LangGraph Docker 服务启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否运行
Write-Host "[1/4] 检查 Docker 服务..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1 | Select-String "Server Version"
if (-not $dockerRunning) {
    Write-Host "错误: Docker 未运行，请先启动 Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker 服务正常运行" -ForegroundColor Green
Write-Host ""

# 拉取最新镜像
Write-Host "[2/4] 拉取 Docker 镜像（可能需要几分钟）..." -ForegroundColor Yellow
docker-compose pull
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 部分镜像拉取失败，将使用本地镜像" -ForegroundColor Yellow
}
Write-Host "✓ 镜像拉取完成" -ForegroundColor Green
Write-Host ""

# 启动服务
Write-Host "[3/4] 启动所有服务..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 服务启动失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 服务启动成功" -ForegroundColor Green
Write-Host ""

# 等待服务就绪
Write-Host "[4/4] 等待服务就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  服务状态" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  服务访问地址" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Ollama:        http://localhost:11434" -ForegroundColor White
Write-Host "Milvus:        localhost:19530 (gRPC)" -ForegroundColor White
Write-Host "Attu (UI):     http://localhost:3000" -ForegroundColor White
Write-Host "MinIO API:     http://localhost:9000" -ForegroundColor White
Write-Host "MinIO Console: http://localhost:9001" -ForegroundColor White
Write-Host "MySQL:         localhost:3306" -ForegroundColor White
Write-Host "PostgreSQL:    localhost:5432" -ForegroundColor White
Write-Host "Redis:         localhost:6379" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  默认账号密码" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MinIO:     minioadmin / minioadmin123" -ForegroundColor White
Write-Host "MySQL:     root / root123456" -ForegroundColor White
Write-Host "           aiuser / aipass123" -ForegroundColor White
Write-Host "PostgreSQL: postgres / postgres123" -ForegroundColor White
Write-Host "Redis:     密码: redis123456" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  常用命令" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "查看日志:   docker-compose logs -f [服务名]" -ForegroundColor White
Write-Host "停止服务:   docker-compose stop" -ForegroundColor White
Write-Host "重启服务:   docker-compose restart" -ForegroundColor White
Write-Host "删除服务:   docker-compose down" -ForegroundColor White
Write-Host "查看状态:   docker-compose ps" -ForegroundColor White
Write-Host ""

Write-Host "✓ 所有服务已启动！" -ForegroundColor Green
Write-Host ""

# 询问是否下载 Ollama 模型
Write-Host "是否要下载 Ollama 模型? (y/n): " -NoNewline -ForegroundColor Yellow
$download = Read-Host
if ($download -eq 'y' -or $download -eq 'Y') {
    Write-Host ""
    Write-Host "可选模型:" -ForegroundColor Cyan
    Write-Host "1. qwen2.5:7b      (推荐，中文支持好)" -ForegroundColor White
    Write-Host "2. llama3.2:3b     (轻量级)" -ForegroundColor White
    Write-Host "3. deepseek-r1:7b  (推理能力强)" -ForegroundColor White
    Write-Host "4. nomic-embed-text (文本嵌入)" -ForegroundColor White
    Write-Host "0. 跳过" -ForegroundColor White
    Write-Host ""
    Write-Host "请选择要下载的模型 (1-4, 0=跳过): " -NoNewline -ForegroundColor Yellow
    $choice = Read-Host
    
    $model = ""
    switch ($choice) {
        "1" { $model = "qwen2.5:7b" }
        "2" { $model = "llama3.2:3b" }
        "3" { $model = "deepseek-r1:7b" }
        "4" { $model = "nomic-embed-text" }
        "0" { 
            Write-Host "跳过模型下载" -ForegroundColor Yellow
            exit 0
        }
        default {
            Write-Host "无效选择" -ForegroundColor Red
            exit 0
        }
    }
    
    if ($model -ne "") {
        Write-Host ""
        Write-Host "正在下载模型: $model (这可能需要几分钟到几十分钟)..." -ForegroundColor Yellow
        docker exec -it ollama ollama pull $model
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 模型下载完成: $model" -ForegroundColor Green
        } else {
            Write-Host "错误: 模型下载失败" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "完成！按任意键退出..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

