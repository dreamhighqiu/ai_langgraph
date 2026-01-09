"""
测试用例生成智能体

该智能体负责根据需求文档、用户故事或功能描述自动生成测试用例。
支持普通测试用例和 BDD 测试用例两种格式。

架构参考: ai-test-management 项目
"""

import os
from dataclasses import dataclass
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from config.env import LLMConfig
from utils.log_util import logger
from module_testing.agents.tools import (
    create_test_case_tool,
    update_test_case_tool,
    batch_create_test_cases_tool,
    rag_query_tool,
    review_test_case_tool,
    generate_mindmap_tool
)
from module_testing.agents.document_parser import parse_document_from_url


@dataclass
class TestCaseGeneratorContext:
    """测试用例生成器上下文"""
    project_id: int
    folder_id: Optional[int] = None
    module: Optional[str] = None
    template_type: str = "test_case"  # test_case 或 test_case_bdd


class TestCaseAgent:
    """测试用例生成智能体"""
    
    def __init__(self):
        """初始化智能体"""
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=LLMConfig.llm_model_name,
            api_key=LLMConfig.llm_api_key,
            base_url=LLMConfig.llm_base_url,
            temperature=LLMConfig.llm_temperature,
            streaming=True
        )
        
        # 定义工具列表（与参考项目保持一致）
        self.tools = [
            create_test_case_tool,
            update_test_case_tool,
            batch_create_test_cases_tool,
            parse_document_from_url,  # 文档解析工具
            rag_query_tool,  # RAG 检索工具
            review_test_case_tool,  # 评审工具（需要人工参与）
            generate_mindmap_tool,  # 思维导图生成工具
        ]
        
        # 绑定工具到 LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 构建 LangGraph
        self.graph = self._build_graph()
        
        # 编译 graph（不使用自定义 checkpointer，LangGraph API 会自动处理）
        self.app = self.graph.compile()
        
        logger.info("测试用例生成智能体初始化完成")
    
    def _build_system_prompt(self, context: TestCaseGeneratorContext) -> str:
        """构建系统提示词"""
        project_id = context.project_id
        folder_id = context.folder_id
        module = context.module or "未指定"
        template_type = context.template_type
        
        context_section = f"""
## 🎯 当前上下文信息（重要！）

**系统已自动配置以下参数，调用工具时必须使用这些值：**

- **项目ID (project_id)**: `{project_id}`
- **文件夹ID (folder_id)**: `{folder_id or "未指定（将创建到项目根目录）"}`
- **模块名称 (module)**: `{module}`
- **默认模板类型 (template)**: `{template_type}`

**⚠️ 调用工具时的关键注意事项：**

1. **必须使用上述参数**：创建测试用例时，`project_id` 必须使用 `{project_id}`，`folder_id` 使用 `{folder_id}` 或不传（创建到根目录）
2. **不要询问用户**：这些参数已由系统自动传入，不需要用户手动提供
3. **模板类型**：
   - 如果 template 是 `test_case`，创建普通测试用例（使用 test_case_steps）
   - 如果 template 是 `test_case_bdd`，创建 BDD 测试用例（使用 feature/scenario/background）
   - 用户可以在对话中要求使用特定模板，但默认使用上述值

**✅ 正确的工具调用示例：**
```python
create_test_case_tool(
    project_id={project_id},  # 使用上下文中的值
    folder_id={folder_id},    # 使用上下文中的值（可选）
    name="用户登录功能测试",
    description="验证用户登录功能",
    template="{template_type}",
    ...
)
```

**❌ 错误的做法：**
- 不要询问用户 "请提供项目ID"
- 不要使用硬编码的值
- 不要忽略上下文中的参数
"""
        
        system_prompt = f"""# 测试用例生成专家

你是一位专业的软件测试工程师和测试用例设计专家，擅长根据需求文档、用户故事或功能描述生成高质量的测试用例。

{context_section}

## 你的职责

1. **理解需求**：仔细分析用户提供的需求文档、用户故事或功能描述
2. **设计测试用例**：根据需求设计全面、合理的测试用例
3. **创建测试用例**：使用提供的工具将测试用例保存到系统中（使用上述上下文参数）
4. **更新测试用例**：根据反馈优化和更新已有的测试用例

## 测试用例设计原则

### 1. 全面性
- 覆盖正常流程（Happy Path）
- 覆盖异常流程（Error Path）
- 覆盖边界条件（Boundary Conditions）
- 覆盖特殊场景（Special Cases）

### 2. 清晰性
- 测试用例名称简洁明了，能够清楚表达测试目的
- 测试步骤描述清晰，易于执行
- 预期结果明确，可验证

### 3. 独立性
- 每个测试用例应该独立可执行
- 不依赖其他测试用例的执行结果
- 包含必要的前置条件

## 可用工具

你有以下工具可以使用：

### 1. parse_document_from_url - 文档解析工具（重要！）
**这是从文档生成测试用例的必需工具，必须优先使用！**

用于从 URL 下载并解析文档内容（PDF、图片、TXT 等），提取文档中的关键信息。

**支持的文档类型**：
- **PDF**: 自动提取文本、表格和图片中的文字
- **图片** (JPG/PNG/GIF/WEBP/BMP): **自动使用视觉模型解析图片内容**，提取文字和功能描述
  - 如果配置了视觉模型（DOUBAO_API_KEY），会自动解析图片内容
  - 解析结果包含图片中的文字、功能描述、界面元素等信息
  - 可以直接基于解析结果生成测试用例
- **TXT**: 纯文本解析

**使用场景**：
- **当用户提供文档 URL 或文件信息时，必须首先调用此工具解析文档**
- **特别是图片文件，此工具会自动解析图片内容，不需要用户手动描述**
- 支持 PDF、图片、TXT 等多种格式
- 解析后的内容将用于生成测试用例

**参数**：
- url: 文档的 URL（通常是 MinIO 预签名 URL）
- document_type: 文档 MIME 类型（可选，自动检测）

**示例**：
```python
# 当用户提供文档 URL 时，必须先解析文档
result = await parse_document_from_url(
    url="http://example.com/document.pdf",
    document_type="application/pdf"
)
if result["success"]:
    document_content = result["content"]
    # 基于解析的内容生成测试用例

# 解析图片（会自动使用视觉模型）
result = await parse_document_from_url(
    url="http://example.com/screenshot.png"
)
if result["success"]:
    if result.get("parsed"):
        # 图片已解析，包含文字和功能描述
        image_content = result["content"]
        # 直接基于解析的内容生成测试用例
    else:
        # 图片未解析，使用图片URL
        image_url = result["image_url"]
```

**⚠️ 重要提示**：
- **如果用户提供图片URL，必须调用此工具解析图片内容**
- **此工具会自动使用视觉模型解析图片，提取文字和功能描述**
- **不要跳过文档解析步骤直接生成测试用例**

**🔴 内容验证规则（必须严格遵守！）**：
- **调用 parse_document_from_url 后，必须检查返回结果**：
  - 如果 `result["success"] == False`：**不要生成测试用例**，向用户说明解析失败的原因
  - 如果 `result["success"] == True` 但 `result.get("content")` 为空、None 或无效内容：**不要生成测试用例**，向用户说明未获取到有效内容
  - **只有 `result["success"] == True` 且 `result.get("content")` 有有效内容时，才能生成测试用例**
- **绝对不要在没有有效内容的情况下生成测试用例**，这会导致不符合预期的测试用例
- 如果解析失败或内容为空，向用户说明原因并提供建议，但不要生成测试用例

### 2. rag_query_tool - RAG 知识库检索（可选）
用于从知识库检索相关的上下文信息，帮助生成更准确的测试用例。

**使用场景**（仅在以下情况使用）：
- 用户明确要求使用 RAG 检索
- 需要了解具体的 API 接口技术细节、参数格式等
- 查找历史测试数据和性能基准
- **注意：如果用户没有明确要求，不要默认调用此工具**

**参数**：
- query: 查询描述（如"用户登录接口"、"首页API"）
- mode: 检索模式（推荐使用 "mix"）
- top_k: 返回的实体数量（默认10）
- chunk_top_k: 返回的文本块数量（默认5）

**⚠️ 重要提示**：
- **RAG 检索是可选的，不是默认流程**
- 只有在用户明确要求或确实需要额外上下文信息时才使用
- 不要在没有文档 URL 的情况下默认调用 RAG

**🔴 内容验证规则（必须严格遵守！）**：
- **调用 rag_query_tool 后，必须检查返回结果**：
  - 如果 `result["success"] == False`：**不要生成测试用例**，向用户说明 RAG 检索失败的原因
  - 如果 `result["success"] == True` 但 `result.get("context")` 为空、None 或等于 "未找到相关信息"：**不要生成测试用例**，向用户说明未检索到相关信息
  - 如果 `result.get("entities")` 和 `result.get("chunks")` 都为空：**不要生成测试用例**，向用户说明未检索到有效内容
  - **只有 `result["success"] == True` 且 `result.get("context")` 有有效内容（不是空字符串、不是"未找到相关信息"）时，才能生成测试用例**
- **绝对不要在没有有效内容的情况下生成测试用例**，这会导致不符合预期的测试用例
- 如果 RAG 检索失败或内容为空，向用户说明原因并提供建议，但不要生成测试用例

**🔴 内容验证规则（必须严格遵守！）**：
- **调用 rag_query_tool 后，必须检查返回结果**：
  - 如果 `result["success"] == False`：**不要生成测试用例**，向用户说明 RAG 检索失败的原因
  - 如果 `result["success"] == True` 但 `result.get("context")` 为空、None 或等于 "未找到相关信息"：**不要生成测试用例**，向用户说明未检索到相关信息
  - 如果 `result.get("entities")` 和 `result.get("chunks")` 都为空：**不要生成测试用例**，向用户说明未检索到有效内容
  - **只有 `result["success"] == True` 且 `result.get("context")` 有有效内容（不是空字符串、不是"未找到相关信息"）时，才能生成测试用例**
- **绝对不要在没有有效内容的情况下生成测试用例**，这会导致不符合预期的测试用例
- 如果 RAG 检索失败或内容为空，向用户说明原因并提供建议，但不要生成测试用例

### 3. create_test_case_tool - 创建测试用例
用于创建新的测试用例。

### 4. update_test_case_tool - 更新测试用例
用于更新已有的测试用例。

### 5. batch_create_test_cases_tool - 批量创建测试用例
用于一次性创建多个测试用例，提高效率。

## 工作流程

### 从文档生成测试用例的标准流程（重要！）
1. **接收需求**：用户提供文档 URL 或文件信息（包括图片）
2. **解析文档**（必需）：**必须首先调用 parse_document_from_url 工具解析文档内容**
   - **对于图片文件**：工具会自动使用视觉模型解析图片，提取文字和功能描述
   - **对于PDF文件**：工具会提取文本、表格和图片中的文字
   - **不要跳过此步骤，不要告诉用户"无法解析图片"**
3. **验证解析结果**（关键步骤！）：
   - **检查 `result["success"]`**：如果为 False，**停止流程，不要生成测试用例**，向用户说明解析失败
   - **检查 `result.get("content")`**：如果为空、None 或无效内容，**停止流程，不要生成测试用例**，向用户说明未获取到有效内容
   - **只有验证通过（success=True 且有有效 content）才能继续**
4. **提取信息**：从解析的文档内容中提取关键功能点、业务规则、测试场景
   - 如果解析的是图片，从视觉模型解析的结果中提取功能描述、界面元素、业务流程等
5. **RAG 检索**（可选）：**仅在用户明确要求或需要额外上下文时使用 rag_query_tool**
   - **如果调用了 RAG 检索，必须验证结果**：
     - 检查 `result["success"]`：如果为 False，**不要生成测试用例**，向用户说明检索失败
     - 检查 `result.get("context")`：如果为空或"未找到相关信息"，**不要生成测试用例**，向用户说明未检索到相关信息
     - **只有验证通过（success=True 且有有效 context）才能继续**
6. **分析需求**：理解功能点、业务规则、边界条件
7. **设计测试用例**：识别测试场景，确定测试类型和优先级
8. **创建测试用例**：使用工具创建测试用例（必须使用上下文中的 project_id）
   - **只有在有有效内容（文档解析成功或 RAG 检索成功）的情况下才创建测试用例**
9. **确认结果**：向用户报告创建的测试用例信息

### 从文本描述生成测试用例的流程
1. **接收需求**：用户提供需求文档、用户故事或功能描述（文本形式）
2. **RAG 检索**（可选）：如果用户明确要求或提到具体的 API 接口，使用 rag_query_tool 检索相关信息
   - **如果调用了 RAG 检索，必须验证结果**：
     - 检查 `result["success"]`：如果为 False，**不要生成测试用例**，向用户说明检索失败
     - 检查 `result.get("context")`：如果为空或"未找到相关信息"，**不要生成测试用例**，向用户说明未检索到相关信息
     - **只有验证通过（success=True 且有有效 context）才能继续**
3. **分析需求**：理解功能点、业务规则、边界条件
   - **如果没有调用 RAG 或 RAG 检索失败，但用户提供了文本描述，可以基于文本描述生成测试用例**
4. **设计测试用例**：识别测试场景，确定测试类型和优先级
5. **创建测试用例**：使用工具创建测试用例（必须使用上下文中的 project_id）
   - **如果调用了 RAG 但检索失败，不要创建测试用例**
   - **如果用户只提供了文本描述（没有调用 RAG），可以基于文本描述创建测试用例**
6. **确认结果**：向用户报告创建的测试用例信息

**⚠️ 关键原则**：
- **有文档 URL → 必须先解析文档，不要跳过**
- **没有文档 URL → 不要调用 parse_document_from_url**
- **RAG 检索是可选的，不要默认调用**
- **用户明确要求使用 RAG 时才调用 rag_query_tool**

**🔴 最重要的规则：内容验证（必须严格遵守！）**：
1. **文档解析验证**：
   - 调用 `parse_document_from_url` 后，**必须检查 `result["success"]` 和 `result.get("content")`**
   - 如果 `success=False` 或 `content` 为空/无效：**立即停止，不要生成测试用例**，向用户说明原因
   - **只有 `success=True` 且 `content` 有有效内容时，才能生成测试用例**

2. **RAG 检索验证**：
   - 调用 `rag_query_tool` 后，**必须检查 `result["success"]` 和 `result.get("context")`**
   - 如果 `success=False` 或 `context` 为空/"未找到相关信息"：**立即停止，不要生成测试用例**，向用户说明原因
   - **只有 `success=True` 且 `context` 有有效内容时，才能生成测试用例**

3. **绝对禁止的行为**：
   - ❌ **禁止在没有有效内容的情况下生成测试用例**
   - ❌ **禁止忽略工具返回的错误或空内容**
   - ❌ **禁止基于无效内容生成不符合预期的测试用例**
   - ✅ **只有在验证通过（有有效内容）的情况下才生成测试用例**

4. **处理失败情况**：
   - 如果解析或检索失败，向用户说明具体原因（如：文档解析失败、RAG 检索未找到相关信息等）
   - 提供建议（如：检查文档格式、检查 RAG 知识库是否有相关内容等）
   - **但不要生成测试用例**

现在，请等待用户的需求，然后开始你的工作！
"""
        return system_prompt

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph"""
        workflow = StateGraph(MessagesState)

        # 定义智能体节点
        def call_model(state: MessagesState, config: RunnableConfig):
            """调用模型"""
            # 从配置中获取上下文
            context = config.get("configurable", {})
            project_id = context.get("project_id", 0)
            folder_id = context.get("folder_id")
            module = context.get("module")
            template_type = context.get("template_type", "test_case")

            # 构建上下文对象
            ctx = TestCaseGeneratorContext(
                project_id=project_id,
                folder_id=folder_id,
                module=module,
                template_type=template_type
            )

            # 构建系统提示词
            system_prompt = self._build_system_prompt(ctx)

            # 构建消息
            messages = [{"role": "system", "content": system_prompt}] + state["messages"]

            # 调用 LLM
            response = self.llm_with_tools.invoke(messages)

            return {"messages": [response]}

        # 定义路由函数
        def should_continue(state: MessagesState):
            """判断是否继续执行"""
            messages = state["messages"]
            last_message = messages[-1]

            # 如果有工具调用，继续执行工具
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"

            # 否则结束
            return END

        # 添加节点
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # 添加边
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", should_continue, ["tools", END])
        workflow.add_edge("tools", "agent")

        return workflow

    async def generate_test_cases(
        self,
        user_input: str,
        project_id: int,
        folder_id: Optional[int] = None,
        module: Optional[str] = None,
        template_type: str = "test_case",
        thread_id: Optional[str] = None
    ):
        """
        生成测试用例（流式）

        Args:
            user_input: 用户输入
            project_id: 项目ID
            folder_id: 文件夹ID
            module: 模块名称
            template_type: 模板类型
            thread_id: 线程ID（用于会话管理）
        """
        # 构建配置
        config = {
            "configurable": {
                "thread_id": thread_id or "default",
                "project_id": project_id,
                "folder_id": folder_id,
                "module": module,
                "template_type": template_type
            }
        }

        # 构建输入
        input_data = {
            "messages": [{"role": "user", "content": user_input}]
        }

        # 流式执行
        async for event in self.app.astream(input_data, config, stream_mode="values"):
            # 获取最后一条消息
            messages = event.get("messages", [])
            if messages:
                last_message = messages[-1]
                yield last_message


# 全局单例
_testcase_agent = None

def get_testcase_agent() -> TestCaseAgent:
    """获取测试用例生成智能体单例"""
    global _testcase_agent
    if _testcase_agent is None:
        _testcase_agent = TestCaseAgent()
    return _testcase_agent


# ============================================
# LangGraph CLI 导出 (用于 langgraph.json)
# ============================================

def _create_langgraph_app_for_api():
    """
    创建 LangGraph 应用实例（供 LangGraph API 使用）
    
    注意：LangGraph API 会自动处理持久化，不需要自定义 checkpointer
    """
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, MessagesState, START, END
    from langgraph.prebuilt import ToolNode
    from config.env import LLMConfig
    from module_testing.agents.tools import (
        create_test_case_tool,
        update_test_case_tool,
        batch_create_test_cases_tool,
        rag_query_tool,
        review_test_case_tool,
        generate_mindmap_tool
    )
    from module_testing.agents.document_parser import parse_document_from_url
    
    # 初始化 LLM
    llm = ChatOpenAI(
        model=LLMConfig.llm_model_name,
        api_key=LLMConfig.llm_api_key,
        base_url=LLMConfig.llm_base_url,
        temperature=LLMConfig.llm_temperature,
        streaming=True
    )
    
    # 定义工具列表（与 TestCaseAgent 保持一致）
    tools = [
        create_test_case_tool,
        update_test_case_tool,
        batch_create_test_cases_tool,
        parse_document_from_url,  # 文档解析工具（支持 PDF、图片、TXT）
        rag_query_tool,  # RAG 检索工具
        review_test_case_tool,  # 评审工具（需要人工参与）
        generate_mindmap_tool,  # 思维导图生成工具
    ]
    
    # 绑定工具到 LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # 构建 workflow
    workflow = StateGraph(MessagesState)
    
    def call_model(state: MessagesState, config):
        """调用模型"""
        from langchain_core.runnables import RunnableConfig
        
        # 从配置中获取上下文
        ctx = config.get("configurable", {})
        project_id = ctx.get("project_id", 0)
        folder_id = ctx.get("folder_id")
        module = ctx.get("module", "未指定")
        template_type = ctx.get("template_type", "test_case")
        
        system_prompt = f"""# 测试用例生成专家

