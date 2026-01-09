#!/bin/bash
# ================================
# AI智能测试平台 - LangGraph & MCP 服务部署脚本
# 
# 用于启动/管理 LangGraph API 和 MCP 服务
# 
# 服务端口:
#   - LangGraph API: 2027 (智能体服务)
#   - RAG MCP: 9002 (知识库检索)
#   - MindMap MCP: 9003 (思维导图生成)
# ================================

set -e

# 配置变量
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${ROOT}/ruoyi-fastapi-backend"
RUNTIME_DIR="${ROOT}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
LOG_DIR="${RUNTIME_DIR}/logs"
VENV_DIR="${BACKEND_DIR}/.venv"

# 端口配置
LANGGRAPH_PORT="${LANGGRAPH_PORT:-2027}"
RAG_MCP_PORT="${RAG_MCP_PORT:-9002}"
MINDMAP_MCP_PORT="${MINDMAP_MCP_PORT:-9003}"

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

# 创建目录
mkdir -p "$PID_DIR" "$LOG_DIR"

# 显示帮助
show_help() {
    echo "
AI智能测试平台 - LangGraph & MCP 服务管理脚本

========================================
服务说明:
  - LangGraph API (端口 $LANGGRAPH_PORT): 智能体服务，提供测试用例生成、需求分析等 AI 功能
  - RAG MCP (端口 $RAG_MCP_PORT): 知识库检索服务
  - MindMap MCP (端口 $MINDMAP_MCP_PORT): 思维导图生成服务
========================================

用法: ./deploy-langgraph.sh [命令]

命令:
  start         启动所有 AI 服务 (LangGraph + MCP)
  stop          停止所有 AI 服务
  restart       重启所有 AI 服务
  status        查看服务状态
  
  langgraph     仅启动 LangGraph API 服务
  mcp           仅启动 MCP 服务 (RAG + MindMap)
  rag           仅启动 RAG MCP 服务
  mindmap       仅启动 MindMap MCP 服务
  
  logs [name]   查看服务日志 (langgraph, rag-mcp, mindmap-mcp)
  install       安装依赖
  help          显示帮助

环境变量:
  LANGGRAPH_PORT      LangGraph API 端口 (默认: 2027)
  RAG_MCP_PORT        RAG MCP 端口 (默认: 9002)
  MINDMAP_MCP_PORT    MindMap MCP 端口 (默认: 9003)

示例:
  ./deploy-langgraph.sh start           # 启动所有 AI 服务
  ./deploy-langgraph.sh langgraph       # 仅启动 LangGraph
  ./deploy-langgraph.sh logs langgraph  # 查看 LangGraph 日志
"
}

# 检测 Python 路径
get_python() {
    if [ -x "${VENV_DIR}/Scripts/python.exe" ]; then
        echo "${VENV_DIR}/Scripts/python.exe"
    elif [ -x "${VENV_DIR}/Scripts/python3.exe" ]; then
        echo "${VENV_DIR}/Scripts/python3.exe"
    elif [ -x "${VENV_DIR}/bin/python" ]; then
        echo "${VENV_DIR}/bin/python"
    elif [ -x "${VENV_DIR}/bin/python3" ]; then
        echo "${VENV_DIR}/bin/python3"
    else
        echo "python"
    fi
}

pidfile() { echo "${PID_DIR}/$1.pid"; }
logfile() { echo "${LOG_DIR}/$1.log"; }

is_running() {
    local name="$1"
    local pid
    pid="$(cat "$(pidfile "$name")" 2>/dev/null || true)"
    [ -n "${pid}" ] && kill -0 "${pid}" 2>/dev/null
}

write_pid() {
    local name="$1"
    local pid="$2"
    echo "${pid}" >"$(pidfile "$name")"
}

# 停止服务
stop_service() {
    local name="$1"
    if ! is_running "${name}"; then
        print_warning "${name} 未运行"
        return 0
    fi
    
    local pid
    pid="$(cat "$(pidfile "$name")")"
    print_info "停止 ${name} (PID ${pid})..."
    kill "${pid}" 2>/dev/null || true
    
    # 等待进程退出
    local count=0
    while kill -0 "${pid}" 2>/dev/null && [ $count -lt 30 ]; do
        sleep 0.5
        count=$((count + 1))
    done
    
    if kill -0 "${pid}" 2>/dev/null; then
        print_warning "强制终止 ${name}..."
        kill -9 "${pid}" 2>/dev/null || true
    fi
    
    rm -f "$(pidfile "$name")"
    print_success "${name} 已停止"
}

