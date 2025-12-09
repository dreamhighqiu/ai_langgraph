#!/bin/bash
# =============================================================================
# AI LangGraph 环境初始化脚本
# 
# 功能: 使用 uv 创建统一虚拟环境并安装所有依赖
#
# 使用方法:
#   ./setup.sh              # 初始化环境
#   ./setup.sh --reinstall  # 重新安装（删除旧环境）
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

print_info() {
    printf "${BLUE}[INFO]${NC} $1\n"
}

print_success() {
    printf "${GREEN}[✓]${NC} $1\n"
}

print_warning() {
    printf "${YELLOW}[!]${NC} $1\n"
}

print_error() {
    printf "${RED}[✗]${NC} $1\n"
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
    print_success "uv 已安装 ($(uv --version))"
}

# 检查 Node.js
check_node() {
    if command -v node &> /dev/null; then
        local node_version=$(node --version)
        print_success "Node.js 版本: $node_version"
    else
        print_warning "Node.js 未安装（前端服务需要）"
    fi
}

# 清理旧环境
clean_env() {
    if [ "$1" = "--reinstall" ]; then
        print_info "删除旧的虚拟环境..."
        rm -rf .venv
        rm -f uv.lock
        print_success "旧环境已清理"
    fi
}

# 使用 uv sync 安装依赖
install_with_uv() {
    print_info "使用 uv 同步依赖（可能需要几分钟）..."
    
    # 使用 uv sync 安装主项目依赖
    print_info "同步主项目依赖..."
    uv sync --python 3.11
    
    # 安装 anything-chat-rag (可编辑模式)
    print_info "安装 LightRAG (anything-chat-rag)..."
    uv pip install -e "./anything-chat-rag[api]" --quiet
    
    # 配置 Python 路径
    print_info "配置 Python 路径..."
    local site_packages=$(.venv/bin/python -c "import site; print(site.getsitepackages()[0])")
    
    # 创建 .pth 文件以添加 src 目录到 Python 路径
    cat > "$site_packages/ai-langgraph.pth" << EOF
$PROJECT_ROOT/testing-deep-agents-service/src
$PROJECT_ROOT/mcp-server/src
$PROJECT_ROOT/anything-chat-rag
EOF
    
    print_success "所有依赖安装完成"
}

# 创建必要的目录
create_dirs() {
    mkdir -p logs
    mkdir -p .pids
    print_success "目录结构创建完成"
}

# 检查 .env 文件
check_env() {
    local missing_env=()
    
    if [ ! -f "anything-chat-rag/.env" ]; then
        missing_env+=("anything-chat-rag/.env")
    fi
    
    if [ ! -f "testing-deep-agents-service/.env" ]; then
        missing_env+=("testing-deep-agents-service/.env")
    fi
    
    if [ ${#missing_env[@]} -gt 0 ]; then
        print_warning "以下 .env 文件缺失，请创建并配置:"
        for env in "${missing_env[@]}"; do
            echo "  - $env"
        done
        echo ""
        echo "可以参考对应目录下的 .env.example 文件"
    else
        print_success ".env 文件检查通过"
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --reinstall  删除旧环境并重新安装"
    echo "  --help       显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 首次安装"
    echo "  $0 --reinstall  # 重新安装"
}

# 主程序
main() {
    # 解析参数
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
    esac
    
    printf "${CYAN}\n"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           🔧 AI LangGraph 环境初始化 (uv)                      ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    printf "${NC}\n"
    echo ""
    
    # 检查依赖
    print_info "检查系统依赖..."
    check_uv
    check_node
    echo ""
    
    # 清理旧环境（如果需要）
    clean_env "$1"
    
    # 使用 uv 安装
    install_with_uv
    echo ""
    
    # 创建目录
    create_dirs
    echo ""
    
    # 检查 .env
    check_env
    echo ""
    
    printf "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"
    printf "${GREEN}               🎉 环境初始化完成！                             ${NC}\n"
    printf "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"
    echo ""
    echo "虚拟环境位置: ${CYAN}$PROJECT_ROOT/.venv${NC}"
    echo ""
    echo "下一步:"
    printf "  1. 配置 .env 文件（如果还没配置）\n"
    printf "  2. 激活环境: ${CYAN}source .venv/bin/activate${NC}\n"
    printf "  3. 启动所有服务: ${CYAN}./start_all.sh${NC}\n"
    printf "  4. 启动包含前端: ${CYAN}./start_all.sh --all${NC}\n"
    echo ""
    echo "或者使用 uv run 直接运行命令（无需手动激活）:"
    printf "  ${CYAN}uv run python start_server.py${NC}\n"
    printf "  ${CYAN}uv run lightrag-server${NC}\n"
    echo ""
}

main "$@"
