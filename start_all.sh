#!/bin/bash
# =============================================================================
# AI LangGraph Service Starter (using uv)
# 
# Function: One-click start all backend services (using unified virtual environment managed by uv)
# 
# Service List:
#   1. LightRAG Server (Knowledge Base)     - http://localhost:9621
#   2. MCP Server (RAG Anything)            - http://localhost:8001
#   3. Anything RAG MCP (LightRAG HTTP)     - http://localhost:8006/sse
#   4. API Agent MCP Servers                - http://localhost:8002-8005
#      - RAG MCP Server                     - http://localhost:8002/sse
#      - Pytest MCP Server                  - http://localhost:8004/sse
#      - Automation Quality MCP Server      - stdio mode (no HTTP)
#   5. LangGraph Server (Agent Backend)     - http://localhost:2025
#   6. AI Platform Backend (Main Backend)   - http://localhost:9999
#   7. AI Platform Frontend (Frontend UI)   - http://localhost:5174
#
# Usage:
#   ./start_all.sh          # Start all backend services
#   ./start_all.sh --all    # Start all services (including frontend)
#   ./start_all.sh --stop   # Stop all services
# =============================================================================

# Don't exit on error - we want to start all services even if one fails
# set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# PID file directory
PID_DIR="$PROJECT_ROOT/.pids"
mkdir -p "$PID_DIR"

# Log directory
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

# Current environment (local/remote)
CURRENT_ENV="local"
ENV_FILE="$PROJECT_ROOT/.env"

# Detect OS and set Python path
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash/MSYS2/Cygwin)
    VENV_PYTHON="$PROJECT_ROOT/.venv/Scripts/python.exe"
    VENV_BIN="$PROJECT_ROOT/.venv/Scripts"
    MCP_VENV_PYTHON="$PROJECT_ROOT/mcp-server/.venv/Scripts/python.exe"
    MCP_VENV_BIN="$PROJECT_ROOT/mcp-server/.venv/Scripts"
else
    # Linux/macOS
    VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
    VENV_BIN="$PROJECT_ROOT/.venv/bin"
    MCP_VENV_PYTHON="$PROJECT_ROOT/mcp-server/.venv/bin/python"
    MCP_VENV_BIN="$PROJECT_ROOT/mcp-server/.venv/bin"
    fi

# =============================================================================
# Utility Functions
# =============================================================================

print_banner() {
    printf "${CYAN}"
    printf "================================================================\n"
    printf "          AI LangGraph Service Starter (uv)                    \n"
    printf "                                                                \n"
    printf "          Unified Virtual Env · One-Click Start · Simple       \n"
    printf "================================================================\n"
    printf "${NC}"
}

print_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

print_success() {
    printf "${GREEN}[OK]${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}[!]${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}[X]${NC} %s\n" "$1"
}

print_access_url() {
    local label=$1
    local url=$2
    if check_http "$url" 2; then
        printf "  ${GREEN}[OK]${NC} %-22s ${CYAN}%s${NC}\n" "$label" "$url"
    else
        printf "  ${RED}[X]${NC}  %-22s ${CYAN}%s${NC}\n" "$label" "$url"
    fi
}

# Load environment variables from .env if present (best-effort)
load_env_file() {
    if [ -f "$ENV_FILE" ]; then
        # shellcheck disable=SC1090
        source "$ENV_FILE"
    fi
}

# Get a usable Python executable for helper checks
get_python_bin() {
    if [ -n "$VENV_PYTHON" ] && [ -x "$VENV_PYTHON" ]; then
        echo "$VENV_PYTHON"
        return 0
    fi
    if command -v python3 &> /dev/null; then
        command -v python3
        return 0
    fi
    if command -v python &> /dev/null; then
        command -v python
        return 0
    fi
    return 1
}

# Check if a PID is running (cross-platform best-effort)
pid_is_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        if command -v tasklist &> /dev/null; then
            # Git Bash/MSYS will path-convert args starting with '/', so exclude conversion.
            MSYS2_ARG_CONV_EXCL="*" tasklist /FI "PID eq $pid" 2>/dev/null | grep -qE "[[:space:]]$pid[[:space:]]" && return 0 || return 1
        fi
        return 1
    fi
    kill -0 "$pid" 2>/dev/null && return 0 || return 1
}

win_taskkill_pid() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi
    if command -v taskkill &> /dev/null; then
        MSYS2_ARG_CONV_EXCL="*" taskkill /F /PID "$pid" >/dev/null 2>&1 && return 0 || return 1
    fi
    return 1
}

# Get PID that is listening on a port (best-effort, cross-platform)
get_pid_by_port() {
    local port=$1
    if [ -z "$port" ]; then
        return 1
    fi

    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        local py
        py="$(get_python_bin)" || return 1
        "$py" -c "import subprocess, sys
port=int(sys.argv[1])
try:
    p=subprocess.run(['netstat','-ano'], capture_output=True, text=True, shell=True, timeout=5)
    for line in p.stdout.splitlines():
        if f':{port}' in line and ('LISTENING' in line or 'LISTEN' in line):
            parts=line.split()
            if parts and parts[-1].isdigit() and parts[-1] != '0':
                print(parts[-1])
                sys.exit(0)
except Exception:
    pass
sys.exit(1)
" "$port" 2>/dev/null | tr -d '\r\n ' | head -1
        return 0
    fi

    if command -v lsof &> /dev/null; then
        lsof -ti:"$port" 2>/dev/null | head -1
        return 0
    fi
    return 1
}

# Check HTTP endpoint is healthy (status 200-399). Works for SSE endpoints too.
check_http() {
    local url=$1
    local timeout=${2:-3}
    local py
    py="$(get_python_bin)" || return 1

    "$py" -c "import sys, urllib.request
url=sys.argv[1]; timeout=float(sys.argv[2])
try:
    req=urllib.request.Request(url, headers={'User-Agent':'healthcheck','Accept':'*/*'})
    resp=urllib.request.urlopen(req, timeout=timeout)
    code=getattr(resp, 'status', None) or resp.getcode()
    try: resp.close()
    except: pass
    sys.exit(0 if 200 <= int(code) < 400 else 1)
except Exception:
    sys.exit(1)
" "$url" "$timeout" >/dev/null 2>&1
}

