# ================================
# AI智能测试平台 - 本地开发部署脚本 (Windows PowerShell)
# 
# 本地开发场景：
#   - 前端服务: 本地 (localhost:5173)
#   - 后端服务: 本地 (localhost:9099)
#   - 基础设施: 远程 (47.110.95.246)
# ================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# 配置变量
$REMOTE_SERVER = "47.110.95.246"
$BACKEND_DIR = "ruoyi-fastapi-backend"
$FRONTEND_DIR = "ruoyi-fastapi-frontend"
$ENV_MODE = "dev"

# 打印函数
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-Err { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# 显示帮助
function Show-Help {
    Write-Host @"

AI智能测试平台 - 本地开发部署脚本

========================================
部署模式说明:
  本地开发: 前端+后端在本地，基础设施在远程服务器
  
  本地服务:
    - 前端: http://localhost:5173
    - 后端: http://localhost:9099
    
  远程服务 ($REMOTE_SERVER):
    - MySQL:  3306
    - Redis:  6379
    - MinIO:  9000/9001
    - Milvus: 19530
    - Ollama: 11434
========================================

用法: .\deploy-local.ps1 [命令]

命令:
  init        初始化本地开发环境
  check       检查远程服务连接
  backend     启动后端服务
  frontend    启动前端服务
  all         启动所有本地服务
  stop        停止所有本地服务
  status      查看服务状态
  db          初始化数据库
  help        显示帮助

示例:
  .\deploy-local.ps1 init       # 初始化环境
  .\deploy-local.ps1 check      # 检查远程服务
  .\deploy-local.ps1 all        # 启动本地服务

"@
}

# 检查依赖
function Test-Dependencies {
    Write-Info "检查本地依赖..."
    
    $hasError = $false
    
    # Python
    try {
        $ver = python --version 2>&1
        Write-Success "Python: $ver"
    } catch {
        Write-Err "Python 未安装"
        $hasError = $true
    }
    
    # Node.js
    try {
        $ver = node --version 2>&1
        Write-Success "Node.js: $ver"
    } catch {
        Write-Err "Node.js 未安装"
        $hasError = $true
    }
    
    # npm
    try {
        $ver = npm --version 2>&1
        Write-Success "npm: $ver"
    } catch {
        Write-Err "npm 未安装"
        $hasError = $true
    }
    
    if ($hasError) {
        exit 1
    }
}

# 检查远程服务连接
function Test-RemoteServices {
    Write-Info "检查远程服务连接 ($REMOTE_SERVER)..."
    Write-Host ""
    
    $services = @(
        @{Name="MySQL"; Port=3306},
        @{Name="Redis"; Port=6379},
        @{Name="MinIO API"; Port=9000},
        @{Name="MinIO Console"; Port=9001},
        @{Name="Milvus"; Port=19530},
        @{Name="Attu"; Port=3000},
        @{Name="Ollama"; Port=11434}
    )
    
    $allOk = $true
    foreach ($svc in $services) {
        try {
            $result = Test-NetConnection -ComputerName $REMOTE_SERVER -Port $svc.Port -WarningAction SilentlyContinue -InformationLevel Quiet
            if ($result) {
                Write-Success "$($svc.Name): OK (${REMOTE_SERVER}:$($svc.Port))"
            } else {
                Write-Err "$($svc.Name): 无法连接 (${REMOTE_SERVER}:$($svc.Port))"
                $allOk = $false
            }
        } catch {
            Write-Err "$($svc.Name): 连接异常"
            $allOk = $false
        }
    }
    
    Write-Host ""
    if ($allOk) {
        Write-Success "所有远程服务连接正常！"
    } else {
        Write-Warn "部分服务无法连接，请检查网络或服务状态"
    }
}

# 初始化环境
function Initialize-Environment {
    Write-Info "初始化本地开发环境..."
    Write-Host ""
    
    Test-Dependencies
    Write-Host ""
    
    # Python虚拟环境
    Write-Info "创建Python虚拟环境..."
    Push-Location $BACKEND_DIR
    
    if (-not (Test-Path "venv")) {
        python -m venv venv
        Write-Success "虚拟环境创建成功"
    } else {
        Write-Info "虚拟环境已存在"
    }
    
    # 安装依赖
    Write-Info "安装Python依赖..."
    & .\venv\Scripts\Activate.ps1
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    pip install minio python-dotenv -q
    Write-Success "Python依赖安装完成"
    
    # 创建环境配置
    if (-not (Test-Path ".env.dev")) {
        Write-Info "创建环境配置文件..."
        Copy-Item "env.example" ".env.dev"
        Write-Success "已创建 .env.dev，请检查配置"
    } else {
        Write-Info "环境配置文件已存在"
    }
    
    Pop-Location
    
    # 前端依赖
    Write-Info "安装前端依赖..."
    Push-Location $FRONTEND_DIR
    npm install --silent
    Write-Success "前端依赖安装完成"
    Pop-Location
    
    # 创建目录
    New-Item -ItemType Directory -Force -Path "logs", ".pids" | Out-Null
    
    Write-Host ""
    Write-Success "本地开发环境初始化完成！"
    Write-Host ""
    Write-Info "下一步:"
    Write-Host "  1. 运行 .\deploy-local.ps1 check 检查远程服务"
    Write-Host "  2. 运行 .\deploy-local.ps1 db 初始化数据库"
    Write-Host "  3. 运行 .\deploy-local.ps1 all 启动服务"
}

# 初始化数据库
function Initialize-Database {
    Write-Info "数据库初始化..."
    Write-Host ""
    Write-Host "请使用MySQL客户端连接远程数据库执行SQL文件:"
    Write-Host ""
    Write-Host "  服务器: $REMOTE_SERVER"
    Write-Host "  端口:   3306"
    Write-Host "  用户名: root"
    Write-Host "  密码:   root123456"
    Write-Host "  数据库: ai_db"
    Write-Host ""
    Write-Host "SQL文件:"
    Write-Host "  1. $BACKEND_DIR\sql\ruoyi-fastapi.sql (RuoYi基础表)"
    Write-Host "  2. $BACKEND_DIR\sql\testing_platform.sql (测试平台表)"
    Write-Host ""
    Write-Host "命令示例 (MySQL客户端):"
    Write-Host "  mysql -h $REMOTE_SERVER -P 3306 -u root -proot123456 ai_db < $BACKEND_DIR\sql\ruoyi-fastapi.sql"
    Write-Host "  mysql -h $REMOTE_SERVER -P 3306 -u root -proot123456 ai_db < $BACKEND_DIR\sql\testing_platform.sql"
    Write-Host ""
    Write-Host "或使用 Navicat/DBeaver 等工具执行"
}

# 启动后端
function Start-Backend {
    Write-Info "启动后端服务..."
    
    Push-Location $BACKEND_DIR
    
    # 检查是否已运行
    if (Test-Path "..\`.pids\backend.pid") {
        $pid = Get-Content "..\`.pids\backend.pid"
        try {
            Get-Process -Id $pid -ErrorAction Stop | Out-Null
            Write-Warn "后端服务已在运行 (PID: $pid)"
            Pop-Location
            return
        } catch {}
    }
    
    # 激活虚拟环境
    & .\venv\Scripts\Activate.ps1
    $env:APP_ENV = "dev"
    
    # 启动
    Write-Info "启动中..."
    $process = Start-Process -FilePath "python" -ArgumentList "app.py", "--env", "dev" -PassThru -WindowStyle Hidden -RedirectStandardOutput "..\logs\backend.log" -RedirectStandardError "..\logs\backend_error.log"
    
    Start-Sleep -Seconds 2
    
    if ($process.HasExited) {
        Write-Err "后端启动失败，请查看日志: logs\backend_error.log"
    } else {
        $process.Id | Out-File -FilePath "..\`.pids\backend.pid"
        Write-Success "后端服务启动成功"
        Write-Host "  地址: http://localhost:9099/dev-api"
        Write-Host "  文档: http://localhost:9099/dev-api/docs"
        Write-Host "  PID:  $($process.Id)"
        Write-Host "  日志: logs\backend.log"
    }
    
    Pop-Location
}

# 启动前端
function Start-Frontend {
    Write-Info "启动前端服务..."
    
    Push-Location $FRONTEND_DIR
    
    # 检查是否已运行
    if (Test-Path "..\`.pids\frontend.pid") {
        $pid = Get-Content "..\`.pids\frontend.pid"
        try {
            Get-Process -Id $pid -ErrorAction Stop | Out-Null
            Write-Warn "前端服务已在运行 (PID: $pid)"
            Pop-Location
            return
        } catch {}
    }
    
    # 启动
    Write-Info "启动中..."
    $process = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -WindowStyle Hidden -RedirectStandardOutput "..\logs\frontend.log" -RedirectStandardError "..\logs\frontend_error.log"
    
    Start-Sleep -Seconds 3
    
    if ($process.HasExited) {
        Write-Err "前端启动失败，请查看日志: logs\frontend_error.log"
    } else {
        $process.Id | Out-File -FilePath "..\`.pids\frontend.pid"
        Write-Success "前端服务启动成功"
        Write-Host "  地址: http://localhost:5173"
        Write-Host "  PID:  $($process.Id)"
        Write-Host "  日志: logs\frontend.log"
    }
    
    Pop-Location
}

# 启动所有服务
function Start-All {
    Write-Info "启动本地开发服务..."
    Write-Host ""
    
    # 创建目录
    New-Item -ItemType Directory -Force -Path "logs", ".pids" | Out-Null
    
    Start-Backend
    Write-Host ""
    Start-Frontend
    
    Write-Host ""
    Write-Host "========================================"
    Write-Success "本地开发服务启动完成！"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "本地服务:"
    Write-Host "  前端: http://localhost:5173"
    Write-Host "  后端: http://localhost:9099/dev-api"
    Write-Host "  文档: http://localhost:9099/dev-api/docs"
    Write-Host ""
    Write-Host "远程服务 ($REMOTE_SERVER):"
    Write-Host "  MySQL:        ${REMOTE_SERVER}:3306"
    Write-Host "  Redis:        ${REMOTE_SERVER}:6379"
    Write-Host "  MinIO控制台:  http://${REMOTE_SERVER}:9001"
    Write-Host "  Milvus管理:   http://${REMOTE_SERVER}:3000"
    Write-Host ""
    Write-Host "默认账号: admin / admin123"
    Write-Host "========================================"
}

# 停止服务
function Stop-All {
    Write-Info "停止本地服务..."
    
    # 停止后端
    if (Test-Path ".pids\backend.pid") {
        $pid = Get-Content ".pids\backend.pid"
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Success "后端服务已停止 (PID: $pid)"
        } catch {
            Write-Warn "后端服务可能已停止"
        }
        Remove-Item ".pids\backend.pid" -Force -ErrorAction SilentlyContinue
    }
    
    # 停止前端
    if (Test-Path ".pids\frontend.pid") {
        $pid = Get-Content ".pids\frontend.pid"
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Write-Success "前端服务已停止 (PID: $pid)"
        } catch {
            Write-Warn "前端服务可能已停止"
        }
        Remove-Item ".pids\frontend.pid" -Force -ErrorAction SilentlyContinue
    }
    
    Write-Success "本地服务已停止"
}

