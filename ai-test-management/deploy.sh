#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${ROOT}/.runtime"
PID_DIR="${RUNTIME_DIR}/pids"
LOG_DIR="${RUNTIME_DIR}/logs"
mkdir -p "$PID_DIR" "$LOG_DIR"

VENV_DIR="${ROOT}/.venv"
# VENV_PY 将在 ensure_python_env() 中根据实际路径设置
VENV_PY="${VENV_DIR}/bin/python"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8080}"
GRAPH_HOST="${GRAPH_HOST:-0.0.0.0}"
GRAPH_PORT="${GRAPH_PORT:-2026}"
UI_HOST="${UI_HOST:-0.0.0.0}"
UI_PORT="${UI_PORT:-3000}"

die() { echo >&2 "ERROR: $*"; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"; }

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

ensure_env_files() {
  if [ ! -f "${ROOT}/backend/.env" ] && [ -f "${ROOT}/backend/.env.example" ]; then
    cp "${ROOT}/backend/.env.example" "${ROOT}/backend/.env"
  fi

  if [ ! -f "${ROOT}/.env" ] && [ -f "${ROOT}/backend/.env" ]; then
    ln -s "backend/.env" "${ROOT}/.env" 2>/dev/null || cp "${ROOT}/backend/.env" "${ROOT}/.env"
  fi
}

ensure_python_env() {
  need uv
  
  # 检查是否有服务正在运行（Windows 上更新依赖时需要停止服务以避免文件锁定）
  local running_services=()
  # 检查主服务
  for name in graph backend ui; do
    if is_running "${name}"; then
      running_services+=("${name}")
    fi
  done
  
  # 检查 MCP 服务（如果存在 PID 文件）
  for name in rag-mcp mindmap-mcp; do
    if is_running "${name}"; then
      running_services+=("${name}")
    fi
  done
  
  if [ ${#running_services[@]} -gt 0 ]; then
    echo "⚠️  Warning: The following services are running: ${running_services[*]}"
    echo "   Stopping them to avoid file locking issues during dependency update..."
    for name in "${running_services[@]}"; do
      stop_service "${name}"
    done
    sleep 2  # 等待进程完全退出
  fi
  
  echo "Installing/updating Python dependencies..."
  # 使用 --reinstall 选项来修复可能损坏的包元数据（Windows 上常见问题）
  # 这会强制重新安装所有包，但可以解决 "missing RECORD file" 等警告
  if [ "${UV_REINSTALL:-0}" = "1" ] || [ -n "${UV_FORCE_REINSTALL:-}" ]; then
    echo "  Using --reinstall to fix corrupted package metadata..."
    (cd "${ROOT}" && uv sync --reinstall)
  else
    # 正常同步，捕获输出以检查是否有错误
    local sync_output
    sync_output=$(cd "${ROOT}" && uv sync 2>&1)
    local sync_exit_code=$?
    
    # 检查输出中是否包含各种错误模式
    local needs_reinstall=false
    
    # 检查文件锁定错误
    if echo "${sync_output}" | grep -qiE "(拒绝访问|access denied|failed to remove.*os error 5)"; then
      needs_reinstall=true
      echo ""
      echo "⚠️  Warning: File locking detected, stopping all services and retrying..."
      # 再次检查并停止所有可能运行的服务
      for name in graph backend ui rag-mcp mindmap-mcp; do
        if is_running "${name}"; then
          stop_service "${name}"
        fi
      done
      sleep 3  # 等待文件完全释放
    # 检查元数据损坏错误
    elif echo "${sync_output}" | grep -qiE "(Failed to read.*metadata|failed to open file.*METADATA|系统找不到指定的文件|os error 2)"; then
      needs_reinstall=true
      echo ""
      echo "⚠️  Warning: Corrupted package metadata detected, retrying with --reinstall..."
    # 检查其他错误
    elif [ ${sync_exit_code} -ne 0 ]; then
      needs_reinstall=true
      echo ""
      echo "⚠️  Warning: uv sync encountered errors, retrying with --reinstall..."
      echo "   This will fix corrupted package metadata (common on Windows)"
    fi
    
    if [ "$needs_reinstall" = true ]; then
      echo "   Retrying with --reinstall..."
      (cd "${ROOT}" && uv sync --reinstall)
    else
      # 成功，但可能有一些警告，输出信息
      echo "${sync_output}"
    fi
  fi

  # 重新检测 Python 路径（Windows 和 Unix 路径不同）
  if [ -x "${VENV_DIR}/Scripts/python.exe" ]; then
    VENV_PY="${VENV_DIR}/Scripts/python.exe"
  elif [ -x "${VENV_DIR}/Scripts/python3.exe" ]; then
    VENV_PY="${VENV_DIR}/Scripts/python3.exe"
  elif [ -x "${VENV_DIR}/bin/python" ]; then
    VENV_PY="${VENV_DIR}/bin/python"
  elif [ -x "${VENV_DIR}/bin/python3" ]; then
    VENV_PY="${VENV_DIR}/bin/python3"
  fi

  [ -x "${VENV_PY}" ] || die "uv created no venv at: ${VENV_PY}"
  echo "Using Python at: ${VENV_PY}"

  if [ -f "${ROOT}/backend/requirements.txt" ]; then
    # 安装额外的依赖，如果遇到元数据错误则使用 --reinstall
    # 使用 || true 防止脚本因错误退出
    local req_output
    req_output=$(cd "${ROOT}" && uv pip install -r backend/requirements.txt 2>&1) || true
    local req_exit_code=$?
    
    # 检查是否有元数据读取错误
    if echo "${req_output}" | grep -qiE "(Failed to read.*metadata|failed to open file.*METADATA|系统找不到指定的文件|os error 2)"; then
      echo ""
      echo "⚠️  Warning: Corrupted package metadata detected in requirements, retrying with --reinstall..."
      (cd "${ROOT}" && uv pip install -r backend/requirements.txt --reinstall) || {
        echo "⚠️  Warning: Some packages may have metadata issues, but continuing..."
      }
    elif [ ${req_exit_code} -ne 0 ]; then
      echo ""
      echo "⚠️  Warning: Failed to install some requirements, retrying with --reinstall..."
      (cd "${ROOT}" && uv pip install -r backend/requirements.txt --reinstall) || {
        echo "⚠️  Warning: Some packages may have installation issues, but continuing..."
      }
    fi
  fi
  echo "Python dependencies ready"
}

install_deps() {
  echo "Installing all dependencies..."
  ensure_python_env
  install_ui_deps
  echo "All dependencies installed"
}

install_ui_deps() {
  need node
  need pnpm
  echo "Installing/updating UI dependencies..."
  (cd "${ROOT}/ui" && pnpm install --frozen-lockfile)
  echo "UI dependencies ready"
}

run_migrations() {
  ensure_python_env
  ensure_env_files
  echo "Running database migrations..."
  (
    cd "${ROOT}/backend"
    export PYTHONPATH="${ROOT}/backend:${PYTHONPATH:-}"
    "${VENV_PY}" -m alembic upgrade head
  )
  echo "Database migrations completed"
}

start_graph() {
  local dev="$1"
  local wait_ready="${2:-0}"  # 是否等待服务就绪
  if is_running graph; then
    echo "graph: already running (pid $(cat "$(pidfile graph)"))"
    return 0
  fi

  ensure_env_files

  (
    cd "${ROOT}"
    export PYTHONPATH="${ROOT}/backend:${PYTHONPATH:-}"
    export PYTHONUTF8=1
    export PYTHONIOENCODING="utf-8"
    export LANGGRAPH_HOST="${GRAPH_HOST}"
    export LANGGRAPH_PORT="${GRAPH_PORT}"
    export LANGGRAPH_RELOAD="$([ "${dev}" = "1" ] && echo true || echo false)"
    nohup "${VENV_PY}" "${ROOT}/start_server.py" >"$(logfile graph)" 2>&1 &
    write_pid graph "$!"
  )
  echo "graph: starting (pid $(cat "$(pidfile graph)")), logs: $(logfile graph)"
  
  if [ "${wait_ready}" = "1" ]; then
    wait_for_service "graph" "http://localhost:${GRAPH_PORT}" 60
  fi
}

start_backend() {
  local dev="$1"
  local wait_ready="${2:-0}"  # 是否等待服务就绪
  if is_running backend; then
    echo "backend: already running (pid $(cat "$(pidfile backend)"))"
    return 0
  fi

  (
    cd "${ROOT}/backend"
    export PYTHONPATH="${ROOT}/backend:${PYTHONPATH:-}"
    export PYTHONUTF8=1
    export PYTHONIOENCODING="utf-8"
    local -a args
    args=(--host "${BACKEND_HOST}" --port "${BACKEND_PORT}")
    if [ "${dev}" = "1" ]; then
      args+=(--reload)
    fi
    nohup "${VENV_PY}" -m uvicorn app.main:app "${args[@]}" >"$(logfile backend)" 2>&1 &
    write_pid backend "$!"
  )
  echo "backend: starting (pid $(cat "$(pidfile backend)")), logs: $(logfile backend)"
  
  if [ "${wait_ready}" = "1" ]; then
    wait_for_service "backend" "http://localhost:${BACKEND_PORT}" 60
  fi
}

start_ui() {
  local dev="$1"
  local wait_ready="${2:-0}"  # 是否等待服务就绪
  if is_running ui; then
    echo "ui: already running (pid $(cat "$(pidfile ui)"))"
    return 0
  fi

  need node
  need pnpm

  (
    cd "${ROOT}/ui"
    # 检查 node_modules 是否存在，如果不存在或 lockfile 更新了才安装
    local need_install=0
    if [ ! -d "node_modules" ]; then
      need_install=1
    elif [ -f "pnpm-lock.yaml" ] && [ "pnpm-lock.yaml" -nt "node_modules" ]; then
      need_install=1
    elif [ -f "package.json" ] && [ "package.json" -nt "node_modules" ]; then
      need_install=1
    fi

    if [ "${need_install}" = "1" ]; then
      echo "Installing UI dependencies..."
      pnpm install --frozen-lockfile
    fi

    if [ "${dev}" = "1" ]; then
      nohup pnpm dev -- -p "${UI_PORT}" >"$(logfile ui)" 2>&1 &
    else
      # 生产环境：检查是否需要重新构建
      local need_build=0
      if [ ! -d ".next" ]; then
        need_build=1
      elif [ -f "package.json" ] && [ "package.json" -nt ".next" ]; then
        need_build=1
      elif [ -f "pnpm-lock.yaml" ] && [ "pnpm-lock.yaml" -nt ".next" ]; then
        need_build=1
      fi

      if [ "${need_build}" = "1" ]; then
        echo "Building UI for production..."
        pnpm build
      fi
      nohup pnpm start -- -p "${UI_PORT}" >"$(logfile ui)" 2>&1 &
    fi
    write_pid ui "$!"
  )
  echo "ui: starting (pid $(cat "$(pidfile ui)")), logs: $(logfile ui)"
  
  if [ "${wait_ready}" = "1" ]; then
    wait_for_service "ui" "http://localhost:${UI_PORT}" 90
  fi
}

stop_service() {
  local name="$1"
  if ! [ -f "$(pidfile "$name")" ]; then
    echo "${name}: not running (no pidfile)"
    return 0
  fi

  local pid
  pid="$(cat "$(pidfile "$name")" 2>/dev/null || true)"
  if [ -z "${pid}" ]; then
    rm -f "$(pidfile "$name")"
    echo "${name}: not running (empty pidfile)"
    return 0
  fi

  if kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}" 2>/dev/null || true
    for _ in {1..30}; do
      if ! kill -0 "${pid}" 2>/dev/null; then
        break
      fi
      sleep 1
    done
    if kill -0 "${pid}" 2>/dev/null; then
      kill -9 "${pid}" 2>/dev/null || true
    fi
    echo "${name}: stopped (pid ${pid})"
  else
    echo "${name}: not running (stale pid ${pid})"
  fi

  rm -f "$(pidfile "$name")"
}

wait_for_service() {
  local name="$1"
  local url="$2"
  local max_attempts="${3:-60}"
  local attempt=0

  # 检查是否有 curl 命令
  if ! command -v curl >/dev/null 2>&1; then
    echo "⚠️  curl not found, skipping health check for ${name}"
    echo "   Waiting ${max_attempts} seconds for service to start..."
    sleep "${max_attempts}"
    # 检查服务是否还在运行
    if is_running "${name}"; then
      return 0
    else
      echo "❌ ${name} process died during startup"
      return 1
    fi
  fi

  echo "Waiting for ${name} to be ready..."
  while [ $attempt -lt $max_attempts ]; do
    # 检查进程是否还在运行
    if ! is_running "${name}"; then
      echo "❌ Error: ${name} process died during startup"
      echo "   Check logs at: $(logfile "${name}")"
      return 1
    fi
    
    # 尝试连接服务（尝试多个可能的健康检查端点）
    if curl -sf "${url}" >/dev/null 2>&1 || \
       curl -sf "${url}/health" >/dev/null 2>&1 || \
       curl -sf "${url}/docs" >/dev/null 2>&1 || \
       curl -sf "${url}/ok" >/dev/null 2>&1 || \
       curl -sf "${url}/api/health" >/dev/null 2>&1 || \
       curl -sf "${url}/api/v2/health" >/dev/null 2>&1; then
      echo "✅ ${name} is ready"
      return 0
    fi
    
    attempt=$((attempt + 1))
    if [ $((attempt % 5)) -eq 0 ]; then
      echo "  Still waiting... (${attempt}/${max_attempts})"
    fi
    sleep 1
  done
  
  echo "⚠️  Warning: ${name} health check failed after ${max_attempts} attempts"
  echo "   Service may still be starting. Check logs at: $(logfile "${name}")"
  return 1
}

health_check() {
  local name="$1"
  local url="$2"
  wait_for_service "${name}" "${url}" 10
}

status() {
  echo "Service Status:"
  echo "==============="
  local name
  local all_running=true
  for name in graph backend ui; do
    if is_running "${name}"; then
      local pid
      pid="$(cat "$(pidfile "${name}")" 2>/dev/null || echo "?")"
      echo "✅ ${name}: running (pid ${pid})"
      echo "   Log: $(logfile "${name}")"
    else
      echo "❌ ${name}: stopped"
      all_running=false
    fi
  done

  echo ""
  echo "Service URLs:"
  echo "=============="
  echo "  Graph API   : http://localhost:${GRAPH_PORT}"
  echo "  Backend API : http://localhost:${BACKEND_PORT}"
  echo "  UI          : http://localhost:${UI_PORT}"
  
  if [ "$all_running" = false ]; then
    echo ""
    echo "⚠️  Some services are not running. Check logs above for details."
    return 1
  fi
  return 0
}

logs() {
  local name="${1:-}"
  case "${name}" in
    graph|backend|ui)
      tail -n 200 -f "$(logfile "${name}")"
      ;;
    "")
      die "Missing service name (graph|backend|ui)"
      ;;
    *)
      die "Unknown service: ${name}"
      ;;
  esac
}

