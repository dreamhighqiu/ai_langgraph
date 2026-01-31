# UI Java Agent 本地测试启动脚本 (PowerShell)
# 
# 使用方式:
#   cd d:\yunxia\ai_langgraph\testing-agents-service
#   .\start_test_ui_java.ps1

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  UI Java Agent 本地测试启动脚本" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查当前目录
$currentPath = Get-Location
Write-Host "📁 当前目录: $currentPath" -ForegroundColor Yellow

# 确保在正确的目录
if (-not (Test-Path ".\agents\ui_java\agent.py")) {
    Write-Host ""
    Write-Host "❌ 错误: 请在 testing-agents-service 目录下运行此脚本" -ForegroundColor Red
    Write-Host ""
    Write-Host "正确的命令:" -ForegroundColor Yellow
    Write-Host "  cd d:\yunxia\ai_langgraph\testing-agents-service" -ForegroundColor Yellow
    Write-Host "  .\start_test_ui_java.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# 检查 .env 文件
if (-not (Test-Path ".\.env")) {
    Write-Host ""
    Write-Host "⚠️  警告: .env 文件不存在" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请先创建 .env 文件并配置:" -ForegroundColor Yellow
    Write-Host "  cp env.example .env" -ForegroundColor Yellow
    Write-Host "  notepad .env  # 填入 OPENAI_API_KEY 等配置" -ForegroundColor Yellow
    Write-Host ""
    
    $continue = Read-Host "是否继续？(y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 0
    }
}

# 显示测试选项菜单
Write-Host ""
Write-Host "请选择测试方式:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. 🚀 启动 LangGraph Studio (推荐)" -ForegroundColor Green
Write-Host "  2. 🔧 直接运行 Python 测试脚本" -ForegroundColor Yellow
Write-Host "  3. 🌐 启动服务 + HTTP API 测试" -ForegroundColor Yellow
Write-Host "  4. 🧪 运行 Pytest 单元测试" -ForegroundColor Yellow
Write-Host "  5. ✅ 验证配置" -ForegroundColor Cyan
Write-Host "  6. 🔍 查看 Agent 信息" -ForegroundColor Cyan
Write-Host "  0. ❌ 退出" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "请输入选项 (0-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 启动 LangGraph Studio..." -ForegroundColor Green
        Write-Host ""
        Write-Host "提示: Studio 启动后，访问 http://localhost:2025/ui" -ForegroundColor Yellow
        Write-Host "      然后选择 'ui_java_agent' 开始测试" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
        Write-Host ""
        
        python start_server.py
    }
    "2" {
        Write-Host ""
        Write-Host "🔧 运行 Python 测试脚本..." -ForegroundColor Yellow
        Write-Host ""
        
        # 先验证配置
        Write-Host "📋 验证配置..." -ForegroundColor Cyan
        python -m config.validate_config
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ 配置验证通过，开始测试..." -ForegroundColor Green
            Write-Host ""
            python quick_test_ui_java.py
        } else {
            Write-Host ""
            Write-Host "❌ 配置验证失败，请先修复配置问题" -ForegroundColor Red
        }
    }
    "3" {
        Write-Host ""
        Write-Host "🌐 启动服务 + HTTP API 测试..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "步骤 1: 启动 LangGraph 服务..." -ForegroundColor Cyan
        Write-Host "        (服务将在后台运行)" -ForegroundColor Gray
        Write-Host ""
        
        # 在新窗口启动服务
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentPath'; Write-Host '🚀 LangGraph 服务启动中...' -ForegroundColor Green; python start_server.py"
        
        Write-Host "⏳ 等待服务启动（15秒）..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        
        Write-Host ""
        Write-Host "步骤 2: 运行 HTTP API 测试..." -ForegroundColor Cyan
        Write-Host ""
        
        python test_ui_java_http.py
        
        Write-Host ""
        Write-Host "💡 提示: LangGraph 服务仍在后台运行" -ForegroundColor Yellow
        Write-Host "        请手动关闭服务窗口以停止服务" -ForegroundColor Yellow
    }
    "4" {
        Write-Host ""
        Write-Host "🧪 运行 Pytest 单元测试..." -ForegroundColor Yellow
        Write-Host ""
        
        # 检查 pytest 是否安装
        $pytestInstalled = python -m pytest --version 2>$null
        
        if (-not $pytestInstalled) {
            Write-Host "⚠️  pytest 未安装，正在安装..." -ForegroundColor Yellow
            pip install pytest pytest-asyncio pytest-html
        }
        
        Write-Host "运行测试..." -ForegroundColor Cyan
        python -m pytest tests/test_ui_java_agent.py -v -s
    }
    "5" {
        Write-Host ""
        Write-Host "✅ 验证配置..." -ForegroundColor Cyan
        Write-Host ""
        
        python -m config.validate_config
        
        Write-Host ""
        Write-Host "测试 LLM 配置..." -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path ".\test_llm_config.py") {
            python test_llm_config.py
        } else {
            Write-Host "⚠️  test_llm_config.py 不存在，跳过" -ForegroundColor Yellow
        }
    }
    "6" {
        Write-Host ""
        Write-Host "🔍 查看 Agent 信息..." -ForegroundColor Cyan
        Write-Host ""
        
        # 显示 Agent 基本信息
        Write-Host "Agent 名称: ui_java_agent" -ForegroundColor Green
        Write-Host "Agent 路径: agents\ui_java\" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "📄 文件列表:" -ForegroundColor Cyan
        Get-ChildItem -Path ".\agents\ui_java\" -Recurse -File | Select-Object -First 15 | ForEach-Object {
            Write-Host "  - $($_.FullName.Replace((Get-Location).Path, '.'))" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "📖 文档:" -ForegroundColor Cyan
        Write-Host "  - README.md: agents\ui_java\README.md" -ForegroundColor Gray
        Write-Host "  - USAGE.md: agents\ui_java\USAGE.md" -ForegroundColor Gray
        Write-Host "  - 测试指南: agents\ui_java\LOCAL_TESTING_GUIDE.md" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "🎯 Skills:" -ForegroundColor Cyan
        Write-Host "  - Planner (测试计划)" -ForegroundColor Gray
        Write-Host "  - Generator (代码生成)" -ForegroundColor Gray
        Write-Host "  - Healer (错误修复)" -ForegroundColor Gray
        Write-Host ""
    }
    "0" {
        Write-Host ""
        Write-Host "👋 再见！" -ForegroundColor Green
        Write-Host ""
        exit 0
    }
    default {
        Write-Host ""
        Write-Host "❌ 无效的选项: $choice" -ForegroundColor Red
        Write-Host ""
        exit 1
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  测试完成" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

