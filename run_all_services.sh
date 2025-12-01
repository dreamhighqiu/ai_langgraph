#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="/Users/qiuyunxia/code/ai_langGraph"
MCP_ENV="$ROOT/.venv/bin/activate"
MCP_SRC="$ROOT/mcp-server/src"
AGENT_DIR="$ROOT/agent-service"
LIGHTRAG_ENV="$ROOT/anything-chat-rag/.venv/bin/activate"
UI_DIR="$ROOT/testing-agent-chat-ui"
export PYTHONPATH="$ROOT/mcp-server/src:$ROOT/anything-chat-rag${PYTHONPATH:+:$PYTHONPATH}"

pids=()

log() {
  printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"
}

ensure_port_free() {
  local port="$1"
  local pids
  pids=$(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    log "检测到端口 $port 已被进程: $pids 占用，尝试终止..."
    for pid in $pids; do
      if kill "$pid" 2>/dev/null; then
        sleep 1
      fi
      if lsof -ti tcp:"$port" -sTCP:LISTEN | grep -q "$pid" 2>/dev/null; then
        log "发送 SIGKILL 给 PID $pid"
        kill -9 "$pid" 2>/dev/null || true
      fi
    done
    sleep 1
    if lsof -ti tcp:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      log "端口 $port 仍被占用，请手动释放后再运行该脚本。"
      exit 1
    fi
    log "端口 $port 已释放，继续启动服务。"
  fi
}

wait_for_port() {
  local port="$1"
  local retries="${2:-30}"
  local delay="${3:-1}"
  for ((i=1; i<=retries; i++)); do
    if lsof -ti tcp:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      log "端口 $port 已就绪"
      return 0
    fi
    sleep "$delay"
  done
  log "等待端口 $port 超时，请检查对应服务是否启动成功"
  exit 1
}

ensure_path() {
  if [[ ! -e "$1" ]]; then
    log "路径不存在: $1"
    exit 1
  fi
}

start_process() {
  local name="$1"
  shift
  log "启动 $name ..."
  (
    "$@"
  ) &
  local pid=$!
  pids+=("$pid")
  log "$name 已启动 (PID=$pid)"
}

start_mcp_server() {
  (
    source "$MCP_ENV"
    cd "$MCP_SRC"
    python -m mcp_server_rag_anything.server
  )
}

start_agent_service() {
  (
    source "$MCP_ENV"
    cd "$AGENT_DIR"
    python start_server.py
  )
}

start_lightrag_server() {
  (
    source "$LIGHTRAG_ENV"
    lightrag-server
  )
}

start_testing_ui() {
  (
    source "$MCP_ENV"
    cd "$UI_DIR"
    npm run dev
  )
}

cleanup() {
  log '停止所有服务...'
  for pid in "${pids[@]}"; do
    if kill "$pid" 2>/dev/null; then
      log "已发送终止信号: PID $pid"
    fi
  done
  wait 2>/dev/null || true
  exit 0
}

trap cleanup SIGINT SIGTERM

ensure_path "$MCP_ENV"
ensure_path "$MCP_SRC"
ensure_path "$AGENT_DIR/start_server.py"
ensure_path "$LIGHTRAG_ENV"
ensure_path "$UI_DIR"

for port in 8001 9621 3000 5173; do
  ensure_port_free "$port"
done

start_process 'MCP Server (python -m mcp_server_rag_anything.server)' start_mcp_server
wait_for_port 8001
start_process 'Agent Service (python start_server.py)' start_agent_service
start_process 'LightRAG Server' start_lightrag_server
wait_for_port 9621
start_process 'Testing Agent Chat UI (npm run dev)' start_testing_ui

log '所有服务已启动，按 Ctrl+C 停止'
wait
