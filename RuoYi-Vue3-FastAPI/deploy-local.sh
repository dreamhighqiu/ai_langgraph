#!/bin/bash
# ================================
# AI智能测试平台 - 本地开发部署脚本 (Linux/Mac/Git Bash)
# 
# 使用 uv 管理 Python 虚拟环境
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
PYTHON_VERSION="3.11"

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
  使用 uv 管理 Python 虚拟环境
  
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
  init        初始化本地开发环境 (使用uv)
  check       检查远程服务连接
  backend     启动后端服务
  frontend    启动前端服务
  all         启动所有本地服务
  stop        停止所有本地服务
  status      查看服务状态
  db          初始化数据库
  restart     重启所有服务（先停止再启动）
  help        显示帮助

示例:
  ./deploy-local.sh init       # 初始化环境
  ./deploy-local.sh check      # 检查远程服务
  ./deploy-local.sh all        # 启动本地服务
  ./deploy-local.sh restart    # 重启所有服务
"
}

# 检查并安装 uv
check_uv() {
    if command -v uv &> /dev/null; then
        print_success "uv: $(uv --version)"
        return 0
    else
        print_warning "uv 未安装，正在安装..."
        
        # 根据系统安装 uv
        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "mingw"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
            # Windows (Git Bash / MSYS2)
            print_info "在 Windows 上安装 uv..."
            powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
            
            # 添加到 PATH (当前会话)
            export PATH="$HOME/.local/bin:$PATH"
            export PATH="$USERPROFILE/.local/bin:$PATH"
            export PATH="$HOME/.cargo/bin:$PATH"
        else
            # Linux / Mac
            curl -LsSf https://astral.sh/uv/install.sh | sh
            export PATH="$HOME/.local/bin:$PATH"
        fi
        
        # 验证安装
        if command -v uv &> /dev/null; then
            print_success "uv 安装成功: $(uv --version)"
            return 0
        else
            print_error "uv 安装失败，请手动安装: https://docs.astral.sh/uv/getting-started/installation/"
            print_info "Windows: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\""
            print_info "Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh"
            return 1
        fi
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查本地依赖..."
    
    local has_error=false
    
    # 检查 uv
    if ! check_uv; then
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
        
        # 使用多种方式检测端口
        if nc -z -w 2 $REMOTE_SERVER $port 2>/dev/null; then
            print_success "$name: OK (${REMOTE_SERVER}:${port})"
        elif timeout 2 bash -c "echo >/dev/tcp/$REMOTE_SERVER/$port" 2>/dev/null; then
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
    
    # 使用 uv 创建 Python 虚拟环境
    print_info "使用 uv 创建 Python 虚拟环境..."
    cd $BACKEND_DIR
    
    # 创建虚拟环境
    if [ ! -d ".venv" ]; then
        uv venv --python $PYTHON_VERSION
        print_success "虚拟环境创建成功 (.venv)"
    else
        print_info "虚拟环境已存在"
    fi
    
    # 安装依赖
    print_info "使用 uv 安装 Python 依赖..."
    uv pip install -r requirements.txt
    uv pip install minio python-dotenv
    print_success "Python 依赖安装完成"
    
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
    print_info "安装前端依赖 (可能需要几分钟)..."
    cd $FRONTEND_DIR
    
    # 检查是否已有 node_modules
    if [ -d "node_modules" ]; then
        print_info "node_modules 已存在，检查是否需要更新..."
        npm install --prefer-offline --no-audit --progress=true || npm install
    else
        print_info "首次安装，请稍候..."
        npm install --no-audit --progress=true
    fi
    
    if [ $? -eq 0 ]; then
        print_success "前端依赖安装完成"
    else
        print_error "前端依赖安装失败"
        exit 1
    fi
    
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
    
    cd $BACKEND_DIR
    
    # 检查 pymysql 是否安装
    if ! uv pip show pymysql &>/dev/null; then
        print_info "安装 pymysql..."
        uv pip install pymysql
    fi
    
    # 激活虚拟环境并运行初始化脚本
    activate_venv
    
    # 运行数据库初始化工具
    python init_db.py --env dev
    
    cd ..
}

