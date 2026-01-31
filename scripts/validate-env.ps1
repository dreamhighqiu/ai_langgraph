# ==============================================================
# 环境变量验证脚本 (PowerShell)
# ==============================================================
# 
# 用途：在启动 Docker Compose 前验证必需的环境变量
# 使用方法：.\scripts\validate-env.ps1
# ==============================================================

$ErrorCount = 0
$WarningCount = 0

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "环境变量验证脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 .env 文件是否存在
if (-not (Test-Path ".env")) {
    Write-Host "❌ 错误: .env 文件不存在" -ForegroundColor Red
    Write-Host "请先复制 .env.example 为 .env 并配置："
    Write-Host "  Copy-Item .env.example .env"
    $ErrorCount++
    exit 1
} else {
    Write-Host "✅ .env 文件存在" -ForegroundColor Green
    # 加载 .env 文件
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# 检查必需的 API Key
Write-Host ""
Write-Host "检查 API Keys..." -ForegroundColor Cyan
$openaiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "Process")
if ([string]::IsNullOrEmpty($openaiKey) -or $openaiKey -eq "your-openai-api-key-here") {
    Write-Host "❌ 错误: OPENAI_API_KEY 未配置或使用默认值" -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "✅ OPENAI_API_KEY 已配置" -ForegroundColor Green
}

# 检查服务配置文件
Write-Host ""
Write-Host "检查服务配置文件..." -ForegroundColor Cyan

# 检查 LightRAG .env
if (-not (Test-Path "anything-chat-rag\.env")) {
    Write-Host "⚠️  警告: anything-chat-rag\.env 不存在" -ForegroundColor Yellow
    Write-Host "  建议从 env.example 创建："
    Write-Host "    Copy-Item anything-chat-rag\env.example anything-chat-rag\.env"
    $WarningCount++
} else {
    Write-Host "✅ anything-chat-rag\.env 存在" -ForegroundColor Green
}

# 检查 LangGraph .env
if (-not (Test-Path "testing-agents-service\.env")) {
    Write-Host "⚠️  警告: testing-agents-service\.env 不存在" -ForegroundColor Yellow
    Write-Host "  建议从 env.example 创建："
    Write-Host "    Copy-Item testing-agents-service\env.example testing-agents-service\.env"
    $WarningCount++
} else {
    Write-Host "✅ testing-agents-service\.env 存在" -ForegroundColor Green
}

# 检查关键环境变量
Write-Host ""
Write-Host "检查关键环境变量..." -ForegroundColor Cyan

# Redis 配置
$redisPassword = [Environment]::GetEnvironmentVariable("REDIS_PASSWORD", "Process")
if ([string]::IsNullOrEmpty($redisPassword)) {
    Write-Host "⚠️  警告: REDIS_PASSWORD 未设置，将使用默认值" -ForegroundColor Yellow
    $WarningCount++
} else {
    Write-Host "✅ REDIS_PASSWORD 已配置" -ForegroundColor Green
}

# Milvus 配置
$milvusUri = [Environment]::GetEnvironmentVariable("MILVUS_URI", "Process")
if ([string]::IsNullOrEmpty($milvusUri)) {
    Write-Host "⚠️  警告: MILVUS_URI 未设置，将使用默认值" -ForegroundColor Yellow
    $WarningCount++
} else {
    Write-Host "✅ MILVUS_URI 已配置: $milvusUri" -ForegroundColor Green
}

# 服务地址配置
$lightragUrl = [Environment]::GetEnvironmentVariable("LIGHTRAG_BASE_URL", "Process")
if ([string]::IsNullOrEmpty($lightragUrl)) {
    Write-Host "⚠️  警告: LIGHTRAG_BASE_URL 未设置，将使用默认值" -ForegroundColor Yellow
    $WarningCount++
} else {
    Write-Host "✅ LIGHTRAG_BASE_URL 已配置: $lightragUrl" -ForegroundColor Green
}

# 前端访问地址
$frontendUrl = [Environment]::GetEnvironmentVariable("NEXT_PUBLIC_LANGGRAPH_URL", "Process")
if ([string]::IsNullOrEmpty($frontendUrl)) {
    Write-Host "⚠️  警告: NEXT_PUBLIC_LANGGRAPH_URL 未设置，将使用默认值" -ForegroundColor Yellow
    $WarningCount++
} else {
    Write-Host "✅ NEXT_PUBLIC_LANGGRAPH_URL 已配置: $frontendUrl" -ForegroundColor Green
}

# 检查端口冲突
Write-Host ""
Write-Host "检查端口占用..." -ForegroundColor Cyan

function Test-Port {
    param([int]$Port, [string]$Service)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "⚠️  警告: 端口 $Port ($Service) 已被占用" -ForegroundColor Yellow
        $script:WarningCount++
    } else {
        Write-Host "✅ 端口 $Port ($Service) 可用" -ForegroundColor Green
    }
}

$redisPort = [Environment]::GetEnvironmentVariable("REDIS_PORT", "Process")
if ([string]::IsNullOrEmpty($redisPort)) { $redisPort = "6379" }
Test-Port -Port $redisPort -Service "Redis"

$milvusPort = [Environment]::GetEnvironmentVariable("MILVUS_PORT", "Process")
if ([string]::IsNullOrEmpty($milvusPort)) { $milvusPort = "19530" }
Test-Port -Port $milvusPort -Service "Milvus"

$lightragPort = [Environment]::GetEnvironmentVariable("LIGHTRAG_PORT", "Process")
if ([string]::IsNullOrEmpty($lightragPort)) { $lightragPort = "9621" }
Test-Port -Port $lightragPort -Service "LightRAG"

$langgraphPort = [Environment]::GetEnvironmentVariable("LANGGRAPH_PORT", "Process")
if ([string]::IsNullOrEmpty($langgraphPort)) { $langgraphPort = "2025" }
Test-Port -Port $langgraphPort -Service "LangGraph"

$frontendPort = [Environment]::GetEnvironmentVariable("FRONTEND_PORT", "Process")
if ([string]::IsNullOrEmpty($frontendPort)) { $frontendPort = "3200" }
Test-Port -Port $frontendPort -Service "Frontend"

# 总结
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "验证完成" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "错误: $ErrorCount" -ForegroundColor $(if ($ErrorCount -gt 0) { "Red" } else { "Green" })
Write-Host "警告: $WarningCount" -ForegroundColor $(if ($WarningCount -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

if ($ErrorCount -gt 0) {
    Write-Host "❌ 验证失败，请修复上述错误后重试" -ForegroundColor Red
    exit 1
} elseif ($WarningCount -gt 0) {
    Write-Host "⚠️  验证通过，但有警告，建议检查上述警告项" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "✅ 所有检查通过，可以启动服务" -ForegroundColor Green
    exit 0
}