# 查看状态
function Show-Status {
    Write-Host ""
    Write-Host "========== 本地服务状态 =========="
    Write-Host ""
    
    # 后端
    if (Test-Path ".pids\backend.pid") {
        $pid = Get-Content ".pids\backend.pid"
        try {
            Get-Process -Id $pid -ErrorAction Stop | Out-Null
            Write-Success "后端: 运行中 (PID: $pid) - http://localhost:9099"
        } catch {
            Write-Err "后端: 已停止"
        }
    } else {
        Write-Warn "后端: 未启动"
    }
    
    # 前端
    if (Test-Path ".pids\frontend.pid") {
        $pid = Get-Content ".pids\frontend.pid"
        try {
            Get-Process -Id $pid -ErrorAction Stop | Out-Null
            Write-Success "前端: 运行中 (PID: $pid) - http://localhost:5173"
        } catch {
            Write-Err "前端: 已停止"
        }
    } else {
        Write-Warn "前端: 未启动"
    }
    
    Write-Host ""
    Write-Host "========== 远程服务状态 ($REMOTE_SERVER) =========="
    Write-Host ""
    
    Test-RemoteServices
}

# 主函数
switch ($Command) {
    "init" { Initialize-Environment }
    "check" { Test-RemoteServices }
    "db" { Initialize-Database }
    "backend" { Start-Backend }
    "frontend" { Start-Frontend }
    "all" { Start-All }
    "stop" { Stop-All }
    "status" { Show-Status }
    default { Show-Help }
}

