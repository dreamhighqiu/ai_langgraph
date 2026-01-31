# =============================================================================
# AI LangGraph Service Starter for Windows (PowerShell)
# 
# Function: One-click start all backend services
# 
# Usage:
#   .\start_all.ps1          # Start all backend services
#   .\start_all.ps1 -All     # Start all services (including frontend)
#   .\start_all.ps1 -Stop    # Stop all services
#   .\start_all.ps1 -Status  # Show service status
# =============================================================================

param(
    [switch]$All,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Update,
    [string]$Start,
    [string]$Restart,
    [string]$StopService
)

# Project root directory
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

# PID file directory
$PidDir = Join-Path $ProjectRoot ".pids"
if (-not (Test-Path $PidDir)) {
    New-Item -ItemType Directory -Path $PidDir -Force | Out-Null
}

# Log directory
$LogDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Virtual environment paths
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

# Environment file
$EnvFile = Join-Path $ProjectRoot ".env"

# =============================================================================
# Utility Functions
# =============================================================================

function Write-Banner {
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "          AI LangGraph Service Starter (Windows)                " -ForegroundColor Cyan
    Write-Host "                                                                " -ForegroundColor Cyan
    Write-Host "          Unified Virtual Env · One-Click Start · Simple       " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
}

function Write-Info {
    param($Message)
    Write-Host "[INFO] " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Write-Success {
    param($Message)
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Warning {
    param($Message)
    Write-Host "[!] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error {
    param($Message)
    Write-Host "[X] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Test-PortInUse {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $connection -ne $null
    } catch {
        return $false
    }
}

function Get-ProcessByPort {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($connection) {
            return $connection.OwningProcess
        }
    } catch {}
    return $null
}

function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    $pid = Get-ProcessByPort -Port $Port
    if ($pid) {
        Write-Info "Killing process on port $Port (PID: $pid) for $ServiceName..."
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            return $true
        } catch {
            Write-Warning "Failed to kill process on port $Port"
            return $false
        }
    }
    return $true
}

function Test-HttpEndpoint {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 3
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSeconds -UseBasicParsing -ErrorAction SilentlyContinue
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
    } catch {
        return $false
    }
}

function Wait-ForHttpEndpoint {
    param(
        [string]$Name,
        [string[]]$Urls,
        [int]$MaxWaitSeconds = 60
    )
    Write-Info "Waiting for $Name to become ready..."
    $count = 0
    while ($count -lt $MaxWaitSeconds) {
        foreach ($url in $Urls) {
            if (Test-HttpEndpoint -Url $url -TimeoutSeconds 2) {
                return $true
            }
        }
        Start-Sleep -Seconds 1
        $count++
        if ($count % 5 -eq 0) {
            Write-Host "." -NoNewline
        }
    }
    Write-Host ""
    return $false
}

function Load-EnvFile {
    if (Test-Path $EnvFile) {
        Get-Content $EnvFile | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }
}

# =============================================================================
# Service Start Functions
# =============================================================================

function Start-LightRAGService {
    $port = 9621
    $name = "LightRAG Server"
    $pidFile = Join-Path $PidDir "lightrag.pid"
    $logFile = Join-Path $LogDir "lightrag.log"
    
    if (Test-PortInUse -Port $port) {
        Stop-ProcessOnPort -Port $port -ServiceName $name
    }
    
    Write-Info "Starting $name..."
    
    Push-Location (Join-Path $ProjectRoot "anything-chat-rag")
    $process = Start-Process -FilePath $VenvPython -ArgumentList "-m","lightrag.api.lightrag_server" `
        -RedirectStandardOutput $logFile -RedirectStandardError $logFile `
        -WindowStyle Hidden -PassThru
    $process.Id | Out-File -FilePath $pidFile
    Pop-Location
    
    $urls = @("http://127.0.0.1:$port/openapi.json", "http://127.0.0.1:$port/docs")
    if (Wait-ForHttpEndpoint -Name $name -Urls $urls -MaxWaitSeconds 180) {
        Write-Success "$name started (PID: $($process.Id), Port: $port)"
        Write-Host "         API Docs: " -NoNewline
        Write-Host "http://localhost:$port/docs" -ForegroundColor Cyan
        return $true
    } else {
        Write-Error "$name failed to start, check log: $logFile"
        return $false
    }
}

