# ================================
# AI智能测试平台部署脚本 (Windows PowerShell)
# 服务器: 47.110.95.246
# ================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$EnvMode = "dev"
)

# 配置变量
$SERVER_IP = "47.110.95.246"
$PROJECT_NAME = "ai-testing-platform"
$BACKEND_DIR = "ruoyi-fastapi-backend"
$FRONTEND_DIR = "ruoyi-fastapi-frontend"

# 打印带颜色的消息
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-Err { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# 显示帮助信息
function Show-Help {
    Write-Host @"

AI智能测试平台部署脚本 (Windows)

用法: .\deploy.ps1 [命令] [选项]

命令:
  init        初始化环境 (安装依赖)
  db          初始化数据库
  backend     启动后端服务
  frontend    启动前端服务
  all         启动所有服务
  stop        停止所有服务
  status      查看服务状态
  help        显示帮助信息

选项:
  dev         开发环境 (默认)
  prod        生产环境

示例:
  .\deploy.ps1 init          # 初始化环境
  .\deploy.ps1 db            # 初始化数据库
  .\deploy.ps1 all dev       # 开发环境启动所有服务
  .\deploy.ps1 all prod      # 生产环境启动所有服务
  .\deploy.ps1 stop          # 停止所有服务

"@
}

# 检查依赖
function Test-Dependencies {
    Write-Info "检查依赖..."
    
    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python 已安装: $pythonVersion"
    } catch {
        Write-Err "Python 未安装"
        exit 1
    }
    
    # 检查Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js 已安装: $nodeVersion"
    } catch {
        Write-Err "Node.js 未安装"
        exit 1
    }
    
    # 检查npm
    try {
        $npmVersion = npm --version 2>&1
        Write-Success "npm 已安装: $npmVersion"
    } catch {
        Write-Err "npm 未安装"
        exit 1
    }
}

# 初始化环境
function Initialize-Environment {
    Write-Info "初始化环境..."
    
    Test-Dependencies
    
    # 创建Python虚拟环境
    Write-Info "创建Python虚拟环境..."
    Push-Location $BACKEND_DIR
    
    if (-not (Test-Path "venv")) {
        python -m venv venv
        Write-Success "虚拟环境创建成功"
    }
    
    # 激活虚拟环境并安装依赖
    Write-Info "安装Python依赖..."
    & .\venv\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 安装额外依赖
    pip install minio langgraph-sdk python-dotenv
    
    Write-Success "Python依赖安装完成"
    
    # 创建环境配置文件
    $envFile = ".env.$EnvMode"
    if (-not (Test-Path $envFile)) {
        Write-Info "创建环境配置文件..."
        Copy-Item "env.example" $envFile
        Write-Warn "请编辑 $envFile 文件配置数据库等信息"
    }
    
    Pop-Location
    
    # 安装前端依赖
    Write-Info "安装前端依赖..."
    Push-Location $FRONTEND_DIR
    npm install
    Write-Success "前端依赖安装完成"
    Pop-Location
    
    Write-Success "环境初始化完成！"
}

# 初始化数据库
function Initialize-Database {
    Write-Info "初始化数据库..."
    
    $DB_HOST = if ($env:DB_HOST) { $env:DB_HOST } else { $SERVER_IP }
    $DB_PORT = if ($env:DB_PORT) { $env:DB_PORT } else { "3306" }
    $DB_USER = if ($env:DB_USERNAME) { $env:DB_USERNAME } else { "root" }
    $DB_PASS = if ($env:DB_PASSWORD) { $env:DB_PASSWORD } else { "root123456" }
    $DB_NAME = if ($env:DB_DATABASE) { $env:DB_DATABASE } else { "ai_db" }
    
    Write-Info "数据库配置:"
    Write-Host "  Host: $DB_HOST"
    Write-Host "  Port: $DB_PORT"
    Write-Host "  User: $DB_USER"
    Write-Host "  Database: $DB_NAME"
    
    Write-Info "请使用MySQL客户端执行以下SQL文件:"
    Write-Host "  1. $BACKEND_DIR\sql\ruoyi-fastapi.sql"
    Write-Host "  2. $BACKEND_DIR\sql\testing_platform.sql"
    
    Write-Host ""
    Write-Host "命令示例:"
    Write-Host "mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p $DB_NAME < $BACKEND_DIR\sql\ruoyi-fastapi.sql"
    Write-Host "mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p $DB_NAME < $BACKEND_DIR\sql\testing_platform.sql"
}

# 启动后端服务
function Start-Backend {
    Write-Info "启动后端服务 (环境: $EnvMode)..."
    
    # 创建必要目录
    New-Item -ItemType Directory -Force -Path "logs", ".pids" | Out-Null
    
    Push-Location $BACKEND_DIR
    
    # 激活虚拟环境
    & .\venv\Scripts\Activate.ps1
    
    # 设置环境变量
    $env:APP_ENV = $EnvMode
    
    # 启动服务
    $process = Start-Process -FilePath "python" -ArgumentList "app.py", "--env", $EnvMode -PassThru -RedirectStandardOutput "..\logs\backend.log" -RedirectStandardError "..\logs\backend_error.log" -WindowStyle Hidden
    
    # 保存PID
    $process.Id | Out-File -FilePath "..\`.pids\backend.pid"
    
    Pop-Location
    
    Write-Success "后端服务启动成功 (PID: $($process.Id))"
    Write-Info "日志文件: logs\backend.log"
}

