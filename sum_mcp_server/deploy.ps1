param(
  [ValidateSet("start", "stop", "status", "list")]
  [string]$Action = "start",
  [switch]$All = $true
)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Ctl = Join-Path $PSScriptRoot "mcpctl.py"

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
  switch ($Action) {
    "list"   { & $Python $Ctl list; exit $LASTEXITCODE }
    "status" { & $Python $Ctl status; exit $LASTEXITCODE }
    "stop"   { & $Python $Ctl stop --all; exit $LASTEXITCODE }
    "start"  { & $Python $Ctl start --all; exit $LASTEXITCODE }
  }
} finally {
  Pop-Location
}

