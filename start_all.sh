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
#      - Login MCP Server                   - http://localhost:8003/sse
#      - Test Executor MCP Server           - http://localhost:8004/sse
#      - Pytest Generator MCP Server        - http://localhost:8005/sse
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
            if command -v taskkill &> /dev/null; then
                taskkill /F /PID "$pid" >/dev/null 2>&1 && killed=true
            else
                # Fallback: try kill command (Git Bash)
                kill -9 "$pid" >/dev/null 2>&1 && killed=true
            fi
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
    local site_packages=$("$VENV_PYTHON" -c "import site; print(site.getsitepackages()[0])")
    cat > "$site_packages/ai-langgraph.pth" << EOF
$PROJECT_ROOT/testing-agents-service/testing-agents-service/src
$PROJECT_ROOT/mcp-server/src
EOF
    
    # Ensure mcp-server/src is in Python path (for Windows compatibility)
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # Convert to Windows path format for .pth file
        local mcp_path_win=$(cygpath -w "$PROJECT_ROOT/mcp-server/src" 2>/dev/null || echo "$PROJECT_ROOT/mcp-server/src")
        local testing_path_win=$(cygpath -w "$PROJECT_ROOT/testing-agents-service/testing-agents-service/src" 2>/dev/null || echo "$PROJECT_ROOT/testing-agents-service/testing-agents-service/src")
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
    if wait_for_service $port "$name" 90; then
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
    
    if wait_for_service $port "$name"; then
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

    if wait_for_service $port "$name" 30; then
        print_success "$name started (PID: $pid, Port: $port)"
    else
        print_warning "$name may not have started properly, check log: $log_file"
    fi
}

