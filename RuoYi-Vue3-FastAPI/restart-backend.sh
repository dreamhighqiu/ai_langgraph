#!/bin/bash
# 快速重启后端服务脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "🔄 手动重启后端服务"
echo "=========================================="
echo ""

# 1. 停止后端服务
echo "[1/4] 停止后端服务..."
for pid in $(netstat -ano 2>/dev/null | awk '/:9099/ {print $5}' | sort -u); do
  if [ "$pid" != "0" ] && [ -n "$pid" ] && [ "$pid" != "-" ]; then
    echo "  → 杀掉进程 PID: $pid"
    taskkill /F /PID $pid 2>/dev/null || kill -9 $pid 2>/dev/null
  fi
done
rm -f .pids/backend.pid
sleep 2

# 2. 确认端口已释放
echo "[2/4] 确认端口已释放..."
if netstat -ano 2>/dev/null | grep -q ":9099.*LISTENING"; then
  echo "  ⚠️  警告: 端口 9099 仍被占用，请手动检查"
  netstat -ano | grep :9099
  read -p "  是否继续? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
else
  echo "  ✅ 端口 9099 已释放"
fi

# 3. 启动后端服务
echo "[3/4] 启动后端服务..."
cd ruoyi-fastapi-backend

# 检查虚拟环境
if [ ! -d ".venv" ]; then
  echo "  ❌ 错误: 虚拟环境不存在，请先运行: ./deploy-local.sh init"
  exit 1
fi

# 激活虚拟环境
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "mingw"* ]] || [[ "$OSTYPE" == "cygwin"* ]]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

export APP_ENV=dev

# 创建日志目录
mkdir -p ../logs

# 启动服务
echo "  → 启动 uvicorn (端口: 9099, 热重载: 已启用)..."
nohup uvicorn app:app --host 0.0.0.0 --port 9099 --reload --reload-dir . > ../logs/backend.log 2>&1 &
backend_pid=$!
echo $backend_pid > ../.pids/backend.pid

# 4. 验证启动
echo "[4/4] 验证服务启动..."
sleep 5

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
    echo "  🔥 热重载: 已启用 (代码更改自动生效)"
    echo ""
    echo "=========================================="
    
    # 显示最后几行日志
    echo ""
    echo "📝 最近日志:"
    echo "----------------------------------------"
    tail -10 ../logs/backend.log
    echo "----------------------------------------"
  else
    echo ""
    echo "⚠️  进程已启动但端口未监听，请查看日志:"
    tail -30 ../logs/backend.log
    exit 1
  fi
else
  echo ""
  echo "❌ 后端服务启动失败！"
  echo ""
  echo "📝 错误日志:"
  echo "----------------------------------------"
  tail -30 ../logs/backend.log
  echo "----------------------------------------"
  exit 1
fi

cd ..

