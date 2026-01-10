param(
  [ValidateSet("start", "stop", "status", "list", "restart", "doctor", "vendorize", "bundle")]
  [string]$Action = "start",
  [switch]$AutoPort,
  [switch]$KillPort,
  [string]$BundleOutDir = "dist\\sum_mcp_bundle"
)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Ctl = Join-Path $PSScriptRoot "mcpctl.py"
$Vendorize = Join-Path $PSScriptRoot "vendorize.ps1"
$BuildBundle = Join-Path $PSScriptRoot "build_bundle.ps1"

$Candidates = @(
  (Join-Path $RepoRoot ".venv\\Scripts\\python.exe"),
  (Join-Path $RepoRoot ".venv\\bin\\python"),
  "python"
)

$Python = $null
foreach ($c in $Candidates) {
  if ($c -eq "python") { $Python = $c; break }
  if (Test-Path $c) { $Python = $c; break }
}

if (-not $Python) { throw "Python not found" }

Push-Location $RepoRoot
try {
  $Extra = @()
  if ($AutoPort) { $Extra += "--auto-port" }
  if ($KillPort) { $Extra += "--kill-port" }

  switch ($Action) {
    "list"     { & $Python $Ctl list; exit $LASTEXITCODE }
    "status"   { & $Python $Ctl status; exit $LASTEXITCODE }
    "doctor"   { & $Python $Ctl doctor; exit $LASTEXITCODE }
    "stop"     { & $Python $Ctl stop --all; exit $LASTEXITCODE }
    "start"    { & $Python $Ctl start --all @Extra; exit $LASTEXITCODE }
    "restart"  { & $Python $Ctl restart --all @Extra; exit $LASTEXITCODE }
    "vendorize" { & $Vendorize -RepoRoot $RepoRoot; exit $LASTEXITCODE }
    "bundle"   { & $BuildBundle -OutDir $BundleOutDir; exit $LASTEXITCODE }
  }
} finally {
  Pop-Location
}
