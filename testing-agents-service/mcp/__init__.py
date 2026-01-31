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