start_api_agent_mcp_servers() {
    local src_dir="$PROJECT_ROOT/testing-agents-service/testing-agents-service/src"
    local services_dir="$src_dir/api_agent/mcp_servers"
    
    print_info "Starting API Agent MCP Servers..."
    
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
    else
        print_info "Starting $rag_name on port $rag_port..."
        # Run from project root with PYTHONPATH set (export already done above)
        cd "$PROJECT_ROOT"
        # Ensure PYTHONPATH is set for this command
        PYTHONPATH="$src_dir:$PYTHONPATH" nohup "$VENV_PYTHON" -m api_agent.mcp_servers.rag_mcp_server --port $rag_port > "$rag_log_file" 2>&1 &
        local rag_pid=$!
        echo $rag_pid > "$rag_pid_file"
        
        if wait_for_service $rag_port "$rag_name" 30; then
            print_success "$rag_name started (PID: $rag_pid, Port: $rag_port)"
        else
            print_warning "$rag_name may not have started properly, check log: $rag_log_file"
        fi
    fi
    
    # Start Login MCP Server (port 8003)
    local login_port=8003
    local login_name="Login MCP Server"
    local login_pid_file="$PID_DIR/login_mcp.pid"
    local login_log_file="$LOG_DIR/login_mcp.log"
    
    if ! ensure_port_free $login_port "$login_name"; then
        print_warning "Port $login_port is occupied, skipping $login_name"
    else
        print_info "Starting $login_name on port $login_port..."
        # Run from project root with PYTHONPATH set
        cd "$PROJECT_ROOT"
        PYTHONPATH="$src_dir:$PYTHONPATH" nohup "$VENV_PYTHON" -m api_agent.mcp_servers.login_mcp_server --port $login_port > "$login_log_file" 2>&1 &
        local login_pid=$!
        echo $login_pid > "$login_pid_file"
        
        if wait_for_service $login_port "$login_name" 30; then
            print_success "$login_name started (PID: $login_pid, Port: $login_port)"
        else
            print_warning "$login_name may not have started properly, check log: $login_log_file"
        fi
    fi
    
    # Start Pytest Generator MCP Server (port 8005 - changed from 8003 to avoid conflict)
    local pytest_gen_port=8005
    local pytest_gen_name="Pytest Generator MCP Server"
    local pytest_gen_pid_file="$PID_DIR/pytest_generator_mcp.pid"
    local pytest_gen_log_file="$LOG_DIR/pytest_generator_mcp.log"
    
    if ! ensure_port_free $pytest_gen_port "$pytest_gen_name"; then
        print_warning "Port $pytest_gen_port is occupied, skipping $pytest_gen_name"
    else
        print_info "Starting $pytest_gen_name on port $pytest_gen_port..."
        # Run from project root with PYTHONPATH set
        cd "$PROJECT_ROOT"
        PYTHONPATH="$src_dir:$PYTHONPATH" nohup "$VENV_PYTHON" -m api_agent.mcp_servers.pytest_generator --port $pytest_gen_port > "$pytest_gen_log_file" 2>&1 &
        local pytest_gen_pid=$!
        echo $pytest_gen_pid > "$pytest_gen_pid_file"
        
        if wait_for_service $pytest_gen_port "$pytest_gen_name" 30; then
            print_success "$pytest_gen_name started (PID: $pytest_gen_pid, Port: $pytest_gen_port)"
        else
            print_warning "$pytest_gen_name may not have started properly, check log: $pytest_gen_log_file"
        fi
    fi
    
    # Start Pytest Generator MCP Server (port 8005 - changed from 8003 to avoid conflict with login_mcp)
    local pytest_gen_port=8005
    local pytest_gen_name="Pytest Generator MCP Server"
    local pytest_gen_pid_file="$PID_DIR/pytest_generator_mcp.pid"
    local pytest_gen_log_file="$LOG_DIR/pytest_generator_mcp.log"
    
    if ! ensure_port_free $pytest_gen_port "$pytest_gen_name"; then
        print_warning "Port $pytest_gen_port is occupied, skipping $pytest_gen_name"
    else
        print_info "Starting $pytest_gen_name on port $pytest_gen_port..."
        # Run from project root with PYTHONPATH set
        cd "$PROJECT_ROOT"
        PYTHONPATH="$src_dir:$PYTHONPATH" nohup "$VENV_PYTHON" -m api_agent.mcp_servers.pytest_generator --port $pytest_gen_port > "$pytest_gen_log_file" 2>&1 &
        local pytest_gen_pid=$!
        echo $pytest_gen_pid > "$pytest_gen_pid_file"
        
        if wait_for_service $pytest_gen_port "$pytest_gen_name" 30; then
            print_success "$pytest_gen_name started (PID: $pytest_gen_pid, Port: $pytest_gen_port)"
        else
            print_warning "$pytest_gen_name may not have started properly, check log: $pytest_gen_log_file"
        fi
    fi
    
    # Start Test Executor MCP Server (port 8004)
    local executor_port=8004
    local executor_name="Test Executor MCP Server"
    local executor_pid_file="$PID_DIR/test_executor_mcp.pid"
    local executor_log_file="$LOG_DIR/test_executor_mcp.log"
    
    if ! ensure_port_free $executor_port "$executor_name"; then
        print_warning "Port $executor_port is occupied, skipping $executor_name"
    else
        print_info "Starting $executor_name on port $executor_port..."
        # Run from project root with PYTHONPATH set
        cd "$PROJECT_ROOT"
        PYTHONPATH="$src_dir:$PYTHONPATH" nohup "$VENV_PYTHON" -m api_agent.mcp_servers.test_executor --port $executor_port > "$executor_log_file" 2>&1 &
        local executor_pid=$!
        echo $executor_pid > "$executor_pid_file"
        
        if wait_for_service $executor_port "$executor_name" 30; then
            print_success "$executor_name started (PID: $executor_pid, Port: $executor_port)"
        else
            print_warning "$executor_name may not have started properly, check log: $executor_log_file"
        fi
    fi
    
    # Start Automation Quality MCP Server (Node.js stdio mode, no port needed)
    local automation_mcp_name="Automation Quality MCP Server"
    local automation_mcp_pid_file="$PID_DIR/automation_quality_mcp.pid"
    local automation_mcp_log_file="$LOG_DIR/automation_quality_mcp.log"
    local automation_mcp_dir="$services_dir/automation-quality-mcp"
    
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
    
    if [ -d "$automation_mcp_dir/node_modules" ]; then
        print_info "Starting $automation_mcp_name (stdio mode)..."
        cd "$automation_mcp_dir"
        # Automation Quality MCP uses stdio mode, not SSE, so no port check needed
        # It will be used via stdio by LangGraph when needed
        # We can start it in the background for monitoring, but it won't listen on a port
        nohup node mcpServer.js > "$automation_mcp_log_file" 2>&1 &
        local automation_mcp_pid=$!
        echo $automation_mcp_pid > "$automation_mcp_pid_file"
        print_success "$automation_mcp_name started (PID: $automation_mcp_pid, stdio mode)"
        cd "$PROJECT_ROOT"
    fi
    
    # Start Automation Quality MCP Server (Node.js stdio mode, no port needed)
    local automation_mcp_name="Automation Quality MCP Server"
    local automation_mcp_pid_file="$PID_DIR/automation_quality_mcp.pid"
    local automation_mcp_log_file="$LOG_DIR/automation_quality_mcp.log"
    local automation_mcp_dir="$services_dir/automation-quality-mcp"
    
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
    
    if [ -d "$automation_mcp_dir/node_modules" ]; then
        print_info "Starting $automation_mcp_name (stdio mode)..."
        cd "$automation_mcp_dir"
        # Automation Quality MCP uses stdio mode, not SSE, so no port check needed
        # It will be used via stdio by LangGraph when needed
        # We can start it in the background for monitoring, but it won't listen on a port
        nohup node mcpServer.js > "$automation_mcp_log_file" 2>&1 &
        local automation_mcp_pid=$!
        echo $automation_mcp_pid > "$automation_mcp_pid_file"
        print_success "$automation_mcp_name started (PID: $automation_mcp_pid, stdio mode)"
        cd "$PROJECT_ROOT"
    fi
    
    cd "$PROJECT_ROOT"
    echo ""
}