check_http_any() {
    local timeout=${1:-3}
    shift || true
    local url
    for url in "$@"; do
        if check_http "$url" "$timeout"; then
            return 0
        fi
    done
    return 1
}

# Wait for any of the given URLs to become healthy.
wait_for_http_any() {
    local name=$1
    local max_wait=${2:-60}
    local timeout_per_try=${3:-3}
    shift 3 || true
    local count=0

    print_info "Waiting for $name HTTP readiness..."
    while [ $count -lt $max_wait ]; do
        if check_http_any "$timeout_per_try" "$@"; then
            return 0
        fi
        sleep 1
        count=$((count + 1))
        if [ $((count % 5)) -eq 0 ]; then
            printf "."
        fi
    done
    echo ""
    return 1
}

# Check if port is occupied (cross-platform)
check_port() {
    local port=$1
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # Windows: use netstat or Python
        if command -v netstat &> /dev/null; then
            netstat -an | grep -q ":$port.*LISTEN" 2>/dev/null && return 0 || return 1
        else
            # Fallback to Python
            "$VENV_PYTHON" -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = s.connect_ex(('127.0.0.1', $port))
s.close()
exit(0 if result == 0 else 1)
" 2>/dev/null && return 0 || return 1
        fi
    else
        # Linux/macOS: use lsof
        if command -v lsof &> /dev/null; then
            lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 && return 0 || return 1
        else
            # Fallback to Python
            "$VENV_PYTHON" -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = s.connect_ex(('127.0.0.1', $port))
s.close()
exit(0 if result == 0 else 1)
" 2>/dev/null && return 0 || return 1
        fi
    fi
}

# Kill process using a specific port (cross-platform)
kill_port() {
    local port=$1
    local killed=false
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # Windows: use Python to find and kill process on port
        local pid=$("$VENV_PYTHON" -c "
import socket
import subprocess
import sys
import os

port = $port
try:
    # Use netstat to find PID
    if os.name == 'nt':
        try:
            # Run netstat -ano to find listening processes
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True,
                shell=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid_str = parts[-1].strip()
                        if pid_str.isdigit() and pid_str != '0':
                            print(pid_str)
                            break
        except Exception as e:
            pass
except:
    pass
" 2>/dev/null)
        
        if [ -n "$pid" ] && [ "$pid" != "0" ]; then
            print_info "Killing process on port $port (PID: $pid)..."
            win_taskkill_pid "$pid" && killed=true || {
                # Fallback: try kill command (Git Bash)
                kill -9 "$pid" >/dev/null 2>&1 && killed=true
            }
        fi
    else
        # Linux/macOS: use lsof to find PID, then kill
        if command -v lsof &> /dev/null; then
            local pid=$(lsof -ti:$port 2>/dev/null | head -1)
            if [ -n "$pid" ]; then
                print_info "Killing process on port $port (PID: $pid)..."
                kill -9 "$pid" >/dev/null 2>&1 && killed=true
            fi
        else
            # Fallback: use fuser (Linux)
            if command -v fuser &> /dev/null; then
                fuser -k "$port/tcp" >/dev/null 2>&1 && killed=true
            fi
        fi
    fi
    
    if [ "$killed" = true ]; then
        # Wait a moment for the port to be released
        sleep 2
        # Verify port is actually free
        if ! check_port $port; then
            return 0
        else
            print_warning "Port $port may still be in use after kill attempt"
            return 1
        fi
    else
        return 1
    fi
}

# Ensure port is free, kill if occupied
ensure_port_free() {
    local port=$1
    local name=$2
    
    if check_port $port; then
        print_warning "Port $port is already in use ($name)"
        if kill_port $port; then
            print_success "Freed port $port"
            return 0
        else
            print_error "Failed to free port $port"
            return 1
        fi
    fi
    return 0
}

# Wait for service to start
wait_for_service() {
    local port=$1
    local name=$2
    local max_wait=${3:-60}  # Default 60 seconds, can be overridden
    local count=0
    
    print_info "Waiting for $name to start on port $port..."
    
    while [ $count -lt $max_wait ]; do
        if check_port $port; then
            return 0
        fi
        sleep 1
        count=$((count + 1))
        # Show progress every 5 seconds
        if [ $((count % 5)) -eq 0 ]; then
            printf "."
        fi
    done
    echo ""
    return 1
}

# Check if uv is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed! Please install uv first:"
        echo ""
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo ""
        exit 1
    fi
}

# Get file modification time (cross-platform)
get_file_mtime() {
    local file="$1"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # Windows Git Bash: use Python to get mtime
        "$VENV_PYTHON" -c "import os; print(int(os.path.getmtime('$file')))" 2>/dev/null || echo "0"
    else
        # Linux/macOS: use stat
        stat -c "%Y" "$file" 2>/dev/null || stat -f "%m" "$file" 2>/dev/null || echo "0"
    fi
}

# Check if requirements.txt has been modified since last sync
check_dependencies_updated() {
    local requirements_file="$PROJECT_ROOT/requirements.txt"
    local sync_marker="$PROJECT_ROOT/.venv/.last_sync"
    
    if [ ! -f "$sync_marker" ]; then
        return 1  # Needs sync
    fi
    
    if [ ! -f "$requirements_file" ]; then
        return 0  # No requirements file, skip check
    fi
    
    # Use Python for cross-platform compatibility
    local requirements_mtime=$(get_file_mtime "$requirements_file")
    local sync_mtime=$(get_file_mtime "$sync_marker")
    
    # Compare as integers
    if [ -n "$requirements_mtime" ] && [ -n "$sync_mtime" ] && [ "$requirements_mtime" -gt "$sync_mtime" ] 2>/dev/null; then
        return 1  # Requirements updated, needs sync
    fi
    
    return 0  # Up to date
}

