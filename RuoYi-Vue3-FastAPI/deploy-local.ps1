# ================================
# AI智能测试平台 - 本地开发部署脚本 (Windows PowerShell)
# 
# 使用 uv 管理 Python 虚拟环境
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
$PYTHON_VERSION = "3.11"

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
  使用 uv 管理 Python 虚拟环境
  
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
  init        初始化本地开发环境 (使用uv)
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

# 检查并安装 uv
function Test-UV {
    try {
        $uvVersion = uv --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "uv: $uvVersion"
            return $true
        }
    } catch {}
    
    Write-Warn "uv 未安装，正在安装..."
    
    try {
        # 使用 PowerShell 安装 uv
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        
        # 刷新环境变量
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # 验证安装
        $uvVersion = uv --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "uv 安装成功: $uvVersion"
            return $true
        }
    } catch {
        Write-Err "uv 安装失败: $_"
    }
    
    Write-Err "请手动安装 uv: powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    return $false
}

# 检查依赖
function Test-Dependencies {
    Write-Info "检查本地依赖..."
    
    $hasError = $false
    
    # 检查 uv
    if (-not (Test-UV)) {
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
    
    # 使用 uv 创建 Python 虚拟环境
    Write-Info "使用 uv 创建 Python 虚拟环境..."
    Push-Location $BACKEND_DIR
    
    try {
        if (-not (Test-Path ".venv")) {
            uv venv --python $PYTHON_VERSION
            Write-Success "虚拟环境创建成功 (.venv)"
        } else {
            Write-Info "虚拟环境已存在"
        }
        
        # 安装依赖
        Write-Info "使用 uv 安装 Python 依赖..."
        uv pip install -r requirements.txt
        uv pip install minio python-dotenv
        Write-Success "Python 依赖安装完成"
        
        # 创建环境配置
        if (-not (Test-Path ".env.dev")) {
            Write-Info "创建环境配置文件..."
            Copy-Item "env.example" ".env.dev"
            Write-Success "已创建 .env.dev，请检查配置"
        } else {
            Write-Info "环境配置文件已存在"
        }
    } finally {
        Pop-Location
    }
    
    # 前端依赖
    Write-Info "安装前端依赖 (可能需要几分钟)..."
    Push-Location $FRONTEND_DIR
    try {
        # 检查是否已有 node_modules
        if (Test-Path "node_modules") {
            Write-Info "node_modules 已存在，检查是否需要更新..."
            npm install --prefer-offline --no-audit --progress=true
        } else {
            Write-Info "首次安装，请稍候..."
            npm install --no-audit --progress=true
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "前端依赖安装完成"
        } else {
            Write-Err "前端依赖安装失败"
            exit 1
        }
    } finally {
        Pop-Location
    }
    
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
    
    Push-Location $BACKEND_DIR
    
    try {
        # 检查 pymysql 是否安装
        $result = uv pip show pymysql 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Info "安装 pymysql..."
            uv pip install pymysql
        }
        
        # 运行数据库初始化工具
        uv run python init_db.py --env dev
    } finally {
        Pop-Location
    }
}

# 启动后端
function Start-Backend {
    Write-Info "启动后端服务 (热重载模式)..."
    
    # 检查是否已运行
    if (Test-Path ".pids\backend.pid") {
        $pid = Get-Content ".pids\backend.pid"
        try {
            Get-Process -Id $pid -ErrorAction Stop | Out-Null
            Write-Warn "后端服务已在运行 (PID: $pid)"
            Write-Info "💡 代码更改将自动重载，无需重启"
            return
        } catch {}
    }
    
    # 创建目录
    New-Item -ItemType Directory -Force -Path "logs", ".pids" | Out-Null
    
    Push-Location $BACKEND_DIR
    
    try {
        # 激活虚拟环境并启动
        $env:APP_ENV = "dev"
        
        Write-Info "启动中 (uvicorn --reload)..."
        
        # 使用 uvicorn 直接启动，启用热重载
        $process = Start-Process -FilePath "uv" -ArgumentList "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9099", "--reload", "--reload-dir", "." `
            -PassThru -WindowStyle Hidden `
            -RedirectStandardOutput "..\logs\backend.log" `
            -RedirectStandardError "..\logs\backend_error.log"
        
        Start-Sleep -Seconds 5
        
        if (-not $process.HasExited) {
            $process.Id | Out-File -FilePath "..\`.pids\backend.pid"
            Write-Success "后端服务启动成功 ✅"
            Write-Host "  🌐 地址: http://localhost:9099/dev-api"
            Write-Host "  📚 文档: http://localhost:9099/dev-api/docs"
            Write-Host "  🔧 PID:  $($process.Id)"
            Write-Host "  📝 日志: logs\backend.log"
            Write-Host "  🔥 热重载: 已启用 (代码更改自动生效)"
        } else {
            Write-Err "后端启动失败，请查看日志: logs\backend_error.log"
            if (Test-Path "..\logs\backend_error.log") {
                Get-Content "..\logs\backend_error.log" | Select-Object -Last 20
            }
        }
    } finally {
        Pop-Location
    }
}

# 启动前端
function Start-Frontend {
    Write-Info "启动前端服务 (HMR 热更新模式)..."
    
    # 检查是否已运行
    if (Test-Path ".pids\frontend.pid") {
        $pid = Get-Content ".pids\frontend.pid"
        try {
            Get-Process -Id $pid -ErrorAction Stop | Out-Null
            Write-Warn "前端服务已在运行 (PID: $pid)"
            Write-Info "💡 代码更改将自动热更新，无需重启"
            return
        } catch {}
    }
    
    Push-Location $FRONTEND_DIR
    
    try {
        Write-Info "启动中 (Vite HMR)..."
        $process = Start-Process -FilePath "npm" -ArgumentList "run", "dev" `
            -PassThru -WindowStyle Hidden `
            -RedirectStandardOutput "..\logs\frontend.log" `
            -RedirectStandardError "..\logs\frontend_error.log"
        
        Start-Sleep -Seconds 8
        
        if (-not $process.HasExited) {
            $process.Id | Out-File -FilePath "..\`.pids\frontend.pid"
            Write-Success "前端服务启动成功 ✅"
            Write-Host "  🌐 地址: http://localhost:5173"
            Write-Host "  🔧 PID:  $($process.Id)"
            Write-Host "  📝 日志: logs\frontend.log"
            Write-Host "  🔥 HMR:  已启用 (代码更改自动热更新)"
        } else {
            Write-Err "前端启动失败，请查看日志: logs\frontend_error.log"
        }
    } finally {
        Pop-Location
    }
}

