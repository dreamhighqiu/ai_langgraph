"""
AI 需求分析控制器
提供 AI 智能分析需求的 API 接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_testing.agents.langgraph_client import get_langgraph_client
from module_testing.service.requirement_service import RequirementService
from common.annotation.log_annotation import Log
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.enums import BusinessType
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/ai-requirement", tags=["AI 需求分析"])


class AIAnalyzeRequirementRequest(BaseModel):
    """AI 分析需求请求"""
    project_id: int = Field(..., description="项目ID")
    requirement_id: Optional[int] = Field(None, description="需求ID（如果分析现有需求）")
    title: str = Field(..., description="需求标题")
    content: str = Field(..., description="需求内容")
    analysis_type: str = Field("full", description="分析类型: full(完整分析), completeness(完整性), testability(可测试性), risk(风险分析)")
    use_rag: bool = Field(False, description="是否使用 RAG 知识库增强")


class AIGenerateTestPointsRequest(BaseModel):
    """AI 生成测试点请求"""
    project_id: int = Field(..., description="项目ID")
    requirement_id: Optional[int] = Field(None, description="需求ID")
    requirement_content: str = Field(..., description="需求内容")


class RequirementAnalysisSaveRequest(BaseModel):
    """保存需求分析结果请求"""
    project_id: int = Field(..., description="项目ID")
    requirement_id: Optional[int] = Field(None, description="关联需求ID")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="需求内容")
    analysis_result: str = Field(..., description="分析结果")
    completeness_score: Optional[float] = Field(None, ge=0, le=100, description="完整性评分")
    testability_score: Optional[float] = Field(None, ge=0, le=100, description="可测试性评分")
    risk_level: Optional[str] = Field(None, description="风险等级: high/medium/low")
    suggestions: Optional[List[str]] = Field(None, description="优化建议")
    test_points: Optional[List[str]] = Field(None, description="测试点")


@router.post("/analyze", summary="AI 分析需求", dependencies=[UserInterfaceAuthDependency('testing:requirement:list')])
@Log(title='AI分析需求', business_type=BusinessType.OTHER)
async def ai_analyze_requirement(
    request: AIAnalyzeRequirementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    AI 分析需求
    
    使用 AI 分析需求的完整性、可测试性、风险等维度。
    """
    try:
        client = get_langgraph_client()
        
        # 根据分析类型构建提示词
        analysis_prompts = {
            "full": "请进行全面分析，包括完整性、可测试性和风险分析",
            "completeness": "请重点分析需求的完整性，包括功能覆盖、边界条件、异常处理等",
            "testability": "请重点分析需求的可测试性，包括验收标准、测试点提取等",
            "risk": "请重点分析需求的潜在风险，包括技术风险、业务风险、依赖风险等"
        }
        
        analysis_instruction = analysis_prompts.get(request.analysis_type, analysis_prompts["full"])
        
        prompt = f"""请分析以下需求。

需求标题：{request.title}

需求内容：
{request.content}

分析要求：
{analysis_instruction}

请提供：
1. 完整性评分（0-100）
2. 可测试性评分（0-100）
3. 风险等级（high/medium/low）
4. 详细分析说明
5. 优化建议列表
6. 提取的测试点列表

{"请先使用 rag_query_tool 从知识库检索相关的需求分析案例，然后基于检索结果进行分析。" if request.use_rag else ""}

分析完成后，请使用 save_requirement_analysis_tool 保存分析结果。"""

        # 构建配置
        config = {
            'project_id': request.project_id,
            'requirement_id': request.requirement_id,
            'analysis_type': request.analysis_type
        }
        
        # 调用 AI Agent
        result = await client.invoke_agent(
            assistant_id="requirement_analyzer_agent",
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
                msg="需求分析完成"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '需求分析失败'))
            
    except Exception as e:
        logger.error(f"AI 分析需求失败: {str(e)}")
        return ResponseUtil.failure(msg=f"AI 分析需求失败: {str(e)}")


@router.post("/generate-test-points", summary="AI 生成测试点", dependencies=[UserInterfaceAuthDependency('testing:requirement:list')])
@Log(title='AI生成测试点', business_type=BusinessType.OTHER)
async def generate_test_points(
    request: AIGenerateTestPointsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    AI 生成测试点
    
    从需求内容中提取和生成测试点。
    """
    try:
        client = get_langgraph_client()
        
        prompt = f"""请从以下需求中提取测试点。

需求内容：
{request.requirement_content}

请识别并列出所有可测试的功能点，包括：
1. 正常功能测试点
2. 边界条件测试点
3. 异常场景测试点
4. 性能测试点（如有必要）
5. 安全测试点（如有必要）

对每个测试点，请说明：
- 测试点描述
- 测试优先级
- 预期的测试方法"""

        # 构建配置
        config = {
            'project_id': request.project_id,
            'requirement_id': request.requirement_id
        }
        
        # 调用 AI Agent
        result = await client.invoke_agent(
            assistant_id="requirement_analyzer_agent",
            message=prompt,
            config=config
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                data={
                    'content': result.get('content', ''),
                    'thread_id': result.get('thread_id')
                },
                msg="测试点生成完成"
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '测试点生成失败'))
            
    except Exception as e:
        logger.error(f"AI 生成测试点失败: {str(e)}")
        return ResponseUtil.failure(msg=f"AI 生成测试点失败: {str(e)}")


@router.post("/save-analysis", summary="保存需求分析结果", dependencies=[UserInterfaceAuthDependency('testing:requirement:add')])
@Log(title='保存需求分析结果', business_type=BusinessType.INSERT)
async def save_analysis_result(
    request: RequirementAnalysisSaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    保存需求分析结果
    
    将 AI 分析的结果保存到数据库。
    """
    try:
        from module_testing.entity.vo.requirement_vo import RequirementAnalysisCreateVO
        from module_testing.service.requirement_analysis_service import RequirementAnalysisService
        
        analysis_service = RequirementAnalysisService()
        
        # 创建分析结果
        vo = RequirementAnalysisCreateVO(
            project_id=request.project_id,
            requirement_id=request.requirement_id,
            title=request.title,
            content=request.content,
            analysis_result=request.analysis_result,
            completeness_score=request.completeness_score,
            testability_score=request.testability_score,
            risk_level=request.risk_level,
            suggestions=request.suggestions,
            test_points=request.test_points
        )
        
        result = await analysis_service.create_analysis(db, vo, current_user.get('user_name', 'system'))
        
        return ResponseUtil.success(
            data={'analysis_id': result.analysis_id},
            msg="分析结果保存成功"
        )
        
    except Exception as e:
        logger.error(f"保存需求分析结果失败: {str(e)}")
        return ResponseUtil.failure(msg=f"保存需求分析结果失败: {str(e)}")


@router.get("/history", summary="获取需求分析历史", dependencies=[UserInterfaceAuthDependency('testing:requirement:list')])
async def get_analysis_history(
    project_id: int = Query(..., description="项目ID"),
    requirement_id: Optional[int] = Query(None, description="需求ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """
    获取需求分析历史
    
    查询指定项目或需求的分析历史记录。
    """
    try:
        from module_testing.service.requirement_analysis_service import RequirementAnalysisService
        
        analysis_service = RequirementAnalysisService()
        
        result = await analysis_service.get_analysis_list(
            db,
            project_id=project_id,
            requirement_id=requirement_id,
            page=page,
            page_size=page_size
        )
        
        return ResponseUtil.success(data=result)
        
    except Exception as e:
        logger.error(f"获取需求分析历史失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取需求分析历史失败: {str(e)}")