# Install or update dependencies
install_dependencies() {
    print_info "Installing/updating dependencies (may take a few minutes)..."
    
    # Try with pre-compiled wheels first (except forbiddenfruit which needs compilation)
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # Windows: allow source builds for specific packages
        print_info "Windows detected: allowing source builds for packages without wheels..."
        uv pip install -r requirements.txt
    else
        # Linux/macOS: try binary only first, fallback to compilation
        uv pip install --only-binary :all: -r requirements.txt 2>/dev/null || {
            print_warning "Some packages need compilation, retrying without --only-binary..."
            uv pip install -r requirements.txt
        }
    fi
    
    # Install critical dependencies for LightRAG (especially ascii_colors for pipmaster)
    # Note: pipmaster requires ascii_colors, but it might not be installed yet
    print_info "Installing critical LightRAG dependencies..."
    uv pip install ascii-colors pipmaster 2>/dev/null || {
        print_warning "Failed to install ascii-colors/pipmaster, will try from requirements..."
    }
    
    # Install LightRAG dependencies from requirements.txt
    if [ -f "./anything-chat-rag/requirements.txt" ]; then
        print_info "Installing LightRAG dependencies from requirements.txt..."
        uv pip install -r ./anything-chat-rag/requirements.txt
    fi
    
    # Install LightRAG in editable mode (with dependencies to ensure everything is installed)
    print_info "Installing LightRAG..."
    uv pip install -e ./anything-chat-rag
    
    # Configure Python path for other modules
    # NOTE: testing-agents-service has been flattened to a single-level directory:
    #   from: testing-agents-service/testing-agents-service/src
    #   to:   testing-agents-service/src
    local site_packages=$("$VENV_PYTHON" -c "import site; print(site.getsitepackages()[0])")
    cat > "$site_packages/ai-langgraph.pth" << EOF
$PROJECT_ROOT/testing-agents-service/src
$PROJECT_ROOT/mcp-server/src
EOF
    
    # Ensure testing-agents-service/src 和 mcp-server/src 在 Windows 下也能正常加入 Python path
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # Convert to Windows path format for .pth file
        local mcp_path_win=$(cygpath -w "$PROJECT_ROOT/mcp-server/src" 2>/dev/null || echo "$PROJECT_ROOT/mcp-server/src")
        local testing_path_win=$(cygpath -w "$PROJECT_ROOT/testing-agents-service/src" 2>/dev/null || echo "$PROJECT_ROOT/testing-agents-service/src")
        cat > "$site_packages/ai-langgraph.pth" << EOF
$testing_path_win
$mcp_path_win
EOF
    fi
    
    # Mark sync time
    touch "$PROJECT_ROOT/.venv/.last_sync"
}

# Check virtual environment, create or update if needed
check_venv() {
    local force_update=false
    
    # Check for --update flag
    for arg in "$@"; do
        if [[ "$arg" == "--update" || "$arg" == "-u" ]]; then
            force_update=true
            break
        fi
    done
    
    if [ ! -d "$PROJECT_ROOT/.venv" ]; then
        print_warning "Virtual environment does not exist, creating with uv..."
        
        # Create virtual environment
        print_info "Creating virtual environment..."
        uv venv --python 3.11
        
        # Install dependencies
        install_dependencies
        
        print_success "Virtual environment created and dependencies installed"
    elif [ "$force_update" = true ] || ! check_dependencies_updated; then
        if [ "$force_update" = true ]; then
            print_info "Force update requested, updating dependencies..."
        else
            print_warning "Dependencies have been updated, syncing virtual environment..."
        fi
        
        # Update dependencies
        install_dependencies
        
        print_success "Dependencies updated"
    else
        print_success "Virtual environment is up to date"
    fi
}

# =============================================================================
# Service Start Functions (using uv run)
# =============================================================================

start_lightrag() {
    local port=9621
    local name="LightRAG Server"
    local pid_file="$PID_DIR/lightrag.pid"
    local log_file="$LOG_DIR/lightrag.log"
    
    # Ensure port is free
    if ! ensure_port_free $port "$name"; then
        print_error "Cannot start $name: port $port is occupied and cannot be freed"
        return 1
    fi
    
    print_info "Starting $name..."
    
    cd "$PROJECT_ROOT/anything-chat-rag"
    export PATH="$VENV_BIN:$PATH"
    export PYTHONIOENCODING=utf-8
    nohup "$VENV_PYTHON" -m lightrag.api.lightrag_server > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    # LightRAG may take longer to initialize (storage initialization)
    if wait_for_http_any "$name" 180 3 \
        "http://127.0.0.1:$port/openapi.json" \
        "http://127.0.0.1:$port/docs"; then
        local real_pid="$(get_pid_by_port "$port")"
        if [ -n "$real_pid" ]; then
            pid="$real_pid"
            echo "$pid" > "$pid_file"
        fi
        print_success "$name started (PID: $pid, Port: $port)"
        printf "         API Docs: ${CYAN}http://localhost:$port/docs${NC}\n"
    else
        print_error "$name failed to start, check log: $log_file"
        return 1
    fi
}

