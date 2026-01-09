# ================================
# AI智能测试平台 - LangGraph & MCP 服务部署脚本 (PowerShell)
# 
# 用于启动/管理 LangGraph API 和 MCP 服务
# 
# 服务端口:
#   - LangGraph API: 2027 (智能体服务)
#   - RAG MCP: 9002 (知识库检索)
#   - MindMap MCP: 9003 (思维导图生成)
# ================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# 配置变量
$Script:ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$Script:BACKEND_DIR = Join-Path $ROOT "ruoyi-fastapi-backend"
$Script:RUNTIME_DIR = Join-Path $ROOT ".runtime"
$Script:PID_DIR = Join-Path $RUNTIME_DIR "pids"
$Script:LOG_DIR = Join-Path $RUNTIME_DIR "logs"
$Script:VENV_DIR = Join-Path $BACKEND_DIR ".venv"

# 端口配置
$Script:LANGGRAPH_PORT = if ($env:LANGGRAPH_PORT) { $env:LANGGRAPH_PORT } else { 2027 }
$Script:RAG_MCP_PORT = if ($env:RAG_MCP_PORT) { $env:RAG_MCP_PORT } else { 9002 }
$Script:MINDMAP_MCP_PORT = if ($env:MINDMAP_MCP_PORT) { $env:MINDMAP_MCP_PORT } else { 9003 }

# 创建目录
New-Item -ItemType Directory -Force -Path $PID_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

function Print-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Blue }
function Print-Success { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Print-Warning { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Print-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

function Get-PidFile { param($name) return Join-Path $PID_DIR "$name.pid" }
function Get-LogFile { param($name) return Join-Path $LOG_DIR "$name.log" }

function Get-PythonPath {
    $candidates = @(
        (Join-Path $VENV_DIR "Scripts\python.exe"),
        (Join-Path $VENV_DIR "Scripts\python3.exe"),
        (Join-Path $VENV_DIR "bin\python"),
        (Join-Path $VENV_DIR "bin\python3")
    )
    foreach ($path in $candidates) {
        if (Test-Path $path) { return $path }
    }
    return "python"
}

function Test-ServiceRunning {
    param($name)
    $pidFile = Get-PidFile $name
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pid) {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            return $null -ne $process
        }
    }
    return $false
}

function Stop-Service-ByName {
    param($name)
    
    if (-not (Test-ServiceRunning $name)) {
        Print-Warning "$name 未运行"
        return
    }
    
    $pidFile = Get-PidFile $name
    $pid = Get-Content $pidFile
    Print-Info "停止 $name (PID $pid)..."
    
    try {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    } catch {}
    
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    Print-Success "$name 已停止"
}

function Kill-Port {
    param($port, $name)
    
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connections) {
            foreach ($conn in $connections) {
                $pid = $conn.OwningProcess
                if ($pid -and $pid -ne 0) {
                    Print-Info "发现占用端口 $port 的进程: $pid"
                    taskkill /F /PID $pid 2>$null
                    Print-Success "已杀掉占用端口 $port 的进程 (PID: $pid)"
                }
            }
        } else {
            Print-Info "端口 $port 当前无占用进程"
        }
    } catch {
        Print-Info "端口 $port 当前无占用进程"
    }
}

function Start-LangGraph {
    if (Test-ServiceRunning "langgraph") {
        $pidFile = Get-PidFile "langgraph"
        $pid = Get-Content $pidFile
        Print-Warning "LangGraph API 已在运行 (PID $pid)"
        return
    }
    
    Print-Info "启动 LangGraph API 服务 (端口: $LANGGRAPH_PORT)..."
    
    $pythonPath = Get-PythonPath
    
    # 检查虚拟环境
    if ($pythonPath -eq "python") {
        Print-Error "虚拟环境未创建，请先运行: .\deploy-local.ps1 init"
        return
    }
    
    # 检查 langgraph 是否安装
    $checkResult = & $pythonPath -c "import langgraph" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Print-Warning "langgraph 未安装，正在安装..."
        Push-Location $BACKEND_DIR
        uv pip install langgraph langgraph-cli[inmem] langgraph-sdk
        Pop-Location
    }
    
    # 检查配置文件
    $configPath = Join-Path $BACKEND_DIR "langgraph.json"
    if (-not (Test-Path $configPath)) {
        Print-Error "langgraph.json 配置文件不存在"
        return
    }
    
    Push-Location $BACKEND_DIR
    
    # 设置环境变量
    $env:APP_ENV = "dev"
    $env:PYTHONPATH = "$BACKEND_DIR;$env:PYTHONPATH"
    
    # 启动 LangGraph API
    $logFile = Get-LogFile "langgraph"
    $process = Start-Process -FilePath $pythonPath -ArgumentList "-m", "langgraph", "dev", "--host", "0.0.0.0", "--port", $LANGGRAPH_PORT, "--config", "langgraph.json" -RedirectStandardOutput $logFile -RedirectStandardError $logFile -PassThru -WindowStyle Hidden
    
    $pidFile = Get-PidFile "langgraph"
    $process.Id | Out-File -FilePath $pidFile -Encoding ASCII
    
    Pop-Location
    
    # 等待启动
    Start-Sleep -Seconds 5
    
    if (Test-ServiceRunning "langgraph") {
        Print-Success "LangGraph API 启动成功"
        Write-Host "  地址: http://localhost:$LANGGRAPH_PORT"
        Write-Host "  文档: http://localhost:$LANGGRAPH_PORT/docs"
        Write-Host "  PID:  $($process.Id)"
        Write-Host "  日志: $logFile"
    } else {
        Print-Error "LangGraph API 启动失败，请查看日志"
        if (Test-Path $logFile) {
            Get-Content $logFile -Tail 30
        }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
}

