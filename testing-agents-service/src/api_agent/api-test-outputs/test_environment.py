#!/usr/bin/env python3
"""
测试环境检查
"""
import sys
import subprocess

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✓ Python版本符合要求 (>= 3.8)")
        return True
    else:
        print("✗ Python版本不符合要求 (需要 >= 3.8)")
        return False

def check_pytest_installation():
    """检查pytest安装"""
    print("\n检查pytest安装...")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ pytest已安装: {result.stdout.strip()}")
            return True
        else:
            print("✗ pytest未正确安装")
            return False
    except Exception as e:
        print(f"✗ 检查pytest时出错: {e}")
        return False

def check_pytest_xdist():
    """检查pytest-xdist安装"""
    print("\n检查pytest-xdist安装...")
    try:
        import pytest_xdist
        print(f"✓ pytest-xdist已安装: {pytest_xdist.__version__}")
        return True
    except ImportError:
        print("✗ pytest-xdist未安装")
        return False

def check_allure_pytest():
    """检查allure-pytest安装"""
    print("\n检查allure-pytest安装...")
    try:
        import allure
        print(f"✓ allure-pytest已安装: {allure.__version__}")
        return True
    except ImportError:
        print("✗ allure-pytest未安装")
        return False

def check_requests():
    """检查requests安装"""
    print("\n检查requests安装...")
    try:
        import requests
        print(f"✓ requests已安装: {requests.__version__}")
        return True
    except ImportError:
        print("✗ requests未安装")
        return False

def check_test_files():
    """检查测试文件"""
    print("\n检查测试文件...")
    import os
    
    test_files = [
        "tests/test_auth.py",
        "tests/test_game_data.py", 
        "tests/test_social.py",
        "tests/test_payment.py",
        "tests/test_system.py"
    ]
    
    all_exist = True
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"✓ {test_file} 存在")
        else:
            print(f"✗ {test_file} 不存在")
            all_exist = False
    
    return all_exist

def main():
    """主函数"""
    print("=" * 60)
    print("PlayTurbo API测试环境检查")
    print("=" * 60)
    
    checks = [
        ("Python版本", check_python_version()),
        ("pytest安装", check_pytest_installation()),
        ("pytest-xdist", check_pytest_xdist()),
        ("allure-pytest", check_allure_pytest()),
        ("requests", check_requests()),
        ("测试文件", check_test_files())
    ]
    
    print("\n" + "=" * 60)
    print("环境检查结果:")
    print("=" * 60)
    
    all_passed = True
    for check_name, check_result in checks:
        status = "✓ 通过" if check_result else "✗ 失败"
        print(f"{check_name}: {status}")
        if not check_result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有环境检查通过，可以执行测试")
        return 0
    else:
        print("环境检查失败，请先解决上述问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())