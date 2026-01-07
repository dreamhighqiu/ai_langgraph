#!/usr/bin/env python3
"""
PlayTurbo API测试运行脚本
用于运行和管理测试套件
"""
import os
import sys
import subprocess
import argparse
import json
from datetime import datetime
from pathlib import Path


def print_banner():
    """打印测试套件横幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                 PlayTurbo API 测试套件                   ║
║                 ======================                   ║
║  用户认证 | 游戏数据 | 社交功能 | 支付模块 | 系统状态    ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")
    
    required_packages = [
        "pytest",
        "requests",
        "allure-pytest",
        "pytest-html"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✓ 所有依赖已安装")
    return True


def create_test_directories():
    """创建测试输出目录"""
    directories = [
        "test-results",
        "allure-results",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ 创建目录: {directory}")
    
    return True


def run_tests(test_type, markers, parallel=False, verbose=False):
    """运行测试"""
    print(f"\n运行 {test_type} 测试...")
    
    # 构建pytest命令
    cmd = [
        "pytest",
        "-v" if verbose else "",
        f"--html=test-results/{test_type}_report.html",
        f"--alluredir=allure-results/{test_type}",
        f"--junitxml=test-results/{test_type}_junit.xml"
    ]
    
    # 添加标记过滤
    if markers:
        marker_expr = " or ".join(markers)
        cmd.extend(["-m", marker_expr])
    
    # 添加并行执行
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # 添加测试路径
    if test_type == "all":
        cmd.append("tests/")
    else:
        cmd.append(f"tests/test_{test_type}.py")
    
    # 移除空字符串
    cmd = [arg for arg in cmd if arg]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    # 运行测试
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"测试执行错误: {e}")
        return False
    except FileNotFoundError:
        print("错误: pytest未安装或不在PATH中")
        return False


def generate_allure_report():
    """生成Allure报告"""
    print("\n生成Allure报告...")
    
    allure_results_dir = "allure-results"
    allure_report_dir = "allure-report"
    
    if not Path(allure_results_dir).exists():
        print("警告: 未找到Allure结果目录")
        return False
    
    try:
        # 检查是否安装了allure命令行工具
        subprocess.run(["allure", "--version"], capture_output=True, check=False)
        
        # 生成报告
        cmd = ["allure", "generate", allure_results_dir, "-o", allure_report_dir, "--clean"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Allure报告已生成: {allure_report_dir}/index.html")
            return True
        else:
            print(f"Allure报告生成失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("警告: allure命令行工具未安装，跳过Allure报告生成")
        print("安装方法: https://docs.qameta.io/allure/#_installing_a_commandline")
        return False


def run_smoke_tests():
    """运行冒烟测试"""
    print("\n运行冒烟测试...")
    return run_tests("all", ["smoke"], verbose=True)


def run_regression_tests():
    """运行回归测试"""
    print("\n运行回归测试...")
    return run_tests("all", ["regression"], parallel=True)


def run_module_tests(module):
    """运行指定模块的测试"""
    modules = {
        "auth": "用户认证模块",
        "game_data": "游戏数据模块",
        "social": "社交功能模块",
        "payment": "支付模块",
        "system": "系统状态模块"
    }
    
    if module not in modules:
        print(f"错误: 未知模块 '{module}'")
        print(f"可用模块: {', '.join(modules.keys())}")
        return False
    
    print(f"\n运行{modules[module]}测试...")
    return run_tests(module, [], verbose=True)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="PlayTurbo API测试套件")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "smoke", "regression", "auth", "game_data", "social", "payment", "system"],
        help="测试类型 (默认: all)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行执行测试"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出"
    )
    parser.add_argument(
        "--no-deps-check",
        action="store_true",
        help="跳过依赖检查"
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="生成Allure报告"
    )
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 检查依赖
    if not args.no_deps_check and not check_dependencies():
        sys.exit(1)
    
    # 创建目录
    if not create_test_directories():
        sys.exit(1)
    
    # 记录开始时间
    start_time = datetime.now()
    print(f"\n测试开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行测试
    success = False
    if args.test_type == "smoke":
        success = run_smoke_tests()
    elif args.test_type == "regression":
        success = run_regression_tests()
    elif args.test_type in ["auth", "game_data", "social", "payment", "system"]:
        success = run_module_tests(args.test_type)
    else:  # all
        success = run_tests("all", [], args.parallel, args.verbose)
    
    # 记录结束时间
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n测试结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试持续时间: {duration}")
    
    # 生成报告
    if args.generate_report:
        generate_allure_report()
    
    # 输出测试结果摘要
    print("\n" + "="*60)
    print("测试结果摘要")
    print("="*60)
    print(f"测试类型: {args.test_type}")
    print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"持续时间: {duration}")
    print(f"测试结果: {'✓ 通过' if success else '✗ 失败'}")
    
    # 检查测试报告文件
    report_files = [
        "test-results/report.html",
        "test-results/junit.xml"
    ]
    
    print("\n生成的报告:")
    for report_file in report_files:
        if Path(report_file).exists():
            print(f"  ✓ {report_file}")
        else:
            print(f"  ✗ {report_file} (未生成)")
    
    if Path("allure-report").exists():
        print("  ✓ allure-report/index.html")
    
    print("\n" + "="*60)
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()