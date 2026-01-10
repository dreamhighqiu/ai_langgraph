param(
  [string]$OutDir = "dist\\sum_mcp_bundle"
)

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Target = Join-Path $RepoRoot $OutDir

$ErrorActionPreference = "Stop"

if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }
New-Item -ItemType Directory -Force $Target | Out-Null

Write-Host "[1/3] Copy sum_mcp_server -> $OutDir"
Copy-Item -Recurse -Force (Join-Path $RepoRoot "sum_mcp_server") $Target

Write-Host "[2/3] Vendorize deps into bundle"
& (Join-Path $Target "sum_mcp_server\\vendorize.ps1") -RepoRoot $RepoRoot

Write-Host "[3/3] Done"
Write-Host "Bundle ready: $Target"
Write-Host "Run:"
Write-Host "  cd $Target"
Write-Host "  python sum_mcp_server\\mcpctl.py start --all"

