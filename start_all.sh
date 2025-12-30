#!/bin/bash
# =============================================================================
# AI LangGraph Service Starter (using uv)
# 
# Function: One-click start all backend services (using unified virtual environment managed by uv)
# 
# Service List:
#   1. LightRAG Server (Knowledge Base)     - http://localhost:9621
#   2. MCP Server (RAG Anything)            - http://localhost:8001
#   3. LangGraph Server (Agent Backend)     - http://localhost:2025
#   4. AI Platform Backend (Main Backend)   - http://localhost:9999
#   5. AI Platform Frontend (Frontend UI)   - http://localhost:5174
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
else
    # Linux/macOS
    VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"
    VENV_BIN="$PROJECT_ROOT/.venv/bin"
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
    
    # Install LightRAG in editable mode
    print_info "Installing LightRAG..."
    uv pip install -e ./anything-chat-rag --no-deps
    
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
    
    # Ensure port is free (MCP Server must use fixed port 8001)
    if ! ensure_port_free $port "$name"; then
        print_error "Cannot start $name: port $port is occupied and cannot be freed"
        return 1
    fi
    
    print_info "Starting $name..."
    
    cd "$PROJECT_ROOT/mcp-server/src"
    export PATH="$VENV_BIN:$PATH"
    export PYTHONIOENCODING=utf-8
    # Add current directory to Python path
    export PYTHONPATH="$PROJECT_ROOT/mcp-server/src:$PYTHONPATH"
    # Use python -m with explicit path or direct script execution
    nohup "$VENV_PYTHON" -m mcp_server_rag_anything.server > "$log_file" 2>&1 &
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
            echo "  lightrag   - LightRAG Server (Port 9621)"
            echo "  mcp        - MCP Server (Port 8001)"
            echo "  langgraph  - LangGraph Server (Port 2025)"
            echo "  agent-ui   - Agent UI (Port 3200)"
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
                echo "  lightrag   - LightRAG Server (Port 9621)"
                echo "  mcp        - MCP Server (Port 8001)"
                echo "  langgraph  - LangGraph Server (Port 2025)"
                echo "  agent-ui   - Agent UI (Port 3200)"
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
    printf "  LangGraph API:    ${CYAN}http://localhost:2025/docs${NC}\n"
    printf "  LangGraph Studio: ${CYAN}http://localhost:2025/ui${NC}\n"
    if [ "$include_frontend" = true ]; then
        printf "  Agent UI:         ${CYAN}http://localhost:3200${NC}\n"
    fi
}

# Run main program
main "$@"