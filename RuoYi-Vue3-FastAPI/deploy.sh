#!/bin/bash
# ================================
# AI智能测试平台部署脚本
# 服务器: 47.110.95.246
# ================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SERVER_IP="47.110.95.246"
PROJECT_NAME="ai-testing-platform"
BACKEND_DIR="ruoyi-fastapi-backend"
FRONTEND_DIR="ruoyi-fastapi-frontend"
ENV_MODE="${1:-dev}"  # 默认dev环境

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "
AI智能测试平台部署脚本

用法: ./deploy.sh [命令] [选项]

命令:
  init        初始化环境 (安装依赖)
  db          初始化数据库
  backend     启动后端服务
  frontend    启动前端服务
  all         启动所有服务
  stop        停止所有服务
  status      查看服务状态
  help        显示帮助信息

选项:
  dev         开发环境 (默认)
  prod        生产环境

示例:
  ./deploy.sh init          # 初始化环境
  ./deploy.sh db            # 初始化数据库
  ./deploy.sh all dev       # 开发环境启动所有服务
  ./deploy.sh all prod      # 生产环境启动所有服务
  ./deploy.sh stop          # 停止所有服务
"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    print_success "Python3 已安装: $(python3 --version)"
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装"
        exit 1
    fi
    print_success "Node.js 已安装: $(node --version)"
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装"
        exit 1
    fi
    print_success "npm 已安装: $(npm --version)"
}

# 初始化环境
init_environment() {
    print_info "初始化环境..."
    
    check_dependencies
    
    # 创建Python虚拟环境
    print_info "创建Python虚拟环境..."
    cd $BACKEND_DIR
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    fi
    
    # 激活虚拟环境并安装依赖
    print_info "安装Python依赖..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 安装额外依赖
    pip install minio langgraph-sdk python-dotenv
    
    print_success "Python依赖安装完成"
    
    # 创建环境配置文件
    if [ ! -f ".env.${ENV_MODE}" ]; then
        print_info "创建环境配置文件..."
        cp env.example .env.${ENV_MODE}
        print_warning "请编辑 .env.${ENV_MODE} 文件配置数据库等信息"
    fi
    
    cd ..
    
    # 安装前端依赖
    print_info "安装前端依赖..."
    cd $FRONTEND_DIR
    npm install
    print_success "前端依赖安装完成"
    
    cd ..
    
    print_success "环境初始化完成！"
}

# 初始化数据库
init_database() {
    print_info "初始化数据库..."
    
    # 读取数据库配置
    DB_HOST="${DB_HOST:-$SERVER_IP}"
    DB_PORT="${DB_PORT:-3306}"
    DB_USER="${DB_USERNAME:-root}"
    DB_PASS="${DB_PASSWORD:-root123456}"
    DB_NAME="${DB_DATABASE:-ai_db}"
    
    print_info "数据库配置:"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  User: $DB_USER"
    echo "  Database: $DB_NAME"
    
    # 执行RuoYi基础SQL
    print_info "执行RuoYi基础SQL..."
    mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME < $BACKEND_DIR/sql/ruoyi-fastapi.sql
    print_success "RuoYi基础SQL执行完成"
    
    # 执行测试平台SQL
    print_info "执行测试平台SQL..."
    mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS $DB_NAME < $BACKEND_DIR/sql/testing_platform.sql
    print_success "测试平台SQL执行完成"
    
    print_success "数据库初始化完成！"
}

# 启动后端服务
start_backend() {
    print_info "启动后端服务 (环境: $ENV_MODE)..."
    
    cd $BACKEND_DIR
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 导出环境变量
    export APP_ENV=$ENV_MODE
    
    # 启动服务
    if [ "$ENV_MODE" = "prod" ]; then
        # 生产环境使用gunicorn
        print_info "使用生产模式启动..."
        nohup python app.py --env prod > ../logs/backend.log 2>&1 &
    else
        # 开发环境
        print_info "使用开发模式启动..."
        nohup python app.py --env dev > ../logs/backend.log 2>&1 &
    fi
    
    # 保存PID
    echo $! > ../.pids/backend.pid
    
    cd ..
    
    print_success "后端服务启动成功 (PID: $(cat .pids/backend.pid))"
    print_info "日志文件: logs/backend.log"
}

