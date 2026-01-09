"""
AI 测试用例生成控制器
提供 AI 智能生成测试用例的 API 接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_testing.agents.langgraph_client import get_langgraph_client
from module_testing.service.test_case_service import TestCaseService
from common.annotation.log_annotation import Log
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.enums import BusinessType
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/ai-testcase", tags=["AI 测试用例生成"])
test_case_service = TestCaseService()


class AIGenerateRequest(BaseModel):
    """AI 生成测试用例请求"""
    project_id: int = Field(..., description="项目ID")
    folder_id: Optional[int] = Field(None, description="目标文件夹ID")
    prompt: str = Field(..., description="需求描述")
    count: int = Field(5, ge=1, le=20, description="生成数量")
    template: str = Field("test_case", description="模板类型: test_case 或 test_case_bdd")
    use_rag: bool = Field(False, description="是否使用 RAG 知识库增强")


class AIGenerateFromDocRequest(BaseModel):
    """从文档生成测试用例请求"""
    project_id: int = Field(..., description="项目ID")
    folder_id: Optional[int] = Field(None, description="目标文件夹ID")
    document_content: str = Field(..., description="文档内容")
    document_type: str = Field("text", description="文档类型: text, markdown, html")
    additional_notes: Optional[str] = Field(None, description="附加说明")
    count: int = Field(5, ge=1, le=20, description="生成数量")
    template: str = Field("test_case", description="模板类型")


class TestCaseItem(BaseModel):
    """测试用例项"""
    case_name: str = Field(..., description="用例名称")
    description: Optional[str] = Field(None, description="描述")
    case_type: str = Field("functional", description="用例类型")
    priority: str = Field("medium", description="优先级")
    preconditions: Optional[str] = Field(None, description="前置条件")
    test_case_steps: Optional[List[dict]] = Field(None, description="测试步骤")
    expected_result: Optional[str] = Field(None, description="预期结果")
    tags: Optional[List[str]] = Field(None, description="标签")


class BatchCreateFromAIRequest(BaseModel):
    """批量创建测试用例请求（从 AI 结果）"""
    project_id: int = Field(..., description="项目ID")
    folder_id: Optional[int] = Field(None, description="文件夹ID")
    test_cases: List[TestCaseItem] = Field(..., description="测试用例列表")


@router.post("/generate", summary="AI 生成测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:add')])
@Log(title='AI生成测试用例', business_type=BusinessType.INSERT)
async def ai_generate_test_cases(
    request: AIGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    AI 生成测试用例
    
    根据需求描述使用 AI 智能生成测试用例。
    支持使用 RAG 知识库增强生成效果。
    """
    try:
        client = get_langgraph_client()
        
        # 构建 AI 提示词
        prompt = f"""请帮我生成测试用例。

需求描述：
{request.prompt}

生成要求：
- 生成数量：{request.count} 个
- 模板类型：{'标准测试用例（步骤-预期结果格式）' if request.template == 'test_case' else 'BDD 测试用例（Given-When-Then格式）'}
- 项目ID：{request.project_id}
{f'- 文件夹ID：{request.folder_id}' if request.folder_id else ''}

请生成完整的测试用例，每个用例包含：
1. 用例名称
2. 前置条件
3. 测试步骤（步骤编号、操作、预期结果）
4. 优先级（high/medium/low）
5. 用例类型（functional/performance/security等）

{"请先使用 rag_query_tool 从知识库检索相关信息，然后基于检索结果生成测试用例。" if request.use_rag else ""}

生成完成后，请使用 batch_create_test_cases_tool 工具保存测试用例。"""

        # 构建配置
        config = {
            'project_id': request.project_id,
            'folder_id': request.folder_id,
            'template': request.template
        }
        
        # 调用 AI Agent
        result = await client.invoke_agent(
            assistant_id="testcase_generator_agent",
            message=prompt,
            config=config
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                data={
                    'content': result.get('content', ''),
                    'thread_id': result.get('thread_id'),
                    'messages': result.get('messages', [])
                },
                msg="AI 生成测试用例请求已提交"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', 'AI 生成失败'))
            
    except Exception as e:
        logger.error(f"AI 生成测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"AI 生成测试用例失败: {str(e)}")


@router.post("/generate-from-doc", summary="从文档生成测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:add')])
@Log(title='从文档生成测试用例', business_type=BusinessType.INSERT)
async def generate_from_document(
    request: AIGenerateFromDocRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    从文档内容生成测试用例
    
    分析文档内容，提取测试场景并生成测试用例。
    """
    try:
        client = get_langgraph_client()
        
        # 构建 AI 提示词
        prompt = f"""请分析以下文档内容，并生成测试用例。

文档类型：{request.document_type}

文档内容：
{request.document_content}

{f'附加说明：{request.additional_notes}' if request.additional_notes else ''}

生成要求：
- 生成数量：{request.count} 个
- 模板类型：{'标准测试用例' if request.template == 'test_case' else 'BDD 测试用例'}
- 项目ID：{request.project_id}

请：
1. 分析文档，提取关键功能点和测试场景
2. 针对每个场景生成完整的测试用例
3. 确保覆盖正常流程、异常流程和边界条件
4. 使用 batch_create_test_cases_tool 保存生成的测试用例"""

        # 构建配置
        config = {
            'project_id': request.project_id,
            'folder_id': request.folder_id,
            'template': request.template
        }
        
        # 调用 AI Agent
        result = await client.invoke_agent(
            assistant_id="testcase_generator_agent",
            message=prompt,
            config=config
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                data={
                    'content': result.get('content', ''),
                    'thread_id': result.get('thread_id'),
                    'messages': result.get('messages', [])
                },
                msg="文档分析完成"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '文档分析失败'))
            
    except Exception as e:
        logger.error(f"从文档生成测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"从文档生成测试用例失败: {str(e)}")


@router.post("/batch-create", summary="批量创建 AI 生成的测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:add')])
@Log(title='批量创建测试用例', business_type=BusinessType.INSERT)
async def batch_create_from_ai(
    request: BatchCreateFromAIRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    批量创建 AI 生成的测试用例
    
    将 AI 生成的测试用例批量保存到数据库。
    """
    try:
        from module_testing.entity.vo.test_case_vo import TestCaseCreateVO
        
        # 转换为 TestCaseCreateVO 列表
        test_case_vos = []
        for tc in request.test_cases:
            vo = TestCaseCreateVO(
                project_id=request.project_id,
                folder_id=request.folder_id,
                case_name=tc.case_name,
                description=tc.description,
                case_type=tc.case_type,
                priority=tc.priority,
                preconditions=tc.preconditions,
                test_case_steps=tc.test_case_steps,
                expected_result=tc.expected_result,
                tags=tc.tags
            )
            test_case_vos.append(vo)
        
        # 批量创建
        results = await test_case_service.batch_create_test_cases(
            db, test_case_vos, current_user.get('user_name', 'system')
        )
        
        return ResponseUtil.success(
            data={
                'created_count': len(results),
                'case_ids': [r.case_id for r in results]
            },
            msg=f"成功创建 {len(results)} 个测试用例"
        )
        
    except Exception as e:
        logger.error(f"批量创建测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"批量创建测试用例失败: {str(e)}")


@router.get("/suggestions", summary="获取 AI 生成建议", dependencies=[UserInterfaceAuthDependency('testing:testcase:list')])
async def get_generation_suggestions(
    project_id: int = Query(..., description="项目ID"),
    context: Optional[str] = Query(None, description="上下文信息"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    获取 AI 生成建议
    
    根据项目上下文提供测试用例生成建议。
    """
    try:
        # 获取项目信息
        from module_testing.service.project_service import ProjectService
        project_service = ProjectService()
        
        project = await project_service.get_project_by_id(db, project_id)
        if not project:
            return ResponseUtil.failure(msg="项目不存在")
        
        # 构建建议
        suggestions = [
            {
                "label": "为登录功能生成测试用例",
                "prompt": f"为 {project.project_name} 项目的用户登录功能生成测试用例，包括用户名密码验证、记住密码、忘记密码、第三方登录等场景"
            },
            {
                "label": "为注册功能生成测试用例",
                "prompt": f"为 {project.project_name} 项目的用户注册功能生成测试用例，包括表单验证、邮箱/手机验证、用户协议等场景"
            },
            {
                "label": "为搜索功能生成测试用例",
                "prompt": f"为 {project.project_name} 项目的搜索功能生成测试用例，包括关键词搜索、筛选、排序、分页等场景"
            }
        ]
        
        return ResponseUtil.success(data=suggestions)
        
    except Exception as e:
        logger.error(f"获取生成建议失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取生成建议失败: {str(e)}")

