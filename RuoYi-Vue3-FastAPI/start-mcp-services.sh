#!/usr/bin/env bash
# 启动所有 MCP 相关服务
# 包括：RAG MCP Server、MindMap MCP Server

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${ROOT}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
LOG_DIR="${RUNTIME_DIR}/logs"
mkdir -p "$PID_DIR" "$LOG_DIR"

# 服务端口配置
RAG_MCP_PORT="${RAG_MCP_PORT:-9002}"
MINDMAP_MCP_PORT="${MINDMAP_MCP_PORT:-9003}"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

die() { echo -e >&2 "${RED}ERROR: $*${NC}"; exit 1; }
info() { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
title() { echo -e "${BLUE}===${NC} $*"; }

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

stop_service() {
  local name="$1"
  if ! is_running "${name}"; then
    warn "${name} is not running"
    return 0
  fi
  
  local pid
  pid="$(cat "$(pidfile "$name")")"
  echo "Stopping ${name} (PID ${pid})..."
  kill "${pid}" 2>/dev/null || true
  
  # 等待进程退出
  local count=0
  while kill -0 "${pid}" 2>/dev/null && [ $count -lt 30 ]; do
    sleep 0.5
    count=$((count + 1))
  done
  
  if kill -0 "${pid}" 2>/dev/null; then
    warn "Force killing ${name}..."
    kill -9 "${pid}" 2>/dev/null || true
  fi
  
  rm -f "$(pidfile "$name")"
  info "${name} stopped"
}

# 检测 Python 路径（Windows 和 Unix 路径不同）
get_python_path() {
  local backend_dir="${ROOT}/ruoyi-fastapi-backend"
  local venv_dir="${backend_dir}/.venv"
  
  if [ -x "${venv_dir}/Scripts/python.exe" ]; then
    echo "${venv_dir}/Scripts/python.exe"
  elif [ -x "${venv_dir}/Scripts/python3.exe" ]; then
    echo "${venv_dir}/Scripts/python3.exe"
  elif [ -x "${venv_dir}/bin/python" ]; then
    echo "${venv_dir}/bin/python"
  elif [ -x "${venv_dir}/bin/python3" ]; then
    echo "${venv_dir}/bin/python3"
  elif command -v python3 &>/dev/null; then
    echo "python3"
  elif command -v python &>/dev/null; then
    echo "python"
  else
    die "Python 未找到，请先安装 Python 或创建虚拟环境"
  fi
}

# 1. 启动 RAG MCP Server
start_rag_mcp() {
  if is_running "rag-mcp"; then
    warn "RAG MCP Server 已经在运行"
    return 0
  fi
  
  title "Step 1/2: Starting RAG MCP Server"
  echo "Starting RAG MCP Server on port ${RAG_MCP_PORT}..."
  
  # 检查 RAG MCP Server 文件
  local rag_server_path="${ROOT}/ruoyi-fastapi-backend/mcp_servers/rag_mcp_server.py"
  if [ ! -f "${rag_server_path}" ]; then
    warn "RAG MCP Server 未找到: ${rag_server_path}"
    echo ""
    echo "  请确认文件路径是否正确"
    echo ""
    read -p "是否跳过 RAG MCP 并继续？ (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      die "用户取消"
    fi
    return 0
  fi
  
  # 获取 Python 路径
  local python_cmd=$(get_python_path)
  
  # 检查并安装必要的依赖
  echo "Checking dependencies for RAG MCP Server..."
  if ! "${python_cmd}" -c "import fastmcp" 2>/dev/null; then
    echo "Installing fastmcp..."
    "${python_cmd}" -m pip install fastmcp httpx pydantic || die "Failed to install fastmcp"
  fi
  
  # 设置环境变量
  export LIGHTRAG_BASE_URL="${LIGHTRAG_BASE_URL:-http://localhost:9621}"
  export LIGHTRAG_API_KEY="${LIGHTRAG_API_KEY:-}"
  export LIGHTRAG_TIMEOUT="${LIGHTRAG_TIMEOUT:-60.0}"
  
  # 启动服务
  cd "$(dirname "${rag_server_path}")"
  nohup "${python_cmd}" rag_mcp_server.py --port "${RAG_MCP_PORT}" --sse \
    > "$(logfile rag-mcp)" 2>&1 &
  
  local pid=$!
  write_pid "rag-mcp" "${pid}"
  cd "${ROOT}"
  
  # 等待服务就绪
  sleep 2
  if ! is_running "rag-mcp"; then
    warn "RAG MCP Server 启动失败，查看日志: $(logfile rag-mcp)"
    return 1
  fi
  
  info "RAG MCP Server started (PID ${pid}), listening on http://localhost:${RAG_MCP_PORT}"
  info "Logs: $(logfile rag-mcp)"
}

# 2. 启动 MindMap MCP Server
start_mindmap_mcp() {
  if is_running "mindmap-mcp"; then
    warn "MindMap MCP Server 已经在运行"
    return 0
  fi
  
  title "Step 2/2: Starting MindMap MCP Server"
  echo "Starting MindMap MCP Server on port ${MINDMAP_MCP_PORT}..."
  
  # 检查 MindMap MCP Server 文件
  local mindmap_server_path="${ROOT}/ruoyi-fastapi-backend/mcp_servers/mindmap_mcp_server.py"
  if [ ! -f "${mindmap_server_path}" ]; then
    die "MindMap MCP Server not found at: ${mindmap_server_path}"
  fi
  
  # 获取 Python 路径
  local python_cmd=$(get_python_path)
  
  # 检查并安装必要的依赖
  echo "Checking dependencies for MindMap MCP Server..."
  if ! "${python_cmd}" -c "import fastmcp" 2>/dev/null; then
    echo "Installing fastmcp..."
    "${python_cmd}" -m pip install fastmcp || die "Failed to install fastmcp"
  fi
  
  # 检查 Node.js (用于 markmap-cli)
  if ! command -v node &>/dev/null && ! command -v npx &>/dev/null; then
    warn "Node.js 未安装，思维导图生成功能可能受限"
    warn "请安装 Node.js: https://nodejs.org/"
  fi
  
  # 启动 MindMap MCP Server
  cd "$(dirname "${mindmap_server_path}")"
  nohup "${python_cmd}" mindmap_mcp_server.py --port "${MINDMAP_MCP_PORT}" --sse \
    > "$(logfile mindmap-mcp)" 2>&1 &
  
  local pid=$!
  write_pid "mindmap-mcp" "${pid}"
  cd "${ROOT}"
  
  # 等待服务就绪
  sleep 2
  if ! is_running "mindmap-mcp"; then
    warn "MindMap MCP Server 启动失败，查看日志: $(logfile mindmap-mcp)"
    return 1
  fi
  
  info "MindMap MCP Server started (PID ${pid}), listening on http://localhost:${MINDMAP_MCP_PORT}"
  info "Logs: $(logfile mindmap-mcp)"
}

# 启动所有服务
start_all() {
  echo ""
  echo "=========================================="
  echo "  Starting All MCP Services"
  echo "=========================================="
  echo ""
  
  start_rag_mcp || warn "RAG MCP 启动失败"
  echo ""
  
  start_mindmap_mcp || warn "MindMap MCP 启动失败"
  echo ""
  
  title "All MCP Services Started"
  status
}

# 停止所有服务
stop_all() {
  echo ""
  echo "Stopping all MCP services..."
  echo ""
  
  stop_service "mindmap-mcp"
  stop_service "rag-mcp"
  
  echo ""
  info "All MCP services stopped"
}

# 查看状态
status() {
  echo ""
  echo "=========================================="
  echo "  MCP Services Status"
  echo "=========================================="
  echo ""
  
  # RAG MCP
  if is_running "rag-mcp"; then
    local pid=$(cat "$(pidfile rag-mcp)")
    info "RAG MCP Server: Running (PID ${pid}) on http://localhost:${RAG_MCP_PORT}"
  else
    warn "RAG MCP Server: Not running"
  fi
  
  # MindMap MCP
  if is_running "mindmap-mcp"; then
    local pid=$(cat "$(pidfile mindmap-mcp)")
    info "MindMap MCP Server: Running (PID ${pid}) on http://localhost:${MINDMAP_MCP_PORT}"
  else
    warn "MindMap MCP Server: Not running"
  fi
  
  echo ""
}

# 查看日志
logs() {
  local name="${1:-}"
  
  if [ -z "${name}" ]; then
    echo "Available logs:"
    echo "  - rag-mcp"
    echo "  - mindmap-mcp"
    echo ""
    echo "Usage: $0 logs <service-name>"
    return 1
  fi
  
  if [ ! -f "$(logfile "${name}")" ]; then
    die "Log file not found: $(logfile "${name}")"
  fi
  
  tail -f "$(logfile "${name}")"
}

# 使用说明
usage() {
  cat <<EOF
启动所有 MCP 服务的脚本

Usage: $0 <command>

Commands:
  start         启动所有 MCP 服务（RAG MCP + MindMap MCP）
  stop          停止所有 MCP 服务
  restart       重启所有 MCP 服务
  status        查看所有服务状态
  logs [name]   查看服务日志 (rag-mcp|mindmap-mcp)
  
  start-rag          仅启动 RAG MCP Server
  start-mindmap      仅启动 MindMap MCP Server
  
  help          显示此帮助信息

Environment Variables:
  RAG_MCP_PORT       RAG MCP 端口 (默认: 9002)
  MINDMAP_MCP_PORT   MindMap MCP 端口 (默认: 9003)
  LIGHTRAG_BASE_URL  LightRAG 服务器地址 (默认: http://localhost:9621)
  LIGHTRAG_API_KEY   LightRAG API 密钥 (可选)
  LIGHTRAG_TIMEOUT   LightRAG 超时时间 (默认: 60.0)

Service Details:
  1. RAG MCP Server (9002)  - RAG 工具服务
  2. MindMap MCP (9003)     - 思维导图服务

Examples:
  # 启动所有 MCP 服务
  $0 start
  
  # 查看状态
  $0 status
  
  # 查看 RAG MCP 日志
  $0 logs rag-mcp
  
  # 使用自定义端口
  RAG_MCP_PORT=9004 $0 start-rag
  
  # 停止所有服务
  $0 stop

Notes:
  - RAG MCP Server 需要 LightRAG 服务运行在 9621 端口（可选）
  - MindMap MCP Server 需要 Node.js 和 npx（用于 markmap-cli）
  - 所有服务使用项目虚拟环境中的 Python
EOF
}

# 主命令处理
cmd="${1:-help}"
shift || true

case "${cmd}" in
  start)
    start_all
    ;;
  stop)
    stop_all
    ;;
  restart)
    stop_all
    sleep 2
    start_all
    ;;
  status)
    status
    ;;
  logs)
    logs "${1:-}"
    ;;
  start-rag)
    start_rag_mcp
    status
    ;;
  start-mindmap)
    start_mindmap_mcp
    status
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage
    die "Unknown command: ${cmd}"
    ;;
esac

