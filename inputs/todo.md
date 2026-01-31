需要优化抽屉ai 对话框
1. 左侧列表状态信息 以及标题展示 支持状态筛选
2. 新建对话框应该支持上传文件（图片 各个文档格式）以及支持选择rag 支持选择这些内容之后和大模型对话
使用deepagents去和大模型对话 完成问答
3. 支持多轮对话问答有记忆体功能

需要实现知识库和缺陷管理 用例管理 需求分析的上传文档功能是互通的
上传过程中这些文件会入库到知识库rag 调用向量化入库功能 http://localhost:9621/docs
可以分析 @anything-chat-rag



需要参照 测试用例智能实现的实现逻辑 去实现UI自动化的功能
不过UI自动化除了生成测试用例之外 还需要在平台执行测试用例 生成测试报告
这里面的逻辑已经实现在 @testing-agents-service/src/ui_automation 
需要参照这里面的实现技术
去实现UI自动化相关功能
UI自动化前端已经实现了相关功能 需要按照现有的要求去更新或者重新实现这块
技术方案是参照测试用例智能生成的逻辑
但是底层技术是参照 @testing-agents-service/src/ui_automation 
智能生成自动化测试用例可以用agent实现
其他的功能可以用工具去实现
通过调用API 去保存脚本 和执行的结果 生成的报告
思路参照测试用例智能生成 

其他模块有UI自动化相关的代码可以删除掉 避免重复
UI自动化的后端处理都可以放在  @RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_ui_testing 

切记 UI自动化测试相关的代码都要挪到 RuoYi-Vue3-FastAPI\ruoyi-fastapi-backend\module_ui_testing这个目录下 做好项目功能分离
