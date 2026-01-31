#!/bin/bash
# Docker Compose 部署测试脚本

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Docker Compose 部署验证${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 检查 Docker
echo "1. 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker 已安装${NC}"

# 2. 检查 Docker Compose
echo ""
echo "2. 检查 Docker Compose..."
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}✓ Docker Compose V2 已安装${NC}"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo -e "${GREEN}✓ Docker Compose V1 已安装${NC}"
else
    echo -e "${RED}✗ Docker Compose 未安装${NC}"
    exit 1
fi

# 3. 验证配置文件
echo ""
echo "3. 验证配置文件..."
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}✗ docker-compose.yml 不存在${NC}"
    exit 1
fi
echo -e "${GREEN}✓ docker-compose.yml 存在${NC}"

# 验证配置语法
if $COMPOSE_CMD config > /dev/null 2>&1; then
    echo -e "${GREEN}✓ docker-compose.yml 语法正确${NC}"
else
    echo -e "${RED}✗ docker-compose.yml 语法错误${NC}"
    $COMPOSE_CMD config
    exit 1
fi

# 4. 检查环境变量
echo ""
echo "4. 检查环境变量..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env 文件不存在${NC}"
    echo "创建 .env 文件..."
    cp env.docker.example .env
    echo -e "${GREEN}✓ 已从 env.docker.example 创建 .env${NC}"
fi

# 检查必需的环境变量
if grep -q "OPENAI_API_KEY" .env && ! grep -q "OPENAI_API_KEY=$" .env; then
    echo -e "${GREEN}✓ OPENAI_API_KEY 已配置${NC}"
else
    echo -e "${YELLOW}⚠ OPENAI_API_KEY 未配置或为空${NC}"
fi

# 5. 检查 Dockerfile
echo ""
echo "5. 检查 Dockerfile..."
required_dockerfiles=("Dockerfile.backend" "Dockerfile.frontend")
for dockerfile in "${required_dockerfiles[@]}"; do
    if [ -f "$dockerfile" ]; then
        echo -e "${GREEN}✓ $dockerfile 存在${NC}"
    else
        echo -e "${RED}✗ $dockerfile 不存在${NC}"
        exit 1
    fi
done

# 6. 检查必需目录
echo ""
echo "6. 检查必需目录..."
required_dirs=(
    "anything-chat-rag"
    "testing-agents-service"
    "testing-deep-agents-ui"
    "deepagents"
)
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ $dir 存在${NC}"
    else
        echo -e "${RED}✗ $dir 不存在${NC}"
        exit 1
    fi
done

# 7. 检查敏感文件
echo ""
echo "7. 检查敏感文件（应该不存在）..."
sensitive_found=0
while IFS= read -r -d '' file; do
    echo -e "${RED}✗ 发现敏感文件: $file${NC}"
    sensitive_found=1
done < <(find . -type f \( -name "*邱云霞*" -o -name "*简历*" -o -name "*学历*" \) -print0 2>/dev/null)

if [ $sensitive_found -eq 0 ]; then
    echo -e "${GREEN}✓ 未发现敏感文件${NC}"
fi

# 8. 检查端口占用
echo ""
echo "8. 检查端口占用..."
ports=(2025 3200 6379 9621 19530)
ports_in_use=()
for port in "${ports[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port " || lsof -i ":$port" &>/dev/null; then
        ports_in_use+=($port)
        echo -e "${YELLOW}⚠ 端口 $port 已被占用${NC}"
    else
        echo -e "${GREEN}✓ 端口 $port 可用${NC}"
    fi
done

if [ ${#ports_in_use[@]} -gt 0 ]; then
    echo -e "${YELLOW}提示: 以下端口被占用: ${ports_in_use[*]}${NC}"
    echo "      这些端口将由 Docker 容器使用，请确保没有冲突"
fi

# 9. 检查磁盘空间
echo ""
echo "9. 检查磁盘空间..."
available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
required_space=20
if [ "$available_space" -gt "$required_space" ]; then
    echo -e "${GREEN}✓ 磁盘空间充足 (${available_space}GB 可用)${NC}"
else
    echo -e "${YELLOW}⚠ 磁盘空间可能不足 (${available_space}GB 可用, 建议 ${required_space}GB+)${NC}"
fi

# 10. 生成部署报告
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  验证完成${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "部署命令:"
echo ""
echo "1. 最小配置（推荐）:"
echo "   $COMPOSE_CMD up -d"
echo ""
echo "2. 完整配置（包含可选服务）:"
echo "   $COMPOSE_CMD --profile full up -d"
echo ""
echo "3. 查看日志:"
echo "   $COMPOSE_CMD logs -f [service-name]"
echo ""
echo "4. 检查状态:"
echo "   $COMPOSE_CMD ps"
echo ""
echo "5. 停止服务:"
echo "   $COMPOSE_CMD down"
echo ""

# 询问是否立即部署
read -p "是否现在部署服务？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "开始部署..."
    $COMPOSE_CMD up -d
    
    echo ""
    echo "等待服务启动..."
    sleep 10
    
    echo ""
    echo "服务状态:"
    $COMPOSE_CMD ps
    
    echo ""
    echo -e "${GREEN}部署完成！${NC}"
    echo ""
    echo "访问地址:"
    echo "  - 前端: http://localhost:3200"
    echo "  - API: http://localhost:2025"
    echo "  - API 文档: http://localhost:2025/docs"
fi

