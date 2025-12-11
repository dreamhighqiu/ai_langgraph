#!/bin/bash

echo ""
echo "================================================================="
echo "🔄 LightRAG 重启脚本"
echo "================================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${YELLOW}步骤1: 停止 LightRAG 服务...${NC}"
./start_all.sh --stop lightrag
sleep 2

echo ""
echo -e "${YELLOW}步骤2: 启动 LightRAG 服务...${NC}"
./start_all.sh --start lightrag
sleep 5

echo ""
echo -e "${YELLOW}步骤3: 验证 Embedding 配置...${NC}"
echo "查看日志（按Ctrl+C退出）:"
echo ""
tail -f anything-chat-rag/lightrag.log | grep -A 4 "Embedding Configuration" | head -20

echo ""
echo "================================================================="
echo -e "${GREEN}✅ LightRAG 已重启！${NC}"
echo "================================================================="
echo ""
echo "📋 应该看到:"
echo "  ✅ Binding: ollama"
echo "  ✅ Host: http://54.179.103.192:11434"
echo "  ✅ Model: qwen3-embedding:0.6b"
echo "  ✅ Dimensions: 1024"
echo ""
echo "🌐 访问 LightRAG WebUI:"
echo "  http://localhost:9621"
echo ""
echo "🧪 测试 embedding:"
echo "  上传一个文档并观察是否成功处理"
echo ""