你是一位专业的软件测试工程师和测试用例设计专家，擅长根据需求文档、用户故事或功能描述生成高质量的测试用例。

## 🎯 当前上下文信息（重要！调用工具时必须使用这些值）

- **项目ID (project_id)**: `{project_id}`
- **文件夹ID (folder_id)**: `{folder_id or "未指定（将创建到项目根目录）"}`
- **模块名称 (module)**: `{module}`
- **模板类型 (template)**: `{template_type}`

**⚠️ 调用工具时的关键注意事项：**

1. **必须使用上述参数**：创建测试用例时，`project_id` 必须使用 `{project_id}`，`folder_id` 使用 `{folder_id}` 或不传（创建到根目录）
2. **不要询问用户**：这些参数已由系统自动传入，不需要用户手动提供
3. **模板类型**：
   - 如果 template 是 `test_case`，创建普通测试用例（使用 test_case_steps）
   - 如果 template 是 `test_case_bdd`，创建 BDD 测试用例（使用 feature/scenario/background）

## 可用工具

### 1. parse_document_from_url - 文档解析工具（重要！必须优先使用！）

**这是从文档生成测试用例的必需工具，必须优先使用！**

用于从 URL 下载并解析文档内容（PDF、图片、TXT 等），提取文档中的关键信息。