start_mcp_server() {
    local port=8001
    local name="MCP Server"
    local pid_file="$PID_DIR/mcp.pid"
    local log_file="$LOG_DIR/mcp.log"
    # Prefer dedicated mcp-server venv if present
    local mcp_python="$MCP_VENV_PYTHON"
    local mcp_bin="$MCP_VENV_BIN"
    if [ ! -x "$mcp_python" ]; then
        print_warning "Dedicated MCP venv not found, fallback to root venv"
        mcp_python="$VENV_PYTHON"
        mcp_bin="$VENV_BIN"
    fi
    
    # Ensure port is free (MCP Server must use fixed port 8001)
    if ! ensure_port_free $port "$name"; then
        print_error "Cannot start $name: port $port is occupied and cannot be freed"
        return 1
    fi
    
    print_info "Starting $name..."
    
    cd "$PROJECT_ROOT/mcp-server/src"
    export PATH="$mcp_bin:$PATH"
    export PYTHONIOENCODING=utf-8
    # Add current directory和本地 lightrag 实现到 Python path
    export PYTHONPATH="$PROJECT_ROOT/anything-chat-rag:$PROJECT_ROOT/mcp-server/src:$PYTHONPATH"
    # Set API Key if not already set (for DeepSeek)
    if [ -z "$LLM_API_KEY" ] && [ -z "$DEEPSEEK_API_KEY" ]; then
        # Try to load from .env file if exists
        if [ -f "$PROJECT_ROOT/.env" ]; then
            source "$PROJECT_ROOT/.env"
        fi
    fi
    # Ensure DEEPSEEK_API_KEY is available for MCP server
    if [ -n "$DEEPSEEK_API_KEY" ] && [ -z "$LLM_API_KEY" ]; then
        export LLM_API_KEY="$DEEPSEEK_API_KEY"
    fi
    # Use python -m with explicit path or direct script execution
    nohup "$mcp_python" -m mcp_server_rag_anything.server > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    if wait_for_http_any "$name" 60 3 \
        "http://127.0.0.1:$port/sse"; then
        local real_pid="$(get_pid_by_port "$port")"
        if [ -n "$real_pid" ]; then
            pid="$real_pid"
            echo "$pid" > "$pid_file"
        fi
        print_success "$name started (PID: $pid, Port: $port)"
    else
        print_error "$name failed to start, check log: $log_file"
        return 1
    fi
}

start_anything_rag_mcp() {
    local port=8006
    local name="Anything RAG MCP Server"
    local pid_file="$PID_DIR/anything_rag_mcp.pid"
    local log_file="$LOG_DIR/anything_rag_mcp.log"

    if ! ensure_port_free $port "$name"; then
        print_error "Cannot start $name: port $port is occupied and cannot be freed"
        return 1
    fi

    print_info "Starting $name..."

    cd "$PROJECT_ROOT"
    export PATH="$VENV_BIN:$PATH"
    export PYTHONIOENCODING=utf-8
    # Load environment variables if .env exists (for LIGHTRAG_BASE_URL, API keys, etc.)
    if [ -f "$PROJECT_ROOT/.env" ]; then
        source "$PROJECT_ROOT/.env"
    fi
    nohup "$VENV_PYTHON" "$PROJECT_ROOT/anything_rag_mcp/server.py" --port $port --transport sse > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"

    if wait_for_http_any "$name" 60 3 \
        "http://127.0.0.1:$port/sse"; then
        local real_pid="$(get_pid_by_port "$port")"
        if [ -n "$real_pid" ]; then
            pid="$real_pid"
            echo "$pid" > "$pid_file"
        fi
        print_success "$name started (PID: $pid, Port: $port)"
    else
        print_error "$name failed to start, check log: $log_file"
        return 1
    fi
}

