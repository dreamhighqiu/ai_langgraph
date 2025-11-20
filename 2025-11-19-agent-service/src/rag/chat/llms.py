"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import os
from langchain.chat_models import init_chat_model
# noqa  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Wkhwa1p3PT06Y2FkZWU5MWM=


def deepseek_model():
    os.environ["DEEPSEEK_API_KEY"] = "sk-d631bd0f6956421a98b880b77090471e"
    model = init_chat_model("deepseek:deepseek-chat")
    return model
# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Wkhwa1p3PT06Y2FkZWU5MWM=
