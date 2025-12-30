#!/bin/bash
# ================================
# AI智能测试平台 - 本地开发部署脚本 (Linux/Mac)
# 
# 本地开发场景：
#   - 前端服务: 本地 (localhost:5173)
#   - 后端服务: 本地 (localhost:9099)
#   - 基础设施: 远程 (47.110.95.246)
# ================================

set -e

# 配置变量
REMOTE_SERVER="47.110.95.246"
BACKEND_DIR="ruoyi-fastapi-backend"
FRONTEND_DIR="ruoyi-fastapi-frontend"
ENV_MODE="dev"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示帮助
show_help() {
    echo "
AI智能测试平台 - 本地开发部署脚本

========================================
部署模式说明:
  本地开发: 前端+后端在本地，基础设施在远程服务器
  
  本地服务:
    - 前端: http://localhost:5173
    - 后端: http://localhost:9099
    
  远程服务 ($REMOTE_SERVER):
    - MySQL:  3306
    - Redis:  6379
    - MinIO:  9000/9001
    - Milvus: 19530
    - Ollama: 11434
========================================

用法: ./deploy-local.sh [命令]

命令:
  init        初始化本地开发环境
  check       检查远程服务连接
  backend     启动后端服务
  frontend    启动前端服务
  all         启动所有本地服务
  stop        停止所有本地服务
  status      查看服务状态
  db          初始化数据库
  help        显示帮助

示例:
  ./deploy-local.sh init       # 初始化环境
  ./deploy-local.sh check      # 检查远程服务
  ./deploy-local.sh all        # 启动本地服务
"
}

# 检查依赖
check_dependencies() {
    print_info "检查本地依赖..."
    
    local has_error=false
    
    # Python
    if command -v python3 &> /dev/null; then
        print_success "Python: $(python3 --version)"
    else
        print_error "Python3 未安装"
        has_error=true
    fi
    
    # Node.js
    if command -v node &> /dev/null; then
        print_success "Node.js: $(node --version)"
    else
        print_error "Node.js 未安装"
        has_error=true
    fi
    
    # npm
    if command -v npm &> /dev/null; then
        print_success "npm: $(npm --version)"
    else
        print_error "npm 未安装"
        has_error=true
    fi
    
    if [ "$has_error" = true ]; then
        exit 1
    fi
}

# 检查远程服务
check_remote_services() {
    print_info "检查远程服务连接 ($REMOTE_SERVER)..."
    echo ""
    
    local services=(
        "MySQL:3306"
        "Redis:6379"
        "MinIO API:9000"
        "MinIO Console:9001"
        "Milvus:19530"
        "Attu:3000"
        "Ollama:11434"
    )
    
    local all_ok=true
    for svc in "${services[@]}"; do
        name="${svc%%:*}"
        port="${svc##*:}"
        
        if nc -z -w 2 $REMOTE_SERVER $port 2>/dev/null; then
            print_success "$name: OK (${REMOTE_SERVER}:${port})"
        else
            print_error "$name: 无法连接 (${REMOTE_SERVER}:${port})"
            all_ok=false
        fi
    done
    
    echo ""
    if [ "$all_ok" = true ]; then
        print_success "所有远程服务连接正常！"
    else
        print_warning "部分服务无法连接，请检查网络或服务状态"
    fi
}

# 初始化环境
init_environment() {
    print_info "初始化本地开发环境..."
    echo ""
    
    check_dependencies
    echo ""
    
    # Python虚拟环境
    print_info "创建Python虚拟环境..."
    cd $BACKEND_DIR
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    else
        print_info "虚拟环境已存在"
    fi
    
    # 安装依赖
    print_info "安装Python依赖..."
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    pip install minio python-dotenv -q
    print_success "Python依赖安装完成"
    
    # 创建环境配置
    if [ ! -f ".env.dev" ]; then
        print_info "创建环境配置文件..."
        cp env.example .env.dev
        print_success "已创建 .env.dev，请检查配置"
    else
        print_info "环境配置文件已存在"
    fi
    
    cd ..
    
    # 前端依赖
    print_info "安装前端依赖..."
    cd $FRONTEND_DIR
    npm install --silent
    print_success "前端依赖安装完成"
    cd ..
    
    # 创建目录
    mkdir -p logs .pids
    
    echo ""
    print_success "本地开发环境初始化完成！"
    echo ""
    print_info "下一步:"
    echo "  1. 运行 ./deploy-local.sh check 检查远程服务"
    echo "  2. 运行 ./deploy-local.sh db 初始化数据库"
    echo "  3. 运行 ./deploy-local.sh all 启动服务"
}