# 启动前端服务
start_frontend() {
    print_info "启动前端服务 (环境: $ENV_MODE)..."
    
    cd $FRONTEND_DIR
    
    if [ "$ENV_MODE" = "prod" ]; then
        # 生产环境：构建并使用nginx
        print_info "构建生产版本..."
        npm run build:prod
        print_success "前端构建完成，请配置nginx指向dist目录"
    else
        # 开发环境
        print_info "启动开发服务器..."
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        echo $! > ../.pids/frontend.pid
        print_success "前端服务启动成功 (PID: $(cat ../.pids/frontend.pid))"
    fi
    
    cd ..
    
    print_info "日志文件: logs/frontend.log"
}

# 启动所有服务
start_all() {
    print_info "启动所有服务..."
    
    # 创建必要目录
    mkdir -p logs .pids
    
    start_backend
    sleep 3
    start_frontend
    
    print_success "所有服务启动完成！"
    
    echo ""
    print_info "服务地址:"
    echo "  后端API: http://${SERVER_IP}:9099/dev-api"
    echo "  前端页面: http://${SERVER_IP}:80 (生产) 或 http://localhost:5173 (开发)"
    echo ""
    print_info "基础设施服务:"
    echo "  MySQL: ${SERVER_IP}:3306"
    echo "  Redis: ${SERVER_IP}:6379"
    echo "  MinIO: ${SERVER_IP}:9000 (API) / ${SERVER_IP}:9001 (Console)"
    echo "  Milvus: ${SERVER_IP}:19530"
    echo "  Attu: ${SERVER_IP}:3000"
    echo "  Ollama: ${SERVER_IP}:11434"
}

# 停止所有服务
stop_all() {
    print_info "停止所有服务..."
    
    # 停止后端
    if [ -f ".pids/backend.pid" ]; then
        PID=$(cat .pids/backend.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            print_success "后端服务已停止 (PID: $PID)"
        fi
        rm -f .pids/backend.pid
    fi
    
    # 停止前端
    if [ -f ".pids/frontend.pid" ]; then
        PID=$(cat .pids/frontend.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            print_success "前端服务已停止 (PID: $PID)"
        fi
        rm -f .pids/frontend.pid
    fi
    
    print_success "所有服务已停止"
}

# 查看服务状态
show_status() {
    print_info "服务状态:"
    
    echo ""
    echo "=== 应用服务 ==="
    
    # 后端状态
    if [ -f ".pids/backend.pid" ]; then
        PID=$(cat .pids/backend.pid)
        if kill -0 $PID 2>/dev/null; then
            print_success "后端服务: 运行中 (PID: $PID)"
        else
            print_error "后端服务: 已停止"
        fi
    else
        print_warning "后端服务: 未启动"
    fi
    
    # 前端状态
    if [ -f ".pids/frontend.pid" ]; then
        PID=$(cat .pids/frontend.pid)
        if kill -0 $PID 2>/dev/null; then
            print_success "前端服务: 运行中 (PID: $PID)"
        else
            print_error "前端服务: 已停止"
        fi
    else
        print_warning "前端服务: 未启动"
    fi
    
    echo ""
    echo "=== 基础设施服务 (${SERVER_IP}) ==="
    
    # 检查MySQL
    if nc -z $SERVER_IP 3306 2>/dev/null; then
        print_success "MySQL: 运行中 (${SERVER_IP}:3306)"
    else
        print_error "MySQL: 无法连接"
    fi
    
    # 检查Redis
    if nc -z $SERVER_IP 6379 2>/dev/null; then
        print_success "Redis: 运行中 (${SERVER_IP}:6379)"
    else
        print_error "Redis: 无法连接"
    fi
    
    # 检查MinIO
    if nc -z $SERVER_IP 9000 2>/dev/null; then
        print_success "MinIO: 运行中 (${SERVER_IP}:9000)"
    else
        print_error "MinIO: 无法连接"
    fi
    
    # 检查Milvus
    if nc -z $SERVER_IP 19530 2>/dev/null; then
        print_success "Milvus: 运行中 (${SERVER_IP}:19530)"
    else
        print_error "Milvus: 无法连接"
    fi
    
    # 检查Ollama
    if nc -z $SERVER_IP 11434 2>/dev/null; then
        print_success "Ollama: 运行中 (${SERVER_IP}:11434)"
    else
        print_error "Ollama: 无法连接"
    fi
}

# 主函数
main() {
    COMMAND="${1:-help}"
    ENV_MODE="${2:-dev}"
    
    case $COMMAND in
        init)
            init_environment
            ;;
        db)
            init_database
            ;;
        backend)
            start_backend
            ;;
        frontend)
            start_frontend
            ;;
        all)
            start_all
            ;;
        stop)
            stop_all
            ;;
        status)
            show_status
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"

