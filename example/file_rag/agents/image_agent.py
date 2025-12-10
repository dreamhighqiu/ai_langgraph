

from langchain.agents import create_agent
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZvMVpBPT06YzM1ZWZiMmY=

from file_rag.core.llms import image_llm_model
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZvMVpBPT06YzM1ZWZiMmY=

agent = create_agent(
    model=image_llm_model,
    tools=[],
    system_prompt="你是AI智能助手，专门针对用户上传的图片，回答用户问题。请仔细分析图片内容并提供详细的回答。",
    name="image_chat_agent",
)