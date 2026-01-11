"""
UI自动化测试模块 (Playwright等)

本模块负责所有UI自动化测试相关的功能：
- Playwright测试脚本生成
- Playwright测试脚本执行
- 测试报告生成和管理
- 与module_testing的集成

架构设计：
- agents/: UI自动化测试智能体（基于LangGraph）
- tools/: Agent使用的工具（脚本生成、执行、报告解析）
- controller/: API接口层
- service/: 业务逻辑层
- entity/: 数据模型（DO和VO）
- config.py: 配置文件

集成方式：
- module_testing通过service/integration.py调用UI自动化功能
- 保持模块间的清晰分离，避免循环依赖
"""

__version__ = "1.0.0"
