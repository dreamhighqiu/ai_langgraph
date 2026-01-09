"""
AI 缺陷分析控制器
提供 AI 智能分析缺陷的 API 接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_testing.agents.langgraph_client import get_langgraph_client
from common.annotation.log_annotation import Log
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.enums import BusinessType
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/ai-defect", tags=["AI 缺陷分析"])


class AIAnalyzeDefectRequest(BaseModel):
    """AI 分析缺陷请求"""
    project_id: int = Field(..., description="项目ID")
    defect_id: Optional[int] = Field(None, description="缺陷ID")
    title: str = Field(..., description="缺陷标题")
    description: str = Field(..., description="缺陷描述")
    steps_to_reproduce: Optional[str] = Field(None, description="重现步骤")
    environment: Optional[str] = Field(None, description="环境信息")
    severity: Optional[str] = Field(None, description="严重程度")
    analysis_type: str = Field("full", description="分析类型: full(完整分析), cause(原因分析), impact(影响分析), fix(修复建议)")
    use_rag: bool = Field(False, description="是否使用 RAG 知识库增强")


class AIClassifyDefectRequest(BaseModel):
    """AI 缺陷分类请求"""
    project_id: int = Field(..., description="项目ID")
    title: str = Field(..., description="缺陷标题")
    description: str = Field(..., description="缺陷描述")


class DefectAnalysisSaveRequest(BaseModel):
    """保存缺陷分析结果请求"""
    project_id: int = Field(..., description="项目ID")
    defect_id: Optional[int] = Field(None, description="关联缺陷ID")
    title: str = Field(..., description="缺陷标题")
    description: str = Field(..., description="缺陷描述")
    analysis_result: str = Field(..., description="分析结果")
    root_cause: Optional[str] = Field(None, description="根本原因")
    impact_scope: Optional[str] = Field(None, description="影响范围")
    severity_suggestion: Optional[str] = Field(None, description="严重程度建议")
    priority_suggestion: Optional[str] = Field(None, description="优先级建议")
    fix_suggestions: Optional[List[str]] = Field(None, description="修复建议")
    similar_defects: Optional[List[int]] = Field(None, description="相似缺陷ID列表")


@router.post("/analyze", summary="AI 分析缺陷", dependencies=[UserInterfaceAuthDependency('testing:defect:list')])
@Log(title='AI分析缺陷', business_type=BusinessType.OTHER)
async def ai_analyze_defect(
    request: AIAnalyzeDefectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    AI 分析缺陷
    
    使用 AI 分析缺陷的根本原因、影响范围和修复建议。
    """
    try:
        client = get_langgraph_client()
        
        # 根据分析类型构建提示词
        analysis_prompts = {
            "full": "请进行全面分析，包括根本原因、影响范围和修复建议",
            "cause": "请重点分析缺陷的根本原因，可能涉及的代码模块和逻辑问题",
            "impact": "请重点分析缺陷的影响范围，包括功能影响、用户影响和业务影响",
            "fix": "请重点提供修复建议，包括临时修复方案和长期解决方案"
        }
        
        analysis_instruction = analysis_prompts.get(request.analysis_type, analysis_prompts["full"])
        
        prompt = f"""请分析以下缺陷。

缺陷标题：{request.title}

缺陷描述：
{request.description}

{f'重现步骤：{chr(10)}{request.steps_to_reproduce}' if request.steps_to_reproduce else ''}

{f'环境信息：{request.environment}' if request.environment else ''}

{f'当前严重程度：{request.severity}' if request.severity else ''}

分析要求：
{analysis_instruction}

请提供：
1. 根本原因分析
2. 影响范围评估
3. 严重程度建议（critical/major/minor/trivial）
4. 优先级建议（high/medium/low）
5. 修复建议列表
6. 预防措施

{"请先使用 rag_query_tool 从知识库检索相似的缺陷案例，然后基于历史经验进行分析。" if request.use_rag else ""}

分析完成后，请使用 save_defect_analysis_tool 保存分析结果。"""

        # 构建配置
        config = {
            'project_id': request.project_id,
            'defect_id': request.defect_id,
            'analysis_type': request.analysis_type
        }
        
        # 调用 AI Agent
        result = await client.invoke_agent(
            assistant_id="defect_analyzer_agent",
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
                msg="缺陷分析完成"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '缺陷分析失败'))
            
    except Exception as e:
        logger.error(f"AI 分析缺陷失败: {str(e)}")
        return ResponseUtil.failure(msg=f"AI 分析缺陷失败: {str(e)}")