start_api_agent_mcp_servers() {
    # MCP 服务器已统一到 testing-agents-service/mcp/ 目录
    local mcp_dir="$PROJECT_ROOT/testing-agents-service/mcp"
    local src_dir="$PROJECT_ROOT/testing-agents-service"
    
    print_info "Starting API Agent MCP Servers..."
    local any_failed=false
    
    # Set up environment - must be done before any cd commands
    export PATH="$VENV_BIN:$PATH"
    export PYTHONIOENCODING=utf-8
    export PYTHONPATH="$src_dir:$PYTHONPATH"
    
    # Load environment variables if .env exists
    if [ -f "$PROJECT_ROOT/.env" ]; then
        source "$PROJECT_ROOT/.env"
    fi
    
    # Ensure DEEPSEEK_API_KEY is available
    if [ -n "$DEEPSEEK_API_KEY" ] && [ -z "$LLM_API_KEY" ]; then
        export LLM_API_KEY="$DEEPSEEK_API_KEY"
    fi
    
    # Start RAG MCP Server (port 8002)
    local rag_port=8002
    local rag_name="RAG MCP Server"
    local rag_pid_file="$PID_DIR/rag_mcp.pid"
    local rag_log_file="$LOG_DIR/rag_mcp.log"
    
    if ! ensure_port_free $rag_port "$rag_name"; then
        print_error "Cannot start $rag_name: port $rag_port is occupied and cannot be freed"
        any_failed=true
    else
        print_info "Starting $rag_name on port $rag_port..."
        cd "$PROJECT_ROOT/testing-agents-service"
        PYTHONPATH="$src_dir:$PYTHONPATH" nohup "$VENV_PYTHON" -m mcp.rag_query.server --port $rag_port > "$rag_log_file" 2>&1 &
        local rag_pid=$!
        echo $rag_pid > "$rag_pid_file"
        
        if wait_for_http_any "$rag_name" 60 3 "http://127.0.0.1:$rag_port/sse"; then
            local real_pid="$(get_pid_by_port "$rag_port")"
            if [ -n "$real_pid" ]; then
                rag_pid="$real_pid"
                echo "$rag_pid" > "$rag_pid_file"
            fi
            print_success "$rag_name started (PID: $rag_pid, Port: $rag_port)"
        else
            print_error "$rag_name failed to start, check log: $rag_log_file"
            any_failed=true
        fi
        cd "$PROJECT_ROOT"
    fi
    
    # Start Pytest MCP Server (port 8004) - 合并了 pytest_generator 和 test_executor
    local pytest_port=8004
    local pytest_name="Pytest MCP Server"
    local pytest_pid_file="$PID_DIR/pytest_mcp.pid"
    local pytest_log_file="$LOG_DIR/pytest_mcp.log"
    
    if ! ensure_port_free $pytest_port "$pytest_name"; then
        print_warning "Port $pytest_port is occupied, skipping $pytest_name"
        any_failed=true
    else
        print_info "Starting $pytest_name on port $pytest_port..."
        cd "$PROJECT_ROOT/testing-agents-service"
        PYTHONPATH="$src_dir:$PYTHONPATH" nohup "$VENV_PYTHON" -m mcp.pytest_mcp.server --port $pytest_port > "$pytest_log_file" 2>&1 &
        local pytest_pid=$!
        echo $pytest_pid > "$pytest_pid_file"
        
        if wait_for_http_any "$pytest_name" 60 3 "http://127.0.0.1:$pytest_port/sse"; then
            local real_pid="$(get_pid_by_port "$pytest_port")"
            if [ -n "$real_pid" ]; then
                pytest_pid="$real_pid"
                echo "$pytest_pid" > "$pytest_pid_file"
            fi
            print_success "$pytest_name started (PID: $pytest_pid, Port: $pytest_port)"
        else
            print_error "$pytest_name failed to start, check log: $pytest_log_file"
            any_failed=true
        fi
        cd "$PROJECT_ROOT"
    fi
    
    # Start Automation Quality MCP Server (Node.js stdio mode, no port needed)
    local automation_mcp_name="Automation Quality MCP Server"
    local automation_mcp_pid_file="$PID_DIR/automation_quality_mcp.pid"
    local automation_mcp_log_file="$LOG_DIR/automation_quality_mcp.log"
    local automation_mcp_dir="$mcp_dir/automation_quality"
    
    if [ ! -d "$automation_mcp_dir" ]; then
        print_warning "$automation_mcp_name directory not found, skipping"
    elif [ ! -d "$automation_mcp_dir/node_modules" ]; then
        print_warning "$automation_mcp_name node_modules not found, installing dependencies..."
        cd "$automation_mcp_dir"
        if command -v npm &> /dev/null; then
            npm install 2>&1 | head -20
            cd "$PROJECT_ROOT"
        else
            print_warning "npm not found, skipping $automation_mcp_name"
            cd "$PROJECT_ROOT"
        fi
    fi
    
    if [ -d "$automation_mcp_dir/node_modules" ] || [ -f "$automation_mcp_dir/mcpServer.js" ]; then
        print_info "Starting $automation_mcp_name (stdio mode)..."
        cd "$automation_mcp_dir"
        # Install dependencies if not present
        if [ ! -d "node_modules" ] && [ -f "package.json" ]; then
            npm install 2>&1 | head -20
        fi
        # Automation Quality MCP uses stdio mode, not SSE, so no port check needed
        nohup node mcpServer.js > "$automation_mcp_log_file" 2>&1 &
        local automation_mcp_pid=$!
        echo $automation_mcp_pid > "$automation_mcp_pid_file"
        print_success "$automation_mcp_name started (PID: $automation_mcp_pid, stdio mode)"
        cd "$PROJECT_ROOT"
    fi
    
    cd "$PROJECT_ROOT"
    echo ""

    if [ "$any_failed" = true ]; then
        return 1
    fi
    return 0
}

start_langgraph_server() {
    # Allow overriding LangGraph port via env (useful when 2025 is occupied)
    if [ -f "$PROJECT_ROOT/.env" ]; then
        # shellcheck disable=SC1090
        source "$PROJECT_ROOT/.env"
    fi
    local port="${LANGGRAPH_PORT:-2025}"
    local name="LangGraph Server"
    local pid_file="$PID_DIR/langgraph.pid"
    local log_file="$LOG_DIR/langgraph.log"
    
    # Ensure port is free
    if ! ensure_port_free $port "$name"; then
        print_error "Cannot start $name: port $port is occupied and cannot be freed"
        return 1
    fi
    
    print_info "Starting $name..."
    
    # Install Node.js dependencies for automation_quality MCP if needed
    # MCP 服务器已统一到 testing-agents-service/mcp/ 目录
    local automation_mcp_dir="$PROJECT_ROOT/testing-agents-service/mcp/automation_quality"
    if [ -d "$automation_mcp_dir" ] && [ ! -d "$automation_mcp_dir/node_modules" ]; then
        print_info "Installing Node.js dependencies for automation_quality MCP..."
        cd "$automation_mcp_dir"
        if command -v npm &> /dev/null; then
            npm install 2>&1 | head -20
        else
            print_warning "npm not found, automation_quality MCP may not work"
        fi
        cd "$PROJECT_ROOT"
    fi
    
    # LangGraph 后端工程根目录也从两级目录改成单一级目录 testing-agents-service
    cd "$PROJECT_ROOT/testing-agents-service"
    export PATH="$VENV_BIN:$PATH"
    export PYTHONIOENCODING=utf-8
    # Add testing-agents-service/src to Python path（使用新目录）
    export PYTHONPATH="$PROJECT_ROOT/testing-agents-service/src:$PYTHONPATH"
    nohup "$VENV_PYTHON" start_server.py --port "$port" > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    # LangGraph may take longer to initialize (graph loading, MCP connections)
    if wait_for_http_any "$name" 300 3 \
        "http://127.0.0.1:$port/ok" \
        "http://127.0.0.1:$port/docs"; then
        local real_pid="$(get_pid_by_port "$port")"
        if [ -n "$real_pid" ]; then
            pid="$real_pid"
            echo "$pid" > "$pid_file"
        fi
        print_success "$name started (PID: $pid, Port: $port)"
        printf "         API Docs: ${CYAN}http://localhost:$port/docs${NC}\n"
        printf "         Studio:   ${CYAN}http://localhost:$port/ui${NC}\n"
    else
        print_error "$name failed to become ready, check log: $log_file"
        return 1
    fi
}