function Start-LightRAGWebUI {
    $port = 5173
    $name = "LightRAG WebUI"
    $pidFile = Join-Path $PidDir "lightrag_webui.pid"
    $logFile = Join-Path $LogDir "lightrag_webui.log"
    
    if (Test-PortInUse -Port $port) {
        Stop-ProcessOnPort -Port $port -ServiceName $name
    }
    
    Write-Info "Starting $name..."
    
    Push-Location (Join-Path $ProjectRoot "anything-chat-rag\lightrag_webui")
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installing LightRAG WebUI dependencies..."
        npm install
    }
    
    # Set environment variable for API base URL
    $env:VITE_API_BASE_URL = "http://localhost:9621"
    
    # Start the dev server
    $process = Start-Process -FilePath "npm" -ArgumentList "run","dev-no-bun" `
        -RedirectStandardOutput $logFile -RedirectStandardError $logFile `
        -WindowStyle Hidden -PassThru
    $process.Id | Out-File -FilePath $pidFile
    Pop-Location
    
    if (Wait-ForHttpEndpoint -Name $name -Urls @("http://127.0.0.1:$port/") -MaxWaitSeconds 120) {
        Write-Success "$name started (PID: $($process.Id), Port: $port)"
        Write-Host "         URL: " -NoNewline
        Write-Host "http://localhost:$port" -ForegroundColor Cyan
        return $true
    } else {
        Write-Error "$name failed to start, check log: $logFile"
        return $false
    }
}

function Start-LangGraphService {
    $port = if ($env:LANGGRAPH_PORT) { $env:LANGGRAPH_PORT } else { 2025 }
    $name = "LangGraph Server"
    $pidFile = Join-Path $PidDir "langgraph.pid"
    $logFile = Join-Path $LogDir "langgraph.log"
    
    if (Test-PortInUse -Port $port) {
        Stop-ProcessOnPort -Port $port -ServiceName $name
    }
    
    Write-Info "Starting $name..."
    
    Push-Location (Join-Path $ProjectRoot "testing-agents-service")
    $env:PYTHONPATH = Join-Path $ProjectRoot "testing-agents-service"
    $process = Start-Process -FilePath $VenvPython -ArgumentList "start_server.py","--port",$port `
        -RedirectStandardOutput $logFile -RedirectStandardError $logFile `
        -WindowStyle Hidden -PassThru
    $process.Id | Out-File -FilePath $pidFile
    Pop-Location
    
    $urls = @("http://127.0.0.1:$port/ok", "http://127.0.0.1:$port/docs")
    if (Wait-ForHttpEndpoint -Name $name -Urls $urls -MaxWaitSeconds 300) {
        Write-Success "$name started (PID: $($process.Id), Port: $port)"
        Write-Host "         API Docs: " -NoNewline
        Write-Host "http://localhost:$port/docs" -ForegroundColor Cyan
        Write-Host "         Studio:   " -NoNewline
        Write-Host "http://localhost:$port/ui" -ForegroundColor Cyan
        return $true
    } else {
        Write-Error "$name failed to start, check log: $logFile"
        return $false
    }
}