function Start-All {
    Print-Info "启动所有 AI 服务..."
    Write-Host ""
    
    Start-LangGraph
    
    Write-Host ""
    Write-Host "========================================"
    Print-Success "AI 服务启动完成！"
    Write-Host "========================================"
    Show-Status
}

function Stop-All {
    Print-Info "停止所有 AI 服务..."
    Write-Host ""
    
    Stop-Service-ByName "langgraph"
    Stop-Service-ByName "rag-mcp"
    Stop-Service-ByName "mindmap-mcp"
    
    Write-Host ""
    Print-Info "检查并清理端口占用..."
    Kill-Port $LANGGRAPH_PORT "LangGraph"
    Kill-Port $RAG_MCP_PORT "RAG MCP"
    Kill-Port $MINDMAP_MCP_PORT "MindMap MCP"
    
    Write-Host ""
    Print-Success "所有 AI 服务已停止"
}

function Show-Status {
    Write-Host ""
    Write-Host "========== AI 服务状态 =========="
    Write-Host ""
    
    if (Test-ServiceRunning "langgraph") {
        $pidFile = Get-PidFile "langgraph"
        $pid = Get-Content $pidFile
        Print-Success "LangGraph API: 运行中 (PID: $pid)"
        Write-Host "  http://localhost:$LANGGRAPH_PORT"
    } else {
        Print-Warning "LangGraph API: 未运行"
    }
    
    if (Test-ServiceRunning "rag-mcp") {
        $pidFile = Get-PidFile "rag-mcp"
        $pid = Get-Content $pidFile
        Print-Success "RAG MCP: 运行中 (PID: $pid)"
        Write-Host "  http://localhost:$RAG_MCP_PORT"
    } else {
        Print-Warning "RAG MCP: 未运行"
    }
    
    if (Test-ServiceRunning "mindmap-mcp") {
        $pidFile = Get-PidFile "mindmap-mcp"
        $pid = Get-Content $pidFile
        Print-Success "MindMap MCP: 运行中 (PID: $pid)"
        Write-Host "  http://localhost:$MINDMAP_MCP_PORT"
    } else {
        Print-Warning "MindMap MCP: 未运行"
    }
    
    Write-Host ""
}

function Show-Logs {
    param($name = "langgraph")
    
    $logFile = Get-LogFile $name
    if (-not (Test-Path $logFile)) {
        Print-Error "日志文件不存在: $logFile"
        return
    }
    
    Print-Info "查看 $name 日志 (Ctrl+C 退出)..."
    Get-Content $logFile -Wait -Tail 50
}

function Show-Help {
    Write-Host @"

AI智能测试平台 - LangGraph & MCP 服务管理脚本 (PowerShell)

========================================
服务说明:
  - LangGraph API (端口 $LANGGRAPH_PORT): 智能体服务，提供测试用例生成、需求分析等 AI 功能
  - RAG MCP (端口 $RAG_MCP_PORT): 知识库检索服务
  - MindMap MCP (端口 $MINDMAP_MCP_PORT): 思维导图生成服务
========================================

用法: .\deploy-langgraph.ps1 [命令]

命令:
  start         启动所有 AI 服务 (LangGraph + MCP)
  stop          停止所有 AI 服务
  restart       重启所有 AI 服务
  status        查看服务状态
  
  langgraph     仅启动 LangGraph API 服务
  
  logs [name]   查看服务日志 (langgraph, rag-mcp, mindmap-mcp)
  help          显示帮助

示例:
  .\deploy-langgraph.ps1 start           # 启动所有 AI 服务
  .\deploy-langgraph.ps1 langgraph       # 仅启动 LangGraph
  .\deploy-langgraph.ps1 logs langgraph  # 查看 LangGraph 日志

"@
}

# 主函数
switch ($Command.ToLower()) {
    "start" { Start-All }
    "stop" { Stop-All }
    "restart" { Stop-All; Start-Sleep -Seconds 2; Start-All }
    "status" { Show-Status }
    "langgraph" { Start-LangGraph }
    "logs" { 
        $logName = if ($args.Count -gt 0) { $args[0] } else { "langgraph" }
        Show-Logs $logName 
    }
    default { Show-Help }
}