start_agent_ui() {
    local port=3200
    local name="Agent UI"
    local pid_file="$PID_DIR/agent_ui.pid"
    local log_file="$LOG_DIR/agent_ui.log"
    
    # Ensure port is free
    if ! ensure_port_free $port "$name"; then
        print_error "Cannot start $name: port $port is occupied and cannot be freed"
        return 1
    fi
    
    print_info "Starting $name..."
    
    cd "$PROJECT_ROOT/testing-deep-agents-ui"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing frontend dependencies..."
        if command -v yarn &> /dev/null; then
            yarn install
        else
            npm install
    fi
    fi
    
    # Use npm if yarn is not available
    if command -v yarn &> /dev/null; then
    nohup env PORT=$port yarn dev > "$log_file" 2>&1 &
    else
        nohup env PORT=$port npm run dev > "$log_file" 2>&1 &
    fi
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    if wait_for_http_any "$name" 120 3 "http://127.0.0.1:$port/"; then
        local real_pid="$(get_pid_by_port "$port")"
        if [ -n "$real_pid" ]; then
            pid="$real_pid"
            echo "$pid" > "$pid_file"
        fi
        print_success "$name started (PID: $pid, Port: $port)"
        printf "         URL: ${CYAN}http://localhost:$port${NC}\n"
    else
        print_error "$name failed to become ready, check log: $log_file"
        return 1
    fi
}

# =============================================================================
# Service Stop Functions
# =============================================================================

stop_service() {
    local name=$1
    local pid_file=$2
    local port=$3
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
            if win_taskkill_pid "$pid"; then
                print_success "Stopped $name (PID: $pid)"
            fi
        else
            if kill -0 $pid 2>/dev/null; then
                kill $pid
                print_success "Stopped $name (PID: $pid)"
            fi
        fi
        rm -f "$pid_file"
    fi
    
    # Ensure port is released (cross-platform)
    if [ -n "$port" ] && check_port $port; then
        local pids=""
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
            # Windows: use Python to find PID via netstat
            pids=$("$VENV_PYTHON" -c "
import socket
import subprocess
import os

port = $port
try:
    if os.name == 'nt':
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            shell=True,
            timeout=5
        )
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid_str = parts[-1].strip()
                    if pid_str.isdigit() and pid_str != '0':
                        print(pid_str)
except:
    pass
" 2>/dev/null)
        else
            # Linux/macOS: use lsof
            if command -v lsof &> /dev/null; then
                pids=$(lsof -ti:$port 2>/dev/null)
            fi
        fi
        
        if [ -n "$pids" ]; then
            for pid in $pids; do
                if [ -n "$pid" ] && [ "$pid" != "0" ]; then
                    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
                        win_taskkill_pid "$pid" || kill -9 "$pid" >/dev/null 2>&1
                    else
                        kill -9 "$pid" >/dev/null 2>&1
                    fi
                fi
            done
        fi
    fi
}

stop_all() {
    print_info "Stopping all services..."
    load_env_file
    
    stop_service "Agent UI" "$PID_DIR/agent_ui.pid" 3200
    stop_service "LangGraph Server" "$PID_DIR/langgraph.pid" "${LANGGRAPH_PORT:-2025}"
    stop_service "Automation Quality MCP Server" "$PID_DIR/automation_quality_mcp.pid"
    stop_service "Pytest MCP Server" "$PID_DIR/pytest_mcp.pid" 8004
    stop_service "RAG MCP Server" "$PID_DIR/rag_mcp.pid" 8002
    stop_service "Anything RAG MCP Server" "$PID_DIR/anything_rag_mcp.pid" 8006
    stop_service "MCP Server" "$PID_DIR/mcp.pid" 8001
    stop_service "LightRAG Server" "$PID_DIR/lightrag.pid" 9621
    
    print_success "All services stopped"
}

# =============================================================================
# Service Status Check
# =============================================================================

show_status() {
    echo ""
    printf "${CYAN}================================================================${NC}\n"
    printf "${CYAN}                      Service Status                            ${NC}\n"
    printf "${CYAN}================================================================${NC}\n"
    echo ""

    load_env_file
    local lg_port="${LANGGRAPH_PORT:-2025}"

    show_one_status() {
        local name=$1
        local port=$2
        local pid_file=$3
        shift 3 || true

        local pid=""
        if [ -f "$pid_file" ]; then
            pid="$(cat "$pid_file" 2>/dev/null | tr -d '\r\n ' )"
        fi

        local port_open=false
        if check_port "$port"; then
            port_open=true
        fi

        local http_ok=false
        if [ "$port_open" = true ] && check_http_any 2 "$@"; then
            http_ok=true
        fi

        local owned=false
        if [ -n "$pid" ] && pid_is_running "$pid"; then
            owned=true
        fi

        local listener_pid=""
        if [ "$port_open" = true ]; then
            listener_pid="$(get_pid_by_port "$port" | tr -d '\r\n ')"
        fi

        if [ "$http_ok" = true ] && [ "$owned" = true ]; then
            printf "  ${GREEN}[*]${NC} %-25s ${GREEN}READY${NC} (Port: %s, PID: %s)\n" "$name" "$port" "$pid"
        elif [ "$http_ok" = true ] && [ "$owned" = false ] && [ "$port_open" = true ]; then
            if [ -n "$listener_pid" ]; then
                printf "  ${YELLOW}[!]${NC} %-25s ${YELLOW}READY*${NC} (Port: %s, Listener PID: %s)\n" "$name" "$port" "$listener_pid"
            else
                printf "  ${YELLOW}[!]${NC} %-25s ${YELLOW}READY*${NC} (Port: %s, not managed by pid file)\n" "$name" "$port"
            fi
        elif [ "$port_open" = true ]; then
            if [ -n "$listener_pid" ]; then
                printf "  ${YELLOW}[!]${NC} %-25s ${YELLOW}STARTING/UNHEALTHY${NC} (Port: %s, Listener PID: %s)\n" "$name" "$port" "$listener_pid"
            else
                printf "  ${YELLOW}[!]${NC} %-25s ${YELLOW}STARTING/UNHEALTHY${NC} (Port: %s)\n" "$name" "$port"
            fi
        else
            printf "  ${RED}[ ]${NC} %-25s ${RED}STOPPED${NC} (Port: %s)\n" "$name" "$port"
        fi
    }

    show_one_status "LightRAG Server" 9621 "$PID_DIR/lightrag.pid" \
        "http://127.0.0.1:9621/openapi.json" "http://127.0.0.1:9621/docs"
    show_one_status "MCP Server" 8001 "$PID_DIR/mcp.pid" \
        "http://127.0.0.1:8001/sse"
    show_one_status "Anything RAG MCP Server" 8006 "$PID_DIR/anything_rag_mcp.pid" \
        "http://127.0.0.1:8006/sse"
    show_one_status "RAG MCP Server" 8002 "$PID_DIR/rag_mcp.pid" \
        "http://127.0.0.1:8002/sse"
    show_one_status "Pytest MCP Server" 8004 "$PID_DIR/pytest_mcp.pid" \
        "http://127.0.0.1:8004/sse"
    show_one_status "LangGraph Server" "$lg_port" "$PID_DIR/langgraph.pid" \
        "http://127.0.0.1:${lg_port}/ok"
    show_one_status "Agent UI" 3200 "$PID_DIR/agent_ui.pid" \
        "http://127.0.0.1:3200/"
    
    echo ""
    printf "${CYAN}================================================================${NC}\n"
    echo ""
}