# 启动所有服务
function Start-All {
    Write-Info "启动本地开发服务 (Debug 模式)..."
    Write-Host ""
    
    Start-Backend
    Write-Host ""
    Start-Frontend
    
    Write-Host ""
    Write-Host "========================================"
    Write-Success "🚀 本地开发服务启动完成！"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "本地服务:"
    Write-Host "  🌐 前端: http://localhost:5173"
    Write-Host "  🔧 后端: http://localhost:9099/dev-api"
    Write-Host "  📚 文档: http://localhost:9099/dev-api/docs"
    Write-Host ""
    Write-Host "远程服务 ($REMOTE_SERVER):"
    Write-Host "  MySQL:        ${REMOTE_SERVER}:3306"
    Write-Host "  Redis:        ${REMOTE_SERVER}:6379"
    Write-Host "  MinIO控制台:  http://${REMOTE_SERVER}:9001"
    Write-Host "  Milvus管理:   http://${REMOTE_SERVER}:3000"
    Write-Host ""
    Write-Host "默认账号: admin / admin123"
    Write-Host ""
    Write-Host "========================================"
    Write-Host "🔥 热重载模式已启用:"
    Write-Host "  • 后端: 修改 Python 代码后自动重载 (uvicorn --reload)"
    Write-Host "  • 前端: 修改 Vue/JS 代码后自动热更新 (Vite HMR)"
    Write-Host "  • 无需手动重启服务，代码更改自动生效!"
    Write-Host "========================================"
}

# 根据端口杀进程
function Stop-PortProcess {
    param([int]$Port, [string]$Name)
    
    # 获取占用端口的进程
    $connections = netstat -ano | Select-String ":$Port\s+" | Select-String "LISTENING"
    
    if ($connections) {
        $pids = @()
        foreach ($line in $connections) {
            $parts = $line.ToString().Trim() -split '\s+'
            $pidStr = $parts[-1]
            if ($pidStr -match '^\d+$' -and $pidStr -ne '0') {
                $pids += [int]$pidStr
            }
        }
        
        $pids = $pids | Sort-Object -Unique
        
        foreach ($pid in $pids) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Success "已杀掉占用端口 $Port 的进程 (PID: $pid)"
            } catch {
                Write-Warn "无法杀掉进程 $pid"
            }
        }
    }
}

# 停止服务
function Stop-All {
    Write-Info "停止本地服务..."
    Write-Host ""
    
    # 1. 首先尝试通过 PID 文件停止
    Write-Info "通过 PID 文件停止服务..."
    
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
    
    # 2. 强制清理端口占用（确保端口被释放）
    Write-Host ""
    Write-Info "检查并清理端口占用..."
    
    # 清理后端端口 9099
    Stop-PortProcess -Port 9099 -Name "后端"
    
    # 清理前端端口 5173 和 5174
    Stop-PortProcess -Port 5173 -Name "前端"
    Stop-PortProcess -Port 5174 -Name "前端备用"
    
    # 3. 清理 PID 文件
    Remove-Item ".pids\backend.pid" -Force -ErrorAction SilentlyContinue
    Remove-Item ".pids\frontend.pid" -Force -ErrorAction SilentlyContinue
    
    Write-Host ""
    Write-Success "本地服务已全部停止，端口已释放"
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
