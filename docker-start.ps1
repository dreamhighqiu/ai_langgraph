# Docker Compose Startup Script for Windows

Write-Host "========================================" -ForegroundColor Green
Write-Host "  AI LangGraph Docker Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Creating .env from env.docker.example..."
    if (Test-Path env.docker.example) {
        Copy-Item env.docker.example .env
        Write-Host "Please edit .env file and set OPENAI_API_KEY" -ForegroundColor Yellow
    } else {
        Write-Host "Error: env.docker.example not found" -ForegroundColor Red
        exit 1
    }
}

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker is not installed" -ForegroundColor Red
    exit 1
}

# Use docker compose (v2) if available
$composeCmd = "docker compose"
try {
    docker compose version | Out-Null
} catch {
    $composeCmd = "docker-compose"
}

Write-Host "Starting services..."
& $composeCmd.Split(' ') up -d

Write-Host ""
Write-Host "Services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Access URLs:"
Write-Host "  Frontend UI:     http://localhost:3200"
Write-Host "  LangGraph API:   http://localhost:2025"
Write-Host "  API Docs:        http://localhost:2025/docs"
Write-Host "  LangGraph Studio: http://localhost:2025/ui"
Write-Host "  LightRAG API:    http://localhost:9621/docs"
Write-Host "  Milvus UI:       http://localhost:3000"
Write-Host "  MinIO Console:   http://localhost:9001"
Write-Host ""
Write-Host "View logs: docker compose logs -f [service-name]"
Write-Host "Stop all:  docker compose down"

