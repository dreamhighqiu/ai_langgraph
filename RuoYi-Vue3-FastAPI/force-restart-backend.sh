#!/bin/bash
# 强制重启后端服务 - 确保使用最新代码

cd "$(dirname "$0")"

echo "=========================================="
echo "🔄 强制重启后端服务（确保使用最新代码）"
echo "=========================================="
echo ""

# 1. 强制停止所有相关进程
echo "[1/5] 强制停止所有后端相关进程..."
echo "  → 查找所有 Python 进程..."
for pid in $(tasklist /FI "IMAGENAME eq python.exe" /FO CSV | awk -F',' '{print $2}' | tr -d '"' | grep -v PID); do
  if [ -n "$pid" ] && [ "$pid" != "0" ]; then
    # 检查进程是否占用 9099 端口
    if netstat -ano 2>/dev/null | grep -q ":9099.*$pid"; then
      echo "  → 杀掉占用 9099 端口的 Python 进程: $pid"
      taskkill /F /PID $pid 2>/dev/null || kill -9 $pid 2>/dev/null
    fi
  fi
done

# 杀掉所有占用 9099 的进程
echo "  → 杀掉所有占用 9099 端口的进程..."
for pid in $(netstat -ano 2>/dev/null | awk '/:9099/ {print $5}' | sort -u); do
  if [ "$pid" != "0" ] && [ -n "$pid" ] && [ "$pid" != "-" ]; then
    echo "  → 杀掉进程 PID: $pid"
    taskkill /F /PID $pid 2>/dev/null || kill -9 $pid 2>/dev/null
  fi
done

# 清理 PID 文件
rm -f .pids/backend.pid
sleep 3

# 2. 确认端口已释放
echo "[2/5] 确认端口已释放..."
if netstat -ano 2>/dev/null | grep -q ":9099.*LISTENING"; then
  echo "  ⚠️  警告: 端口 9099 仍被占用"
  netstat -ano | grep :9099
  echo ""
  echo "  请手动杀掉上述进程，然后重新运行此脚本"
  exit 1
else
  echo "  ✅ 端口 9099 已完全释放"
fi

# 3. 检查代码是否有语法错误
echo "[3/5] 检查代码语法..."
cd ruoyi-fastapi-backend

if [ ! -d ".venv" ]; then
  echo "  ❌ 错误: 虚拟环境不存在"
  exit 1
fi

# 激活虚拟环境
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "mingw"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

# 检查 Python 语法
echo "  → 检查 agent_controller.py 语法..."
python -m py_compile module_testing/controller/agent_controller.py 2>&1
if [ $? -ne 0 ]; then
  echo "  ❌ agent_controller.py 有语法错误！"
  exit 1
fi
echo "  ✅ 语法检查通过"

# 4. 测试路由导入
echo "[4/5] 测试路由导入..."
python ../check_routes.py 2>&1
if [ $? -ne 0 ]; then
  echo "  ⚠️  路由检查有警告，但继续启动..."
fi

# 5. 启动服务
echo "[5/5] 启动后端服务..."
export APP_ENV=dev

# 创建日志目录
mkdir -p ../logs

# 启动服务（使用 uvicorn，确保热重载）
echo "  → 启动 uvicorn (端口: 9099, 热重载: 已启用)..."
nohup uvicorn app:app --host 0.0.0.0 --port 9099 --reload --reload-dir . > ../logs/backend.log 2>&1 &
backend_pid=$!
echo $backend_pid > ../.pids/backend.pid

# 等待启动
echo "  → 等待服务启动..."
sleep 8

# 验证
if kill -0 $backend_pid 2>/dev/null; then
  if netstat -ano 2>/dev/null | grep -q ":9099.*LISTENING"; then
    echo ""
    echo "=========================================="
    echo "✅ 后端服务启动成功！"
    echo "=========================================="
    echo ""
    echo "  📍 服务信息:"
    echo "    PID:      $backend_pid"
    echo "    地址:     http://localhost:9099/dev-api"
    echo "    文档:     http://localhost:9099/dev-api/docs"
    echo "    日志:     logs/backend.log"
    echo ""
    echo "  🔥 热重载: 已启用"
    echo ""
    echo "=========================================="
    echo ""
    echo "📝 最近日志:"
    echo "----------------------------------------"
    tail -15 ../logs/backend.log
    echo "----------------------------------------"
    echo ""
    echo "🔍 验证路由注册:"
    echo "  访问: http://localhost:9099/dev-api/docs"
    echo "  查找: /testing/agent 相关接口"
    echo ""
  else
    echo ""
    echo "⚠️  进程已启动但端口未监听"
    echo "📝 错误日志:"
    tail -30 ../logs/backend.log
    exit 1
  fi
else
  echo ""
  echo "❌ 后端服务启动失败！"
  echo "📝 错误日志:"
  tail -30 ../logs/backend.log
  exit 1
fi

cd ..