start_langgraph_server() {
    local port=2025
    local name="LangGraph Server"
    local pid_file="$PID_DIR/langgraph.pid"
    local log_file="$LOG_DIR/langgraph.log"
    
    # Ensure port is free
    if ! ensure_port_free $port "$name"; then
        print_error "Cannot start $name: port $port is occupied and cannot be freed"
        return 1
    fi
    
    print_info "Starting $name..."
    
    # Install Node.js dependencies for automation-quality-mcp if needed
    local automation_mcp_dir="$PROJECT_ROOT/testing-agents-service/testing-agents-service/src/api_agent/mcp_servers/automation-quality-mcp"
    if [ -d "$automation_mcp_dir" ] && [ ! -d "$automation_mcp_dir/node_modules" ]; then
        print_info "Installing Node.js dependencies for automation-quality-mcp..."
        cd "$automation_mcp_dir"
        if command -v npm &> /dev/null; then
            npm install 2>&1 | head -20
        else
            print_warning "npm not found, automation-quality-mcp may not work"
        fi
        cd "$PROJECT_ROOT"
    fi
    
    cd "$PROJECT_ROOT/testing-agents-service/testing-agents-service"
    export PATH="$VENV_BIN:$PATH"
    export PYTHONIOENCODING=utf-8
    # Add testing-agents-service/src to Python path
    export PYTHONPATH="$PROJECT_ROOT/testing-agents-service/testing-agents-service/src:$PYTHONPATH"
    nohup "$VENV_PYTHON" start_server.py > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    cd "$PROJECT_ROOT"
    
    # LangGraph may take longer to initialize (graph loading, MCP connections)
    if wait_for_service $port "$name" 120; then
        print_success "$name started (PID: $pid, Port: $port)"
        printf "         API Docs: ${CYAN}http://localhost:$port/docs${NC}\n"
        printf "         Studio:   ${CYAN}http://localhost:$port/ui${NC}\n"
    else
        print_error "$name failed to start, check log: $log_file"
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
    
    if wait_for_service $port "$name"; then
        print_success "$name started (PID: $pid, Port: $port)"
        printf "         URL: ${CYAN}http://localhost:$port${NC}\n"
    else
        print_error "$name failed to start, check log: $log_file"
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
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "Stopped $name (PID: $pid)"
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
                        if command -v taskkill &> /dev/null; then
                            taskkill /F /PID "$pid" >/dev/null 2>&1
                        else
                            kill -9 "$pid" >/dev/null 2>&1
                        fi
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
    
    stop_service "Agent UI" "$PID_DIR/agent_ui.pid" 3200
    stop_service "LangGraph Server" "$PID_DIR/langgraph.pid" 2025
    stop_service "Automation Quality MCP Server" "$PID_DIR/automation_quality_mcp.pid"
    stop_service "Test Executor MCP Server" "$PID_DIR/test_executor_mcp.pid" 8004
    stop_service "Pytest Generator MCP Server" "$PID_DIR/pytest_generator_mcp.pid" 8005
    stop_service "Login MCP Server" "$PID_DIR/login_mcp.pid" 8003
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
    
    local services=(
        "LightRAG Server:9621"
        "MCP Server:8001"
        "Anything RAG MCP Server:8006"
        "RAG MCP Server:8002"
        "Login MCP Server:8003"
        "Test Executor MCP Server:8004"
        "Pytest Generator MCP Server:8005"
        "LangGraph Server:2025"
        "Agent UI:3200"
    )
    
    for service in "${services[@]}"; do
        local name="${service%%:*}"
        local port="${service##*:}"
        
        if check_port $port; then
            printf "  ${GREEN}[*]${NC} %-25s ${GREEN}RUNNING${NC} (Port: $port)\n" "$name"
        else
            printf "  ${RED}[ ]${NC} %-25s ${RED}STOPPED${NC} (Port: $port)\n" "$name"
        fi
    done
    
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
            stop_service "Test Executor MCP Server" "$PID_DIR/test_executor_mcp.pid" 8004
            stop_service "Pytest Generator MCP Server" "$PID_DIR/pytest_generator_mcp.pid" 8005
            stop_service "Login MCP Server" "$PID_DIR/login_mcp.pid" 8003
            stop_service "RAG MCP Server" "$PID_DIR/rag_mcp.pid" 8002
            start_api_agent_mcp_servers
            ;;
        langgraph)
            stop_service "LangGraph Server" "$PID_DIR/langgraph.pid" 2025
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
            echo "  langgraph  - LangGraph Server (Port 2025)"
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
            echo "  langgraph     - LangGraph Server (Port 2025)"
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
            stop_service "Test Executor MCP Server" "$PID_DIR/test_executor_mcp.pid" 8004
            stop_service "Pytest Generator MCP Server" "$PID_DIR/pytest_generator_mcp.pid" 8005
            stop_service "Login MCP Server" "$PID_DIR/login_mcp.pid" 8003
            stop_service "RAG MCP Server" "$PID_DIR/rag_mcp.pid" 8002
            ;;
        langgraph)
            stop_service "LangGraph Server" "$PID_DIR/langgraph.pid" 2025
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
                echo "  langgraph  - LangGraph Server (Port 2025)"
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
                echo "  langgraph     - LangGraph Server (Port 2025)"
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
    
    # Show status
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
    printf "  LightRAG API:     ${CYAN}http://localhost:9621/docs${NC}\n"
    printf "  Anything RAG MCP: ${CYAN}http://localhost:8006/sse${NC}\n"
    printf "  RAG MCP Server:         ${CYAN}http://localhost:8002/sse${NC}\n"
    printf "  Login MCP Server:      ${CYAN}http://localhost:8003/sse${NC}\n"
    printf "  Test Executor MCP:      ${CYAN}http://localhost:8004/sse${NC}\n"
    printf "  Pytest Generator MCP:  ${CYAN}http://localhost:8005/sse${NC}\n"
    printf "  Automation Quality MCP: ${CYAN}stdio mode (no HTTP)${NC}\n"
    printf "  LangGraph API:    ${CYAN}http://localhost:2025/docs${NC}\n"
    printf "  LangGraph Studio: ${CYAN}http://localhost:2025/ui${NC}\n"
    if [ "$include_frontend" = true ]; then
        printf "  Agent UI:         ${CYAN}http://localhost:3200${NC}\n"
    fi
}

# Run main program
main "$@"
