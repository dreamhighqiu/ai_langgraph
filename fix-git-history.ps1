# 🔐 Git 历史清理脚本 (PowerShell)
# 用于移除 Git 历史中的敏感信息

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Git 历史清理工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已撤销 API Key
Write-Host "⚠️  重要：在运行此脚本前，请确认已完成以下步骤：" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. ✅ 访问 OpenAI 控制台: https://platform.openai.com/api-keys" -ForegroundColor Yellow
Write-Host "2. ✅ 撤销（删除）泄露的 API Key" -ForegroundColor Yellow
Write-Host "3. ✅ 生成新的 API Key 并保存到本地 .env 文件" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "已完成以上步骤？(y/n)"
if ($confirm -ne 'y') {
    Write-Host "❌ 请先完成上述步骤再运行此脚本！" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "选择清理方式：" -ForegroundColor Cyan
Write-Host "1. 使用 git filter-repo（推荐，需要安装）" -ForegroundColor Green
Write-Host "2. 重置分支（简单，会丢失当前分支的所有提交）" -ForegroundColor Yellow
Write-Host "3. 允许推送（不推荐，API Key 会暴露在历史中）" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "请选择 (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "=== 方法 1: 使用 git filter-repo ===" -ForegroundColor Cyan
        Write-Host ""
        
        # 检查是否安装 git-filter-repo
        $hasFilterRepo = Get-Command git-filter-repo -ErrorAction SilentlyContinue
        if (-not $hasFilterRepo) {
            Write-Host "❌ git-filter-repo 未安装" -ForegroundColor Red
            Write-Host ""
            Write-Host "安装方法：" -ForegroundColor Yellow
            Write-Host "  pip install git-filter-repo" -ForegroundColor White
            Write-Host ""
            $installNow = Read-Host "现在安装？(y/n)"
            if ($installNow -eq 'y') {
                pip install git-filter-repo
            } else {
                Write-Host "❌ 取消操作" -ForegroundColor Red
                exit 1
            }
        }
        
        Write-Host "✓ 正在备份当前分支..." -ForegroundColor Green
        git branch backup-ui-demo-$(Get-Date -Format "yyyyMMdd-HHmmss")
        
        Write-Host "✓ 创建替换文件..." -ForegroundColor Green
        $replacements = @"
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==>***REMOVED_API_KEY***
"@
        $replacements | Out-File -FilePath "replacements.txt" -Encoding UTF8
        
        Write-Host "✓ 清理 Git 历史..." -ForegroundColor Green
        git filter-repo --replace-text replacements.txt --force
        
        Write-Host "✓ 重新添加远程仓库..." -ForegroundColor Green
        git remote add origin git@github.com:dreamhighqiu/ai_langgraph.git
        
        Write-Host ""
        Write-Host "✅ 清理完成！" -ForegroundColor Green
        Write-Host ""
        Write-Host "下一步：" -ForegroundColor Cyan
        Write-Host "  git push --force origin ui_demo" -ForegroundColor White
        Write-Host ""
        
        Remove-Item replacements.txt
    }
    
    "2" {
        Write-Host ""
        Write-Host "=== 方法 2: 重置分支 ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠️  警告：这会丢失 ui_demo 分支的所有提交！" -ForegroundColor Red
        Write-Host ""
        
        $confirmReset = Read-Host "确认重置？(yes/no)"
        if ($confirmReset -ne 'yes') {
            Write-Host "❌ 取消操作" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✓ 备份当前分支..." -ForegroundColor Green
        git branch backup-ui-demo-$(Get-Date -Format "yyyyMMdd-HHmmss")
        
        Write-Host "✓ 获取主分支..." -ForegroundColor Green
        git fetch origin main
        
        Write-Host "✓ 重置到主分支..." -ForegroundColor Green
        git reset --hard origin/main
        
        Write-Host "✓ 应用当前修改..." -ForegroundColor Green
        git add -A
        git commit -m "security: fix API key exposure and add security guide"
        
        Write-Host ""
        Write-Host "✅ 重置完成！" -ForegroundColor Green
        Write-Host ""
        Write-Host "下一步：" -ForegroundColor Cyan
        Write-Host "  git push --force origin ui_demo" -ForegroundColor White
        Write-Host ""
    }
    
    "3" {
        Write-Host ""
        Write-Host "=== 方法 3: 允许推送 ===" -ForegroundColor Red
        Write-Host ""
        Write-Host "⚠️  警告：这会将 API Key 暴露在 Git 历史中！" -ForegroundColor Red
        Write-Host "⚠️  只有在以下情况才建议使用：" -ForegroundColor Red
        Write-Host "   - 仓库是私有的" -ForegroundColor Red
        Write-Host "   - 已经撤销了泄露的 Key" -ForegroundColor Red
        Write-Host ""
        
        $confirmAllow = Read-Host "确认允许推送？(yes/no)"
        if ($confirmAllow -ne 'yes') {
            Write-Host "❌ 取消操作" -ForegroundColor Red
            exit 1
        }
        
        Write-Host ""
        Write-Host "GitHub 提供的允许链接：" -ForegroundColor Yellow
        Write-Host "https://github.com/dreamhighqiu/ai_langgraph/security/secret-scanning/unblock-secret/390SjzTbiAX6jrUT3zWYFIc9TBf" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "请：" -ForegroundColor Yellow
        Write-Host "1. 在浏览器中打开上述链接" -ForegroundColor White
        Write-Host "2. 点击 'Allow secret' 按钮" -ForegroundColor White
        Write-Host "3. 然后运行: git push origin ui_demo" -ForegroundColor White
        Write-Host ""
    }
    
    default {
        Write-Host "❌ 无效选择" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "清理完成提示" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "别忘了：" -ForegroundColor Yellow
Write-Host "1. 更新本地 .env 文件为新的 API Key" -ForegroundColor White
Write-Host "2. 测试新 Key 是否正常工作" -ForegroundColor White
Write-Host "3. 验证 GitHub 不再显示警告" -ForegroundColor White
Write-Host ""