# 初始化数据库
init_database() {
    print_info "数据库初始化..."
    echo ""
    echo "请使用MySQL客户端连接远程数据库执行SQL文件:"
    echo ""
    echo "  服务器: $REMOTE_SERVER"
    echo "  端口:   3306"
    echo "  用户名: root"
    echo "  密码:   root123456"
    echo "  数据库: ai_db"
    echo ""
    echo "SQL文件:"
    echo "  1. $BACKEND_DIR/sql/ruoyi-fastapi.sql (RuoYi基础表)"
    echo "  2. $BACKEND_DIR/sql/testing_platform.sql (测试平台表)"
    echo ""
    echo "命令示例:"
    echo "  mysql -h $REMOTE_SERVER -P 3306 -u root -proot123456 ai_db < $BACKEND_DIR/sql/ruoyi-fastapi.sql"
    echo "  mysql -h $REMOTE_SERVER -P 3306 -u root -proot123456 ai_db < $BACKEND_DIR/sql/testing_platform.sql"
}

# 启动后端
start_backend() {
    print_info "启动后端服务..."
    
    # 检查是否已运行
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            print_warning "后端服务已在运行 (PID: $pid)"
            return
        fi
    fi
    
    cd $BACKEND_DIR
    source venv/bin/activate
    export APP_ENV=dev
    
    # 启动
    print_info "启动中..."
    nohup python app.py --env dev > ../logs/backend.log 2>&1 &
    echo $! > ../.pids/backend.pid
    
    sleep 2
    
    if kill -0 $(cat ../.pids/backend.pid) 2>/dev/null; then
        print_success "后端服务启动成功"
        echo "  地址: http://localhost:9099/dev-api"
        echo "  文档: http://localhost:9099/dev-api/docs"
        echo "  PID:  $(cat ../.pids/backend.pid)"
        echo "  日志: logs/backend.log"
    else
        print_error "后端启动失败，请查看日志"
    fi
    
    cd ..
}

# 启动前端
start_frontend() {
    print_info "启动前端服务..."
    
    # 检查是否已运行
    if [ -f ".pids/frontend.pid" ]; then
        pid=$(cat .pids/frontend.pid)
        if kill -0 $pid 2>/dev/null; then
            print_warning "前端服务已在运行 (PID: $pid)"
            return
        fi
    fi
    
    cd $FRONTEND_DIR
    
    # 启动
    print_info "启动中..."
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    echo $! > ../.pids/frontend.pid
    
    sleep 3
    
    if kill -0 $(cat ../.pids/frontend.pid) 2>/dev/null; then
        print_success "前端服务启动成功"
        echo "  地址: http://localhost:5173"
        echo "  PID:  $(cat ../.pids/frontend.pid)"
        echo "  日志: logs/frontend.log"
    else
        print_error "前端启动失败，请查看日志"
    fi
    
    cd ..
}

# 启动所有服务
start_all() {
    print_info "启动本地开发服务..."
    echo ""
    
    mkdir -p logs .pids
    
    start_backend
    echo ""
    start_frontend
    
    echo ""
    echo "========================================"
    print_success "本地开发服务启动完成！"
    echo "========================================"
    echo ""
    echo "本地服务:"
    echo "  前端: http://localhost:5173"
    echo "  后端: http://localhost:9099/dev-api"
    echo "  文档: http://localhost:9099/dev-api/docs"
    echo ""
    echo "远程服务 ($REMOTE_SERVER):"
    echo "  MySQL:        ${REMOTE_SERVER}:3306"
    echo "  Redis:        ${REMOTE_SERVER}:6379"
    echo "  MinIO控制台:  http://${REMOTE_SERVER}:9001"
    echo "  Milvus管理:   http://${REMOTE_SERVER}:3000"
    echo ""
    echo "默认账号: admin / admin123"
    echo "========================================"
}

# 停止服务
stop_all() {
    print_info "停止本地服务..."
    
    # 停止后端
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "后端服务已停止 (PID: $pid)"
        fi
        rm -f .pids/backend.pid
    fi
    
    # 停止前端
    if [ -f ".pids/frontend.pid" ]; then
        pid=$(cat .pids/frontend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "前端服务已停止 (PID: $pid)"
        fi
        rm -f .pids/frontend.pid
    fi
    
    print_success "本地服务已停止"
}

# 查看状态
show_status() {
    echo ""
    echo "========== 本地服务状态 =========="
    echo ""
    
    # 后端
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            print_success "后端: 运行中 (PID: $pid) - http://localhost:9099"
        else
            print_error "后端: 已停止"
        fi
    else
        print_warning "后端: 未启动"
    fi
    
    # 前端
    if [ -f ".pids/frontend.pid" ]; then
        pid=$(cat .pids/frontend.pid)
        if kill -0 $pid 2>/dev/null; then
            print_success "前端: 运行中 (PID: $pid) - http://localhost:5173"
        else
            print_error "前端: 已停止"
        fi
    else
        print_warning "前端: 未启动"
    fi
    
    echo ""
    echo "========== 远程服务状态 ($REMOTE_SERVER) =========="
    echo ""
    
    check_remote_services
}

# 主函数
case "${1:-help}" in
    init) init_environment ;;
    check) check_remote_services ;;
    db) init_database ;;
    backend) start_backend ;;
    frontend) start_frontend ;;
    all) start_all ;;
    stop) stop_all ;;
    status) show_status ;;
    *) show_help ;;
esac

