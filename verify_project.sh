#!/bin/bash
# 项目验证脚本

echo "========================================="
echo "  AI LangGraph 项目验证"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查项目结构
echo "1. 检查项目结构..."
required_dirs=(
    "anything-chat-rag"
    "testing-agents-service"
    "testing-deep-agents-ui"
    "deepagents"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir 存在"
    else
        echo -e "${RED}✗${NC} $dir 不存在"
    fi
done

# 检查配置文件
echo ""
echo "2. 检查配置文件..."
required_files=(
    "docker-compose.yml"
    "env.docker.example"
    "Dockerfile.backend"
    "Dockerfile.frontend"
    ".gitignore"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file 存在"
    else
        echo -e "${RED}✗${NC} $file 不存在"
    fi
done

# 检查敏感文件（应该已删除）
echo ""
echo "3. 检查敏感文件（应该不存在）..."
sensitive_patterns=(
    "**/邱云霞*"
    "**/*简历*"
    "**/*学历*"
)

found_sensitive=0
for pattern in "${sensitive_patterns[@]}"; do
    files=$(find . -name "$pattern" 2>/dev/null)
    if [ ! -z "$files" ]; then
        echo -e "${RED}✗${NC} 发现敏感文件: $files"
        found_sensitive=1
    fi
done

if [ $found_sensitive -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 未发现敏感文件"
fi

# 检查无用目录（应该已删除）
echo ""
echo "4. 检查无用目录（应该不存在）..."
unwanted_dirs=(
    "example"
    "image_install"
    "anything-chat-rag/reproduce"
    "anything-chat-rag/build"
    "testing-agents-service/src"
)

found_unwanted=0
for dir in "${unwanted_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${RED}✗${NC} 发现无用目录: $dir"
        found_unwanted=1
    fi
done

if [ $found_unwanted -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 未发现无用目录"
fi

# 检查 Docker Compose 配置
echo ""
echo "5. 检查 Docker Compose 配置..."
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose 已安装"
    
    # 验证配置文件
    if docker compose config > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} docker-compose.yml 配置有效"
        
        # 统计服务数量
        service_count=$(docker compose config --services | wc -l)
        echo -e "${GREEN}✓${NC} 配置了 $service_count 个服务"
    else
        echo -e "${RED}✗${NC} docker-compose.yml 配置无效"
    fi
else
    echo -e "${RED}✗${NC} Docker Compose 未安装"
fi

# 检查环境变量
echo ""
echo "6. 检查环境变量..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env 文件存在"
    
    # 检查必需的环境变量
    required_vars=("OPENAI_API_KEY" "OPENAI_MODEL")
    for var in "${required_vars[@]}"; do
        if grep -q "$var" .env; then
            echo -e "${GREEN}✓${NC} $var 已配置"
        else
            echo -e "${YELLOW}⚠${NC} $var 未配置"
        fi
    done
else
    echo -e "${YELLOW}⚠${NC} .env 文件不存在（可从 env.docker.example 复制）"
fi

# 检查 Python 依赖
echo ""
echo "7. 检查 Python 依赖..."
if [ -f "requirements.txt" ]; then
    dep_count=$(grep -v "^#" requirements.txt | grep -v "^$" | wc -l)
    echo -e "${GREEN}✓${NC} requirements.txt 包含 $dep_count 个依赖"
fi

# 总结
echo ""
echo "========================================="
echo "  验证完成"
echo "========================================="
echo ""
echo "下一步:"
echo "1. 如果 .env 不存在: cp env.docker.example .env"
echo "2. 编辑 .env 文件，确保 OPENAI_API_KEY 正确"
echo "3. 启动服务: docker compose up -d"
echo "4. 查看日志: docker compose logs -f"
echo ""

