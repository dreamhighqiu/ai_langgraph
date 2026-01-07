#!/usr/bin/env python3
"""
执行PlayTurbo API测试脚本
"""
import subprocess
import sys
import os
import json
from datetime import datetime
import time

def run_pytest_tests():
    """执行pytest测试"""
    print("=" * 80)
    print("开始执行PlayTurbo.com API测试")
    print("=" * 80)
    
    # 创建测试结果目录
    os.makedirs("test-results", exist_ok=True)
    os.makedirs("allure-results", exist_ok=True)
    
    # 构建pytest命令
    cmd = [
        "pytest",
        "tests/",
        "-v",  # 详细输出
        "--tb=short",  # 简短的traceback
        f"--html=test-results/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        "--self-contained-html",
        f"--alluredir=allure-results/{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        f"--junitxml=test-results/junit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml",
        "-n", "auto",  # 使用pytest-xdist并行执行
        "--dist=loadscope",  # 按测试类分发
        "--maxfail=5",  # 最多失败5个测试后停止
        "--disable-warnings",  # 禁用警告
        "-o", "log_cli=true",
        "-o", "log_cli_level=INFO"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print("-" * 80)
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 执行测试
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 记录结束时间
        end_time = time.time()
        duration = end_time - start_time
        
        # 输出测试结果
        print("\n" + "=" * 80)
        print("测试执行完成")
        print("=" * 80)
        
        print(f"返回码: {result.returncode}")
        print(f"执行时间: {duration:.2f}秒")
        
        # 输出标准输出
        if result.stdout:
            print("\n标准输出:")
            print("-" * 40)
            print(result.stdout[-2000:])  # 只显示最后2000字符
        
        # 输出标准错误
        if result.stderr:
            print("\n标准错误:")
            print("-" * 40)
            print(result.stderr[-1000:])  # 只显示最后1000字符
        
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": duration,
            "success": result.returncode == 0
        }
        
    except Exception as e:
        print(f"执行测试时发生错误: {e}")
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": str(e),
            "duration": time.time() - start_time,
            "success": False
        }

def analyze_test_results():
    """分析测试结果"""
    print("\n" + "=" * 80)
    print("分析测试结果")
    print("=" * 80)
    
    # 这里可以添加更详细的结果分析逻辑
    # 例如：解析JUnit XML文件，统计测试用例数量等
    
    print("测试结果分析完成")
    return True

def main():
    """主函数"""
    print("PlayTurbo API测试执行器")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行测试
    test_result = run_pytest_tests()
    
    # 分析结果
    analyze_test_results()
    
    # 输出摘要
    print("\n" + "=" * 80)
    print("测试执行摘要")
    print("=" * 80)
    print(f"执行状态: {'成功' if test_result['success'] else '失败'}")
    print(f"返回码: {test_result['returncode']}")
    print(f"执行时间: {test_result['duration']:.2f}秒")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查生成的报告文件
    print("\n生成的报告文件:")
    for root, dirs, files in os.walk("test-results"):
        for file in files:
            if file.endswith(('.html', '.xml')):
                print(f"  - {os.path.join(root, file)}")
    
    if os.path.exists("allure-results"):
        print("  - allure-results/ (Allure测试结果)")
    
    print("\n" + "=" * 80)
    
    # 返回适当的退出码
    sys.exit(0 if test_result['success'] else 1)

if __name__ == "__main__":
    main()