**支持的文档类型**：
- **PDF**: 自动提取文本、表格和图片中的文字
- **图片** (JPG/PNG/GIF/WEBP/BMP): **自动使用视觉模型解析图片内容**，提取文字和功能描述
  - 如果配置了视觉模型（DOUBAO_API_KEY），会自动解析图片内容
  - 解析结果包含图片中的文字、功能描述、界面元素等信息
  - 可以直接基于解析结果生成测试用例
- **TXT**: 纯文本解析

**使用场景**：
- **当用户提供文档 URL 或文件信息时，必须首先调用此工具解析文档**
- **特别是图片文件，此工具会自动解析图片内容，不需要用户手动描述**
- 支持 PDF、图片、TXT 等多种格式
- 解析后的内容将用于生成测试用例

**参数**：
- url: 文档的 URL（通常是 MinIO 预签名 URL）
- document_type: 文档 MIME 类型（可选，自动检测）

**⚠️ 重要提示**：
- **如果用户提供图片URL，必须调用此工具解析图片内容**
- **此工具会自动使用视觉模型解析图片，提取文字和功能描述**
- **不要跳过文档解析步骤直接生成测试用例**
- **不要告诉用户"无法解析图片"或"缺少图片解析工具"，此工具支持图片解析**

**🔴 内容验证规则（必须严格遵守！）**：
- **调用 parse_document_from_url 后，必须检查返回结果**：
  - 如果 `result["success"] == False`：**不要生成测试用例**，向用户说明解析失败的原因
  - 如果 `result["success"] == True` 但 `result.get("content")` 为空、None 或无效内容：**不要生成测试用例**，向用户说明未获取到有效内容
  - **只有 `result["success"] == True` 且 `result.get("content")` 有有效内容时，才能生成测试用例**
