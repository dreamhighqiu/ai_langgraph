#!/bin/bash

# DeepSeek自动化测试运行脚本

echo "========================================="
echo "DeepSeek网站自动化测试"
echo "========================================="

# 检查Java环境
echo "检查Java环境..."
java -version
if [ $? -ne 0 ]; then
    echo "错误: Java未安装或未配置"
    exit 1
fi

# 检查Maven环境
echo "检查Maven环境..."
mvn -version
if [ $? -ne 0 ]; then
    echo "错误: Maven未安装或未配置"
    exit 1
fi

# 创建必要的目录
echo "创建测试目录..."
mkdir -p screenshots
mkdir -p target

# 清理并安装依赖
echo "清理并安装依赖..."
mvn clean compile

if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

# 运行测试
echo "开始运行测试..."
echo "========================================="

# 根据参数运行不同的测试
if [ "$1" == "smoke" ]; then
    echo "运行冒烟测试..."
    mvn test -Dgroups=smoke
elif [ "$1" == "regression" ]; then
    echo "运行回归测试..."
    mvn test -Dgroups=regression
elif [ "$1" == "all" ]; then
    echo "运行所有测试..."
    mvn test
elif [ "$1" == "single" ] && [ -n "$2" ]; then
    echo "运行单个测试: $2"
    mvn test -Dtest="$2"
else
    echo "运行默认测试套件..."
    mvn test -Dtest=DeepSeekFunctionalTests
fi

# 检查测试结果
TEST_RESULT=$?
echo "========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ 所有测试通过!"
else
    echo "❌ 测试失败!"
    
    # 显示失败的截图
    if [ -d "screenshots" ] && [ "$(ls -A screenshots)" ]; then
        echo "失败的截图已保存到 screenshots/ 目录"
    fi
fi

echo "========================================="
echo "测试完成"
exit $TEST_RESULT