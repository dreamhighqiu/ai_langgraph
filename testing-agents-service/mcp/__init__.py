"""
统一 MCP 服务器管理模块

本模块包含所有 MCP (Model Context Protocol) 服务器实现：

1. rag_anything (Port 8001) - 文档处理 + 多模态查询
   - 文档导入和解析
   - 多模态图片处理
   - 知识库查询

2. rag_query (Port 8002) - LightRAG 查询服务
   - 面向 API 测试的 RAG 查询
   - 知识图谱实体/关系检索

3. pytest_mcp (Port 8004) - Pytest 测试服务
   - 测试代码生成
   - 测试执行
   - Allure 报告生成

4. automation_quality (stdio) - API/浏览器自动化
   - API 测试生成/规划/修复
   - 浏览器控制和自动化

5. ui (Playwright) - UI 测试服务
   - Playwright 测试运行
"""

__version__ = "1.0.0"

# 解决命名冲突：当外部代码尝试从 'mcp' 包导入时（如 mcp.types, mcp.ClientSession），
# 我们需要代理到已安装的 mcp 包，而不是本地的 mcp 目录。
# 
# 注意：Python 的导入机制会在找到本地 mcp 目录时就停止搜索已安装的包。
# 因此，我们需要在 sys.modules 中注册外部包，以便其他模块可以正确导入。

import sys
import importlib

# 缓存外部 mcp 包的引用
_external_mcp_package = None

def _get_external_mcp_package():
    """获取已安装的外部 mcp 包"""
    global _external_mcp_package
    if _external_mcp_package is None:
        try:
            # 尝试从已安装的包中导入
            # 使用 importlib 直接导入，绕过本地模块
            import importlib.util
            spec = importlib.util.find_spec("mcp")
            if spec and spec.origin and 'site-packages' in spec.origin:
                # 这是已安装的包
                _external_mcp_package = importlib.import_module("mcp")
            else:
                # 如果找不到已安装的包，尝试直接导入
                # 这可能会失败，但至少不会拦截
                try:
                    _external_mcp_package = importlib.import_module("mcp")
                except ImportError:
                    pass
        except Exception:
            pass
    return _external_mcp_package

# 当其他模块尝试 from mcp import types 或 from mcp import ClientSession 时，
# Python 会先查找本地的 mcp 目录。为了不拦截这些导入，我们需要：
# 1. 确保本地的 mcp 模块不会定义这些名称
# 2. 或者使用 __getattr__ 来动态代理（但这在模块级别不太容易实现）

# 实际上，最简单的方法是：确保 sys.modules 中有正确的外部包引用
# 但 Python 的导入机制会在找到本地目录时就停止，所以我们无法完全避免冲突

# 临时解决方案：在需要导入外部包的地方，使用绝对导入或者修改导入方式
# 但更好的长期解决方案是：重命名本地的 mcp 目录为 mcp_servers 或其他名称

