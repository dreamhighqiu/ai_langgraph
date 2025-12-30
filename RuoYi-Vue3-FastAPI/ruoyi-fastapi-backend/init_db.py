#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化工具

用法:
    python init_db.py              # 使用 .env.dev 配置
    python init_db.py --env prod   # 使用 .env.prod 配置
    python init_db.py --check      # 仅检查连接
"""

import os
import sys
import argparse
from pathlib import Path

# 颜色输出
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_info(msg): print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")
def print_success(msg): print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")
def print_warning(msg): print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")
def print_error(msg): print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")


def load_env(env_mode: str):
    """加载环境变量"""
    env_file = Path(__file__).parent / f".env.{env_mode}"
    
    if not env_file.exists():
        # 尝试从 env.example 复制
        example_file = Path(__file__).parent / "env.example"
        if example_file.exists():
            print_warning(f".env.{env_mode} 不存在，从 env.example 复制...")
            import shutil
            shutil.copy(example_file, env_file)
        else:
            print_error(f"配置文件不存在: {env_file}")
            return False
    
    # 加载 .env 文件
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print_success(f"已加载配置: {env_file.name}")
        return True
    except ImportError:
        print_warning("python-dotenv 未安装，尝试手动解析...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True


def get_db_config():
    """获取数据库配置"""
    return {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USERNAME', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_DATABASE', 'ai_db'),
        'db_type': os.getenv('DB_TYPE', 'mysql'),
    }


def check_connection(config: dict) -> bool:
    """检查数据库连接"""
    print_info(f"检查数据库连接: {config['host']}:{config['port']}")
    
    if config['db_type'] == 'mysql':
        try:
            import pymysql
            conn = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                connect_timeout=10
            )
            conn.close()
            print_success("数据库连接成功!")
            return True
        except ImportError:
            print_error("pymysql 未安装，请运行: pip install pymysql")
            return False
        except Exception as e:
            print_error(f"数据库连接失败: {e}")
            return False
    else:
        try:
            import asyncpg
            print_warning("PostgreSQL 暂不支持同步检查，请使用 MySQL")
            return False
        except ImportError:
            print_error("asyncpg 未安装")
            return False


def create_database(config: dict) -> bool:
    """创建数据库（如果不存在）"""
    print_info(f"检查/创建数据库: {config['database']}")
    
    try:
        import pymysql
        conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config['database']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        
        cursor.close()
        conn.close()
        print_success(f"数据库 {config['database']} 已就绪")
        return True
    except Exception as e:
        print_error(f"创建数据库失败: {e}")
        return False


def execute_sql_file(config: dict, sql_file: Path) -> bool:
    """执行SQL文件"""
    if not sql_file.exists():
        print_error(f"SQL文件不存在: {sql_file}")
        return False
    
    print_info(f"执行SQL文件: {sql_file.name}")
    
    try:
        import pymysql
        conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset='utf8mb4',
            autocommit=True
        )
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句
        statements = []
        current_statement = []
        delimiter = ';'
        
        for line in sql_content.split('\n'):
            stripped = line.strip()
            
            # 跳过注释
            if stripped.startswith('--') or stripped.startswith('#'):
                continue
            
            # 检查 DELIMITER 命令
            if stripped.upper().startswith('DELIMITER'):
                parts = stripped.split()
                if len(parts) > 1:
                    delimiter = parts[1]
                continue
            
            current_statement.append(line)
            
            # 检查语句结束
            if stripped.endswith(delimiter):
                stmt = '\n'.join(current_statement)
                if delimiter != ';':
                    stmt = stmt.replace(delimiter, '')
                stmt = stmt.strip()
                if stmt:
                    statements.append(stmt)
                current_statement = []
        
        # 处理最后一个语句
        if current_statement:
            stmt = '\n'.join(current_statement).strip()
            if stmt:
                statements.append(stmt)
        
        # 执行SQL语句
        success_count = 0
        error_count = 0
        
        for i, stmt in enumerate(statements):
            if not stmt.strip():
                continue
            try:
                cursor.execute(stmt)
                success_count += 1
            except pymysql.err.OperationalError as e:
                if e.args[0] == 1050:  # 表已存在
                    pass
                elif e.args[0] == 1062:  # 重复记录
                    pass
                else:
                    print_warning(f"  语句 {i+1} 警告: {e.args[1][:50]}...")
                    error_count += 1
            except Exception as e:
                error_count += 1
                if 'Duplicate' not in str(e) and 'already exists' not in str(e):
                    print_warning(f"  语句 {i+1} 错误: {str(e)[:80]}...")
        
        cursor.close()
        conn.close()
        
        if error_count == 0:
            print_success(f"  完成: {success_count} 条语句执行成功")
        else:
            print_warning(f"  完成: {success_count} 成功, {error_count} 跳过/警告")
        
        return True
        
    except ImportError:
        print_error("pymysql 未安装，请运行: pip install pymysql")
        return False
    except Exception as e:
        print_error(f"执行SQL失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='数据库初始化工具')
    parser.add_argument('--env', type=str, default='dev', help='环境: dev/prod')
    parser.add_argument('--check', action='store_true', help='仅检查连接')
    parser.add_argument('--skip-ruoyi', action='store_true', help='跳过RuoYi基础表')
    parser.add_argument('--only-testing', action='store_true', help='仅初始化测试平台表')
    args = parser.parse_args()
    
    print("")
    print("=" * 50)
    print("  AI智能测试平台 - 数据库初始化工具")
    print("=" * 50)
    print("")
    
    # 加载配置
    if not load_env(args.env):
        sys.exit(1)
    
    # 获取配置
    config = get_db_config()
    print_info(f"数据库类型: {config['db_type']}")
    print_info(f"服务器: {config['host']}:{config['port']}")
    print_info(f"数据库: {config['database']}")
    print("")
    
    # 检查连接
    if not check_connection(config):
        print("")
        print_error("请检查:")
        print("  1. 数据库服务是否运行")
        print("  2. 网络是否可达")
        print("  3. 用户名密码是否正确")
        print(f"  4. 配置文件: .env.{args.env}")
        sys.exit(1)
    
    if args.check:
        print("")
        print_success("连接检查完成!")
        sys.exit(0)
    
    print("")
    
    # 创建数据库
    if not create_database(config):
        sys.exit(1)
    
    print("")
    
    # SQL文件路径
    sql_dir = Path(__file__).parent / 'sql'
    ruoyi_sql = sql_dir / 'ruoyi-fastapi.sql'
    testing_sql = sql_dir / 'testing_platform.sql'
    
    # 执行RuoYi基础SQL
    if not args.skip_ruoyi and not args.only_testing:
        if ruoyi_sql.exists():
            execute_sql_file(config, ruoyi_sql)
            print("")
        else:
            print_warning(f"RuoYi SQL文件不存在: {ruoyi_sql}")
    
    # 执行测试平台SQL
    if testing_sql.exists():
        execute_sql_file(config, testing_sql)
    else:
        print_warning(f"测试平台SQL文件不存在: {testing_sql}")
    
    print("")
    print("=" * 50)
    print_success("数据库初始化完成!")
    print("=" * 50)
    print("")
    print("下一步:")
    print("  ./deploy-local.sh all   # 启动服务")
    print("")


if __name__ == '__main__':
    main()