# 激活虚拟环境的辅助函数
activate_venv() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "mingw"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
        # Windows Git Bash
        source .venv/Scripts/activate
    else
        # Linux / Mac
        source .venv/bin/activate
    fi
}

# 启动后端
start_backend() {
    local force_restart=${1:-false}  # 是否强制重启
    
    print_info "启动后端服务 (热重载模式)..."
    
    # 创建目录
    mkdir -p logs .pids
    
    # 检查是否已运行
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            if [ "$force_restart" = "true" ]; then
                print_info "强制重启：停止旧进程 (PID: $pid)..."
                kill $pid 2>/dev/null || true
                sleep 1
                if kill -0 $pid 2>/dev/null; then
                    kill -9 $pid 2>/dev/null || true
                fi
                rm -f .pids/backend.pid
                # 清理端口
                kill_port 9099 "后端"
            else
                print_warning "后端服务已在运行 (PID: $pid)"
                print_info "💡 代码更改将自动重载，无需重启"
                print_info "💡 如需强制重启，请使用: ./deploy-local.sh restart"
                return
            fi
        else
            rm -f .pids/backend.pid
        fi
    fi
    
    cd $BACKEND_DIR
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        print_error "虚拟环境不存在，请先运行: ./deploy-local.sh init"
        cd ..
        return 1
    fi
    
    # 激活虚拟环境
    activate_venv
    export APP_ENV=dev
    
    # 检查依赖
    if ! python -c "import fastapi" 2>/dev/null; then
        print_error "依赖未安装，请先运行: ./deploy-local.sh init"
        cd ..
        return 1
    fi
    
    # 使用 uvicorn 直接启动，启用热重载
    print_info "启动中 (uvicorn --reload)..."
    nohup uvicorn app:app --host 0.0.0.0 --port 9099 --reload --reload-dir . > ../logs/backend.log 2>&1 &
    backend_pid=$!
    echo $backend_pid > ../.pids/backend.pid
    
    # 等待启动
    sleep 5
    
    # 检查进程
    if kill -0 $backend_pid 2>/dev/null; then
        # 检查端口
        sleep 2
        if nc -z localhost 9099 2>/dev/null || timeout 1 bash -c "echo >/dev/tcp/localhost/9099" 2>/dev/null; then
            print_success "后端服务启动成功 ✅"
            echo "  🌐 地址: http://localhost:9099/dev-api"
            echo "  📚 文档: http://localhost:9099/dev-api/docs"
            echo "  🔧 PID:  $backend_pid"
            echo "  📝 日志: logs/backend.log"
            echo "  🔥 热重载: 已启用 (代码更改自动生效)"
        else
            print_warning "进程已启动但端口未监听，请查看日志"
            tail -20 ../logs/backend.log 2>/dev/null
        fi
    else
        print_error "后端启动失败，请查看日志: logs/backend.log"
        tail -30 ../logs/backend.log 2>/dev/null || print_error "日志文件不存在"
        rm -f ../.pids/backend.pid
    fi
    
    cd ..
}

