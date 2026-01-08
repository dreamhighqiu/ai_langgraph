#!/usr/bin/env bash
# MCP 服务启动脚本
# 用于启动 RAG MCP 和 MindMap MCP 服务

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${ROOT}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
LOG_DIR="${RUNTIME_DIR}/logs"
mkdir -p "$PID_DIR" "$LOG_DIR"

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
  
  # 启动服务
  cd "$(dirname "${rag_server_path}")"
  nohup python rag_mcp_server.py --port "${RAG_MCP_PORT}" --sse \
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
  warn "MindMap MCP Server requires manual setup"
  warn "Please see: ${ROOT}/QUICK_START.md for installation instructions"
  echo ""
  echo "  To install:"
  echo "    cd ${ROOT}"
  echo "    git clone https://github.com/MCP-Mirror/YuChenSSR_mindmap-mcp-server.git"
  echo "    cd YuChenSSR_mindmap-mcp-server"
  echo "    npm install"
  echo "    npm start -- --port ${MINDMAP_MCP_PORT}"
  echo ""
}

status() {
  echo ""
  echo "=== MCP Services Status ==="
  
  if is_running "rag-mcp"; then
    local pid
    pid="$(cat "$(pidfile rag-mcp")")"
    info "RAG MCP Server: Running (PID ${pid}) on http://localhost:${RAG_MCP_PORT}"
  else
    warn "RAG MCP Server: Not running"
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
  start-mindmap 显示 MindMap MCP 启动说明
  stop          停止所有 MCP 服务
  restart       重启所有 MCP 服务
  status        查看 MCP 服务状态
  logs [name]   查看服务日志 (rag-mcp)
  help          显示此帮助信息

Environment Variables:
  RAG_MCP_PORT      RAG MCP 端口 (默认: 9002)
  MINDMAP_MCP_PORT  MindMap MCP 端口 (默认: 8003)

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
    echo ""
    info "All MCP services stopped"
    ;;
  restart)
    stop_service "rag-mcp"
    sleep 1
    start_rag_mcp
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

