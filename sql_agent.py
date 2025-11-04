import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
# pip install langchain_community pymysql

# 加载环境变量
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from llm import create_llm
from langchain.agents import AgentState

llm = create_llm()


class MySQLConfig:
    # https://gitlab.mobvista.com/playable/portal-backend/-/blob/master/conf/portal.test.toml
    """MySQL 数据库配置类

    从 .env 文件读取配置，支持以下环境变量：
    - MYSQL_HOST: 数据库主机地址
    - MYSQL_PORT: 数据库端口
    - MYSQL_DATABASE: 数据库名称
    - MYSQL_USER: 数据库用户名
    - MYSQL_PASSWORD: 数据库密码

    使用方法：
        # 获取配置值
        host = MySQLConfig.get_host()
        port = MySQLConfig.get_port()

        # 获取连接 URI
        uri = MySQLConfig.get_connection_uri()

        # 打印配置
        MySQLConfig.print_config()
    """

    @staticmethod
    def get_host() -> str:
        """获取数据库主机地址"""
        return os.getenv("MYSQL_HOST", "playable-portal-test-sg.cpgqn7tqklnb.ap-southeast-1.rds.amazonaws.com")

    @staticmethod
    def get_port() -> int:
        """获取数据库端口"""
        return int(os.getenv("MYSQL_PORT", "3306"))

    @staticmethod
    def get_database() -> str:
        """获取数据库名称"""
        return os.getenv("MYSQL_DATABASE", "playable")

    @staticmethod
    def get_user() -> str:
        """获取数据库用户名"""
        return os.getenv("MYSQL_USER", "root")

    @staticmethod
    def get_password() -> str:
        """获取数据库密码"""
        return os.getenv("MYSQL_PASSWORD", "6dEUgM9y8L3qcEt")

    @classmethod
    def get_connection_uri(cls) -> str:
        """
        生成 MySQL 连接 URI

        Returns:
            str: MySQL 连接字符串
        """
        return f"mysql+pymysql://{cls.get_user()}:{cls.get_password()}@{cls.get_host()}:{cls.get_port()}/{cls.get_database()}"

    @classmethod
    def print_config(cls):
        """打印当前配置（隐藏密码）"""
        print("=" * 60)
        print("MySQL 数据库配置:")
        print("=" * 60)
        print(f"主机: {cls.get_host()}")
        print(f"端口: {cls.get_port()}")
        print(f"数据库: {cls.get_database()}")
        print(f"用户: {cls.get_user()}")
        password = cls.get_password()
        print(f"密码: {'*' * len(password) if password else '(未设置)'}")
        print("=" * 60)


# 创建 MySQL 数据库连接
# 使用 pymysql 驱动连接 MySQL 数据库
try:
    db = SQLDatabase.from_uri(
        MySQLConfig.get_connection_uri(),
        sample_rows_in_table_info=3  # 在表信息中包含3行样本数据
    )
    print(f"✅ 成功连接到 MySQL 数据库: {MySQLConfig.get_database()}")
except Exception as e:
    print(f"❌ 连接 MySQL 数据库失败: {e}")
    raise

# print(db.get_usable_table_names())
# # print(f"Dialect: {db.dialect}")
# # print(f"Available tables: {db.get_usable_table_names()}")
# print(f'Sample output: {db.run("SELECT * FROM Artist LIMIT 5;")}')

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 获取所有的工具
tools = toolkit.get_tools()

for tool in tools:
    print(f"{tool.name}: {tool.description}\n")

# os.environ["DEEPSEEK_API_KEY"] = "sk-7443d4458d1444d2ac620964e4f58767"
# llm = init_chat_model("deepseek:deepseek-chat")

system_prompt = """
你是一个专为与 MySQL 数据库交互而设计的智能体。
根据输入的问题，你需要生成语法正确的 {dialect} 查询语句，
执行查询后分析结果并返回答案。除非用户明确指定要获取的记录数量，
否则始终将查询结果限制在最多 {top_k} 条。

重要规则：
1. 你可以通过相关列对结果进行排序，以返回数据库中最有价值的信息
2. 切勿查询特定表的所有列，只需获取与问题相关的列即可
3. 在执行查询前必须仔细检查语句。若执行过程中出现错误，应重新编写查询语句并再次尝试
4. 严禁对数据库执行任何数据操作语言语句（INSERT、UPDATE、DELETE、DROP等）
5. 开始操作时，你必须始终先查看数据库中的表结构以确定可查询的内容，切勿跳过这一步骤
6. 随后应当查询最相关表的模式结构
7. 使用 MySQL 特定的语法和函数（如 LIMIT、DATE_FORMAT 等）
8. 根据查询的数据特点选择合适的图表生成工具显示

当前数据库信息：
- 数据库类型: {dialect}
- 数据库名称: {database_name}
- 默认返回行数: {top_k}
""".format(
    dialect=db.dialect,
    database_name=MySQLConfig.get_database(),
    top_k=10,
)

mcp_client = MultiServerMCPClient(
    {
        "mcp-server-chart": {
            "command": "npx",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["-y", "@antv/mcp-server-chart"],
            "transport": "stdio",
        }
    }
)


mcp_tools = asyncio.run(mcp_client.get_tools())
agent = create_agent(
    llm,
    tools + mcp_tools,
    system_prompt=system_prompt,
)


async def query_database(question: str):
    """
    查询数据库并返回结果

    Args:
        question: 用户的问题
    """
    print("\n" + "=" * 60)
    print(f"问题: {question}")
    print("=" * 60 + "\n")

    async for step in agent.astream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()


async def main():
    """主函数 - 演示如何使用 MySQL Agent"""

    # 打印配置信息
    MySQLConfig.print_config()

    # 示例问题列表（根据你的数据库调整）
    questions = [
        "数据库中有哪些表？",
        # "查询前10条用户数据",
        # "统计每个表的记录数量",
        # 你可以根据实际的数据库表结构添加更多问题
    ]

    # 执行查询
    for question in questions:
        await query_database(question)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