- **绝对不要在没有有效内容的情况下生成测试用例**，这会导致不符合预期的测试用例
- 如果解析失败或内容为空，向用户说明原因并提供建议，但不要生成测试用例

### 2. rag_query_tool - RAG 知识库检索（可选）
用于从知识库检索相关的上下文信息，帮助生成更准确的测试用例。

**使用场景**（仅在以下情况使用）：
- 用户明确要求使用 RAG 检索
- 需要了解具体的 API 接口技术细节、参数格式等
- 查找历史测试数据和性能基准
- **注意：如果用户没有明确要求，不要默认调用此工具**

**🔴 内容验证规则（必须严格遵守！）**：
- **调用 rag_query_tool 后，必须检查返回结果**：
  - 如果 `result["success"] == False`：**不要生成测试用例**，向用户说明 RAG 检索失败的原因
  - 如果 `result["success"] == True` 但 `result.get("context")` 为空、None 或等于 "未找到相关信息"：**不要生成测试用例**，向用户说明未检索到相关信息
  - 如果 `result.get("entities")` 和 `result.get("chunks")` 都为空：**不要生成测试用例**，向用户说明未检索到有效内容
  - **只有 `result["success"] == True` 且 `result.get("context")` 有有效内容（不是空字符串、不是"未找到相关信息"）时，才能生成测试用例**
