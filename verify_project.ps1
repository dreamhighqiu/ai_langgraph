# 项目验证脚本 (Windows PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  AI LangGraph 项目验证" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查项目结构
Write-Host "1. 检查项目结构..." -ForegroundColor Yellow
$requiredDirs = @(
    "anything-chat-rag",
    "testing-agents-service",
    "testing-deep-agents-ui",
    "deepagents"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "✓ $dir 存在" -ForegroundColor Green
    } else {
        Write-Host "✗ $dir 不存在" -ForegroundColor Red
    }
}

# 检查配置文件
Write-Host ""
Write-Host "2. 检查配置文件..." -ForegroundColor Yellow
$requiredFiles = @(
    "docker-compose.yml",
    "env.docker.example",
    "Dockerfile.backend",
    "Dockerfile.frontend",
    ".gitignore",
    "requirements.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✓ $file 存在" -ForegroundColor Green
    } else {
        Write-Host "✗ $file 不存在" -ForegroundColor Red
    }
}

# 检查敏感文件（应该已删除）
Write-Host ""
Write-Host "3. 检查敏感文件（应该不存在）..." -ForegroundColor Yellow
$sensitivePatterns = @("*邱云霞*", "*简历*", "*学历*")
$foundSensitive = $false

foreach ($pattern in $sensitivePatterns) {
    $files = Get-ChildItem -Path . -Recurse -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "✗ 发现敏感文件: $($files.FullName)" -ForegroundColor Red
        $foundSensitive = $true
    }
}

if (-not $foundSensitive) {
    Write-Host "✓ 未发现敏感文件" -ForegroundColor Green
}

# 检查无用目录（应该已删除）
Write-Host ""
Write-Host "4. 检查无用目录（应该不存在）..." -ForegroundColor Yellow
$unwantedDirs = @(
    "example",
    "image_install",
    "anything-chat-rag\reproduce",
    "anything-chat-rag\build",
    "testing-agents-service\src"
)

$foundUnwanted = $false
foreach ($dir in $unwantedDirs) {
    if (Test-Path $dir) {
        Write-Host "✗ 发现无用目录: $dir" -ForegroundColor Red
        $foundUnwanted = $true
    }
}

if (-not $foundUnwanted) {
    Write-Host "✓ 未发现无用目录" -ForegroundColor Green
}

# 检查 Docker Compose
Write-Host ""
Write-Host "5. 检查 Docker Compose..." -ForegroundColor Yellow
try {
    docker compose version | Out-Null
    Write-Host "✓ Docker Compose 已安装" -ForegroundColor Green
    
    # 验证配置
    docker compose config | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ docker-compose.yml 配置有效" -ForegroundColor Green
        
        $serviceCount = (docker compose config --services).Count
        Write-Host "✓ 配置了 $serviceCount 个服务" -ForegroundColor Green
    } else {
        Write-Host "✗ docker-compose.yml 配置无效" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Docker Compose 未安装或无法运行" -ForegroundColor Red
}

# 检查环境变量
Write-Host ""
Write-Host "6. 检查环境变量..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env 文件存在" -ForegroundColor Green
    
    $envContent = Get-Content ".env" -Raw
    $requiredVars = @("OPENAI_API_KEY", "OPENAI_MODEL")
    
    foreach ($var in $requiredVars) {
        if ($envContent -match $var) {
            Write-Host "✓ $var 已配置" -ForegroundColor Green
        } else {
            Write-Host "⚠ $var 未配置" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "⚠ .env 文件不存在（可从 env.docker.example 复制）" -ForegroundColor Yellow
}

# 检查 Python 依赖
Write-Host ""
Write-Host "7. 检查 Python 依赖..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    $depCount = (Get-Content "requirements.txt" | Where-Object { $_ -notmatch "^#" -and $_ -ne "" }).Count
    Write-Host "✓ requirements.txt 包含 $depCount 个依赖" -ForegroundColor Green
}

# 总结
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  验证完成" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "1. 如果 .env 不存在: Copy-Item env.docker.example .env"
Write-Host "2. 编辑 .env 文件，确保 OPENAI_API_KEY 正确"
Write-Host "3. 启动服务: docker compose up -d"
Write-Host "4. 查看日志: docker compose logs -f"
Write-Host ""

