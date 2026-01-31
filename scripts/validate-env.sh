#!/bin/bash

# ==============================================================
# 环境变量验证脚本
# ==============================================================
# 
# 用途：在启动 Docker Compose 前验证必需的环境变量
# 使用方法：./scripts/validate-env.sh
# ==============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 错误计数
ERROR_COUNT=0
WARNING_COUNT=0

echo "=========================================="
echo "环境变量验证脚本"
echo "=========================================="
echo ""

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ 错误: .env 文件不存在${NC}"
    echo "请先复制 .env.example 为 .env 并配置："
    echo "  cp .env.example .env"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    exit 1
else
    echo -e "${GREEN}✅ .env 文件存在${NC}"
    # 加载 .env 文件
    set -a
    source .env
    set +a
fi

# 检查必需的 API Key
echo ""
echo "检查 API Keys..."
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo -e "${RED}❌ 错误: OPENAI_API_KEY 未配置或使用默认值${NC}"
    ERROR_COUNT=$((ERROR_COUNT + 1))
else
    echo -e "${GREEN}✅ OPENAI_API_KEY 已配置${NC}"
fi

# 检查服务配置文件
echo ""
echo "检查服务配置文件..."

# 检查 LightRAG .env
if [ ! -f "anything-chat-rag/.env" ]; then
    echo -e "${YELLOW}⚠️  警告: anything-chat-rag/.env 不存在${NC}"
    echo "  建议从 env.example 创建："
    echo "    cp anything-chat-rag/env.example anything-chat-rag/.env"
    WARNING_COUNT=$((WARNING_COUNT + 1))
else
    echo -e "${GREEN}✅ anything-chat-rag/.env 存在${NC}"
fi

# 检查 LangGraph .env
if [ ! -f "testing-agents-service/.env" ]; then
    echo -e "${YELLOW}⚠️  警告: testing-agents-service/.env 不存在${NC}"
    echo "  建议从 env.example 创建："
    echo "    cp testing-agents-service/env.example testing-agents-service/.env"
    WARNING_COUNT=$((WARNING_COUNT + 1))
else
    echo -e "${GREEN}✅ testing-agents-service/.env 存在${NC}"
fi

# 检查关键环境变量
echo ""
echo "检查关键环境变量..."

# Redis 配置
if [ -z "$REDIS_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  警告: REDIS_PASSWORD 未设置，将使用默认值${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
else
    echo -e "${GREEN}✅ REDIS_PASSWORD 已配置${NC}"
fi

# Milvus 配置
if [ -z "$MILVUS_URI" ]; then
    echo -e "${YELLOW}⚠️  警告: MILVUS_URI 未设置，将使用默认值${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
else
    echo -e "${GREEN}✅ MILVUS_URI 已配置: $MILVUS_URI${NC}"
fi

# 服务地址配置
if [ -z "$LIGHTRAG_BASE_URL" ]; then
    echo -e "${YELLOW}⚠️  警告: LIGHTRAG_BASE_URL 未设置，将使用默认值${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
else
    echo -e "${GREEN}✅ LIGHTRAG_BASE_URL 已配置: $LIGHTRAG_BASE_URL${NC}"
fi

# 前端访问地址
if [ -z "$NEXT_PUBLIC_LANGGRAPH_URL" ]; then
    echo -e "${YELLOW}⚠️  警告: NEXT_PUBLIC_LANGGRAPH_URL 未设置，将使用默认值${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
else
    echo -e "${GREEN}✅ NEXT_PUBLIC_LANGGRAPH_URL 已配置: $NEXT_PUBLIC_LANGGRAPH_URL${NC}"
fi

# 检查端口冲突
echo ""
echo "检查端口占用..."

check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -an | grep -q ":$port.*LISTEN" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  警告: 端口 $port ($service) 已被占用${NC}"
        WARNING_COUNT=$((WARNING_COUNT + 1))
    else
        echo -e "${GREEN}✅ 端口 $port ($service) 可用${NC}"
    fi
}

check_port "${REDIS_PORT:-6379}" "Redis"
check_port "${MILVUS_PORT:-19530}" "Milvus"
check_port "${LIGHTRAG_PORT:-9621}" "LightRAG"
check_port "${LANGGRAPH_PORT:-2025}" "LangGraph"
check_port "${FRONTEND_PORT:-3200}" "Frontend"

# 总结
echo ""
echo "=========================================="
echo "验证完成"
echo "=========================================="
echo -e "错误: ${RED}$ERROR_COUNT${NC}"
echo -e "警告: ${YELLOW}$WARNING_COUNT${NC}"
echo ""

if [ $ERROR_COUNT -gt 0 ]; then
    echo -e "${RED}❌ 验证失败，请修复上述错误后重试${NC}"
    exit 1
elif [ $WARNING_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  验证通过，但有警告，建议检查上述警告项${NC}"
    exit 0
else
    echo -e "${GREEN}✅ 所有检查通过，可以启动服务${NC}"
    exit 0
fi