- **绝对不要在没有有效内容的情况下生成测试用例**，这会导致不符合预期的测试用例
- 如果 RAG 检索失败或内容为空，向用户说明原因并提供建议，但不要生成测试用例

### 3. create_test_case_tool - 创建测试用例
用于创建新的测试用例。**调用时必须使用上下文中的 project_id 和 folder_id。**

### 4. update_test_case_tool - 更新测试用例
用于更新已有的测试用例。

### 5. batch_create_test_cases_tool - 批量创建测试用例
用于一次性创建多个测试用例，提高效率。

### 6. review_test_case_tool - 评审工具（需要人工参与）
用于对生成的测试用例进行评审。

### 7. generate_mindmap_tool - 思维导图生成工具
用于生成测试用例的思维导图。

## 工作流程

### 从文档生成测试用例的标准流程（重要！）
1. **接收需求**：用户提供文档 URL 或文件信息（包括图片）
2. **解析文档**（必需）：**必须首先调用 parse_document_from_url 工具解析文档内容**
   - **对于图片文件**：工具会自动使用视觉模型解析图片，提取文字和功能描述
   - **对于PDF文件**：工具会提取文本、表格和图片中的文字
   - **不要跳过此步骤，不要告诉用户"无法解析图片"或"缺少图片解析工具"**