# 启动前端服务
function Start-Frontend {
    Write-Info "启动前端服务 (环境: $EnvMode)..."
    
    Push-Location $FRONTEND_DIR
    
    if ($EnvMode -eq "prod") {
        Write-Info "构建生产版本..."
        npm run build:prod
        Write-Success "前端构建完成，请配置nginx指向dist目录"
    } else {
        Write-Info "启动开发服务器..."
        $process = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -RedirectStandardOutput "..\logs\frontend.log" -RedirectStandardError "..\logs\frontend_error.log" -WindowStyle Hidden
        $process.Id | Out-File -FilePath "..\`.pids\frontend.pid"
        Write-Success "前端服务启动成功 (PID: $($process.Id))"
    }
    
    Pop-Location
    
    Write-Info "日志文件: logs\frontend.log"
}

# 启动所有服务
function Start-All {
    Write-Info "启动所有服务..."
    
    Start-Backend
    Start-Sleep -Seconds 3
    Start-Frontend
    
    Write-Success "所有服务启动完成！"
    
    Write-Host ""
    Write-Info "服务地址:"
    Write-Host "  后端API: http://${SERVER_IP}:9099/dev-api"
    Write-Host "  前端页面: http://${SERVER_IP}:80 (生产) 或 http://localhost:5173 (开发)"
    Write-Host ""
    Write-Info "基础设施服务:"
    Write-Host "  MySQL: ${SERVER_IP}:3306"
    Write-Host "  Redis: ${SERVER_IP}:6379"
    Write-Host "  MinIO: ${SERVER_IP}:9000 (API) / ${SERVER_IP}:9001 (Console)"
    Write-Host "  Milvus: ${SERVER_IP}:19530"
    Write-Host "  Attu: ${SERVER_IP}:3000"
    Write-Host "  Ollama: ${SERVER_IP}:11434"
}

# 停止所有服务
function Stop-All {
    Write-Info "停止所有服务..."
    
    # 停止后端
    $backendPidFile = ".pids\backend.pid"
    if (Test-Path $backendPidFile) {
        $pid = Get-Content $backendPidFile
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Success "后端服务已停止 (PID: $pid)"
        } catch {
            Write-Warn "后端服务可能已停止"
        }
        Remove-Item $backendPidFile -Force
    }
    
    # 停止前端
    $frontendPidFile = ".pids\frontend.pid"
    if (Test-Path $frontendPidFile) {
        $pid = Get-Content $frontendPidFile
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Success "前端服务已停止 (PID: $pid)"
        } catch {
            Write-Warn "前端服务可能已停止"
        }
        Remove-Item $frontendPidFile -Force
    }
    
    Write-Success "所有服务已停止"
}

# 查看服务状态
function Show-Status {
    Write-Info "服务状态:"
    
    Write-Host ""
    Write-Host "=== 应用服务 ==="
    
    # 后端状态
    $backendPidFile = ".pids\backend.pid"
    if (Test-Path $backendPidFile) {
        $pid = Get-Content $backendPidFile
        try {
            $process = Get-Process -Id $pid -ErrorAction Stop
            Write-Success "后端服务: 运行中 (PID: $pid)"
        } catch {
            Write-Err "后端服务: 已停止"
        }
    } else {
        Write-Warn "后端服务: 未启动"
    }
    
    # 前端状态
    $frontendPidFile = ".pids\frontend.pid"
    if (Test-Path $frontendPidFile) {
        $pid = Get-Content $frontendPidFile
        try {
            $process = Get-Process -Id $pid -ErrorAction Stop
            Write-Success "前端服务: 运行中 (PID: $pid)"
        } catch {
            Write-Err "前端服务: 已停止"
        }
    } else {
        Write-Warn "前端服务: 未启动"
    }
    
    Write-Host ""
    Write-Host "=== 基础设施服务 ($SERVER_IP) ==="
    
    # 检查端口连接
    $services = @(
        @{Name="MySQL"; Port=3306},
        @{Name="Redis"; Port=6379},
        @{Name="MinIO"; Port=9000},
        @{Name="Milvus"; Port=19530},
        @{Name="Ollama"; Port=11434}
    )
    
    foreach ($svc in $services) {
        $result = Test-NetConnection -ComputerName $SERVER_IP -Port $svc.Port -WarningAction SilentlyContinue
        if ($result.TcpTestSucceeded) {
            Write-Success "$($svc.Name): 运行中 (${SERVER_IP}:$($svc.Port))"
        } else {
            Write-Err "$($svc.Name): 无法连接"
        }
    }
}

# 主函数
switch ($Command) {
    "init" { Initialize-Environment }
    "db" { Initialize-Database }
    "backend" { Start-Backend }
    "frontend" { Start-Frontend }
    "all" { Start-All }
    "stop" { Stop-All }
    "status" { Show-Status }
    default { Show-Help }
}