function Start-AgentUI {
    $port = 3200
    $name = "Agent UI"
    $pidFile = Join-Path $PidDir "agent_ui.pid"
    $logFile = Join-Path $LogDir "agent_ui.log"
    
    if (Test-PortInUse -Port $port) {
        Stop-ProcessOnPort -Port $port -ServiceName $name
    }
    
    Write-Info "Starting $name..."
    
    Push-Location (Join-Path $ProjectRoot "testing-deep-agents-ui")
    
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installing frontend dependencies..."
        if (Get-Command yarn -ErrorAction SilentlyContinue) {
            yarn install
        } else {
            npm install
        }
    }
    
    $env:PORT = $port
    if (Get-Command yarn -ErrorAction SilentlyContinue) {
        $process = Start-Process -FilePath "yarn" -ArgumentList "dev" `
            -RedirectStandardOutput $logFile -RedirectStandardError $logFile `
            -WindowStyle Hidden -PassThru
    } else {
        $process = Start-Process -FilePath "npm" -ArgumentList "run","dev" `
            -RedirectStandardOutput $logFile -RedirectStandardError $logFile `
            -WindowStyle Hidden -PassThru
    }
    $process.Id | Out-File -FilePath $pidFile
    Pop-Location
    
    if (Wait-ForHttpEndpoint -Name $name -Urls @("http://127.0.0.1:$port/") -MaxWaitSeconds 120) {
        Write-Success "$name started (PID: $($process.Id), Port: $port)"
        Write-Host "         URL: " -NoNewline
        Write-Host "http://localhost:$port" -ForegroundColor Cyan
        return $true
    } else {
        Write-Error "$name failed to start, check log: $logFile"
        return $false
    }
}

# =============================================================================
# Service Stop Functions
# =============================================================================