# =============================================================================
# Single Service Restart Functions
# =============================================================================

restart_service() {
    local service_name=$1
    
    case $service_name in
        lightrag)
            stop_service "LightRAG Server" "$PID_DIR/lightrag.pid" 9621
            start_lightrag
            ;;
        mcp)
            stop_service "MCP Server" "$PID_DIR/mcp.pid" 8001
            start_mcp_server
            ;;
        anything-rag-mcp)
            stop_service "Anything RAG MCP Server" "$PID_DIR/anything_rag_mcp.pid" 8006
            start_anything_rag_mcp
            ;;
        api-agent-mcp)
            stop_service "Automation Quality MCP Server" "$PID_DIR/automation_quality_mcp.pid"
            stop_service "Pytest MCP Server" "$PID_DIR/pytest_mcp.pid" 8004
            stop_service "RAG MCP Server" "$PID_DIR/rag_mcp.pid" 8002
            start_api_agent_mcp_servers
            ;;
        langgraph)
            if [ -f "$PROJECT_ROOT/.env" ]; then
                # shellcheck disable=SC1090
                source "$PROJECT_ROOT/.env"
            fi
            stop_service "LangGraph Server" "$PID_DIR/langgraph.pid" "${LANGGRAPH_PORT:-2025}"
            start_langgraph_server
            ;;
        agent-ui)
            stop_service "Agent UI" "$PID_DIR/agent_ui.pid" 3200
            start_agent_ui
            ;;
        *)
            print_error "Unknown service: $service_name"
            echo ""
            echo "Available services:"
            echo "  lightrag   - LightRAG Server (Port 9621)"
            echo "  mcp        - MCP Server (Port 8001)"
            echo "  langgraph  - LangGraph Server (Port 2025, override with LANGGRAPH_PORT)"
            echo "  agent-ui   - Agent UI (Port 3200)"
            exit 1
            ;;
    esac
}

start_single_service() {
    local service_name=$1
    
    case $service_name in
        lightrag)
            start_lightrag
            ;;
        mcp)
            start_mcp_server
            ;;
        anything-rag-mcp)
            start_anything_rag_mcp
            ;;
        api-agent-mcp)
            start_api_agent_mcp_servers
            ;;
        langgraph)
            start_langgraph_server
            ;;
        agent-ui)
            start_agent_ui
            ;;
        *)
            print_error "Unknown service: $service_name"
            echo ""
            echo "Available services:"
            echo "  lightrag      - LightRAG Server (Port 9621)"
            echo "  mcp           - MCP Server (Port 8001)"
            echo "  api-agent-mcp - API Agent MCP Servers (Ports 8002-8004)"
            echo "  langgraph     - LangGraph Server (Port 2025, override with LANGGRAPH_PORT)"
            echo "  agent-ui      - Agent UI (Port 3200)"
            exit 1
            ;;
    esac
}

stop_single_service() {
    local service_name=$1
    
    case $service_name in
        lightrag)
            stop_service "LightRAG Server" "$PID_DIR/lightrag.pid" 9621
            ;;
        mcp)
            stop_service "MCP Server" "$PID_DIR/mcp.pid" 8001
            ;;
        anything-rag-mcp)
            stop_service "Anything RAG MCP Server" "$PID_DIR/anything_rag_mcp.pid" 8006
            ;;
        api-agent-mcp)
            stop_service "Automation Quality MCP Server" "$PID_DIR/automation_quality_mcp.pid"
            stop_service "Pytest MCP Server" "$PID_DIR/pytest_mcp.pid" 8004
            stop_service "RAG MCP Server" "$PID_DIR/rag_mcp.pid" 8002
            ;;
        langgraph)
            if [ -f "$PROJECT_ROOT/.env" ]; then
                # shellcheck disable=SC1090
                source "$PROJECT_ROOT/.env"
            fi
            stop_service "LangGraph Server" "$PID_DIR/langgraph.pid" "${LANGGRAPH_PORT:-2025}"
            ;;
        agent-ui)
            stop_service "Agent UI" "$PID_DIR/agent_ui.pid" 3200
            ;;
        *)
            print_error "Unknown service: $service_name"
            exit 1
            ;;
    esac
}

# =============================================================================
# Main Program
# =============================================================================

