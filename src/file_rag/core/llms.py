import os
from pathlib import Path
from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
from langchain_deepseek.chat_models import ChatDeepSeek
from langchain_openai import ChatOpenAI

# 加载环境变量 - 从项目根目录加载 .env 文件
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

# 设置 DeepSeek API Key - 从环境变量读取，如果没有则使用默认值
os.environ["DEEPSEEK_API_KEY"] = os.getenv("ONE_API_KEY", "sk-253ba6e4ded142edb73ef4e213da")
# DeepSeek 大模型
def get_default_model():
    return ChatDeepSeek(
        model="deepseek-chat",
        verbose=False
    )

# 豆包大模型
def get_doubao_seed_model():
    return ChatOpenAI(model="doubao-seed-1-6-251015",
               base_url="https://ark.cn-beijing.volces.com/api/v3",
               api_key="9c18584a-dbec-4496-af23-ef0bb31")


# llm = get_default_model()
# response = llm.invoke("你好")
# print(response)
# for text in llm.stream("你好"):
#     print(text.content, end="", flush=True)