#!/bin/bash
# AI智能测试平台 - 一键启动脚本
# 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(AI提效)

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${GREEN}"
    echo "═══════════════════════════════════════════════════════════"
    echo "   $1"
    echo "═══════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# 检查依赖
check_dependencies() {
    print_header "检查系统依赖"
    
    local missing_deps=0
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python已安装: $PYTHON_VERSION"
    else
        print_error "Python 3未安装"
        missing_deps=1
    fi
    
    # 检查Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js已安装: $NODE_VERSION"
    else
        print_warning "Node.js未安装 (前端开发需要)"
    fi
    
    # 检查Docker (可选)
    if command -v docker &> /dev/null; then
        print_success "Docker已安装"
        else
        print_warning "Docker未安装 (容器化部署需要)"
    fi
    
    # 检查MySQL/PostgreSQL客户端
    if command -v mysql &> /dev/null || command -v psql &> /dev/null; then
        print_success "数据库客户端已安装"
        else
        print_warning "MySQL/PostgreSQL客户端未安装"
    fi
    
    if [ $missing_deps -eq 1 ]; then
        print_error "请先安装缺失的依赖"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    print_header "初始化数据库"
    
    print_info "请确保MySQL/PostgreSQL服务已启动"
    read -p "是否初始化数据库? (y/n): " init_db
    
    if [ "$init_db" = "y" ]; then
        read -p "数据库类型 (mysql/postgresql): " db_type
        read -p "数据库主机 (默认:localhost): " db_host
        db_host=${db_host:-localhost}
        read -p "数据库端口 (MySQL:3306/PostgreSQL:5432): " db_port
        read -p "数据库用户名: " db_user
        read -sp "数据库密码: " db_password
        echo
        read -p "数据库名称 (默认:ruoyi-fastapi): " db_name
        db_name=${db_name:-ruoyi-fastapi}
        
        print_info "初始化数据库..."
        
        if [ "$db_type" = "mysql" ]; then
            mysql -h $db_host -P ${db_port:-3306} -u $db_user -p$db_password $db_name < RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/testing_platform.sql
            print_success "MySQL数据库初始化完成"
        elif [ "$db_type" = "postgresql" ]; then
            PGPASSWORD=$db_password psql -h $db_host -p ${db_port:-5432} -U $db_user -d $db_name -f RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/sql/testing_platform.sql
            print_success "PostgreSQL数据库初始化完成"
        fi
    else
        print_warning "跳过数据库初始化"
    fi
}

# 配置环境变量
configure_env() {
    print_header "配置环境变量"
    
    cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
    
    if [ ! -f ".env.dev" ]; then
        print_info "创建.env.dev文件..."
        cat > .env.dev << EOF
# 数据库配置
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=root123
DATABASE_NAME=ruoyi-fastapi

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=testing-platform

# LangGraph配置
LANGGRAPH_API_URL=http://localhost:2025
LANGSMITH_API_KEY=

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=
MILVUS_PASSWORD=
EOF
        print_success ".env.dev文件已创建"
    else
        print_info ".env.dev文件已存在"
    fi
    
    cd ../..
}

# 安装Python依赖
install_python_deps() {
    print_header "安装Python依赖"
    
    print_info "安装testing-agents-service依赖..."
    cd testing-agents-service/testing-agents-service
    
    if command -v uv &> /dev/null; then
        print_info "使用uv安装依赖..."
        uv sync
    else
        print_info "使用pip安装依赖..."
        pip3 install -r requirements.txt 2>/dev/null || pip3 install langchain langgraph deepagents fastapi uvicorn minio langchain-deepseek langchain-mcp-adapters
    fi
    
    print_success "testing-agents-service依赖安装完成"
    
    cd ../..
    
    print_info "安装RuoYi后端依赖..."
    cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
    pip3 install -r requirements.txt
    print_success "RuoYi后端依赖安装完成"
    
    cd ../..
}

# 启动testing-agents-service
start_agents_service() {
    print_header "启动AI Agent服务"
    
    cd testing-agents-service/testing-agents-service
    
    print_info "启动testing-agents-service (端口:2025)..."
    python3 start_server.py > ../../logs/agents-service.log 2>&1 &
    AGENTS_PID=$!
    echo $AGENTS_PID > ../../.pids/agents.pid
    
    print_success "Agent服务已启动 (PID: $AGENTS_PID)"
    print_info "日志文件: logs/agents-service.log"
    
    cd ../..
    
    # 等待服务启动
    print_info "等待Agent服务启动..."
    sleep 5
    
    # 检查服务是否正常
    if curl -s http://localhost:2025/ok > /dev/null 2>&1; then
        print_success "Agent服务运行正常"
    else
        print_warning "Agent服务可能未正常启动，请检查日志"
    fi
}

# 启动RuoYi后端
start_ruoyi_backend() {
    print_header "启动RuoYi后端服务"
    
    cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend
    
    print_info "启动RuoYi后端 (端口:8000)..."
    python3 app.py --env=dev > ../../logs/ruoyi-backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../../.pids/backend.pid
    
    print_success "RuoYi后端已启动 (PID: $BACKEND_PID)"
    print_info "日志文件: logs/ruoyi-backend.log"
    
    cd ../..
    
    # 等待服务启动
    print_info "等待后端服务启动..."
    sleep 5
    
    # 检查服务是否正常
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        print_success "后端服务运行正常"
    else
        print_warning "后端服务可能未正常启动，请检查日志"
    fi
}

# 启动前端 (可选)
start_frontend() {
    print_header "启动前端服务 (可选)"
    
    read -p "是否启动前端开发服务器? (y/n): " start_fe
    
    if [ "$start_fe" = "y" ]; then
        cd RuoYi-Vue3-FastAPI/ruoyi-fastapi-frontend
        
        if [ ! -d "node_modules" ]; then
            print_info "安装前端依赖..."
            npm install --registry=https://registry.npmmirror.com
        fi
        
        print_info "启动前端服务 (端口:80)..."
        npm run dev > ../../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../../.pids/frontend.pid
        
        print_success "前端服务已启动 (PID: $FRONTEND_PID)"
        print_info "日志文件: logs/frontend.log"
        
        cd ../..
    else
        print_info "跳过前端启动"
    fi
}

# 显示服务信息
show_service_info() {
    print_header "服务信息"
    
    echo ""
    print_info "AI Agent服务:"
    echo "   URL: http://localhost:2025"
    echo "   文档: http://localhost:2025/docs"
    echo "   健康检查: http://localhost:2025/ok"
    
    echo ""
    print_info "RuoYi后端服务:"
    echo "   URL: http://localhost:8000"
    echo "   API文档: http://localhost:8000/docs"
    
            echo ""
    print_info "前端服务 (如已启动):"
    echo "   URL: http://localhost:80"
    
    echo ""
    print_info "日志文件位置:"
    echo "   Agent服务: logs/agents-service.log"
    echo "   后端服务: logs/ruoyi-backend.log"
    echo "   前端服务: logs/frontend.log"
    
    echo ""
    print_info "停止所有服务:"
    echo "   ./stop_all.sh"
    
    echo ""
    print_success "所有服务已启动完成！"
}

# 主函数
main() {
    clear
    
    print_header "AI智能测试平台 - 一键启动"
    print_info "版权所有 (c) 2023-2026 北京慧测信息技术有限公司"
    echo ""
    
    # 创建必要的目录
    mkdir -p logs .pids
    
    # 执行各个步骤
    check_dependencies
    init_database
    configure_env
    install_python_deps
    start_agents_service
    start_ruoyi_backend
    start_frontend
    show_service_info
}

# 执行主函数
main
