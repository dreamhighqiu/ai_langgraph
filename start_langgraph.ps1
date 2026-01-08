[CmdletBinding()]
param(
  [int]$Port = $(if ($env:LANGGRAPH_PORT) { [int]$env:LANGGRAPH_PORT } else { 2025 }),
  [string]$BindHost = $(if ($env:LANGGRAPH_HOST) { $env:LANGGRAPH_HOST } else { "0.0.0.0" }),
  [switch]$NoReload,
  [int]$WaitSeconds = 300,
  [switch]$Stop,
  [switch]$Status
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSCommandPath
$PidDir = Join-Path $ProjectRoot ".pids"
$LogDir = Join-Path $ProjectRoot "logs"
$PidFile = Join-Path $PidDir "langgraph.pid"
$OutLog = Join-Path $LogDir "langgraph.log"
$ErrLog = Join-Path $LogDir "langgraph.err.log"

New-Item -ItemType Directory -Force -Path $PidDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Get-ListeningPid {
  param([int]$ListenPort)
  try {
    $conn = Get-NetTCPConnection -State Listen -LocalPort $ListenPort -ErrorAction Stop | Select-Object -First 1
    if ($null -ne $conn) { return [int]$conn.OwningProcess }
  } catch {
    $line = netstat -ano | Select-String -Pattern (":$ListenPort\s+.*LISTEN") | Select-Object -First 1
    if ($null -ne $line) {
      $parts = ($line -split "\s+") | Where-Object { $_ -ne "" }
      if ($parts.Count -ge 5) { return [int]$parts[-1] }
    }
  }
  return $null
}

function Stop-LangGraph {
  if (Test-Path $PidFile) {
    $pidText = (Get-Content -Raw $PidFile).Trim()
    if ($pidText) {
      try { Stop-Process -Id ([int]$pidText) -Force -ErrorAction SilentlyContinue } catch {}
    }
    Remove-Item -Force $PidFile -ErrorAction SilentlyContinue | Out-Null
  }

  $listenPid = Get-ListeningPid -ListenPort $Port
  if ($null -ne $listenPid) {
    try { Stop-Process -Id $listenPid -Force -ErrorAction SilentlyContinue } catch {}
  }
}

if ($Status) {
  $listenPid = Get-ListeningPid -ListenPort $Port
  if ($null -ne $listenPid) {
    Write-Host "[RUNNING] LangGraph is listening on :$Port (PID: $listenPid)"
  } else {
    Write-Host "[STOPPED] LangGraph is not listening on :$Port"
  }
  exit 0
}

if ($Stop) {
  Stop-LangGraph
  Write-Host "[OK] Stopped LangGraph (best effort)."
  exit 0
}

$python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (!(Test-Path $python)) {
  throw "Missing venv python at $python. Create it first (e.g. run uv sync / run setup) then retry."
}

$existingPid = Get-ListeningPid -ListenPort $Port
if ($null -ne $existingPid) {
  Write-Host "[WARN] Port $Port is already in use (PID: $existingPid). Trying to stop it..."
  try { Stop-Process -Id $existingPid -Force -ErrorAction SilentlyContinue } catch {}
  Start-Sleep -Seconds 2
  if ($null -ne (Get-ListeningPid -ListenPort $Port)) {
    throw "Port $Port is still in use. Choose another port (set LANGGRAPH_PORT) or reboot to clear stale listeners."
  }
}

$env:PYTHONIOENCODING = "utf-8"
$env:LANGGRAPH_PORT = "$Port"
if ($NoReload) { $env:LANGGRAPH_RELOAD = "false" }

$workdir = Join-Path $ProjectRoot "testing-agents-service"
if (!(Test-Path (Join-Path $workdir "start_server.py"))) {
  throw "Missing $workdir\start_server.py"
}

$args = @("start_server.py", "--host", $BindHost, "--port", "$Port")
if ($NoReload) { $args += @("--reload", "false") }

$proc = Start-Process `
  -FilePath $python `
  -ArgumentList $args `
  -WorkingDirectory $workdir `
  -RedirectStandardOutput $OutLog `
  -RedirectStandardError $ErrLog `
  -PassThru `
  -WindowStyle Hidden

Set-Content -Path $PidFile -Value $proc.Id -Encoding ascii

Write-Host "[OK] LangGraph started (PID: $($proc.Id), Port: $Port)"
Write-Host "     API Docs: http://localhost:$Port/docs"
Write-Host "     Studio:   http://localhost:$Port/ui"

if ($WaitSeconds -gt 0) {
  $deadline = (Get-Date).AddSeconds($WaitSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $resp = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:$Port/ok" -TimeoutSec 3
      if ($resp.StatusCode -eq 200) {
        Write-Host "[READY] http://localhost:$Port/ok"
        exit 0
      }
    } catch {
      Start-Sleep -Seconds 5
    }
  }

  Write-Host "[ERROR] Timed out waiting for readiness after $WaitSeconds seconds."
  if (Test-Path $OutLog) {
    Write-Host "----- logs/langgraph.log (tail) -----"
    Get-Content $OutLog -Tail 80
  }
  if (Test-Path $ErrLog) {
    Write-Host "----- logs/langgraph.err.log (tail) -----"
    Get-Content $ErrLog -Tail 80
  }
  exit 1
}
