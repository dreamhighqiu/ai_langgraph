"""
检查知识库管理菜单是否正确配置
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from config.env import DatabaseConfig


async def check_menu():
    """检查知识库管理菜单配置"""
    # 创建数据库连接
    engine = create_async_engine(
        DatabaseConfig.database_url,
        echo=False,
        pool_pre_ping=True
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        # 1. 检查菜单是否存在
        print("=" * 60)
        print("1. 检查知识库管理菜单")
        print("=" * 60)
        
        result = await db.execute(
            text("""
                SELECT 
                    menu_id, menu_name, parent_id, order_num, 
                    path, component, perms, visible, status, menu_type
                FROM sys_menu 
                WHERE menu_id BETWEEN 2920 AND 2929
                ORDER BY menu_id
            """)
        )
        menus = result.fetchall()
        
        if not menus:
            print("❌ 未找到知识库管理菜单！请执行 knowledge_menu.sql")
            return
        
        print(f"✅ 找到 {len(menus)} 个菜单项：")
        for menu in menus:
            print(f"   - [{menu[0]}] {menu[1]} (path: {menu[4]}, component: {menu[5]})")
        
        # 2. 检查父菜单是否存在
        print("\n" + "=" * 60)
        print("2. 检查父菜单（测试管理）")
        print("=" * 60)
        
        result = await db.execute(
            text("SELECT menu_id, menu_name, path FROM sys_menu WHERE menu_id = 2900")
        )
        parent_menu = result.fetchone()
        
        if not parent_menu:
            print("❌ 父菜单（测试管理）不存在！")
        else:
            print(f"✅ 父菜单存在: [{parent_menu[0]}] {parent_menu[1]} (path: {parent_menu[2]})")
        
        # 3. 检查角色菜单绑定
        print("\n" + "=" * 60)
        print("3. 检查角色菜单绑定")
        print("=" * 60)
        
        result = await db.execute(
            text("""
                SELECT 
                    rm.role_id,
                    r.role_name,
                    COUNT(rm.menu_id) as menu_count
                FROM sys_role_menu rm
                LEFT JOIN sys_role r ON rm.role_id = r.role_id
                WHERE rm.menu_id BETWEEN 2920 AND 2929
                GROUP BY rm.role_id, r.role_name
                ORDER BY rm.role_id
            """)
        )
        role_menus = result.fetchall()
        
        if not role_menus:
            print("❌ 未找到角色菜单绑定！请检查 role_id=1 是否有权限")
        else:
            print(f"✅ 找到 {len(role_menus)} 个角色的菜单绑定：")
            for rm in role_menus:
                print(f"   - 角色 [{rm[0]}] {rm[1]}: {rm[2]} 个菜单")
        
        # 4. 检查当前用户的角色和权限
        print("\n" + "=" * 60)
        print("4. 检查管理员角色权限")
        print("=" * 60)
        
        result = await db.execute(
            text("""
                SELECT 
                    r.role_id, r.role_name, r.status,
                    COUNT(rm.menu_id) as total_menus
                FROM sys_role r
                LEFT JOIN sys_role_menu rm ON r.role_id = rm.role_id
                WHERE r.role_id = 1
                GROUP BY r.role_id, r.role_name, r.status
            """)
        )
        admin_role = result.fetchone()
        
        if admin_role:
            print(f"✅ 管理员角色: [{admin_role[0]}] {admin_role[1]} (状态: {'正常' if admin_role[2] == '0' else '停用'})")
            print(f"   总菜单数: {admin_role[3]}")
        else:
            print("❌ 未找到管理员角色！")
        
        # 5. 检查菜单路径配置
        print("\n" + "=" * 60)
        print("5. 检查菜单路径配置")
        print("=" * 60)
        
        result = await db.execute(
            text("""
                SELECT menu_id, menu_name, path, component, parent_id
                FROM sys_menu 
                WHERE menu_id = 2920
            """)
        )
        knowledge_menu = result.fetchone()
        
        if knowledge_menu:
            print(f"✅ 知识库管理菜单配置：")
            print(f"   - 菜单ID: {knowledge_menu[0]}")
            print(f"   - 菜单名称: {knowledge_menu[1]}")
            print(f"   - 路径 (path): {knowledge_menu[2]}")
            print(f"   - 组件 (component): {knowledge_menu[3]}")
            print(f"   - 父菜单ID: {knowledge_menu[4]}")
            
            # 检查路径是否正确
            if knowledge_menu[2] != 'knowledge':
                print(f"   ⚠️  路径应该是 'knowledge'，当前是 '{knowledge_menu[2]}'")
            if knowledge_menu[3] != 'testing/knowledge/index':
                print(f"   ⚠️  组件应该是 'testing/knowledge/index'，当前是 '{knowledge_menu[3]}'")
        
        print("\n" + "=" * 60)
        print("检查完成！")
        print("=" * 60)
        print("\n如果菜单未显示，请：")
        print("1. 确认已执行 knowledge_menu.sql")
        print("2. 确认当前用户角色有权限（role_id=1）")
        print("3. 清除浏览器缓存并重新登录")
        print("4. 检查后端日志中的 /getRouters 接口返回数据")


if __name__ == '__main__':
    asyncio.run(check_menu())

