#!/usr/bin/env python3
"""
检查路由注册情况
"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent / "ruoyi-fastapi-backend"
sys.path.insert(0, str(project_root))

try:
    # 尝试导入 agent_controller
    print("=" * 60)
    print("检查 agent_controller 导入...")
    print("=" * 60)
    
    from module_testing.controller import agent_controller
    print(f"✅ agent_controller 导入成功")
    print(f"   类型: {type(agent_controller)}")
    print(f"   前缀: {agent_controller.prefix}")
    print(f"   标签: {agent_controller.tags}")
    print(f"   路由数量: {len(agent_controller.routes)}")
    
    print("\n路由列表:")
    for route in agent_controller.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"  {methods:8} {route.path}")
    
    print("\n" + "=" * 60)
    print("检查所有 controller 路由...")
    print("=" * 60)
    
    # 检查所有 controller
    controller_dir = project_root / "module_testing" / "controller"
    for file in controller_dir.glob("*.py"):
        if file.name.startswith("__"):
            continue
        
        module_name = f"module_testing.controller.{file.stem}"
        try:
            module = __import__(module_name, fromlist=[file.stem])
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, 'prefix') and hasattr(attr, 'routes'):
                    print(f"\n✅ {file.name}:")
                    print(f"   变量名: {attr_name}")
                    print(f"   前缀: {attr.prefix}")
                    print(f"   路由数: {len(attr.routes)}")
        except Exception as e:
            print(f"❌ {file.name}: 导入失败 - {e}")
    
    print("\n" + "=" * 60)
    print("测试 FastAPI 应用创建...")
    print("=" * 60)
    
    from server import create_app
    app = create_app()
    
    # 检查注册的路由
    print(f"\n应用路由总数: {len(app.routes)}")
    print("\n所有 /testing/ 相关路由:")
    for route in app.routes:
        if hasattr(route, 'path') and '/testing/' in str(route.path):
            methods = ', '.join(route.methods) if hasattr(route, 'methods') and route.methods else 'N/A'
            print(f"  {methods:15} {route.path}")
    
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

