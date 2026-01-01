#!/usr/bin/env python3
"""
简单测试执行脚本
"""
import pytest
import sys
import os

def main():
    """主函数"""
    print("开始执行PlayTurbo API测试...")
    
    # 设置环境变量
    os.environ["PLAYTURBO_API_URL"] = "https://api.playturbo.com"
    
    # 执行pytest
    test_args = [
        "tests/",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--maxfail=5"
    ]
    
    print(f"执行命令: pytest {' '.join(test_args)}")
    
    # 执行测试
    exit_code = pytest.main(test_args)
    
    print(f"\n测试执行完成，退出码: {exit_code}")
    
    # 根据退出码返回
    sys.exit(exit_code)

if __name__ == "__main__":
    main()