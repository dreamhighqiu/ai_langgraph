# 快速重启后端服务脚本 (PowerShell)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "=========================================="
Write-Host "🔄 手动重启后端服务"
Write-Host "=========================================="
Write-Host ""

# 1. 停止后端服务
Write-Host "[1/4] 停止后端服务..."
$pids = Get-NetTCPConnection -LocalPort 9099 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | 
    Sort-Object -Unique

if ($pids) {
    foreach ($pid in $pids) {
        if ($pid -ne 0) {
            Write-Host "  → 杀掉进程 PID: $pid"
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
}

Remove-Item ".pids\backend.pid" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 2. 确认端口已释放
Write-Host "[2/4] 确认端口已释放..."
$stillListening = Get-NetTCPConnection -LocalPort 9099 -State Listen -ErrorAction SilentlyContinue
if ($stillListening) {
    Write-Host "  ⚠️  警告: 端口 9099 仍被占用"
    $stillListening | Format-Table LocalAddress, LocalPort, State, OwningProcess
    $response = Read-Host "  是否继续? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
} else {
    Write-Host "  ✅ 端口 9099 已释放"
}

# 3. 启动后端服务
Write-Host "[3/4] 启动后端服务..."
Set-Location "ruoyi-fastapi-backend"

# 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host "  ❌ 错误: 虚拟环境不存在，请先运行: .\deploy-local.ps1 init"
    exit 1
}

# 设置环境变量
$env:APP_ENV = "dev"

# 创建日志目录
New-Item -ItemType Directory -Force -Path "..\logs" | Out-Null

# 启动服务
Write-Host "  → 启动 uvicorn (端口: 9099, 热重载: 已启用)..."
$process = Start-Process -FilePath "uv" `
    -ArgumentList "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9099", "--reload", "--reload-dir", "." `
    -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput "..\logs\backend.log" `
    -RedirectStandardError "..\logs\backend_error.log"

$process.Id | Out-File -FilePath "..\.pids\backend.pid"

# 4. 验证启动
Write-Host "[4/4] 验证服务启动..."
Start-Sleep -Seconds 5

if (-not $process.HasExited) {
    $listening = Get-NetTCPConnection -LocalPort 9099 -State Listen -ErrorAction SilentlyContinue
    if ($listening) {
        Write-Host ""
        Write-Host "=========================================="
        Write-Host "✅ 后端服务启动成功！"
        Write-Host "=========================================="
        Write-Host ""
        Write-Host "  📍 服务信息:"
        Write-Host "    PID:      $($process.Id)"
        Write-Host "    地址:     http://localhost:9099/dev-api"
        Write-Host "    文档:     http://localhost:9099/dev-api/docs"
        Write-Host "    日志:     logs\backend.log"
        Write-Host ""
        Write-Host "  🔥 热重载: 已启用 (代码更改自动生效)"
        Write-Host ""
        Write-Host "=========================================="
        
        # 显示最后几行日志
        Write-Host ""
        Write-Host "📝 最近日志:"
        Write-Host "----------------------------------------"
        Get-Content "..\logs\backend.log" -Tail 10
        Write-Host "----------------------------------------"
    } else {
        Write-Host ""
        Write-Host "⚠️  进程已启动但端口未监听，请查看日志:"
        Get-Content "..\logs\backend.log" -Tail 30
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "❌ 后端服务启动失败！"
    Write-Host ""
    Write-Host "📝 错误日志:"
    Write-Host "----------------------------------------"
    if (Test-Path "..\logs\backend_error.log") {
        Get-Content "..\logs\backend_error.log" -Tail 30
    } else {
        Get-Content "..\logs\backend.log" -Tail 30
    }
    Write-Host "----------------------------------------"
    exit 1
}

Set-Location ..

