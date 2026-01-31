# Docker Compose 部署测试脚本 (Windows PowerShell)

$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"

Write-Host "========================================" -ForegroundColor $GREEN
Write-Host "  Docker Compose 部署验证" -ForegroundColor $GREEN
Write-Host "========================================" -ForegroundColor $GREEN
Write-Host ""

# 1. 检查 Docker
Write-Host "1. 检查 Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✓ Docker 已安装" -ForegroundColor $GREEN
} catch {
    Write-Host "✗ Docker 未安装" -ForegroundColor $RED
    exit 1
}

# 2. 检查 Docker Compose
Write-Host ""
Write-Host "2. 检查 Docker Compose..." -ForegroundColor Yellow
try {
    docker compose version | Out-Null
    $ComposeCmd = "docker compose"
    Write-Host "✓ Docker Compose V2 已安装" -ForegroundColor $GREEN
} catch {
    try {
        docker-compose --version | Out-Null
        $ComposeCmd = "docker-compose"
        Write-Host "✓ Docker Compose V1 已安装" -ForegroundColor $GREEN
    } catch {
        Write-Host "✗ Docker Compose 未安装" -ForegroundColor $RED
        exit 1
    }
}

# 3. 验证配置文件
Write-Host ""
Write-Host "3. 验证配置文件..." -ForegroundColor Yellow
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "✗ docker-compose.yml 不存在" -ForegroundColor $RED
    exit 1
}
Write-Host "✓ docker-compose.yml 存在" -ForegroundColor $GREEN

# 验证配置语法
try {
    & $ComposeCmd.Split(' ') config | Out-Null
    Write-Host "✓ docker-compose.yml 语法正确" -ForegroundColor $GREEN
} catch {
    Write-Host "✗ docker-compose.yml 语法错误" -ForegroundColor $RED
    & $ComposeCmd.Split(' ') config
    exit 1
}

# 4. 检查环境变量
Write-Host ""
Write-Host "4. 检查环境变量..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env 文件不存在" -ForegroundColor $YELLOW
    Write-Host "创建 .env 文件..."
    Copy-Item env.docker.example .env
    Write-Host "✓ 已从 env.docker.example 创建 .env" -ForegroundColor $GREEN
}

# 检查必需的环境变量
$envContent = Get-Content ".env" -Raw
if ($envContent -match "OPENAI_API_KEY" -and $envContent -notmatch "OPENAI_API_KEY=\s*$") {
    Write-Host "✓ OPENAI_API_KEY 已配置" -ForegroundColor $GREEN
} else {
    Write-Host "⚠ OPENAI_API_KEY 未配置或为空" -ForegroundColor $YELLOW
}

# 5. 检查 Dockerfile
Write-Host ""
Write-Host "5. 检查 Dockerfile..." -ForegroundColor Yellow
$requiredDockerfiles = @("Dockerfile.backend", "Dockerfile.frontend")
foreach ($dockerfile in $requiredDockerfiles) {
    if (Test-Path $dockerfile) {
        Write-Host "✓ $dockerfile 存在" -ForegroundColor $GREEN
    } else {
        Write-Host "✗ $dockerfile 不存在" -ForegroundColor $RED
        exit 1
    }
}

# 6. 检查必需目录
Write-Host ""
Write-Host "6. 检查必需目录..." -ForegroundColor Yellow
$requiredDirs = @(
    "anything-chat-rag",
    "testing-agents-service",
    "testing-deep-agents-ui",
    "deepagents"
)
foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "✓ $dir 存在" -ForegroundColor $GREEN
    } else {
        Write-Host "✗ $dir 不存在" -ForegroundColor $RED
        exit 1
    }
}

# 7. 检查敏感文件
Write-Host ""
Write-Host "7. 检查敏感文件（应该不存在）..." -ForegroundColor Yellow
$sensitivePatterns = @("*邱云霞*", "*简历*", "*学历*")
$sensitiveFound = $false
foreach ($pattern in $sensitivePatterns) {
    $files = Get-ChildItem -Path . -Recurse -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        foreach ($file in $files) {
            Write-Host "✗ 发现敏感文件: $($file.FullName)" -ForegroundColor $RED
            $sensitiveFound = $true
        }
    }
}
if (-not $sensitiveFound) {
    Write-Host "✓ 未发现敏感文件" -ForegroundColor $GREEN
}

# 8. 检查端口占用
Write-Host ""
Write-Host "8. 检查端口占用..." -ForegroundColor Yellow
$ports = @(2025, 3200, 6379, 9621, 19530)
$portsInUse = @()
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $portsInUse += $port
        Write-Host "⚠ 端口 $port 已被占用" -ForegroundColor $YELLOW
    } else {
        Write-Host "✓ 端口 $port 可用" -ForegroundColor $GREEN
    }
}
if ($portsInUse.Count -gt 0) {
    Write-Host "提示: 以下端口被占用: $($portsInUse -join ', ')" -ForegroundColor $YELLOW
    Write-Host "      这些端口将由 Docker 容器使用，请确保没有冲突"
}

# 9. 检查磁盘空间
Write-Host ""
Write-Host "9. 检查磁盘空间..." -ForegroundColor Yellow
$drive = (Get-Location).Drive
$freeSpace = [math]::Round(($drive.Free / 1GB), 2)
$requiredSpace = 20
if ($freeSpace -gt $requiredSpace) {
    Write-Host "✓ 磁盘空间充足 ($freeSpace GB 可用)" -ForegroundColor $GREEN
} else {
    Write-Host "⚠ 磁盘空间可能不足 ($freeSpace GB 可用, 建议 $requiredSpace GB+)" -ForegroundColor $YELLOW
}

# 10. 生成部署报告
Write-Host ""
Write-Host "========================================" -ForegroundColor $GREEN
Write-Host "  验证完成" -ForegroundColor $GREEN
Write-Host "========================================" -ForegroundColor $GREEN
Write-Host ""
Write-Host "部署命令:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 最小配置（推荐）:"
Write-Host "   $ComposeCmd up -d"
Write-Host ""
Write-Host "2. 完整配置（包含可选服务）:"
Write-Host "   $ComposeCmd --profile full up -d"
Write-Host ""
Write-Host "3. 查看日志:"
Write-Host "   $ComposeCmd logs -f [service-name]"
Write-Host ""
Write-Host "4. 检查状态:"
Write-Host "   $ComposeCmd ps"
Write-Host ""
Write-Host "5. 停止服务:"
Write-Host "   $ComposeCmd down"
Write-Host ""

# 询问是否立即部署
$deploy = Read-Host "是否现在部署服务？(y/n)"
if ($deploy -eq 'y' -or $deploy -eq 'Y') {
    Write-Host ""
    Write-Host "开始部署..." -ForegroundColor $GREEN
    & $ComposeCmd.Split(' ') up -d
    
    Write-Host ""
    Write-Host "等待服务启动..." -ForegroundColor $GREEN
    Start-Sleep -Seconds 10
    
    Write-Host ""
    Write-Host "服务状态:" -ForegroundColor Yellow
    & $ComposeCmd.Split(' ') ps
    
    Write-Host ""
    Write-Host "部署完成！" -ForegroundColor $GREEN
    Write-Host ""
    Write-Host "访问地址:" -ForegroundColor Yellow
    Write-Host "  - 前端: http://localhost:3200"
    Write-Host "  - API: http://localhost:2025"
    Write-Host "  - API 文档: http://localhost:2025/docs"
}

