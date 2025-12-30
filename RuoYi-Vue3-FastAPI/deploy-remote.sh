#!/bin/bash
# ================================
# AI智能测试平台 - 远程服务器部署脚本
# 
# 远程部署场景：
#   所有服务都部署在远程服务器 47.110.95.246
#   包括前端、后端和基础设施
# ================================

set -e

# 配置变量
SERVER_IP="47.110.95.246"
BACKEND_DIR="ruoyi-fastapi-backend"
FRONTEND_DIR="ruoyi-fastapi-frontend"
ENV_MODE="${1:-prod}"

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
AI智能测试平台 - 远程服务器部署脚本

========================================
部署模式说明:
  远程部署: 所有服务部署在服务器 $SERVER_IP
  
  应用服务:
    - 前端: http://${SERVER_IP}:80 (Nginx)
    - 后端: http://${SERVER_IP}:9099
    
  基础设施 (Docker Compose):
    - MySQL:  3306
    - Redis:  6379
    - MinIO:  9000/9001
    - Milvus: 19530
    - Ollama: 11434
========================================

用法: ./deploy-remote.sh [命令] [环境]

命令:
  init        初始化生产环境
  build       构建前端
  backend     启动/重启后端
  deploy      完整部署
  stop        停止应用服务
  status      查看服务状态
  logs        查看日志
  help        显示帮助

环境:
  prod        生产环境 (默认)
  dev         开发环境

示例:
  ./deploy-remote.sh init prod    # 初始化生产环境
  ./deploy-remote.sh deploy       # 完整部署
  ./deploy-remote.sh status       # 查看状态
"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    print_success "Python3: $(python3 --version)"
    
    # Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装"
        exit 1
    fi
    print_success "Node.js: $(node --version)"
    
    # Nginx
    if ! command -v nginx &> /dev/null; then
        print_warning "Nginx 未安装，前端需要手动配置Web服务器"
    else
        print_success "Nginx: $(nginx -v 2>&1)"
    fi
}

# 初始化环境
init_environment() {
    print_info "初始化生产环境..."
    
    check_dependencies
    
    # Python虚拟环境
    print_info "创建Python虚拟环境..."
    cd $BACKEND_DIR
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install minio python-dotenv gunicorn
    
    # 创建生产环境配置
    if [ ! -f ".env.prod" ]; then
        cat > .env.prod << 'EOF'
# 生产环境配置
APP_ENV=prod
APP_NAME=AI智能测试平台
APP_ROOT_PATH=/prod-api
APP_HOST=0.0.0.0
APP_PORT=9099
APP_VERSION=1.0.0
APP_RELOAD=false

# JWT - 请修改为安全的密钥
JWT_SECRET_KEY=your-secure-production-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 数据库
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USERNAME=root
DB_PASSWORD=root123456
DB_DATABASE=ai_db
DB_ECHO=false

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=redis123456

# MinIO
MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=ai-testing

# Milvus
MILVUS_HOST=127.0.0.1
MILVUS_PORT=19530

# LangGraph
LANGGRAPH_API_URL=http://127.0.0.1:2025

# Ollama
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b
EOF
        print_success "已创建 .env.prod"
        print_warning "请编辑 .env.prod 修改安全密钥"
    fi
    
    cd ..
    
    # 前端依赖
    print_info "安装前端依赖..."
    cd $FRONTEND_DIR
    npm install
    cd ..
    
    mkdir -p logs .pids
    
    print_success "生产环境初始化完成！"
}

