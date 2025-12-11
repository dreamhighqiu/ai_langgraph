#!/bin/bash

# 智能体引擎切换测试脚本

set -e

PROJECT_ROOT="/Users/qiuyunxia/code/ai_langGraph"
ENV_FILE="$PROJECT_ROOT/.env"
LOG_FILE="$PROJECT_ROOT/logs/platform.log"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  🔄 智能体引擎切换测试"
echo "=========================================="
echo ""

# 检查当前配置
echo -e "${BLUE}📋 检查当前配置${NC}"
echo "----------------------------------------"
if grep -q "^AGENT_FRAMEWORK=" "$ENV_FILE" 2>/dev/null; then
    CURRENT=$(grep "^AGENT_FRAMEWORK=" "$ENV_FILE" | cut -d'=' -f2)
    echo "   当前配置: $CURRENT"
else
    echo "   当前配置: 未设置（默认为 autogen）"
    CURRENT="autogen"
fi
echo ""

# 函数: 设置框架
set_framework() {
    local framework=$1
    echo -e "${BLUE}⚙️  设置框架为: ${framework}${NC}"
    
    if grep -q "^AGENT_FRAMEWORK=" "$ENV_FILE" 2>/dev/null; then
        # 替换现有配置
        sed -i.bak "s/^AGENT_FRAMEWORK=.*/AGENT_FRAMEWORK=${framework}/" "$ENV_FILE"
    else
        # 添加新配置
        echo "" >> "$ENV_FILE"
        echo "# 智能体框架配置" >> "$ENV_FILE"
        echo "AGENT_FRAMEWORK=${framework}" >> "$ENV_FILE"
    fi
    
    # 验证
    if grep -q "^AGENT_FRAMEWORK=${framework}$" "$ENV_FILE"; then
        echo -e "   ${GREEN}✅ 配置已更新${NC}"
    else
        echo -e "   ${RED}❌ 配置更新失败${NC}"
        exit 1
    fi
}

# 函数: 重启平台
restart_platform() {
    echo -e "${BLUE}🔄 重启平台服务${NC}"
    cd "$PROJECT_ROOT"
    ./start_all.sh --restart platform > /dev/null 2>&1
    sleep 3
    echo -e "   ${GREEN}✅ 平台已重启${NC}"
}

# 函数: 检查日志
check_logs() {
    local framework=$1
    local framework_cap=$(echo "$framework" | sed 's/./\U&/')
    
    echo -e "${BLUE}📝 检查日志输出${NC}"
    echo "----------------------------------------"
    
    # 查找最近的相关日志
    local log_count=$(tail -100 "$LOG_FILE" 2>/dev/null | grep -c "\[$framework_cap\]" || echo "0")
    
    if [ "$log_count" -gt 0 ]; then
        echo -e "   ${GREEN}✅ 找到 $log_count 条 [$framework_cap] 日志${NC}"
        echo ""
        echo "   最近的日志:"
        tail -100 "$LOG_FILE" | grep "\[$framework_cap\]" | head -5 | while read line; do
            echo "     $line"
        done
    else
        echo -e "   ${YELLOW}⚠️  未找到 [$framework_cap] 日志${NC}"
        echo "   可能需要执行一次需求分析来触发日志"
    fi
}

# 测试 1: Autogen
echo ""
echo "=========================================="
echo "  1️⃣  测试 Autogen 引擎"
echo "=========================================="
echo ""

set_framework "autogen"
restart_platform
check_logs "Autogen"

echo ""
echo "  ${GREEN}✅ Autogen 测试完成${NC}"
echo ""

# 询问是否继续测试 DeepAgents
read -p "是否继续测试 DeepAgents？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 测试 2: DeepAgents
    echo ""
    echo "=========================================="
    echo "  2️⃣  测试 DeepAgents 引擎"
    echo "=========================================="
    echo ""
    
    set_framework "deepagents"
    restart_platform
    check_logs "Deepagents"
    
    echo ""
    echo "  ${GREEN}✅ DeepAgents 测试完成${NC}"
    echo ""
fi

# 恢复原始配置
echo ""
echo "=========================================="
echo "  🔙 恢复原始配置"
echo "=========================================="
echo ""

set_framework "$CURRENT"
restart_platform

echo -e "${GREEN}✅ 已恢复到原始配置: $CURRENT${NC}"
echo ""

# 总结
echo "=========================================="
echo "  ✅ 测试完成！"
echo "=========================================="
echo ""
echo "📊 测试结果:"
echo "  - Autogen:    ✅ 已测试"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  - DeepAgents: ✅ 已测试"
else
    echo "  - DeepAgents: ⏭️  已跳过"
fi
echo "  - 当前配置:   $CURRENT"
echo ""
echo "💡 提示:"
echo "  - 查看实时日志: tail -f logs/platform.log | grep '\[.*agents\]' -i"
echo "  - 手动切换框架: 修改 .env 文件的 AGENT_FRAMEWORK 变量"
echo "  - 查看详细文档: cat AGENT_FRAMEWORK_SWITCH_GUIDE.md"
echo ""

