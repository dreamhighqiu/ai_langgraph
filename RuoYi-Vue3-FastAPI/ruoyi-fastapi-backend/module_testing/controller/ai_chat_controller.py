"""
AI对话控制器 - 支持三种独立功能的抽屉式对话
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from module_testing.service.ai_service import AIGenerationService
from module_testing.service.knowledge_service import KnowledgeService
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/ai-chat", tags=["AI对话"])
ai_service = AIGenerationService()
knowledge_service = KnowledgeService()


# ================ 请求模型 ================

class TestCaseChatRequest(BaseModel):
    """测试用例对话请求"""
    project_name: Optional[str] = None
    module_name: Optional[str] = None
    feature_description: str
    test_type: str = "functional"
    priority: str = "medium"
    thread_id: Optional[str] = None
    use_rag: bool = False
    knowledge_id: Optional[int] = None


class RequirementChatRequest(BaseModel):
    """需求分析对话请求"""
    requirement_summary: str
    requirement_description: str
    module: Optional[str] = None
    requirement_type: str = "functional"
    thread_id: Optional[str] = None
    use_rag: bool = False
    knowledge_id: Optional[int] = None


class DefectChatRequest(BaseModel):
    """缺陷分析对话请求"""
    defect_title: str
    defect_description: str
    severity: str = "medium"
    priority: str = "medium"
    thread_id: Optional[str] = None
    use_rag: bool = False
    knowledge_id: Optional[int] = None


# ================ 端点 ================

@router.post("/test-case/stream", summary="测试用例生成 - 流式对话")
async def test_case_chat_stream(
    request: TestCaseChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """测试用例生成 - 流式对话"""
    try:
        # 如果启用RAG,获取上下文
        rag_context = None
        if request.use_rag and request.knowledge_id:
            rag_result = await knowledge_service.query_knowledge(
                db, request.knowledge_id, request.feature_description
            )
            if rag_result:
                rag_context = rag_result.get('context')

        # 流式生成
        async def generate():
            async for chunk in ai_service.generate_test_case_stream(
                project_name=request.project_name,
                module_name=request.module_name,
                feature_description=request.feature_description,
                test_type=request.test_type,
                priority=request.priority,
                thread_id=request.thread_id,
                rag_context=rag_context
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        logger.error(f"测试用例对话失败: {str(e)}")
        return ResponseUtil.failure(msg=f"对话失败: {str(e)}")


@router.post("/requirement/stream", summary="需求分析生成 - 流式对话")
async def requirement_chat_stream(
    request: RequirementChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """需求分析生成 - 流式对话"""
    try:
        # 如果启用RAG,获取上下文
        rag_context = None
        if request.use_rag and request.knowledge_id:
            rag_result = await knowledge_service.query_knowledge(
                db, request.knowledge_id, request.requirement_description
            )
            if rag_result:
                rag_context = rag_result.get('context')

        # 流式生成
        async def generate():
            async for chunk in ai_service.generate_requirement_stream(
                requirement_summary=request.requirement_summary,
                requirement_description=request.requirement_description,
                module=request.module,
                requirement_type=request.requirement_type,
                thread_id=request.thread_id,
                rag_context=rag_context
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        logger.error(f"需求分析对话失败: {str(e)}")
        return ResponseUtil.failure(msg=f"对话失败: {str(e)}")


@router.post("/defect/stream", summary="缺陷分析生成 - 流式对话")
async def defect_chat_stream(
    request: DefectChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """缺陷分析生成 - 流式对话"""
    try:
        # 如果启用RAG,获取上下文
        rag_context = None
        if request.use_rag and request.knowledge_id:
            rag_result = await knowledge_service.query_knowledge(
                db, request.knowledge_id, request.defect_description
            )
            if rag_result:
                rag_context = rag_result.get('context')

        # 流式生成
        async def generate():
            async for chunk in ai_service.generate_defect_stream(
                defect_title=request.defect_title,
                defect_description=request.defect_description,
                severity=request.severity,
                priority=request.priority,
                thread_id=request.thread_id,
                rag_context=rag_context
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        logger.error(f"缺陷分析对话失败: {str(e)}")
        return ResponseUtil.failure(msg=f"对话失败: {str(e)}")


@router.delete("/clear-history/{thread_id}", summary="清除对话历史")
async def clear_chat_history(
    thread_id: str,
    current_user: dict = Depends(LoginService.get_current_user)
):
    """清除对话历史"""
    try:
        ai_service.clear_session_history(thread_id)
        return ResponseUtil.success(msg="清除对话历史成功")
    except Exception as e:
        logger.error(f"清除对话历史失败: {str(e)}")
        return ResponseUtil.failure(msg=f"清除对话历史失败: {str(e)}")
