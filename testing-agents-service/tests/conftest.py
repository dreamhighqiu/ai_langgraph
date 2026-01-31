"""
Pytest 配置文件 - 设置 Python 路径和编码

此文件确保 pytest 能够正确导入项目模块（agents, config 等）
并处理 Windows 终端的编码问题
"""

import sys
import os
from pathlib import Path

# 修复 Windows 终端编码问题
if sys.platform == "win32":
    # 设置标准输出为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 获取项目根目录（testing-agents-service）
project_root = Path(__file__).parent.parent.resolve()

# 将项目根目录添加到 Python 路径
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 可选：添加 src 目录（如果存在）
src_path = project_root / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