clean_venv() {
  echo "Cleaning Python virtual environment..."
  stop_service ui
  stop_service backend
  stop_service graph
  sleep 2
  
  if [ -d "${VENV_DIR}" ]; then
    echo "Removing ${VENV_DIR}..."
    rm -rf "${VENV_DIR}"
  fi
  
  if [ -d "${RUNTIME_DIR}" ]; then
    echo "Removing ${RUNTIME_DIR}..."
    rm -rf "${RUNTIME_DIR}"
  fi
  
  echo "✅ Cleanup completed"
}

usage() {
  cat <<'EOF'
Usage:
  ./deploy.sh up [--dev]              Start graph + backend + UI
  ./deploy.sh down                    Stop all services
  ./deploy.sh restart [--dev]         Restart all services
  ./deploy.sh status                  Show status and URLs
  ./deploy.sh logs <service>          Tail logs (graph|backend|ui)
  ./deploy.sh deps                    Install/update all dependencies
  ./deploy.sh deps-backend            Install/update backend dependencies only
  ./deploy.sh deps-ui                 Install/update UI dependencies only
  ./deploy.sh migrate                 Run database migrations
  ./deploy.sh health                  Check health of all services
  ./deploy.sh clean                   Clean virtual environment and runtime files

Environment overrides:
  BACKEND_HOST BACKEND_PORT GRAPH_HOST GRAPH_PORT UI_HOST UI_PORT
  UV_REINSTALL=1                      Force reinstall all packages (fixes corrupted metadata)

Notes:
  - Requires: uv, node, pnpm
  - Python venv is created at: ai-test-management/.venv (via uv)
  - Logs/PIDs are written under: ai-test-management/.runtime/
  - If backend/.env is missing, backend/.env.example is copied in its place
  - Dependencies are automatically checked and updated on startup
  - If you see "missing RECORD file" warnings, run: UV_REINSTALL=1 ./deploy.sh up
  - Optional MCP services (needed for RAG/MindMap features):
      - RAG MCP (SSE, default :9002): `cd ../testing-agents-service/src/api_agent/mcp_servers && python rag_mcp_server.py --port 9002 --sse`
      - MindMap MCP (SSE, default :9003): see `ai-test-management/QUICK_START.md`
EOF
}

