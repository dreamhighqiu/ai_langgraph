#!/bin/bash
# 修复前端依赖安装脚本

echo "正在修复前端依赖..."

# 删除旧的依赖
echo "1. 清理旧的依赖..."
rm -rf node_modules
rm -f package-lock.json
rm -rf .vite

# 清理 npm 缓存
echo "2. 清理 npm 缓存..."
npm cache clean --force

# 重新安装
echo "3. 重新安装依赖（这可能需要几分钟）..."
npm install

# 验证安装
echo "4. 验证安装..."
if [ -f "node_modules/.bin/vite" ]; then
    echo "✅ vite 安装成功！"
    echo ""
    echo "现在可以运行: npm run dev"
else
    echo "❌ vite 安装失败，请检查网络或使用国内镜像："
    echo "   npm config set registry https://registry.npmmirror.com"
    echo "   然后重新运行: npm install"
fi

