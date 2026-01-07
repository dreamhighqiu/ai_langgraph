#!/bin/bash

# K6首页冒烟测试运行脚本
# 使用方法: ./run_smoke_test.sh [access_token]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本信息
SCRIPT_NAME="home_page_smoke_test.js"
SCRIPT_PATH="/k6_scripts/$SCRIPT_NAME"

# 检查K6是否安装
check_k6_installed() {
    if ! command -v k6 &> /dev/null; then
        echo -e "${RED}错误: K6未安装${NC}"
        echo "请先安装K6:"
        echo "  macOS: brew install k6"
        echo "  Windows: choco install k6"
        echo "  Linux: sudo apt-get install k6"
        exit 1
    fi
    echo -e "${GREEN}✓ K6已安装${NC}"
}

# 检查脚本文件
check_script_file() {
    if [ ! -f "$SCRIPT_PATH" ]; then
        echo -e "${RED}错误: 脚本文件不存在: $SCRIPT_PATH${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 脚本文件存在${NC}"
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}K6首页冒烟测试运行脚本${NC}"
    echo ""
    echo "使用方法:"
    echo "  $0 [access_token] [options]"
    echo ""
    echo "参数:"
    echo "  access_token   访问令牌（可选，也可以通过环境变量设置）"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -d, --debug    启用调试模式"
    echo "  -v, --vus NUM  设置虚拟用户数量（默认: 10）"
    echo "  -t, --time SEC 设置测试时长（默认: 30s）"
    echo "  -e, --env FILE 使用环境变量文件"
    echo ""
    echo "示例:"
    echo "  $0 your_token_here"
    echo "  $0 -d -v 20 -t 60s"
    echo "  $0 --env .env.production"
    echo ""
    echo "环境变量:"
    echo "  ACCESS_TOKEN   访问令牌"
    echo "  DEBUG          调试模式（true/false）"
    echo "  BASE_URL       基础URL"
}

# 解析参数
parse_arguments() {
    ACCESS_TOKEN=""
    DEBUG_MODE="false"
    VUS="10"
    DURATION="30s"
    ENV_FILE=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--debug)
                DEBUG_MODE="true"
                shift
                ;;
            -v|--vus)
                VUS="$2"
                shift 2
                ;;
            -t|--time)
                DURATION="$2"
                shift 2
                ;;
            -e|--env)
                ENV_FILE="$2"
                shift 2
                ;;
            *)
                if [[ -z "$ACCESS_TOKEN" ]]; then
                    ACCESS_TOKEN="$1"
                else
                    echo -e "${YELLOW}警告: 忽略未知参数: $1${NC}"
                fi
                shift
                ;;
        esac
    done
}

# 设置访问令牌
setup_access_token() {
    if [[ -n "$ACCESS_TOKEN" ]]; then
        echo -e "${GREEN}使用命令行参数提供的访问令牌${NC}"
        export ACCESS_TOKEN="$ACCESS_TOKEN"
    elif [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
        echo -e "${GREEN}从环境变量文件加载配置: $ENV_FILE${NC}"
        source "$ENV_FILE"
    elif [[ -n "$ACCESS_TOKEN" ]]; then
        echo -e "${GREEN}使用环境变量中的访问令牌${NC}"
    else
        echo -e "${YELLOW}警告: 未提供访问令牌${NC}"
        echo "请通过以下方式之一提供访问令牌:"
        echo "  1. 命令行参数: $0 your_token"
        echo "  2. 环境变量: export ACCESS_TOKEN=your_token"
        echo "  3. 环境变量文件: $0 -e .env"
        echo ""
        read -p "请输入访问令牌: " user_token
        if [[ -n "$user_token" ]]; then
            export ACCESS_TOKEN="$user_token"
            echo -e "${GREEN}✓ 使用手动输入的访问令牌${NC}"
        else
            echo -e "${RED}错误: 必须提供访问令牌${NC}"
            exit 1
        fi
    fi
    
    if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "your-access-token-here" ]]; then
        echo -e "${RED}错误: 无效的访问令牌${NC}"
        exit 1
    fi
}

# 显示测试配置
show_test_config() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}       首页冒烟测试配置        ${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "脚本文件:   ${GREEN}$SCRIPT_NAME${NC}"
    echo -e "虚拟用户:   ${GREEN}$VUS${NC}"
    echo -e "测试时长:   ${GREEN}$DURATION${NC}"
    echo -e "调试模式:   ${GREEN}$DEBUG_MODE${NC}"
    echo -e "目标URL:    ${GREEN}${BASE_URL:-http://appserver.huice.com}${NC}"
    echo -e "访问令牌:   ${GREEN}${ACCESS_TOKEN:0:10}...${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# 运行测试
run_test() {
    echo -e "${YELLOW}🚀 开始执行冒烟测试...${NC}"
    echo ""
    
    # 构建K6命令
    K6_CMD="k6 run"
    
    # 添加环境变量
    K6_CMD="$K6_CMD -e ACCESS_TOKEN=$ACCESS_TOKEN"
    K6_CMD="$K6_CMD -e DEBUG=$DEBUG_MODE"
    
    # 添加命令行参数
    K6_CMD="$K6_CMD --vus $VUS"
    K6_CMD="$K6_CMD --duration $DURATION"
    
    # 添加输出选项
    K6_CMD="$K6_CMD --summary-export=smoke_test_results.json"
    K6_CMD="$K6_CMD --out json=smoke_test_metrics.json"
    
    # 添加脚本路径
    K6_CMD="$K6_CMD $SCRIPT_PATH"
    
    echo -e "${YELLOW}执行命令:${NC}"
    echo "$K6_CMD"
    echo ""
    
    # 执行测试
    eval $K6_CMD
    
    TEST_EXIT_CODE=$?
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ 测试执行完成${NC}"
    else
        echo -e "${RED}❌ 测试执行失败，退出码: $TEST_EXIT_CODE${NC}"
    fi
    
    return $TEST_EXIT_CODE
}

# 显示测试结果
show_test_results() {
    if [ -f "smoke_test_results.json" ]; then
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}       测试结果摘要        ${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        # 使用jq解析结果（如果可用）
        if command -v jq &> /dev/null; then
            echo -e "${YELLOW}关键指标:${NC}"
            jq -r '.metrics | to_entries[] | select(.key | test("(http_req_duration|errors|http_req_failed|iterations)")) | "  \(.key): \(.value)"' smoke_test_results.json | head -20
        else
            echo -e "${YELLOW}结果文件已生成: smoke_test_results.json${NC}"
            echo -e "${YELLOW}结果文件已生成: smoke_test_metrics.json${NC}"
        fi
    fi
}

# 清理临时文件
cleanup() {
    echo ""
    echo -e "${YELLOW}清理临时文件...${NC}"
    
    # 保留结果文件，只清理可能存在的临时文件
    if [ -f "k6.log" ]; then
        rm k6.log
    fi
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 主函数
main() {
    echo -e "${BLUE}K6首页冒烟测试启动器${NC}"
    echo ""
    
    # 检查依赖
    check_k6_installed
    check_script_file
    
    # 解析参数
    parse_arguments "$@"
    
    # 设置访问令牌
    setup_access_token
    
    # 显示配置
    show_test_config
    
    # 确认执行
    read -p "是否开始测试？(y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}测试已取消${NC}"
        exit 0
    fi
    
    # 运行测试
    run_test
    
    # 显示结果
    show_test_results
    
    # 清理
    cleanup
    
    echo ""
    echo -e "${GREEN}✅ 所有操作完成${NC}"
}

# 执行主函数
main "$@"