@router.post("/classify", summary="AI 缺陷分类", dependencies=[UserInterfaceAuthDependency('testing:defect:list')])
@Log(title='AI缺陷分类', business_type=BusinessType.OTHER)
async def classify_defect(
    request: AIClassifyDefectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    AI 缺陷分类
    
    使用 AI 自动对缺陷进行分类。
    """
    try:
        client = get_langgraph_client()
        
        prompt = f"""请对以下缺陷进行分类。

缺陷标题：{request.title}

缺陷描述：
{request.description}

请提供以下分类信息：
1. 缺陷类型（功能缺陷/性能问题/UI问题/兼容性问题/安全漏洞/其他）
2. 所属模块（根据描述推断）
3. 建议严重程度（critical/major/minor/trivial）
4. 建议优先级（high/medium/low）
5. 分类依据说明"""

        # 构建配置
        config = {
            'project_id': request.project_id
        }
        
        # 调用 AI Agent
        result = await client.invoke_agent(
            assistant_id="defect_analyzer_agent",
            message=prompt,
            config=config
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                data={
                    'content': result.get('content', ''),
                    'thread_id': result.get('thread_id')
                },
                msg="缺陷分类完成"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '缺陷分类失败'))
            
    except Exception as e:
        logger.error(f"AI 缺陷分类失败: {str(e)}")
        return ResponseUtil.failure(msg=f"AI 缺陷分类失败: {str(e)}")


@router.post("/find-similar", summary="查找相似缺陷", dependencies=[UserInterfaceAuthDependency('testing:defect:list')])
@Log(title='查找相似缺陷', business_type=BusinessType.OTHER)
async def find_similar_defects(
    request: AIClassifyDefectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    查找相似缺陷
    
    使用 AI 和知识库查找历史上的相似缺陷。
    """
    try:
        client = get_langgraph_client()
        
        prompt = f"""请帮我查找与以下缺陷相似的历史缺陷。

缺陷标题：{request.title}

缺陷描述：
{request.description}

请使用 rag_query_tool 从知识库中检索相似的缺陷记录，并分析：
1. 相似缺陷列表（包括标题、相似度评分）
2. 这些缺陷的共同特征
3. 历史缺陷的解决方案
4. 对当前缺陷的借鉴意义"""

        # 构建配置
        config = {
            'project_id': request.project_id,
            'use_rag': True
        }
        
        # 调用 AI Agent
        result = await client.invoke_agent(
            assistant_id="defect_analyzer_agent",
            message=prompt,
            config=config
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                data={
                    'content': result.get('content', ''),
                    'thread_id': result.get('thread_id')
                },
                msg="相似缺陷查找完成"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '查找相似缺陷失败'))
            
    except Exception as e:
        logger.error(f"查找相似缺陷失败: {str(e)}")
        return ResponseUtil.failure(msg=f"查找相似缺陷失败: {str(e)}")


@router.post("/save-analysis", summary="保存缺陷分析结果", dependencies=[UserInterfaceAuthDependency('testing:defect:add')])
@Log(title='保存缺陷分析结果', business_type=BusinessType.INSERT)
async def save_analysis_result(
    request: DefectAnalysisSaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    保存缺陷分析结果
    
    将 AI 分析的结果保存到数据库。
    """
    try:
        from module_testing.entity.vo.defect_vo import DefectAnalysisCreateVO
        from module_testing.service.defect_analysis_service import DefectAnalysisService
        
        analysis_service = DefectAnalysisService()
        
        # 创建分析结果
        vo = DefectAnalysisCreateVO(
            project_id=request.project_id,
            defect_id=request.defect_id,
            title=request.title,
            description=request.description,
            analysis_result=request.analysis_result,
            root_cause=request.root_cause,
            impact_scope=request.impact_scope,
            severity_suggestion=request.severity_suggestion,
            priority_suggestion=request.priority_suggestion,
            fix_suggestions=request.fix_suggestions,
            similar_defects=request.similar_defects
        )
        
        result = await analysis_service.create_analysis(db, vo, current_user.get('user_name', 'system'))
        
        return ResponseUtil.success(
            data={'analysis_id': result.analysis_id},
            msg="分析结果保存成功"
        )
        
    except Exception as e:
        logger.error(f"保存缺陷分析结果失败: {str(e)}")
        return ResponseUtil.failure(msg=f"保存缺陷分析结果失败: {str(e)}")


@router.get("/history", summary="获取缺陷分析历史", dependencies=[UserInterfaceAuthDependency('testing:defect:list')])
async def get_analysis_history(
    project_id: int = Query(..., description="项目ID"),
    defect_id: Optional[int] = Query(None, description="缺陷ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    获取缺陷分析历史
    
    查询指定项目或缺陷的分析历史记录。
    """
    try:
        from module_testing.service.defect_analysis_service import DefectAnalysisService
        
        analysis_service = DefectAnalysisService()
        
        result = await analysis_service.get_analysis_list(
            db,
            project_id=project_id,
            defect_id=defect_id,
            page=page,
            page_size=page_size
        )
        
        return ResponseUtil.success(data=result)
        
    except Exception as e:
        logger.error(f"获取缺陷分析历史失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取缺陷分析历史失败: {str(e)}")


@router.post("/generate-regression-cases", summary="生成回归测试用例", dependencies=[UserInterfaceAuthDependency('testing:defect:list')])
@Log(title='生成回归测试用例', business_type=BusinessType.OTHER)
async def generate_regression_cases(
    request: AIAnalyzeDefectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    基于缺陷生成回归测试用例
    
    根据缺陷信息自动生成回归测试用例。
    """
    try:
        client = get_langgraph_client()
        
        prompt = f"""请基于以下缺陷信息生成回归测试用例。

缺陷标题：{request.title}

缺陷描述：
{request.description}

{f'重现步骤：{chr(10)}{request.steps_to_reproduce}' if request.steps_to_reproduce else ''}

请生成：
1. 缺陷验证测试用例（验证缺陷已修复）
2. 相关功能回归测试用例（确保修复未引入新问题）
3. 边界条件测试用例

每个测试用例包含：
- 用例名称
- 前置条件
- 测试步骤
- 预期结果
- 优先级

生成完成后，请使用 batch_create_test_cases_tool 保存测试用例。"""

        # 构建配置
        config = {
            'project_id': request.project_id,
            'defect_id': request.defect_id
        }
        
        # 调用 AI Agent（使用测试用例生成 Agent）
        result = await client.invoke_agent(
            assistant_id="testcase_generator_agent",
            message=prompt,
            config=config
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                data={
                    'content': result.get('content', ''),
                    'thread_id': result.get('thread_id')
                },
                msg="回归测试用例生成完成"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '生成回归测试用例失败'))
            
    except Exception as e:
        logger.error(f"生成回归测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"生成回归测试用例失败: {str(e)}")

