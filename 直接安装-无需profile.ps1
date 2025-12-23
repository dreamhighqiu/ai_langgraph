# 直接运行安装（不加载 PowerShell Profile）
# 这样可以避免 oh-my-posh 等 profile 工具的错误

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  开始安装 AI LangGraph 环境" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 执行安装脚本
$scriptPath = Join-Path $PSScriptRoot "setup.ps1"
& $scriptPath

Write-Host ""
Write-Host "完成！" -ForegroundColor Green



