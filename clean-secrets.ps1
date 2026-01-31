# 清理 Git 历史中的敏感信息脚本
# 用法: .\clean-secrets.ps1

# 需要替换的敏感信息 - 将真实密钥替换为占位符
$secretsToReplace = @{
    # OpenAI API Key (从 Git 历史中发现的)
    "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" = "sk-your-openai-api-key-here"
}

Write-Host "=== Git 历史敏感信息清理工具 ===" -ForegroundColor Cyan
Write-Host ""

# 备份当前分支
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "当前分支: $currentBranch" -ForegroundColor Yellow

# 创建备份
$backupBranch = "backup-before-clean-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host "创建备份分支: $backupBranch" -ForegroundColor Yellow
git branch $backupBranch

Write-Host ""
Write-Host "开始使用 git filter-branch 清理历史..." -ForegroundColor Green
Write-Host "这可能需要几分钟时间..." -ForegroundColor Yellow
Write-Host ""

# 构建 sed 替换命令
$sedCommands = ""
foreach ($key in $secretsToReplace.Keys) {
    $value = $secretsToReplace[$key]
    $sedCommands += "s|$key|$value|g; "
}

# 使用 git filter-branch 重写历史
# 注意：这会修改所有包含敏感信息的提交
git filter-branch -f --tree-filter @"
    find . -type f \( -name '*.env' -o -name '*.example' -o -name '.env' -o -name 'env.*' \) -exec sed -i 's|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|sk-your-openai-api-key-here|g' {} \;
"@ --all

Write-Host ""
Write-Host "=== 清理完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Cyan
Write-Host "1. 验证清理结果: git log --all --full-history -p -- '*.env' '*.example'" -ForegroundColor White
Write-Host "2. 强制推送到远程: git push origin $currentBranch --force" -ForegroundColor White
Write-Host "3. 清理备份引用: git update-ref -d refs/original/refs/heads/$currentBranch" -ForegroundColor White
Write-Host ""
Write-Host "⚠️ 注意: 强制推送会覆盖远程历史，请确保团队成员知晓" -ForegroundColor Red

