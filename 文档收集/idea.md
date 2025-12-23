现状：当前的影响面评估主要依赖开发人员的主观判断，测试人员则基于对业务的记忆进行二次评估。但是对于历史比较悠久的模块或紧急线上修复的代码变更情况，以这种方式进行评估效率低下且极易遗漏，带来潜在的线上风险。
解决方案：
目前想法是构建 “智能感知与影响分析agent”。
利用AI技术，结合代码静态依赖关系（如方法调用链、服务接口引用）和结构性变更信息（diff code），再关联上历史测试用例，构建一个精准的分析模型agent，该系统的目标是能够：

- 自动、精准地识别出受影响的代码模块和功能范围。
- 智能推荐需要回归的测试用例，并自动生成可疑场景的补充测试用例。

作业2：

打开这个页面 https://www.playturbo.com/
针对当前网站 编写20条测试用例 并且执行
把生成的测试用例保存到excel中并写入到本地，
将执行结果以合适的图表格式输出，建议展示3种合适的图表
最终把设计的用例以及执行的结果以html格式写入到本地
html报告要求：
时区需要选择北京时间 一定是最新的时区
要求把所有的生成文件都写入到data目录下
每次执行的测试报告要新创建一个文件夹（按照年月日时分秒去区分）
测试环境 用例生成数 执行情况需要展示清楚 尽可能采用专业的html报告输出
报告要求显示全 测试相关的信息 可以链接测试用例或者其他信息  支持tab 或者分页显示
支持使用mcp工具发布html报告支持在线访问

作业3：

请基于下面内容 帮我实现 测试用例生成系统，大模型文件 **@llm.py** 中  将代码写入到 **@testcase_agent.py**
测试用例生成系统（langgraph实现）
 节点1：编写测试用例--直接与大模型交互
        节点2：测试用例评审（用例未通过，让节点1重新写用例，用例通过，执行节点3）--直接与大模型交互
            条件边（节点4）逻辑判断，控制边的走向
                if 通过 or 评审次数>3
                    return "节点3"
                else
                    return "节点1"

    节点3：将测试用例保存到Excel文件中

    def write_excel_node(state):
                agent = create_agent(tools=[save_test_cases_to_excel])
                agent.invoke(state["messages"])

    start--》节点1--》节点2--》节点4

    agent_builder.add_edge(START, "节点1")
        agent_builder.add_edge("节点1", "节点2")
        agent_builder.add_conditional_edges("节点2", "条件边（节点4）")

作业4：

代码生成参考提示词：
		以下代码请在当前文件 **@pdf_agent.py** 中的add_messages_middleware函数中实现：

    前端state["messages"]中接收的上传的pdf文件内容格式如下：
		[HumanMessage(content=[{'type': 'text', 'text': '总结一下'}, {'type': 'file', 'source_type': 'base64', 'mime_type': 'application/pdf', 'data': 'JVBERi0xLjcNCiWhs8XXDQoxIDAgb2JqDQo8PC9QYWdlcyAyIDAgUiAvU3RydWN0V
		......
		BEOTBDMTIyMzJDOEFDMUYxRkUxMDY+XT4+DQpzdGFydHhyZWYNCjQ5Mjc3Mg0KJSVFT0YNCg==', 'metadata': {'filename': 'llm_course.pdf'}}], additional_kwargs={}, response_metadata={}, id='da159614-312d-4490-9e30-3acff9e6330b')]

    将base64位的数据转换成正常的pdf文件，然后 借助 langchain-pymupdf4llm实现文字内容的提取，langchain-pymupdf4llm的参考地址：https://docs.langchain.com/oss/python/integrations/document_loaders/pymupdf4llm，使用多模态提取图片，多模态代码在 llm_gpt**@pdf_agent.py**

作业5:

    1、实现图片对话

    大模型：豆包/千问

    2、实现pdf对话

    大模型：deepseek

    pdf文件中可以包含图片、流程图等多模态信息

    3、正常对话

    大模型：deepseek

    根据用户上传的文件类型自动判断合适的对话智能体，可以基于graph流程实现

    节点1：检测文件类型

    节点2：图片对话

    节点3：文件对话

    节点4：正常对话

    条件边：选择合适的节点进行处理


作业6：


前端发起对话：后端从目录下读取文件内容+用户问题一起发送给大模型
	目前的实现逻辑
		前端上传base64位的数据
		后端：将base64位的pdf转换成正常的pdf文件，借助pdf文档加载器解析文字内容，将用户问题及解析后的内容发送给大模型

代码生成参考提示词：
		以下代码请在当前文件中的log_before_model 函数中实现：

    前端state["messages"]中接收的上传的pdf文件内容格式如下：
		[HumanMessage(content=[{'type': 'text', 'text': '总结一下'}, {'type': 'file', 'source_type': 'base64', 'mime_type': 'application/pdf', 'data': 'JVBERi0xLjcNCiWhs8XXDQoxIDAgb2JqDQo8PC9QYWdlcyAyIDAgUiAvU3RydWN0V
		......
		BEOTBDMTIyMzJDOEFDMUYxRkUxMDY+XT4+DQpzdGFydHhyZWYNCjQ5Mjc3Mg0KJSVFT0YNCg==', 'metadata': {'filename': 'llm_course.pdf'}}], additional_kwargs={}, response_metadata={}, id='da159614-312d-4490-9e30-3acff9e6330b')]

    将base64位的数据转换成正常的pdf文件，然后 借助 langchain-pymupdf4llm实现文字内容的提取，langchain-pymupdf4llm的参考地址：https://docs.langchain.com/oss/python/integrations/document_loaders/pymupdf4llm，使用多模态提取图片，多模态代码在 @llms.py文件中的get_doubao_seed_model函数

    把解析出的pdf内容作为AImessage 添加到state["messages"]中
