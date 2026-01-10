param(
  [string]$RepoRoot = $(Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$Vendor = Join-Path $PSScriptRoot "vendor"
New-Item -ItemType Directory -Force $Vendor | Out-Null

function Sync-Dir([string]$src, [string]$dst) {
  if (!(Test-Path $src)) { throw "Missing source: $src" }
  if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
  Copy-Item -Recurse -Force $src $dst
}

Write-Host "[1/4] Sync lightrag -> sum_mcp_server/vendor/lightrag"
Sync-Dir (Join-Path $RepoRoot "anything-chat-rag\\lightrag") (Join-Path $Vendor "lightrag")

Write-Host "[2/4] Sync raganything -> sum_mcp_server/vendor/raganything"
Sync-Dir (Join-Path $RepoRoot "anything-chat-rag\\raganything") (Join-Path $Vendor "raganything")

Write-Host "[3/4] Sync mcp_server_rag_anything -> sum_mcp_server/vendor/mcp_server_rag_anything"
Sync-Dir (Join-Path $RepoRoot "mcp-server\\src\\mcp_server_rag_anything") (Join-Path $Vendor "mcp_server_rag_anything")

Write-Host "[4/4] Sync automation-quality-mcp -> sum_mcp_server/vendor/automation-quality-mcp"
$aqSrc = Join-Path $RepoRoot "testing-agents-service\\src\\api_agent\\mcp_servers\\automation-quality-mcp"
$aqDst = Join-Path $Vendor "automation-quality-mcp"
New-Item -ItemType Directory -Force $aqDst | Out-Null
Copy-Item -Recurse -Force (Join-Path $aqSrc "src") (Join-Path $aqDst "src")
Copy-Item -Force (Join-Path $aqSrc "mcpServer.js"),(Join-Path $aqSrc "run-server.js"),(Join-Path $aqSrc "cli.js"),(Join-Path $aqSrc "browserControl.js"),(Join-Path $aqSrc "package.json"),(Join-Path $aqSrc "package-lock.json"),(Join-Path $aqSrc "README.md") $aqDst

Write-Host "[OK] vendor sync complete: $Vendor"

