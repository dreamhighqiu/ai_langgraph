#!/usr/bin/env bash
# 启动所有 MCP 相关服务
# 包括：LightRAG、RAG MCP Server、MindMap MCP Server

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${ROOT}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
LOG_DIR="${RUNTIME_DIR}/logs"
mkdir -p "$PID_DIR" "$LOG_DIR"

# 服务端口配置
LIGHTRAG_PORT="${LIGHTRAG_PORT:-9621}"
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

# 1. 启动 LightRAG 服务
start_lightrag() {
  if is_running "lightrag"; then
    warn "LightRAG 服务已经在运行"
    return 0
  fi
  
  title "Step 1/3: Starting LightRAG Service"
  echo "Starting LightRAG on port ${LIGHTRAG_PORT}..."
  
  # 检查 LightRAG 安装
  if ! command -v lightrag >/dev/null 2>&1 && ! [ -f "${ROOT}/../lightrag/server.py" ]; then
    warn "LightRAG 未安装或未找到"
    echo ""
    echo "  请先安装 LightRAG："
    echo "    pip install lightrag"
    echo ""
    echo "  或者从源码启动："
    echo "    cd ../lightrag && python server.py --port ${LIGHTRAG_PORT}"
    echo ""
    read -p "是否跳过 LightRAG 并继续？ (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      die "用户取消"
    fi
    return 0
  fi
  
  # 尝试启动 LightRAG
  if command -v lightrag >/dev/null 2>&1; then
    # 使用命令行工具启动
    nohup lightrag serve --port "${LIGHTRAG_PORT}" \
      > "$(logfile lightrag)" 2>&1 &
    local pid=$!
    write_pid "lightrag" "${pid}"
  elif [ -f "${ROOT}/../lightrag/server.py" ]; then
    # 从源码启动
    cd "${ROOT}/../lightrag"
    nohup python server.py --port "${LIGHTRAG_PORT}" \
      > "$(logfile lightrag)" 2>&1 &
    local pid=$!
    write_pid "lightrag" "${pid}"
    cd "${ROOT}"
  fi
  
  # 等待服务就绪
  sleep 3
  if ! is_running "lightrag"; then
    warn "LightRAG 启动失败，查看日志: $(logfile lightrag)"
    return 1
  fi
  
  info "LightRAG started (PID $(cat "$(pidfile lightrag)")), listening on http://localhost:${LIGHTRAG_PORT}"
  info "Logs: $(logfile lightrag)"
}

# 2. 启动 RAG MCP Server
start_rag_mcp() {
  if is_running "rag-mcp"; then
    warn "RAG MCP Server 已经在运行"
    return 0
  fi
  
  title "Step 2/3: Starting RAG MCP Server"
  echo "Starting RAG MCP Server on port ${RAG_MCP_PORT}..."
  
  # 检查 RAG MCP Server 文件
  local rag_server_path="${ROOT}/../testing-agents-service/src/api_agent/mcp_servers/rag_mcp_server.py"
  if [ ! -f "${rag_server_path}" ]; then
    warn "RAG MCP Server 未找到: ${rag_server_path}"
    echo ""
    echo "  请确认文件路径或从项目中获取该文件"
    echo ""
    read -p "是否跳过 RAG MCP 并继续？ (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      die "用户取消"
    fi
    return 0
  fi
  
  # 启动服务
  cd "$(dirname "${rag_server_path}")"
  nohup python rag_mcp_server.py --port "${RAG_MCP_PORT}" --sse \
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

# 3. 启动 MindMap MCP Server
start_mindmap_mcp() {
  if is_running "mindmap-mcp"; then
    warn "MindMap MCP Server 已经在运行"
    return 0
  fi
  
  title "Step 3/3: Starting MindMap MCP Server"
  echo "Starting MindMap MCP Server on port ${MINDMAP_MCP_PORT}..."
  
  # 检查 MindMap MCP Server 文件
  local mindmap_server_path="${ROOT}/backend/app/mcp_servers/mindmap_mcp_server.py"
  if [ ! -f "${mindmap_server_path}" ]; then
    die "MindMap MCP Server not found at: ${mindmap_server_path}"
  fi
  
  # 检测 Python 路径（Windows 和 Unix 路径不同）
  VENV_DIR="${ROOT}/.venv"
  if [ -x "${VENV_DIR}/Scripts/python.exe" ]; then
    VENV_PY="${VENV_DIR}/Scripts/python.exe"
  elif [ -x "${VENV_DIR}/Scripts/python3.exe" ]; then
    VENV_PY="${VENV_DIR}/Scripts/python3.exe"
  elif [ -x "${VENV_DIR}/bin/python" ]; then
    VENV_PY="${VENV_DIR}/bin/python"
  elif [ -x "${VENV_DIR}/bin/python3" ]; then
    VENV_PY="${VENV_DIR}/bin/python3"
  else
    VENV_PY="python"
  fi
  
  # 检查并安装必要的依赖
  echo "Checking dependencies for MindMap MCP Server..."
  if ! "${VENV_PY}" -c "import fastmcp" 2>/dev/null; then
    echo "Installing fastmcp..."
    "${VENV_PY}" -m uv pip install fastmcp || die "Failed to install fastmcp"
  fi
  
  # 启动 MindMap MCP Server
  nohup "${VENV_PY}" "${mindmap_server_path}" --port "${MINDMAP_MCP_PORT}" --sse \
    > "$(logfile mindmap-mcp)" 2>&1 &
  
  local pid=$!
  write_pid "mindmap-mcp" "${pid}"
  
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
  
  start_lightrag || warn "LightRAG 启动失败"
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
  stop_service "lightrag"
  
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
  
  # LightRAG
  if is_running "lightrag"; then
    local pid=$(cat "$(pidfile lightrag)")
    info "LightRAG: Running (PID ${pid}) on http://localhost:${LIGHTRAG_PORT}"
  else
    warn "LightRAG: Not running"
  fi
  
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
    echo "  - lightrag"
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
  start         启动所有 MCP 服务（LightRAG + RAG MCP + MindMap MCP）
  stop          停止所有 MCP 服务
  restart       重启所有 MCP 服务
  status        查看所有服务状态
  logs [name]   查看服务日志 (lightrag|rag-mcp|mindmap-mcp)
  
  start-lightrag     仅启动 LightRAG
  start-rag          仅启动 RAG MCP Server
  start-mindmap      仅启动 MindMap MCP Server
  
  help          显示此帮助信息

Environment Variables:
  LIGHTRAG_PORT      LightRAG 端口 (默认: 9621)
  RAG_MCP_PORT       RAG MCP 端口 (默认: 9002)
  MINDMAP_MCP_PORT   MindMap MCP 端口 (默认: 9003)

Service Details:
  1. LightRAG (9621)        - 基础 RAG 服务
  2. RAG MCP Server (9002)  - RAG 工具服务
  3. MindMap MCP (9003)     - 思维导图服务

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
  - LightRAG 需要先安装: pip install lightrag
  - RAG MCP Server 需要 testing-agents-service 项目
  - MindMap MCP Server 会自动从 GitHub 克隆安装
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
  start-lightrag)
    start_lightrag
    status
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