function Stop-Service {
    param(
        [string]$Name,
        [string]$PidFile,
        [int]$Port
    )
    
    if (Test-Path $PidFile) {
        $pid = Get-Content $PidFile
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Success "Stopped $Name (PID: $pid)"
        } catch {
            Write-Warning "Failed to stop $Name (PID: $pid)"
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
    
    if ($Port -and (Test-PortInUse -Port $Port)) {
        Stop-ProcessOnPort -Port $Port -ServiceName $Name | Out-Null
    }
}

function Stop-AllServices {
    Write-Info "Stopping all services..."
    Load-EnvFile
    
    Stop-Service -Name "Agent UI" -PidFile (Join-Path $PidDir "agent_ui.pid") -Port 3200
    Stop-Service -Name "LangGraph Server" -PidFile (Join-Path $PidDir "langgraph.pid") -Port $(if ($env:LANGGRAPH_PORT) { $env:LANGGRAPH_PORT } else { 2025 })
    Stop-Service -Name "LightRAG WebUI" -PidFile (Join-Path $PidDir "lightrag_webui.pid") -Port 5173
    Stop-Service -Name "LightRAG Server" -PidFile (Join-Path $PidDir "lightrag.pid") -Port 9621
    
    Write-Success "All services stopped"
}

# =============================================================================
# Service Status
# =============================================================================

function Show-Status {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "                      Service Status                            " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Load-EnvFile
    $lgPort = if ($env:LANGGRAPH_PORT) { $env:LANGGRAPH_PORT } else { 2025 }
    
    function Show-OneStatus {
        param($Name, $Port, $PidFile, $Urls)
        
        $pid = $null
        if (Test-Path $PidFile) {
            $pid = Get-Content $PidFile
        }
        
        $portOpen = Test-PortInUse -Port $Port
        $httpOk = $false
        if ($portOpen) {
            foreach ($url in $Urls) {
                if (Test-HttpEndpoint -Url $url -TimeoutSeconds 2) {
                    $httpOk = $true
                    break
                }
            }
        }
        
        $running = $false
        if ($pid) {
            try {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                $running = $process -ne $null
            } catch {}
        }
        
        if ($httpOk -and $running) {
            Write-Host "  [*] " -ForegroundColor Green -NoNewline
            Write-Host ("{0,-25}" -f $Name) -NoNewline
            Write-Host " READY" -ForegroundColor Green -NoNewline
            Write-Host " (Port: $Port, PID: $pid)"
        } elseif ($httpOk -and $portOpen) {
            Write-Host "  [!] " -ForegroundColor Yellow -NoNewline
            Write-Host ("{0,-25}" -f $Name) -NoNewline
            Write-Host " READY*" -ForegroundColor Yellow -NoNewline
            Write-Host " (Port: $Port)"
        } elseif ($portOpen) {
            Write-Host "  [!] " -ForegroundColor Yellow -NoNewline
            Write-Host ("{0,-25}" -f $Name) -NoNewline
            Write-Host " STARTING" -ForegroundColor Yellow -NoNewline
            Write-Host " (Port: $Port)"
        } else {
            Write-Host "  [ ] " -ForegroundColor Red -NoNewline
            Write-Host ("{0,-25}" -f $Name) -NoNewline
            Write-Host " STOPPED" -ForegroundColor Red -NoNewline
            Write-Host " (Port: $Port)"
        }
    }
    
    Show-OneStatus -Name "LightRAG Server" -Port 9621 -PidFile (Join-Path $PidDir "lightrag.pid") `
        -Urls @("http://127.0.0.1:9621/openapi.json", "http://127.0.0.1:9621/docs")
    Show-OneStatus -Name "LightRAG WebUI" -Port 5173 -PidFile (Join-Path $PidDir "lightrag_webui.pid") `
        -Urls @("http://127.0.0.1:5173/")
    Show-OneStatus -Name "LangGraph Server" -Port $lgPort -PidFile (Join-Path $PidDir "langgraph.pid") `
        -Urls @("http://127.0.0.1:$lgPort/ok")
    Show-OneStatus -Name "Agent UI" -Port 3200 -PidFile (Join-Path $PidDir "agent_ui.pid") `
        -Urls @("http://127.0.0.1:3200/")
    
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

# =============================================================================
# Main Program
# =============================================================================

function Main {
    Load-EnvFile
    
    if ($Stop) {
        Stop-AllServices
        return
    }
    
    if ($Status) {
        Show-Status
        return
    }
    
    Write-Banner
    
    # Check Python
    if (-not (Test-Path $VenvPython)) {
        Write-Error "Virtual environment not found. Please run setup first:"
        Write-Host ""
        Write-Host "  python -m venv .venv"
        Write-Host "  .\.venv\Scripts\Activate.ps1"
        Write-Host "  pip install -r requirements.txt"
        Write-Host ""
        exit 1
    }
    
    Write-Info "Python environment: $VenvPython"
    Write-Success "Virtual environment ready"
    
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "                      Starting Services                         " -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $failedServices = @()
    
    if (Start-LightRAGService) {
        Write-Host ""
    } else {
        $failedServices += "LightRAG Server"
        Write-Host ""
    }
    
    if ($All) {
        if (Start-LightRAGWebUI) {
            Write-Host ""
        } else {
            $failedServices += "LightRAG WebUI"
            Write-Host ""
        }
    }
    
    if (Start-LangGraphService) {
        Write-Host ""
    } else {
        $failedServices += "LangGraph Server"
        Write-Host ""
    }
    
    if ($All) {
        if (Start-AgentUI) {
            Write-Host ""
        } else {
            $failedServices += "Agent UI"
            Write-Host ""
        }
    }
    
    Show-Status
    
    if ($failedServices.Count -eq 0) {
        Write-Host "All services started successfully!" -ForegroundColor Green
    } else {
        Write-Host "Some services failed to start:" -ForegroundColor Yellow
        foreach ($service in $failedServices) {
            Write-Host "  - $service" -ForegroundColor Red
        }
        Write-Host "Check logs in $LogDir for details" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Common commands:" -ForegroundColor Yellow
    Write-Host "  Check status:   " -NoNewline
    Write-Host ".\start_all.ps1 -Status" -ForegroundColor Cyan
    Write-Host "  Stop services:  " -NoNewline
    Write-Host ".\start_all.ps1 -Stop" -ForegroundColor Cyan
    Write-Host "  View logs:      " -NoNewline
    Write-Host "Get-Content logs\*.log -Tail 50" -ForegroundColor Cyan
    Write-Host ""
}

Main

