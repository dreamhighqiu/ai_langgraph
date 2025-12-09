#!/bin/bash
# =============================================================================
# AI LangGraph 服务启动脚本 (使用 uv)
# 
# 功能: 一键启动所有后端服务（使用 uv 管理的统一虚拟环境）
# 
# 服务列表:
#   1. LightRAG Server (知识库服务) - http://localhost:9621
#   2. MCP Server (RAG Anything)    - http://localhost:8001
#   3. Deep Agents Service          - http://localhost:2025
#   4. Frontend UI (可选)           - http://localhost:3000
#
# 使用方法:
#   ./start_all.sh          # 启动所有后端服务
#   ./start_all.sh --all    # 启动所有服务（包含前端）
#   ./start_all.sh --stop   # 停止所有服务
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# PID 文件目录
PID_DIR="$PROJECT_ROOT/.pids"
mkdir -p "$PID_DIR"

# 日志目录
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# =============================================================================
# 工具函数
# =============================================================================

print_banner() {
    printf "${CYAN}"
    printf "╔═══════════════════════════════════════════════════════════════╗\n"
    printf "║           🚀 AI LangGraph 服务启动器 (uv)                      ║\n"
    printf "║                                                               ║\n"
    printf "║   统一虚拟环境 · 一键启动 · 简单高效                           ║\n"
    printf "╚═══════════════════════════════════════════════════════════════╝\n"
    printf "${NC}"
}

print_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

print_success() {
    printf "${GREEN}[✓]${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}[!]${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}[✗]${NC} %s\n" "$1"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 等待服务启动
wait_for_service() {
    local port=$1
    local name=$2
    local max_wait=30
    local count=0
    
    while [ $count -lt $max_wait ]; do
        if check_port $port; then
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    return 1
}

# 检查 uv 是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv 未安装！请先安装 uv:"
        echo ""
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo ""
        exit 1
    fi
}

# 检查虚拟环境，不存在则创建
check_venv() {
    if [ ! -d "$PROJECT_ROOT/.venv" ]; then
        print_warning "虚拟环境不存在，正在使用 uv 创建..."
        print_info "运行 uv sync 安装依赖（首次运行可能需要几分钟）..."
        uv sync --python 3.11
        
        # 安装 LightRAG
        uv pip install -e ./anything-chat-rag[api]
        
        # 配置 Python 路径
        local site_packages=$(.venv/bin/python -c "import site; print(site.getsitepackages()[0])")
        cat > "$site_packages/ai-langgraph.pth" << EOF
$PROJECT_ROOT/testing-deep-agents-service/src
$PROJECT_ROOT/mcp-server/src
EOF
        
        print_success "虚拟环境创建完成"
    fi
}

# =============================================================================
# 服务启动函数 (使用 uv run)
# =============================================================================

start_lightrag() {
    local port=9621
    local name="LightRAG Server"
    local pid_file="$PID_DIR/lightrag.pid"
    local log_file="$LOG_DIR/lightrag.log"
    
    if check_port $port; then
        print_warning "$name 已在运行 (端口 $port)"
        return 0
    fi
    
    print_info "启动 $name..."
    
    cd "$PROJECT_ROOT/anything-chat-rag"
    nohup uv run --project "$PROJECT_ROOT" python -m lightrag.api.lightrag_server > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    if wait_for_service $port "$name"; then
        print_success "$name 已启动 (PID: $pid, 端口: $port)"
        printf "         📄 API 文档: ${CYAN}http://localhost:$port/docs${NC}\n"
    else
        print_error "$name 启动失败，请检查日志: $log_file"
        return 1
    fi
}

start_mcp_server() {
    local port=8001
    local name="MCP Server"
    local pid_file="$PID_DIR/mcp.pid"
    local log_file="$LOG_DIR/mcp.log"
    
    if check_port $port; then
        print_warning "$name 已在运行 (端口 $port)"
        return 0
    fi
    
    print_info "启动 $name..."
    
    cd "$PROJECT_ROOT/mcp-server"
    nohup uv run --project "$PROJECT_ROOT" python -m mcp_server_rag_anything.server > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    if wait_for_service $port "$name"; then
        print_success "$name 已启动 (PID: $pid, 端口: $port)"
    else
        print_error "$name 启动失败，请检查日志: $log_file"
        return 1
    fi
}