# 安装依赖
install_deps() {
    print_info "安装 LangGraph 和 MCP 依赖..."
    
    cd "${BACKEND_DIR}"
    
    # 检查 uv
    if ! command -v uv &> /dev/null; then
        print_error "uv 未安装，请先运行: ./deploy-local.sh init"
        exit 1
    fi
    
    # 安装 LangGraph 相关依赖
    print_info "安装 LangGraph 依赖..."
    uv pip install langgraph langgraph-cli[inmem] langgraph-sdk langchain-openai langchain-anthropic
    
    # 安装 MCP 相关依赖
    print_info "安装 MCP 依赖..."
    uv pip install fastmcp httpx pydantic python-dotenv
    
    print_success "依赖安装完成"
    
    cd "${ROOT}"
}

# 启动 LangGraph API
start_langgraph() {
    if is_running langgraph; then
        print_warning "LangGraph API 已在运行 (PID $(cat "$(pidfile langgraph)"))"
        return 0
    fi
    
    print_info "启动 LangGraph API 服务 (端口: ${LANGGRAPH_PORT})..."
    
    local VENV_PY=$(get_python)
    
    # 检查虚拟环境
    if [ ! -x "${VENV_PY}" ] || [ "${VENV_PY}" = "python" ]; then
        print_error "虚拟环境未创建，请先运行: ./deploy-local.sh init"
        return 1
    fi
    
    # 检查 langgraph 是否安装
    if ! "${VENV_PY}" -c "import langgraph" 2>/dev/null; then
        print_warning "langgraph 未安装，正在安装..."
        (cd "${BACKEND_DIR}" && uv pip install langgraph langgraph-cli[inmem] langgraph-sdk)
    fi
    
    cd "${BACKEND_DIR}"
    
    # 设置环境变量
    export APP_ENV=dev
    export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH:-}"
    export LANGGRAPH_API_URL="http://localhost:${LANGGRAPH_PORT}"
    
    # 启动 LangGraph API
    print_info "启动 LangGraph API (uvicorn --reload)..."
    nohup "${VENV_PY}" -m langgraph_api.server \
        --host 0.0.0.0 \
        --port ${LANGGRAPH_PORT} \
        --config langgraph.json \
        > "$(logfile langgraph)" 2>&1 &
    
    local pid=$!
    write_pid "langgraph" "${pid}"
    
    # 等待服务就绪
    sleep 3
    
    if is_running langgraph; then
        # 检查端口
        sleep 2
        if nc -z localhost ${LANGGRAPH_PORT} 2>/dev/null || timeout 1 bash -c "echo >/dev/tcp/localhost/${LANGGRAPH_PORT}" 2>/dev/null; then
            print_success "LangGraph API 启动成功 ✅"
            echo "  🌐 地址: http://localhost:${LANGGRAPH_PORT}"
            echo "  📚 文档: http://localhost:${LANGGRAPH_PORT}/docs"
            echo "  🔧 PID:  ${pid}"
            echo "  📝 日志: $(logfile langgraph)"
        else
            print_warning "进程已启动但端口未监听，请查看日志"
            tail -20 "$(logfile langgraph)" 2>/dev/null
        fi
    else
        print_error "LangGraph API 启动失败，请查看日志"
        tail -30 "$(logfile langgraph)" 2>/dev/null
        rm -f "$(pidfile langgraph)"
    fi
    
    cd "${ROOT}"
}

# 启动 RAG MCP
start_rag_mcp() {
    if is_running rag-mcp; then
        print_warning "RAG MCP 已在运行 (PID $(cat "$(pidfile rag-mcp)"))"
        return 0
    fi
    
    print_info "启动 RAG MCP 服务 (端口: ${RAG_MCP_PORT})..."
    
    local VENV_PY=$(get_python)
    
    # 检查 MCP Server 文件
    local rag_server_path="${BACKEND_DIR}/module_testing/mcp_servers/rag_mcp_server.py"
    if [ ! -f "${rag_server_path}" ]; then
        print_warning "RAG MCP Server 文件不存在: ${rag_server_path}"
        print_info "跳过 RAG MCP 服务启动"
        return 0
    fi
    
    # 检查依赖
    if ! "${VENV_PY}" -c "import fastmcp" 2>/dev/null; then
        print_warning "fastmcp 未安装，正在安装..."
        (cd "${BACKEND_DIR}" && uv pip install fastmcp httpx pydantic python-dotenv)
    fi
    
    cd "$(dirname "${rag_server_path}")"
    
    export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH:-}"
    
    nohup "${VENV_PY}" rag_mcp_server.py --port "${RAG_MCP_PORT}" --sse \
        > "$(logfile rag-mcp)" 2>&1 &
    
    local pid=$!
    write_pid "rag-mcp" "${pid}"
    
    sleep 2
    
    if is_running rag-mcp; then
        print_success "RAG MCP 启动成功 (PID ${pid})"
        echo "  🌐 地址: http://localhost:${RAG_MCP_PORT}"
        echo "  📝 日志: $(logfile rag-mcp)"
    else
        print_error "RAG MCP 启动失败，请查看日志"
        tail -20 "$(logfile rag-mcp)" 2>/dev/null
        rm -f "$(pidfile rag-mcp)"
    fi
    
    cd "${ROOT}"
}