cmd="${1:-help}"
shift || true

dev=0
if [ "${1:-}" = "--dev" ]; then
  dev=1
  shift || true
fi

case "${cmd}" in
  up)
    ensure_python_env
    run_migrations
    
    # 按依赖顺序启动服务，并等待每个服务就绪
    local failed_services=()
    
    # 1. 先启动 Graph API (Backend 依赖它)
    echo ""
    echo "=== Step 1/3: Starting Graph API Service ==="
    if start_graph "${dev}" 1; then
      echo "✅ Graph API Service started successfully"
    else
      echo "❌ Graph API Service failed to start"
      failed_services+=("graph")
    fi
    
    # 2. 再启动 Backend API (UI 依赖它)
    echo ""
    echo "=== Step 2/3: Starting Backend API Service ==="
    if start_backend "${dev}" 1; then
      echo "✅ Backend API Service started successfully"
    else
      echo "❌ Backend API Service failed to start"
      failed_services+=("backend")
    fi
    
    # 3. 最后启动 UI
    echo ""
    echo "=== Step 3/3: Starting UI Service ==="
    if start_ui "${dev}" 1; then
      echo "✅ UI Service started successfully"
    else
      echo "❌ UI Service failed to start"
      failed_services+=("ui")
    fi
    
    echo ""
    echo "=========================================="
    if [ ${#failed_services[@]} -eq 0 ]; then
      echo "✅ All services started successfully!"
    else
      echo "⚠️  Some services failed to start: ${failed_services[*]}"
      echo "   Check logs for details:"
      for name in "${failed_services[@]}"; do
        echo "     - ${name}: $(logfile "${name}")"
      done
    fi
    echo "=========================================="
    echo ""
    status
    ;;
  down)
    stop_service ui
    stop_service backend
    stop_service graph
    ;;
  restart)
    "$0" down
    sleep 1
    "$0" up $([ "${dev}" = "1" ] && echo --dev || true)
    ;;
  status)
    status
    ;;
  logs)
    logs "${1:-}"
    ;;
  deps)
    install_deps
    ;;
  deps-backend)
    ensure_python_env
    ;;
  deps-ui)
    install_ui_deps
    ;;
  migrate)
    run_migrations
    ;;
  clean)
    clean_venv
    ;;
  health)
    need curl || die "curl is required for health checks"
    for name in backend ui; do
      case "${name}" in
        backend)
          health_check "backend" "http://localhost:${BACKEND_PORT}" || true
          ;;
        ui)
          health_check "ui" "http://localhost:${UI_PORT}" || true
          ;;
      esac
    done
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage
    die "Unknown command: ${cmd}"
    ;;
esac