# 启动前端
start_frontend() {
    local force_restart=${1:-false}  # 是否强制重启
    
    print_info "启动前端服务 (HMR 热更新模式)..."
    
    # 检查是否已运行
    if [ -f ".pids/frontend.pid" ]; then
        pid=$(cat .pids/frontend.pid)
        if kill -0 $pid 2>/dev/null; then
            if [ "$force_restart" = "true" ]; then
                print_info "强制重启：停止旧进程 (PID: $pid)..."
                kill $pid 2>/dev/null || true
                sleep 1
                if kill -0 $pid 2>/dev/null; then
                    kill -9 $pid 2>/dev/null || true
                fi
                rm -f .pids/frontend.pid
                # 清理端口
                kill_port 5173 "前端"
                kill_port 5174 "前端备用"
            else
                print_warning "前端服务已在运行 (PID: $pid)"
                print_info "💡 代码更改将自动热更新，无需重启"
                print_info "💡 如需强制重启，请使用: ./deploy-local.sh restart"
                return
            fi
        else
            rm -f .pids/frontend.pid
        fi
    fi
    
    cd $FRONTEND_DIR
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        print_error "依赖未安装，请先运行: ./deploy-local.sh init"
        cd ..
        return 1
    fi
    
    # 修复 vite 配置中的端口（从80改为5173）
    if grep -q "port: 80" vite.config.js 2>/dev/null; then
        print_info "修复 vite 配置端口..."
        sed -i 's/port: 80/port: 5173/' vite.config.js
    fi
    
    # 启动 (Vite 开发服务器自带 HMR)
    print_info "启动中 (Vite HMR)..."
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    frontend_pid=$!
    echo $frontend_pid > ../.pids/frontend.pid
    
    # 等待启动
    sleep 8
    
    # 检查进程
    if kill -0 $frontend_pid 2>/dev/null; then
        # 检查端口
        sleep 2
        if nc -z localhost 5173 2>/dev/null || timeout 1 bash -c "echo >/dev/tcp/localhost/5173" 2>/dev/null; then
            print_success "前端服务启动成功 ✅"
            echo "  🌐 地址: http://localhost:5173"
            echo "  🔧 PID:  $frontend_pid"
            echo "  📝 日志: logs/frontend.log"
            echo "  🔥 HMR:  已启用 (代码更改自动热更新)"
        else
            print_warning "进程已启动但端口未监听，请查看日志"
            tail -20 ../logs/frontend.log 2>/dev/null
        fi
    else
        print_error "前端启动失败，请查看日志: logs/frontend.log"
        tail -30 ../logs/frontend.log 2>/dev/null || print_error "日志文件不存在"
        rm -f ../.pids/frontend.pid
    fi
    
    cd ..
}

# 启动所有服务
start_all() {
    local force_restart=${1:-false}  # 是否强制重启
    
    print_info "启动本地开发服务 (Debug 模式)..."
    echo ""
    
    # 先停止已运行的服务（如果存在）
    if [ "$force_restart" = "true" ] || [ -f ".pids/backend.pid" ] || [ -f ".pids/frontend.pid" ]; then
        print_info "检查并停止已运行的服务..."
        stop_all
        sleep 2
        echo ""
        # 如果检测到服务，强制重启
        force_restart="true"
    fi
    
    mkdir -p logs .pids
    
    start_backend "$force_restart"
    echo ""
    start_frontend "$force_restart"
    
    echo ""
    echo "========================================"
    print_success "🚀 本地开发服务启动完成！"
    echo "========================================"
    echo ""
    echo "本地服务:"
    echo "  🌐 前端: http://localhost:5173"
    echo "  🔧 后端: http://localhost:9099/dev-api"
    echo "  📚 文档: http://localhost:9099/dev-api/docs"
    echo ""
    echo "远程服务 ($REMOTE_SERVER):"
    echo "  MySQL:        ${REMOTE_SERVER}:3306"
    echo "  Redis:        ${REMOTE_SERVER}:6379"
    echo "  MinIO控制台:  http://${REMOTE_SERVER}:9001"
    echo "  Milvus管理:   http://${REMOTE_SERVER}:3000"
    echo ""
    echo "默认账号: admin / admin123"
    echo ""
    echo "========================================"
    echo "🔥 热重载模式已启用:"
    echo "  • 后端: 修改 Python 代码后自动重载 (uvicorn --reload)"
    echo "  • 前端: 修改 Vue/JS 代码后自动热更新 (Vite HMR)"
    echo "  • 无需手动重启服务，代码更改自动生效!"
    echo "========================================"
}

