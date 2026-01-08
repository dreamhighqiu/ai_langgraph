#!/usr/bin/env bash
# MCP 服务启动脚本
# 用于启动 RAG MCP 和 MindMap MCP 服务

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${ROOT}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
LOG_DIR="${RUNTIME_DIR}/logs"
mkdir -p "$PID_DIR" "$LOG_DIR"

VENV_DIR="${ROOT}/.venv"
# 检测 Python 路径（Windows 和 Unix 路径不同）
if [ -x "${VENV_DIR}/Scripts/python.exe" ]; then
  VENV_PY="${VENV_DIR}/Scripts/python.exe"
elif [ -x "${VENV_DIR}/Scripts/python3.exe" ]; then
  VENV_PY="${VENV_DIR}/Scripts/python3.exe"
elif [ -x "${VENV_DIR}/bin/python" ]; then
  VENV_PY="${VENV_DIR}/bin/python"
elif [ -x "${VENV_DIR}/bin/python3" ]; then
  VENV_PY="${VENV_DIR}/bin/python3"
else
  # 如果没有虚拟环境，使用系统 Python
  VENV_PY="python"
fi

# MCP 服务配置
RAG_MCP_PORT="${RAG_MCP_PORT:-9002}"
MINDMAP_MCP_PORT="${MINDMAP_MCP_PORT:-9003}"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

die() { echo -e >&2 "${RED}ERROR: $*${NC}"; exit 1; }
info() { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }

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

