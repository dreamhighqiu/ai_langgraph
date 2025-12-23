# =============================================================================
# AI LangGraph 环境初始化脚本 (Windows PowerShell)
# 
# 功能: 使用 uv 创建统一虚拟环境并安装所有依赖
#
# 使用方法:
#   .\setup.ps1              # 初始化环境
#   .\setup.ps1 -Reinstall   # 重新安装（删除旧环境）
# =============================================================================

param(
    [switch]$Reinstall,
    [switch]$Help
)

# 项目根目录
$PROJECT_ROOT = $PSScriptRoot
Set-Location $PROJECT_ROOT

# 显示帮助信息
function Show-Help {
    Write-Host ""
    Write-Host "用法: .\setup.ps1 [选项]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "选项:" -ForegroundColor Yellow
    Write-Host "  -Reinstall   删除旧环境并重新安装"
    Write-Host "  -Help        显示帮助信息"
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1              # 首次安装"
    Write-Host "  .\setup.ps1 -Reinstall   # 重新安装"
    Write-Host ""
}

function Print-Info {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Print-Success {
    param([string]$Message)
    Write-Host "[✓] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[!] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Print-Error {
    param([string]$Message)
    Write-Host "[✗] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

# 检查 uv 是否安装
function Check-UV {
    try {
        $uvVersion = uv --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Print-Success "uv 已安装 ($uvVersion)"
            return $true
        }
    } catch {}
    
    Print-Error "uv 未安装！请先安装 uv:"
    Write-Host ""
    Write-Host "  Windows (PowerShell):" -ForegroundColor Cyan
    Write-Host "  powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    Write-Host ""
    Write-Host "  或使用 pip:" -ForegroundColor Cyan
    Write-Host "  pip install uv"
    Write-Host ""
    return $false
}

# 检查 Python
function Check-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Print-Success "Python 版本: $pythonVersion"
            return $true
        }
    } catch {}
    
    Print-Warning "Python 未安装，uv 会自动下载所需的 Python 版本"
    return $false
}

# 检查 Node.js
function Check-Node {
    try {
        $nodeVersion = node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Print-Success "Node.js 版本: $nodeVersion"
            return $true
        }
    } catch {}
    
    Print-Warning "Node.js 未安装（前端服务需要）"
    return $false
}

# 清理旧环境
function Clean-Environment {
    if ($Reinstall) {
        Print-Info "删除旧的虚拟环境..."
        if (Test-Path ".venv") {
            Remove-Item -Recurse -Force ".venv"
        }
        if (Test-Path "uv.lock") {
            Remove-Item -Force "uv.lock"
        }
        Print-Success "旧环境已清理"
    }
}

# 使用 uv sync 安装依赖
function Install-WithUV {
    Print-Info "使用 uv 同步依赖（可能需要几分钟）..."
    
    # 使用 uv sync 安装主项目依赖
    Print-Info "同步主项目依赖..."
    uv sync --python 3.11
    if ($LASTEXITCODE -ne 0) {
        Print-Error "主项目依赖安装失败"
        return $false
    }
    
    # 安装 anything-chat-rag (可编辑模式)
    Print-Info "安装 LightRAG (anything-chat-rag)..."
    uv pip install -e "./anything-chat-rag[api]" --quiet
    if ($LASTEXITCODE -ne 0) {
        Print-Warning "LightRAG 安装失败（非关键错误）"
    }
    
    # 配置 Python 路径
    Print-Info "配置 Python 路径..."
    try {
        $sitePackages = & .venv\Scripts\python.exe -c "import site; print(site.getsitepackages()[0])"
        
        # 创建 .pth 文件以添加 src 目录到 Python 路径
        $pthContent = @"
$PROJECT_ROOT\testing-deep-agents-service\src
$PROJECT_ROOT\mcp-server\src
$PROJECT_ROOT\anything-chat-rag
"@
        $pthFile = Join-Path $sitePackages "ai-langgraph.pth"
        $pthContent | Out-File -FilePath $pthFile -Encoding utf8
        
        Print-Success "Python 路径配置完成"
    } catch {
        Print-Warning "Python 路径配置失败: $_"
    }
    
    Print-Success "所有依赖安装完成"
    return $true
}

# 创建必要的目录
function Create-Directories {
    $dirs = @("logs", ".pids", "rag_storage")
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    Print-Success "目录结构创建完成"
}

# 检查 .env 文件
function Check-EnvFiles {
    $missingEnv = @()
    
    if (-not (Test-Path "anything-chat-rag\.env")) {
        $missingEnv += "anything-chat-rag\.env"
    }
    
    if (-not (Test-Path "testing-deep-agents-service\.env")) {
        $missingEnv += "testing-deep-agents-service\.env"
    }
    
    if ($missingEnv.Count -gt 0) {
        Print-Warning "以下 .env 文件缺失，请创建并配置:"
        foreach ($env in $missingEnv) {
            Write-Host "  - $env" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host "可以参考对应目录下的 .env.example 文件" -ForegroundColor Cyan
    } else {
        Print-Success ".env 文件检查通过"
    }
}

# 主程序
function Main {
    # 显示帮助
    if ($Help) {
        Show-Help
        exit 0
    }
    
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║           🔧 AI LangGraph 环境初始化 (uv)                      ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # 检查依赖
    Print-Info "检查系统依赖..."
    $uvOk = Check-UV
    if (-not $uvOk) {
        exit 1
    }
    
    Check-Python
    Check-Node
    Write-Host ""
    
    # 清理旧环境（如果需要）
    Clean-Environment
    
    # 使用 uv 安装
    $installOk = Install-WithUV
    if (-not $installOk) {
        Print-Error "依赖安装失败"
        exit 1
    }
    Write-Host ""
    
    # 创建目录
    Create-Directories
    Write-Host ""
    
    # 检查 .env
    Check-EnvFiles
    Write-Host ""
    
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "               🎉 环境初始化完成！                             " -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "虚拟环境位置: " -NoNewline
    Write-Host "$PROJECT_ROOT\.venv" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "下一步:" -ForegroundColor Yellow
    Write-Host "  1. 配置 .env 文件（如果还没配置）"
    Write-Host "  2. 激活环境: " -NoNewline
    Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "  3. 启动后端服务"
    Write-Host ""
    Write-Host "或者使用 uv run 直接运行命令（无需手动激活）:" -ForegroundColor Yellow
    Write-Host "  uv run python start_server.py" -ForegroundColor Cyan
    Write-Host "  uv run lightrag-server" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Docker 服务部署:" -ForegroundColor Yellow
    Write-Host "  cd yml" -ForegroundColor Cyan
    Write-Host "  .\start-docker.ps1" -ForegroundColor Cyan
    Write-Host ""
}

# 执行主程序
Main