# 根据端口杀进程
kill_port() {
    local port=$1
    local name=$2
    
    # 检测系统类型
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "mingw"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
        # Windows (Git Bash / MSYS2) - netstat 输出全部状态，避免遗漏
        local pids=$(netstat -ano 2>/dev/null | grep ":${port}" | awk '{print $5}' | sort -u)
        local killed=0
        if [ -n "$pids" ]; then
            print_info "发现占用端口 $port 的进程: $pids"
        fi
        if [ -n "$pids" ]; then
            for pid in $pids; do
                if [ "$pid" != "0" ] && [ -n "$pid" ] && [ "$pid" != "-" ]; then
                    taskkill /F /PID $pid 2>/dev/null && {
                        print_success "已杀掉占用端口 $port 的进程 (PID: $pid)"
                        killed=1
                    } || true
                fi
            done
        fi
        # 若 netstat 未找到或未杀干净，尝试 PowerShell 获取并杀掉
        if [ $killed -eq 0 ]; then
            local ps_pids=$(powershell.exe -NoProfile -Command "Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess" 2>/dev/null | tr '\r' ' ' | xargs)
            if [ -n "$ps_pids" ]; then
                print_info "PowerShell 发现占用端口 $port 的进程: $ps_pids"
                for pid in $ps_pids; do
                    if [ -n "$pid" ]; then
                        taskkill /F /PID $pid 2>/dev/null && {
                            print_success "已杀掉占用端口 $port 的进程 (PID: $pid)"
                            killed=1
                        } || true
                    fi
                done
            fi
        fi
        # 兜底：再用 netstat 逐个 taskkill，确保清理
        local pids2=$(netstat -ano 2>/dev/null | grep ":${port}" | awk '{print $5}' | sort -u)
        if [ -n "$pids2" ]; then
            print_info "兜底清理端口 $port: $pids2"
            for pid in $pids2; do
                if [ "$pid" != "0" ] && [ -n "$pid" ] && [ "$pid" != "-" ]; then
                    taskkill /F /PID $pid 2>/dev/null && {
                        print_success "兜底已杀掉占用端口 $port 的进程 (PID: $pid)"
                        killed=1
                    } || true
                fi
            done
        fi
        if [ $killed -eq 0 ]; then
            print_info "端口 $port 当前无占用进程"
        fi
    else
        # Linux / Mac
        local pids=$(lsof -t -i:$port 2>/dev/null || ss -tlnp 2>/dev/null | grep ":$port" | awk '{print $7}' | cut -d',' -f2 | cut -d'=' -f2)
        local killed=0
        if [ -n "$pids" ]; then
            for pid in $pids; do
                if [ -n "$pid" ] && [ "$pid" != "-" ]; then
                    kill -9 $pid 2>/dev/null && {
                        print_success "已杀掉占用端口 $port 的进程 (PID: $pid)"
                        killed=1
                    } || true
                fi
            done
        fi
        if [ $killed -eq 0 ]; then
            print_info "端口 $port 当前无占用进程"
        fi
    fi
}

# 停止服务
stop_all() {
    print_info "停止本地服务..."
    echo ""
    
    # 1. 首先尝试通过 PID 文件停止
    print_info "通过 PID 文件停止服务..."
    
    # 停止后端
    if [ -f ".pids/backend.pid" ]; then
        pid=$(cat .pids/backend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null || true
            sleep 1
            # 如果还没停，强制杀
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null || true
            fi
            print_success "后端服务已停止 (PID: $pid)"
        fi
        rm -f .pids/backend.pid
    fi
    
    # 停止前端
    if [ -f ".pids/frontend.pid" ]; then
        pid=$(cat .pids/frontend.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid 2>/dev/null || true
            sleep 1
            if kill -0 $pid 2>/dev/null; then
                kill -9 $pid 2>/dev/null || true
            fi
            print_success "前端服务已停止 (PID: $pid)"
        fi
        rm -f .pids/frontend.pid
    fi
    
    # 2. 强制清理端口占用（确保端口被释放）
    echo ""
    print_info "检查并清理端口占用..."
    
    # 清理后端端口 9099
    kill_port 9099 "后端"
    
    # 清理前端端口 5173 和 5174
    kill_port 5173 "前端"
    kill_port 5174 "前端备用"
    
    # 3. 清理 PID 文件
    rm -f .pids/backend.pid .pids/frontend.pid 2>/dev/null
    
    echo ""
    print_success "本地服务已全部停止，端口已释放"
}

# 重启所有服务
restart_all() {
    print_info "重启本地开发服务..."
    echo ""
    
    # 先停止
    stop_all
    echo ""
    
    # 等待一下确保端口释放
    sleep 2
    
    # 再启动（强制重启模式）
    start_all "true"
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
    restart) restart_all ;;
    stop) stop_all ;;
    status) show_status ;;
    *) show_help ;;
esac