# 启动 MindMap MCP
start_mindmap_mcp() {
    if is_running mindmap-mcp; then
        print_warning "MindMap MCP 已在运行 (PID $(cat "$(pidfile mindmap-mcp)"))"
        return 0
    fi
    
    print_info "启动 MindMap MCP 服务 (端口: ${MINDMAP_MCP_PORT})..."
    
    local VENV_PY=$(get_python)
    
    # 检查 MCP Server 文件
    local mindmap_server_path="${BACKEND_DIR}/module_testing/mcp_servers/mindmap_mcp_server.py"
    if [ ! -f "${mindmap_server_path}" ]; then
        print_warning "MindMap MCP Server 文件不存在: ${mindmap_server_path}"
        print_info "跳过 MindMap MCP 服务启动"
        return 0
    fi
    
    # 检查依赖
    if ! "${VENV_PY}" -c "import fastmcp" 2>/dev/null; then
        print_warning "fastmcp 未安装，正在安装..."
        (cd "${BACKEND_DIR}" && uv pip install fastmcp)
    fi
    
    cd "$(dirname "${mindmap_server_path}")"
    
    export PYTHONPATH="${BACKEND_DIR}:${PYTHONPATH:-}"
    
    nohup "${VENV_PY}" mindmap_mcp_server.py --port "${MINDMAP_MCP_PORT}" --sse \
        > "$(logfile mindmap-mcp)" 2>&1 &
    
    local pid=$!
    write_pid "mindmap-mcp" "${pid}"
    
    sleep 2
    
    if is_running mindmap-mcp; then
        print_success "MindMap MCP 启动成功 (PID ${pid})"
        echo "  🌐 地址: http://localhost:${MINDMAP_MCP_PORT}"
        echo "  📝 日志: $(logfile mindmap-mcp)"
    else
        print_error "MindMap MCP 启动失败，请查看日志"
        tail -20 "$(logfile mindmap-mcp)" 2>/dev/null
        rm -f "$(pidfile mindmap-mcp)"
    fi
    
    cd "${ROOT}"
}

# 启动所有 MCP 服务
start_mcp() {
    print_info "启动 MCP 服务..."
    echo ""
    start_rag_mcp
    echo ""
    start_mindmap_mcp
}

# 启动所有服务
start_all() {
    print_info "启动所有 AI 服务..."
    echo ""
    
    start_langgraph
    echo ""
    start_mcp
    
    echo ""
    echo "========================================"
    print_success "🚀 AI 服务启动完成！"
    echo "========================================"
    show_status
}

# 停止所有服务
stop_all() {
    print_info "停止所有 AI 服务..."
    echo ""
    
    stop_service "langgraph"
    stop_service "rag-mcp"
    stop_service "mindmap-mcp"
    
    echo ""
    print_success "所有 AI 服务已停止"
}

# 重启所有服务
restart_all() {
    print_info "重启所有 AI 服务..."
    echo ""
    
    stop_all
    sleep 2
    start_all
}

# 查看状态
show_status() {
    echo ""
    echo "========== AI 服务状态 =========="
    echo ""
    
    if is_running langgraph; then
        local pid=$(cat "$(pidfile langgraph)")
        print_success "LangGraph API: 运行中 (PID: $pid)"
        echo "  🌐 http://localhost:${LANGGRAPH_PORT}"
    else
        print_warning "LangGraph API: 未运行"
    fi
    
    if is_running rag-mcp; then
        local pid=$(cat "$(pidfile rag-mcp)")
        print_success "RAG MCP: 运行中 (PID: $pid)"
        echo "  🌐 http://localhost:${RAG_MCP_PORT}"
    else
        print_warning "RAG MCP: 未运行"
    fi
    
    if is_running mindmap-mcp; then
        local pid=$(cat "$(pidfile mindmap-mcp)")
        print_success "MindMap MCP: 运行中 (PID: $pid)"
        echo "  🌐 http://localhost:${MINDMAP_MCP_PORT}"
    else
        print_warning "MindMap MCP: 未运行"
    fi
    
    echo ""
}

# 查看日志
show_logs() {
    local name="${1:-langgraph}"
    local log_file="$(logfile "$name")"
    
    if [ ! -f "$log_file" ]; then
        print_error "日志文件不存在: $log_file"
        exit 1
    fi
    
    print_info "查看 ${name} 日志 (Ctrl+C 退出)..."
    tail -f "$log_file"
}

# 主函数
case "${1:-help}" in
    start) start_all ;;
    stop) stop_all ;;
    restart) restart_all ;;
    status) show_status ;;
    langgraph) start_langgraph ;;
    mcp) start_mcp ;;
    rag) start_rag_mcp ;;
    mindmap) start_mindmap_mcp ;;
    install) install_deps ;;
    logs)
        shift
        show_logs "${1:-langgraph}"
        ;;
    *) show_help ;;
esac