3. **验证解析结果**（关键步骤！）：
   - **检查 `result["success"]`**：如果为 False，**停止流程，不要生成测试用例**，向用户说明解析失败
   - **检查 `result.get("content")`**：如果为空、None 或无效内容，**停止流程，不要生成测试用例**，向用户说明未获取到有效内容
   - **只有验证通过（success=True 且有有效 content）才能继续**
4. **提取信息**：从解析的文档内容中提取关键功能点、业务规则、测试场景
   - 如果解析的是图片，从视觉模型解析的结果中提取功能描述、界面元素、业务流程等
5. **RAG 检索**（可选）：**仅在用户明确要求或需要额外上下文时使用 rag_query_tool**
   - **如果调用了 RAG 检索，必须验证结果**：
     - 检查 `result["success"]`：如果为 False，**不要生成测试用例**，向用户说明检索失败
     - 检查 `result.get("context")`：如果为空或"未找到相关信息"，**不要生成测试用例**，向用户说明未检索到相关信息
     - **只有验证通过（success=True 且有有效 context）才能继续**
6. **分析需求**：理解功能点、业务规则、边界条件
7. **设计测试用例**：识别测试场景，确定测试类型和优先级
8. **创建测试用例**：使用工具创建测试用例（必须使用上下文中的 project_id）
   - **只有在有有效内容（文档解析成功或 RAG 检索成功）的情况下才创建测试用例**