start_rag_mcp() {
  if is_running "rag-mcp"; then
    warn "RAG MCP Server is already running"
    return 0
  fi
  
  echo "Starting RAG MCP Server on port ${RAG_MCP_PORT}..."
  
  # 检查 RAG MCP Server 文件
  local rag_server_path="${ROOT}/../testing-agents-service/src/api_agent/mcp_servers/rag_mcp_server.py"
  if [ ! -f "${rag_server_path}" ]; then
    die "RAG MCP Server not found at: ${rag_server_path}"
  fi
  
  # 检查并安装必要的依赖（使用 uv）
  echo "Checking RAG MCP Server dependencies..."
  local missing_deps=()
  "${VENV_PY}" -c "import dotenv" 2>/dev/null || missing_deps+=("python-dotenv")
  "${VENV_PY}" -c "import fastmcp" 2>/dev/null || missing_deps+=("fastmcp")
  "${VENV_PY}" -c "import httpx" 2>/dev/null || missing_deps+=("httpx")
  "${VENV_PY}" -c "import pydantic" 2>/dev/null || missing_deps+=("pydantic")
  
  if [ ${#missing_deps[@]} -gt 0 ]; then
    warn "Missing dependencies for RAG MCP Server: ${missing_deps[*]}"
    echo "Installing required packages using uv..."
    
    # 检查是否有 uv
    if ! command -v uv >/dev/null 2>&1; then
      die "uv is required but not found. Please install uv first: https://github.com/astral-sh/uv"
    fi
    
    # 使用 uv pip install 安装依赖
    (cd "${ROOT}" && uv pip install "${missing_deps[@]}" --quiet) || {
      warn "Failed to install some dependencies. Trying to continue..."
    }
  fi
  
  # 启动服务（使用项目虚拟环境的 Python）
  cd "$(dirname "${rag_server_path}")"
  export PYTHONPATH="${ROOT}/backend:${PYTHONPATH:-}"
  nohup "${VENV_PY}" rag_mcp_server.py --port "${RAG_MCP_PORT}" --sse \
    > "$(logfile rag-mcp)" 2>&1 &
  
  local pid=$!
  write_pid "rag-mcp" "${pid}"
  
  # 等待服务就绪
  sleep 2
  if ! is_running "rag-mcp"; then
    die "RAG MCP Server failed to start. Check logs at: $(logfile rag-mcp)"
  fi
  
  info "RAG MCP Server started (PID ${pid}), listening on http://localhost:${RAG_MCP_PORT}"
  info "Logs: $(logfile rag-mcp)"
}

start_mindmap_mcp() {
  if is_running "mindmap-mcp"; then
    warn "MindMap MCP Server is already running"
    return 0
  fi
  
  echo "Starting MindMap MCP Server on port ${MINDMAP_MCP_PORT}..."
  
  # 检查 MindMap MCP Server 文件
  local mindmap_server_path="${ROOT}/backend/app/mcp_servers/mindmap_mcp_server.py"
  if [ ! -f "${mindmap_server_path}" ]; then
    die "MindMap MCP Server not found at: ${mindmap_server_path}"
  fi
  
  # 检查并安装必要的依赖
  echo "Checking dependencies for MindMap MCP Server..."
  if ! "${VENV_PY}" -c "import fastmcp" 2>/dev/null; then
    echo "Installing fastmcp..."
    # 尝试使用 uv，如果失败则使用 pip
    if "${VENV_PY}" -m uv pip install fastmcp 2>/dev/null; then
      echo "Installed fastmcp using uv"
    elif "${VENV_PY}" -m pip install fastmcp 2>/dev/null; then
      echo "Installed fastmcp using pip"
    else
      die "Failed to install fastmcp"
    fi
  fi
  
  # markmap 是可选的，使用 subprocess 方法（npx markmap-cli）
  # 不需要安装 Python 的 markmap 包
  
  # 启动 MindMap MCP Server
  nohup "${VENV_PY}" "${mindmap_server_path}" --port "${MINDMAP_MCP_PORT}" --sse >"$(logfile mindmap-mcp)" 2>&1 &
  local pid=$!
  
  # 等待进程启动
  sleep 1
  if ! kill -0 "${pid}" 2>/dev/null; then
    die "MindMap MCP Server failed to start. Check logs at: $(logfile mindmap-mcp)"
  fi
  
  write_pid "mindmap-mcp" "${pid}"
  
  # 等待服务就绪
  sleep 2
  if ! is_running "mindmap-mcp"; then
    die "MindMap MCP Server failed to start. Check logs at: $(logfile mindmap-mcp)"
  fi
  
  info "MindMap MCP Server started (PID ${pid}), listening on http://localhost:${MINDMAP_MCP_PORT}"
  info "Logs: $(logfile mindmap-mcp)"
}

status() {
  echo ""
  echo "=== MCP Services Status ==="
  
  if is_running "rag-mcp"; then
    local pid
    pid="$(cat "$(pidfile rag-mcp)")"
    info "RAG MCP Server: Running (PID ${pid}) on http://localhost:${RAG_MCP_PORT}"
  else
    warn "RAG MCP Server: Not running"
  fi
  
  if is_running "mindmap-mcp"; then
    local pid
    pid="$(cat "$(pidfile mindmap-mcp)")"
    info "MindMap MCP Server: Running (PID ${pid}) on http://localhost:${MINDMAP_MCP_PORT}"
  else
    warn "MindMap MCP Server: Not running"
  fi
  
  echo ""
}

usage() {
  cat <<EOF
MCP 服务管理脚本

Usage: $0 <command>

Commands:
  start         启动所有 MCP 服务
  start-rag     仅启动 RAG MCP 服务
  start-mindmap 仅启动 MindMap MCP 服务
  stop          停止所有 MCP 服务
  restart       重启所有 MCP 服务
  status        查看 MCP 服务状态
  logs [name]   查看服务日志 (rag-mcp, mindmap-mcp)
  help          显示此帮助信息

Environment Variables:
  RAG_MCP_PORT      RAG MCP 端口 (默认: 9002)
  MINDMAP_MCP_PORT  MindMap MCP 端口 (默认: 9003)

Examples:
  # 启动 RAG MCP 服务
  $0 start-rag
  
  # 使用自定义端口
  RAG_MCP_PORT=9003 $0 start-rag
  
  # 查看状态
  $0 status
  
  # 查看日志
  $0 logs rag-mcp
EOF
}

cmd="${1:-help}"
shift || true

case "${cmd}" in
  start)
    start_rag_mcp
    start_mindmap_mcp
    status
    ;;
  start-rag)
    start_rag_mcp
    status
    ;;
  start-mindmap)
    start_mindmap_mcp
    ;;
  stop)
    stop_service "rag-mcp"
    stop_service "mindmap-mcp"
    echo ""
    info "All MCP services stopped"
    ;;
  restart)
    stop_service "rag-mcp"
    stop_service "mindmap-mcp"
    sleep 1
    start_rag_mcp
    start_mindmap_mcp
    status
    ;;
  status)
    status
    ;;
  logs)
    name="${1:-rag-mcp}"
    if [ ! -f "$(logfile "${name}")" ]; then
      die "Log file not found: $(logfile "${name}")"
    fi
    tail -f "$(logfile "${name}")"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage
    die "Unknown command: ${cmd}"
    ;;
esac

