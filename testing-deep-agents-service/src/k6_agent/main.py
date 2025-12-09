

import os
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UWxJd1JnPT06ZWZjZGJiYjI=

# from langchain_deepseek import ChatDeepSeek

from k6_agent import create_k6_agent, K6AgentConfig

config = K6AgentConfig()
from core.llms import deepseek_model
# os.environ["DEEPSEEK_API_KEY"] = "sk-ab9554f3b6cc4eaab1fed91b36d09ea7"
# deepseek = ChatDeepSeek(model="deepseek-chat")

agent = create_k6_agent(model=deepseek_model, config=config, enable_knowledge_retrieval=False)
# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UWxJd1JnPT06ZWZjZGJiYjI=
