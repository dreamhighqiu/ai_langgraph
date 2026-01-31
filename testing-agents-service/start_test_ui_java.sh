#!/bin/bash
# UI Java Agent 本地测试启动脚本 (Bash)
# 
# 使用方式:
#   cd /path/to/testing-agents-service
#   chmod +x start_test_ui_java.sh
#   ./start_test_ui_java.sh

echo ""
echo "============================================"
echo "  UI Java Agent 本地测试启动脚本"
echo "============================================"
echo ""

# 检查当前目录
CURRENT_PATH=$(pwd)
echo "📁 当前目录: $CURRENT_PATH"

# 确保在正确的目录
if [ ! -f "agents/ui_java/agent.py" ]; then
    echo ""
    echo "❌ 错误: 请在 testing-agents-service 目录下运行此脚本"
    echo ""
    echo "正确的命令:"
    echo "  cd /path/to/testing-agents-service"
    echo "  ./start_test_ui_java.sh"
    echo ""
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  警告: .env 文件不存在"
    echo ""
    echo "请先创建 .env 文件并配置:"
    echo "  cp env.example .env"
    echo "  vim .env  # 填入 OPENAI_API_KEY 等配置"
    echo ""
    
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 显示测试选项菜单
echo ""
echo "请选择测试方式:"
echo ""
echo "  1. 🚀 启动 LangGraph Studio (推荐)"
echo "  2. 🔧 直接运行 Python 测试脚本"
echo "  3. 🌐 启动服务 + HTTP API 测试"
echo "  4. 🧪 运行 Pytest 单元测试"
echo "  5. ✅ 验证配置"
echo "  6. 🔍 查看 Agent 信息"
echo "  0. ❌ 退出"
echo ""

read -p "请输入选项 (0-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动 LangGraph Studio..."
        echo ""
        echo "提示: Studio 启动后，访问 http://localhost:2025/ui"
        echo "      然后选择 'ui_java_agent' 开始测试"
        echo ""
        echo "按 Ctrl+C 停止服务"
        echo ""
        
        python start_server.py
        ;;
    
    2)
        echo ""
        echo "🔧 运行 Python 测试脚本..."
        echo ""
        
        # 先验证配置
        echo "📋 验证配置..."
        python -m config.validate_config
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ 配置验证通过，开始测试..."
            echo ""
            python quick_test_ui_java.py
        else
            echo ""
            echo "❌ 配置验证失败，请先修复配置问题"
        fi
        ;;
    
    3)
        echo ""
        echo "🌐 启动服务 + HTTP API 测试..."
        echo ""
        echo "步骤 1: 启动 LangGraph 服务..."
        echo "        (服务将在后台运行)"
        echo ""
        
        # 在后台启动服务
        python start_server.py > langgraph.log 2>&1 &
        LANGGRAPH_PID=$!
        
        echo "⏳ 等待服务启动（15秒）..."
        sleep 15
        
        echo ""
        echo "步骤 2: 运行 HTTP API 测试..."
        echo ""
        
        python test_ui_java_http.py
        
        echo ""
        echo "💡 停止 LangGraph 服务..."
        kill $LANGGRAPH_PID 2>/dev/null
        echo "✅ 服务已停止"
        ;;
    
    4)
        echo ""
        echo "🧪 运行 Pytest 单元测试..."
        echo ""
        
        # 检查 pytest 是否安装
        if ! python -m pytest --version > /dev/null 2>&1; then
            echo "⚠️  pytest 未安装，正在安装..."
            pip install pytest pytest-asyncio pytest-html
        fi
        
        echo "运行测试..."
        python -m pytest tests/test_ui_java_agent.py -v -s
        ;;
    
    5)
        echo ""
        echo "✅ 验证配置..."
        echo ""
        
        python -m config.validate_config
        
        echo ""
        echo "测试 LLM 配置..."
        echo ""
        
        if [ -f "test_llm_config.py" ]; then
            python test_llm_config.py
        else
            echo "⚠️  test_llm_config.py 不存在，跳过"
        fi
        ;;
    
    6)
        echo ""
        echo "🔍 查看 Agent 信息..."
        echo ""
        
        # 显示 Agent 基本信息
        echo "Agent 名称: ui_java_agent"
        echo "Agent 路径: agents/ui_java/"
        echo ""
        
        echo "📄 文件列表:"
        find agents/ui_java/ -type f | head -15 | while read file; do
            echo "  - $file"
        done
        
        echo ""
        echo "📖 文档:"
        echo "  - README.md: agents/ui_java/README.md"
        echo "  - USAGE.md: agents/ui_java/USAGE.md"
        echo "  - 测试指南: agents/ui_java/LOCAL_TESTING_GUIDE.md"
        echo ""
        
        echo "🎯 Skills:"
        echo "  - Planner (测试计划)"
        echo "  - Generator (代码生成)"
        echo "  - Healer (错误修复)"
        echo ""
        ;;
    
    0)
        echo ""
        echo "👋 再见！"
        echo ""
        exit 0
        ;;
    
    *)
        echo ""
        echo "❌ 无效的选项: $choice"
        echo ""
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "  测试完成"
echo "============================================"
echo ""

