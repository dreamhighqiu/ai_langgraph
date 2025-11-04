#!/bin/bash

# 启动脚本 - 启动所有必要的服务

set -e

echo "=================================="
echo "🚀 启动测试用例生成系统"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo -e "${YELLOW}检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 已安装${NC}"

# 检查 Node.js
echo -e "${YELLOW}检查 Node.js 环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js 已安装${NC}"

# 安装 Python 依赖
echo -e "${YELLOW}安装 Python 依赖...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Python 依赖已安装${NC}"

# 安装前端依赖
echo -e "${YELLOW}安装前端依赖...${NC}"
cd testing-agent-chat-ui
npm install -q
cd ..
echo -e "${GREEN}✅ 前端依赖已安装${NC}"

# 启动后端 API
echo -e "${YELLOW}启动后端 API 服务...${NC}"
python test_case_api.py &
API_PID=$!
echo -e "${GREEN}✅ 后端 API 已启动 (PID: $API_PID)${NC}"

# 等待 API 启动
sleep 3

# 启动前端
echo -e "${YELLOW}启动前端服务...${NC}"
cd testing-agent-chat-ui
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✅ 前端已启动 (PID: $FRONTEND_PID)${NC}"

# 打印信息
echo ""
echo "=================================="
echo "✅ 所有服务已启动"
echo "=================================="
echo ""
echo "📍 前端地址: http://localhost:3000"
echo "📍 测试用例生成页面: http://localhost:3000/test-case-generator"
echo "📍 后端 API: http://localhost:8000"
echo "📍 API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待中断信号
trap "kill $API_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '✅ 所有服务已停止'; exit 0" SIGINT

wait

