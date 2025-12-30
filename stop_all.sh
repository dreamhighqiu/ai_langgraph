#!/bin/bash
# AI智能测试平台 - 停止所有服务脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "═══════════════════════════════════════════"
echo "   停止AI智能测试平台所有服务"
echo "═══════════════════════════════════════════"
echo ""

# 停止Agent服务
if [ -f ".pids/agents.pid" ]; then
    AGENTS_PID=$(cat .pids/agents.pid)
    if ps -p $AGENTS_PID > /dev/null 2>&1; then
        print_info "停止Agent服务 (PID: $AGENTS_PID)..."
        kill $AGENTS_PID
        print_success "Agent服务已停止"
    else
        print_info "Agent服务未运行"
    fi
    rm .pids/agents.pid
fi

# 停止后端服务
if [ -f ".pids/backend.pid" ]; then
    BACKEND_PID=$(cat .pids/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        print_info "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        print_success "后端服务已停止"
    else
        print_info "后端服务未运行"
    fi
    rm .pids/backend.pid
fi

# 停止前端服务
if [ -f ".pids/frontend.pid" ]; then
    FRONTEND_PID=$(cat .pids/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        print_info "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        print_success "前端服务已停止"
    else
        print_info "前端服务未运行"
    fi
    rm .pids/frontend.pid
fi

echo ""
print_success "所有服务已停止"