start_agent_service() {
    local port=2025
    local name="Deep Agents Service"
    local pid_file="$PID_DIR/agent.pid"
    local log_file="$LOG_DIR/agent.log"
    
    if check_port $port; then
        print_warning "$name 已在运行 (端口 $port)"
        return 0
    fi
    
    print_info "启动 $name..."
    
    cd "$PROJECT_ROOT/testing-deep-agents-service"
    nohup uv run --project "$PROJECT_ROOT" python start_server.py > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    if wait_for_service $port "$name"; then
        print_success "$name 已启动 (PID: $pid, 端口: $port)"
        printf "         📄 API 文档: ${CYAN}http://localhost:$port/docs${NC}\n"
        printf "         🎛️  Studio:  ${CYAN}http://localhost:$port/ui${NC}\n"
    else
        print_error "$name 启动失败，请检查日志: $log_file"
        return 1
    fi
}

start_frontend() {
    local port=3000
    local name="Frontend UI"
    local pid_file="$PID_DIR/frontend.pid"
    local log_file="$LOG_DIR/frontend.log"
    
    if check_port $port; then
        print_warning "$name 已在运行 (端口 $port)"
        return 0
    fi
    
    print_info "启动 $name..."
    
    cd "$PROJECT_ROOT/testing-deep-agents-ui"
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        print_info "安装前端依赖..."
        npm install
    fi
    
    nohup npm run dev > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    if wait_for_service $port "$name"; then
        print_success "$name 已启动 (PID: $pid, 端口: $port)"
        printf "         🌐 访问地址: ${CYAN}http://localhost:$port${NC}\n"
    else
        print_error "$name 启动失败，请检查日志: $log_file"
        return 1
    fi
}

# =============================================================================
# 服务停止函数
# =============================================================================

stop_service() {
    local name=$1
    local pid_file=$2
    local port=$3
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "已停止 $name (PID: $pid)"
        fi
        rm -f "$pid_file"
    fi
    
    # 确保端口释放
    if [ -n "$port" ] && check_port $port; then
        local pids=$(lsof -ti:$port)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null
        fi
    fi
}

stop_all() {
    print_info "停止所有服务..."
    
    stop_service "Frontend UI" "$PID_DIR/frontend.pid" 3000
    stop_service "Deep Agents Service" "$PID_DIR/agent.pid" 2025
    stop_service "MCP Server" "$PID_DIR/mcp.pid" 8001
    stop_service "LightRAG Server" "$PID_DIR/lightrag.pid" 9621
    
    print_success "所有服务已停止"
}

# =============================================================================
# 状态检查
# =============================================================================

show_status() {
    echo ""
    printf "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
    printf "${CYAN}                      服务状态概览                              ${NC}\n"
    printf "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
    echo ""
    
    local services=(
        "LightRAG Server:9621"
        "MCP Server:8001"
        "Deep Agents Service:2025"
        "Frontend UI:3000"
    )
    
    for service in "${services[@]}"; do
        local name="${service%%:*}"
        local port="${service##*:}"
        
        if check_port $port; then
            printf "  ${GREEN}●${NC} $name ${GREEN}运行中${NC} (端口: $port)\n"
        else
            printf "  ${RED}○${NC} $name ${RED}未运行${NC} (端口: $port)\n"
        fi
    done
    
    echo ""
    printf "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
    echo ""
}

# =============================================================================
# 主程序
# =============================================================================

main() {
    local include_frontend=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                include_frontend=true
                shift
                ;;
            --stop)
                stop_all
                exit 0
                ;;
            --status)
                show_status
                exit 0
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --all     启动所有服务（包含前端）"
                echo "  --stop    停止所有服务"
                echo "  --status  显示服务状态"
                echo "  --help    显示帮助信息"
                exit 0
                ;;
            *)
                print_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    print_banner
    
    # 检查 uv
    print_info "检查 uv..."
    check_uv
    print_success "uv 已安装"
    
    # 检查并创建虚拟环境
    print_info "检查虚拟环境..."
    check_venv
    print_success "虚拟环境就绪"
    
    echo ""
    printf "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
    printf "${CYAN}                      启动服务                                  ${NC}\n"
    printf "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
    echo ""
    
    # 按顺序启动服务
    start_lightrag
    echo ""
    
    start_mcp_server
    echo ""
    
    start_agent_service
    echo ""
    
    if [ "$include_frontend" = true ]; then
        start_frontend
        echo ""
    fi
    
    # 显示状态
    show_status
    
    printf "${GREEN}🎉 所有服务启动完成！${NC}\n"
    echo ""
    echo "常用命令:"
    printf "  查看状态: ${CYAN}$0 --status${NC}\n"
    printf "  停止服务: ${CYAN}$0 --stop${NC}\n"
    printf "  查看日志: ${CYAN}tail -f logs/*.log${NC}\n"
    echo ""
    echo "使用 uv run 运行其他命令:"
    printf "  ${CYAN}uv run python your_script.py${NC}\n"
    printf "  ${CYAN}uv run lightrag-server${NC}\n"
}

# 运行主程序
main "$@"
