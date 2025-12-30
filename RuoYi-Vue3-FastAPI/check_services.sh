#!/bin/bash
# 服务状态检查脚本

echo "========== 服务状态检查 =========="
echo ""

# 检查后端
echo "后端服务:"
if [ -f ".pids/backend.pid" ]; then
    pid=$(cat .pids/backend.pid)
    if kill -0 $pid 2>/dev/null; then
        echo "  ✅ 进程运行中 (PID: $pid)"
        
        # 检查端口
        if nc -z localhost 9099 2>/dev/null || timeout 1 bash -c "echo >/dev/tcp/localhost/9099" 2>/dev/null; then
            echo "  ✅ 端口 9099 已监听"
            
            # 测试API
            response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9099/dev-api/docs 2>/dev/null || echo "000")
            if [ "$response" = "200" ]; then
                echo "  ✅ API 可访问 (http://localhost:9099/dev-api/docs)"
            else
                echo "  ⚠️  API 返回状态码: $response"
            fi
        else
            echo "  ❌ 端口 9099 未监听"
        fi
    else
        echo "  ❌ 进程不存在"
    fi
else
    echo "  ❌ PID文件不存在"
fi

echo ""

# 检查前端
echo "前端服务:"
if [ -f ".pids/frontend.pid" ]; then
    pid=$(cat .pids/frontend.pid)
    if kill -0 $pid 2>/dev/null; then
        echo "  ✅ 进程运行中 (PID: $pid)"
        
        # 检查端口
        if nc -z localhost 5173 2>/dev/null || timeout 1 bash -c "echo >/dev/tcp/localhost/5173" 2>/dev/null; then
            echo "  ✅ 端口 5173 已监听"
            echo "  ✅ 前端可访问 (http://localhost:5173)"
        else
            echo "  ❌ 端口 5173 未监听"
        fi
    else
        echo "  ❌ 进程不存在"
    fi
else
    echo "  ❌ PID文件不存在"
fi

echo ""
echo "========== 日志文件 =========="
if [ -f "logs/backend.log" ]; then
    echo "后端日志 (最后10行):"
    tail -10 logs/backend.log
else
    echo "后端日志文件不存在"
fi

echo ""
if [ -f "logs/frontend.log" ]; then
    echo "前端日志 (最后10行):"
    tail -10 logs/frontend.log
else
    echo "前端日志文件不存在"
fi