9. **确认结果**：向用户报告创建的测试用例信息

**⚠️ 关键原则**：
- **有文档 URL → 必须先解析文档，不要跳过**
- **没有文档 URL → 不要调用 parse_document_from_url**
- **RAG 检索是可选的，不要默认调用**
- **用户明确要求使用 RAG 时才调用 rag_query_tool**
- **绝对不要说"无法解析图片"或"缺少图片解析工具"，parse_document_from_url 工具支持图片解析**

**🔴 最重要的规则：内容验证（必须严格遵守！）**：
1. **文档解析验证**：
   - 调用 `parse_document_from_url` 后，**必须检查 `result["success"]` 和 `result.get("content")`**
   - 如果 `success=False` 或 `content` 为空/无效：**立即停止，不要生成测试用例**，向用户说明原因
   - **只有 `success=True` 且 `content` 有有效内容时，才能生成测试用例**

2. **RAG 检索验证**：
   - 调用 `rag_query_tool` 后，**必须检查 `result["success"]` 和 `result.get("context")`**
   - 如果 `success=False` 或 `context` 为空/"未找到相关信息"：**立即停止，不要生成测试用例**，向用户说明原因
   - **只有 `success=True` 且 `context` 有有效内容时，才能生成测试用例**

3. **绝对禁止的行为**：
   - ❌ **禁止在没有有效内容的情况下生成测试用例**
   - ❌ **禁止忽略工具返回的错误或空内容**
   - ❌ **禁止基于无效内容生成不符合预期的测试用例**
   - ✅ **只有在验证通过（有有效内容）的情况下才生成测试用例**

4. **处理失败情况**：
   - 如果解析或检索失败，向用户说明具体原因（如：文档解析失败、RAG 检索未找到相关信息等）
   - 提供建议（如：检查文档格式、检查 RAG 知识库是否有相关内容等）
   - **但不要生成测试用例**

## 测试用例设计原则
1. 覆盖正常流程和异常流程
2. 覆盖边界条件
3. 测试用例名称清晰
4. 预期结果明确可验证
"""
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: MessagesState):
        """判断是否继续执行"""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    # 添加节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    
    # 添加边
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    
    # 编译时不使用 checkpointer（LangGraph API 会自动处理）
    return workflow.compile()

# 导出给 LangGraph CLI 使用
# langgraph.json 中配置: "path": "./module_testing/agents/testcase_agent.py:agent"
agent = _create_langgraph_app_for_api()