main() {
    local include_frontend=false

    # Load .env once so ports/keys apply consistently across start/stop/status/URLs
    load_env_file
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                include_frontend=true
                shift
                ;;
            --stop)
                if [ -n "$2" ] && [[ ! "$2" =~ ^-- ]]; then
                    stop_single_service "$2"
                    print_success "Service $2 stopped"
                    exit 0
                fi
                stop_all
                exit 0
                ;;
            --restart)
                if [ -z "$2" ] || [[ "$2" =~ ^-- ]]; then
                    print_error "Please specify service name to restart"
                echo "Usage: $0 --restart <service_name>"
                echo ""
                echo "Available services:"
                echo "  lightrag   - LightRAG Server (Port 9621)"
                echo "  mcp        - MCP Server (Port 8001)"
                echo "  anything-rag-mcp - LightRAG HTTP MCP Server (Port 8006)"
                echo "  langgraph  - LangGraph Server (Port 2025, override with LANGGRAPH_PORT)"
                echo "  agent-ui   - Agent UI (Port 3200)"
                exit 1
                fi
                print_info "Restarting service: $2"
                restart_service "$2"
                show_status
                exit 0
                ;;
            --start)
                if [ -z "$2" ] || [[ "$2" =~ ^-- ]]; then
                    print_error "Please specify service name to start"
                    exit 1
                fi
                print_info "Starting service: $2"
                start_single_service "$2"
                show_status
                exit 0
                ;;
            --status)
                show_status
                exit 0
                ;;
            --update|-u)
                # Force update flag will be handled in check_venv
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --all              Start all services (including frontend)"
                echo "  --stop             Stop all services"
                echo "  --stop <service>   Stop specific service"
                echo "  --start <service>  Start specific service"
                echo "  --restart <service> Restart specific service"
                echo "  --status           Show service status"
                echo "  --update, -u       Force update dependencies before starting"
                echo "  --help             Show this help"
                echo ""
                echo "Available services:"
                echo "  lightrag      - LightRAG Server (Port 9621)"
                echo "  mcp           - MCP Server (Port 8001)"
                echo "  anything-rag-mcp - LightRAG HTTP MCP Server (Port 8006)"
                echo "  api-agent-mcp - API Agent MCP Servers (Ports 8002-8004)"
                echo "  langgraph     - LangGraph Server (Port 2025, override with LANGGRAPH_PORT)"
                echo "  agent-ui      - Agent UI (Port 3200)"
                echo ""
                echo "Examples:"
                echo "  $0                      # Start all backend services (auto-sync if deps changed)"
                echo "  $0 --all                # Start all services (including frontend)"
                echo "  $0 --update             # Force update dependencies and start services"
                echo "  $0 --restart langgraph  # Restart LangGraph Server"
                echo "  $0 --stop mcp           # Stop MCP Server"
                echo "  $0 --start agent-ui     # Start Agent UI"
                exit 0
                ;;
            *)
                print_error "Unknown argument: $1"
                echo "Use --help to see help information"
                exit 1
                ;;
        esac
    done
    
    print_banner

    # Refresh env after venv checks in case uv scripts updated ENV expectations
    load_env_file
    
    # Check uv
    print_info "Checking uv..."
    check_uv
    print_success "uv is installed"
    
    # Check and create/update virtual environment
    print_info "Checking virtual environment..."
    check_venv "$@"
    print_success "Virtual environment ready"
    
    echo ""
    printf "${CYAN}================================================================${NC}\n"
    printf "${CYAN}                      Starting Services                         ${NC}\n"
    printf "${CYAN}================================================================${NC}\n"
    echo ""
    
    # Start services in order (continue even if one fails)
    local failed_services=()
    
    if start_lightrag; then
        echo ""
    else
        failed_services+=("LightRAG Server")
    echo ""
    fi
    
    if start_mcp_server; then
        echo ""
    else
        failed_services+=("MCP Server")
    echo ""
    fi

    if start_anything_rag_mcp; then
        echo ""
    else
        failed_services+=("Anything RAG MCP Server")
    echo ""
    fi
    
    if start_api_agent_mcp_servers; then
        echo ""
    else
        failed_services+=("API Agent MCP Servers")
    echo ""
    fi
    
    if start_langgraph_server; then
        echo ""
    else
        failed_services+=("LangGraph Server")
    echo ""
    fi
    
    if [ "$include_frontend" = true ]; then
        if start_agent_ui; then
        echo ""
        else
            failed_services+=("Agent UI")
        echo ""
        fi
    fi
    
    # Show status (HTTP-based)
    show_status
    
    # Report results
    if [ ${#failed_services[@]} -eq 0 ]; then
        printf "${GREEN}All services started successfully!${NC}\n"
    else
        printf "${YELLOW}Some services failed to start:${NC}\n"
        for service in "${failed_services[@]}"; do
            printf "  ${RED}-${NC} $service\n"
        done
        printf "${YELLOW}Check logs in $LOG_DIR for details${NC}\n"
    fi
    echo ""
    echo "Common commands:"
    printf "  Check status:   ${CYAN}$0 --status${NC}\n"
    printf "  Stop services:  ${CYAN}$0 --stop${NC}\n"
    printf "  View logs:      ${CYAN}tail -f logs/*.log${NC}\n"
    echo ""
    echo "Access URLs:"
    print_access_url "LightRAG API" "http://127.0.0.1:9621/docs"
    print_access_url "MCP Server" "http://127.0.0.1:8001/sse"
    print_access_url "Anything RAG MCP" "http://127.0.0.1:8006/sse"
    print_access_url "RAG MCP Server" "http://127.0.0.1:8002/sse"
    print_access_url "Pytest MCP Server" "http://127.0.0.1:8004/sse"
    printf "  %-26s %s\n" "Automation Quality MCP" "stdio mode (no HTTP)"
    print_access_url "LangGraph API" "http://127.0.0.1:${LANGGRAPH_PORT:-2025}/docs"
    print_access_url "LangGraph Studio" "http://127.0.0.1:${LANGGRAPH_PORT:-2025}/ui"
    if [ "$include_frontend" = true ]; then
        print_access_url "Agent UI" "http://127.0.0.1:3200/"
    fi

    if [ ${#failed_services[@]} -ne 0 ]; then
        return 1
    fi
    return 0
}

# Run main program
main "$@"