# 构建前端
build_frontend() {
    print_info "构建前端..."
    
    cd $FRONTEND_DIR
    npm run build:prod
    
    print_success "前端构建完成: dist/"
    print_info "请配置Nginx指向 $(pwd)/dist 目录"
    
    # 生成Nginx配置示例
    cat > nginx.conf.example << EOF
# Nginx配置示例
server {
    listen 80;
    server_name $SERVER_IP;
    
    location / {
        root $(pwd)/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    location /prod-api/ {
        proxy_pass http://127.0.0.1:9099/prod-api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
    
    print_info "Nginx配置示例: nginx.conf.example"
    cd ..
}

# 启动后端
start_backend() {
    print_info "启动后端服务..."
    
    # 停止已有服务
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            sleep 2
        fi
        rm -f .pids/backend.pid
    fi
    
    cd $BACKEND_DIR
    source venv/bin/activate
    export APP_ENV=$ENV_MODE
    
    # 使用gunicorn启动
    if [ "$ENV_MODE" = "prod" ]; then
        nohup gunicorn app:app \
            --workers 4 \
            --worker-class uvicorn.workers.UvicornWorker \
            --bind 0.0.0.0:9099 \
            --access-logfile ../logs/backend_access.log \
            --error-logfile ../logs/backend_error.log \
            --daemon
        
        # 获取gunicorn主进程PID
        sleep 2
        pgrep -f "gunicorn.*app:app" | head -1 > ../.pids/backend.pid
    else
        nohup python app.py --env $ENV_MODE > ../logs/backend.log 2>&1 &
        echo $! > ../.pids/backend.pid
    fi
    
    cd ..
    
    sleep 2
    if [ -f ".pids/backend.pid" ] && kill -0 $(cat .pids/backend.pid) 2>/dev/null; then
        print_success "后端服务启动成功 (PID: $(cat .pids/backend.pid))"
    else
        print_error "后端启动失败"
    fi
}

# 完整部署
deploy_all() {
    print_info "开始完整部署..."
    
    init_environment
    build_frontend
    start_backend
    
    echo ""
    print_success "部署完成！"
    echo ""
    echo "服务地址:"
    echo "  前端: http://${SERVER_IP}:80 (需配置Nginx)"
    echo "  后端: http://${SERVER_IP}:9099"
    echo ""
    echo "注意:"
    echo "  1. 请配置Nginx指向前端dist目录"
    echo "  2. 请确保防火墙开放相应端口"
    echo "  3. 请修改 .env.prod 中的安全密钥"
}

# 停止服务
stop_all() {
    print_info "停止服务..."
    
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            # 同时杀掉gunicorn worker进程
            pkill -f "gunicorn.*app:app" 2>/dev/null || true
            print_success "后端服务已停止"
        fi
        rm -f .pids/backend.pid
    fi
    
    print_success "服务已停止"
}

# 查看状态
show_status() {
    echo ""
    echo "========== 应用服务状态 =========="
    echo ""
    
    # 后端
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            print_success "后端: 运行中 (PID: $pid)"
        else
            print_error "后端: 已停止"
        fi
    else
        print_warning "后端: 未启动"
    fi
    
    # Nginx
    if pgrep nginx > /dev/null; then
        print_success "Nginx: 运行中"
    else
        print_warning "Nginx: 未运行"
    fi
    
    echo ""
    echo "========== 基础设施服务状态 =========="
    echo ""
    
    services=("MySQL:3306" "Redis:6379" "MinIO:9000" "Milvus:19530" "Ollama:11434")
    for svc in "${services[@]}"; do
        name="${svc%%:*}"
        port="${svc##*:}"
        if nc -z 127.0.0.1 $port 2>/dev/null; then
            print_success "$name: 运行中 (127.0.0.1:$port)"
        else
            print_error "$name: 未运行"
        fi
    done
}

# 查看日志
show_logs() {
    log_type="${2:-backend}"
    
    case $log_type in
        backend)
            if [ -f "logs/backend.log" ]; then
                tail -f logs/backend.log
            elif [ -f "logs/backend_access.log" ]; then
                tail -f logs/backend_access.log logs/backend_error.log
            else
                print_error "日志文件不存在"
            fi
            ;;
        error)
            tail -f logs/backend_error.log
            ;;
        *)
            print_error "未知日志类型: $log_type"
            ;;
    esac
}

# 主函数
case "${1:-help}" in
    init) init_environment ;;
    build) build_frontend ;;
    backend) start_backend ;;
    deploy) deploy_all ;;
    stop) stop_all ;;
    status) show_status ;;
    logs) show_logs "$@" ;;
    *) show_help ;;
esac

