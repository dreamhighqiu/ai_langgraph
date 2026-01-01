"""
知识库管理控制器
"""
import logging
from typing import Annotated, List, Optional

from fastapi import (
    Path,
    Query,
    Body,
    UploadFile,
    File,
    Form,
    Request,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel
from module_testing.entity.vo.knowledge_vo import (
    KnowledgeModel,
    KnowledgeCreateModel,
    KnowledgeUpdateModel,
    KnowledgeQueryModel,
    KnowledgeStatsModel,
    KnowledgeFileModel,
    KnowledgeFileQueryModel,
    KnowledgeQueryRequestModel,
    KnowledgeQueryResponseModel,
)
from module_testing.service.knowledge_service import KnowledgeService
from module_testing.service.lightrag_client import get_lightrag_manager
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.log_util import logger
from utils.response_util import ResponseUtil

knowledge_controller = APIRouterPro(
    prefix='/testing/knowledge',
    tags=['知识库管理'],
    dependencies=[PreAuthDependency()],
    auto_register=True,
)


@knowledge_controller.post(
    '/create',
    summary='创建知识库',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:add')],
)
@Log(title='知识库管理', business_type=BusinessType.INSERT, log_type='operate')
async def create_knowledge(
    request: Request,
    knowledge_create: KnowledgeCreateModel,
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """创建知识库"""
    try:
        result = await KnowledgeService.create_knowledge(
            db=db,
            knowledge_create=knowledge_create,
            create_by=current_user.user.user_name
        )
        
        return ResponseUtil.success(
            msg='知识库创建成功',
            data={'knowledge_id': result.knowledge_id}
        )
    except Exception as e:
        logger.error(f'创建知识库失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'创建知识库失败: {str(e)}')


@knowledge_controller.get(
    '/list',
    summary='查询知识库列表',
    response_model=PageResponseModel[KnowledgeModel],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def get_knowledge_list(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_id: Optional[int] = Query(None, description='项目ID'),
    knowledge_name: Optional[str] = Query(None, description='知识库名称'),
    status: Optional[str] = Query(None, description='状态'),
) -> Response:
    """查询知识库列表"""
    try:
        query = KnowledgeQueryModel(
            page_num=page_num,
            page_size=page_size,
            project_id=project_id,
            knowledge_name=knowledge_name,
            status=status
        )
        
        knowledge_list, total = await KnowledgeService.get_knowledge_list(db, query)
        
        return ResponseUtil.success(
            data={'rows': [k.model_dump() for k in knowledge_list], 'total': total}
        )
    except Exception as e:
        logger.error(f'查询知识库列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.get(
    '/project/{project_id}',
    summary='获取项目知识库',
    response_model=DataResponseModel[KnowledgeModel],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:query')],
)
async def get_knowledge_by_project(
    request: Request,
    project_id: Annotated[int, Path(description='项目ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取项目的知识库（项目与知识库一对一）
    
    如果项目没有知识库，返回空数据（不会自动创建）
    """
    try:
        from module_testing.dao.knowledge_dao import KnowledgeDao
        knowledge = await KnowledgeDao.select_knowledge_by_project_id(db, project_id)
        if not knowledge:
            return ResponseUtil.success(data=None, msg='项目暂无知识库')
        
        knowledge_model = KnowledgeModel.model_validate(knowledge)
        return ResponseUtil.success(data=knowledge_model.model_dump())
    except Exception as e:
        logger.error(f'获取项目知识库失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'获取失败: {str(e)}')


@knowledge_controller.get(
    '/{knowledge_id}',
    summary='获取知识库详情',
    response_model=DataResponseModel[KnowledgeModel],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:query')],
)
async def get_knowledge(
    request: Request,
    knowledge_id: Annotated[int, Path(description='知识库ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取知识库详情"""
    try:
        knowledge = await KnowledgeService.get_knowledge_by_id(db, knowledge_id)
        if not knowledge:
            return ResponseUtil.error(msg='知识库不存在')
        
        return ResponseUtil.success(data=knowledge.model_dump())
    except Exception as e:
        logger.error(f'获取知识库详情失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.put(
    '/update',
    summary='更新知识库',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:edit')],
)
@Log(title='知识库管理', business_type=BusinessType.UPDATE, log_type='operate')
async def update_knowledge(
    request: Request,
    knowledge_update: KnowledgeUpdateModel,
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """更新知识库"""
    try:
        success = await KnowledgeService.update_knowledge(
            db=db,
            knowledge_update=knowledge_update,
            update_by=current_user.user.user_name
        )
        
        if success:
            return ResponseUtil.success(msg='更新成功')
        else:
            return ResponseUtil.error(msg='更新失败')
    except Exception as e:
        logger.error(f'更新知识库失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'更新失败: {str(e)}')


@knowledge_controller.delete(
    '/{knowledge_id}',
    summary='删除知识库',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:remove')],
)
@Log(title='知识库管理', business_type=BusinessType.DELETE, log_type='operate')
async def delete_knowledge(
    request: Request,
    knowledge_id: Annotated[int, Path(description='知识库ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """删除知识库"""
    try:
        success = await KnowledgeService.delete_knowledge(
            db=db,
            knowledge_id=knowledge_id,
            delete_by=current_user.user.user_name
        )
        
        if success:
            return ResponseUtil.success(msg='删除成功')
        else:
            return ResponseUtil.error(msg='删除失败，知识库不存在')
    except Exception as e:
        logger.error(f'删除知识库失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'删除失败: {str(e)}')


@knowledge_controller.get(
    '/{knowledge_id}/stats',
    summary='获取知识库统计',
    response_model=DataResponseModel[KnowledgeStatsModel],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:query')],
)
async def get_knowledge_stats(
    request: Request,
    knowledge_id: Annotated[int, Path(description='知识库ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取知识库统计信息"""
    try:
        stats = await KnowledgeService.get_knowledge_stats(db, knowledge_id)
        return ResponseUtil.success(data=stats.model_dump())
    except Exception as e:
        logger.error(f'获取统计信息失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


# ==================== 文件管理 ====================


@knowledge_controller.post(
    '/project/{project_id}/files/upload',
    summary='上传文件到项目知识库',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:upload')],
)
@Log(title='知识库管理', business_type=BusinessType.INSERT, log_type='operate')
async def upload_file_by_project(
    request: Request,
    project_id: Annotated[int, Path(description='项目ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    file: UploadFile = File(..., description='上传文件'),
    remark: Optional[str] = Form(None, description='备注'),
) -> Response:
    """
    通过项目ID上传文件到知识库
    
    项目与知识库一对一，如果项目没有知识库会自动创建。
    文件会自动上传到项目对应的 workspace（project_{project_id}），确保数据隔离。
    """
    try:
        result = await KnowledgeService.upload_knowledge_file_by_project(
            db=db,
            project_id=project_id,
            file=file,
            create_by=current_user.user.user_name,
            remark=remark
        )
        
        return ResponseUtil.success(msg='文件上传成功', data=result)
    except ValueError as e:
        return ResponseUtil.error(msg=str(e))
    except Exception as e:
        logger.error(f'上传文件失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'上传失败: {str(e)}')


@knowledge_controller.post(
    '/{knowledge_id}/files/upload',
    summary='上传文件',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:upload')],
)
@Log(title='知识库管理', business_type=BusinessType.INSERT, log_type='operate')
async def upload_file(
    request: Request,
    knowledge_id: Annotated[int, Path(description='知识库ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    file: UploadFile = File(..., description='上传文件'),
    remark: Optional[str] = Form(None, description='备注'),
) -> Response:
    """上传文件到知识库"""
    try:
        result = await KnowledgeService.upload_knowledge_file(
            db=db,
            knowledge_id=knowledge_id,
            file=file,
            create_by=current_user.user.user_name,
            remark=remark
        )
        
        return ResponseUtil.success(msg='文件上传成功', data=result)
    except ValueError as e:
        return ResponseUtil.error(msg=str(e))
    except Exception as e:
        logger.error(f'上传文件失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'上传失败: {str(e)}')


@knowledge_controller.get(
    '/project/{project_id}/files',
    summary='查询项目知识库文件列表',
    response_model=PageResponseModel[KnowledgeFileModel],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def get_file_list_by_project(
    request: Request,
    project_id: Annotated[int, Path(description='项目ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    file_name: Optional[str] = Query(None, description='文件名称'),
    process_status: Optional[str] = Query(None, description='处理状态'),
) -> Response:
    """
    查询项目知识库文件列表（项目与知识库一对一）
    
    如果项目没有知识库，返回空列表
    """
    try:
        from module_testing.dao.knowledge_dao import KnowledgeDao
        knowledge = await KnowledgeDao.select_knowledge_by_project_id(db, project_id)
        if not knowledge:
            return ResponseUtil.success(data={'rows': [], 'total': 0}, msg='项目暂无知识库')
        
        query = KnowledgeFileQueryModel(
            page_num=page_num,
            page_size=page_size,
            knowledge_id=knowledge.knowledge_id,
            file_name=file_name,
            process_status=process_status
        )
        
        file_list, total = await KnowledgeService.get_file_list(db, query)
        
        return ResponseUtil.success(
            data={'rows': [f.model_dump() for f in file_list], 'total': total}
        )
    except Exception as e:
        logger.error(f'查询项目文件列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.get(
    '/{knowledge_id}/files',
    summary='查询文件列表',
    response_model=PageResponseModel[KnowledgeFileModel],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def get_file_list(
    request: Request,
    knowledge_id: Annotated[int, Path(description='知识库ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    file_name: Optional[str] = Query(None, description='文件名称'),
    process_status: Optional[str] = Query(None, description='处理状态'),
) -> Response:
    """查询文件列表"""
    try:
        query = KnowledgeFileQueryModel(
            page_num=page_num,
            page_size=page_size,
            knowledge_id=knowledge_id,
            file_name=file_name,
            process_status=process_status
        )
        
        file_list, total = await KnowledgeService.get_file_list(db, query)
        
        return ResponseUtil.success(
            data={'rows': [f.model_dump() for f in file_list], 'total': total}
        )
    except Exception as e:
        logger.error(f'查询文件列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.delete(
    '/files/{file_id}',
    summary='删除文件',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:remove')],
)
@Log(title='知识库管理', business_type=BusinessType.DELETE, log_type='operate')
async def delete_file(
    request: Request,
    file_id: Annotated[int, Path(description='文件ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """删除文件"""
    try:
        success = await KnowledgeService.delete_file(
            db=db,
            file_id=file_id,
            delete_by=current_user.user.user_name
        )
        
        if success:
            return ResponseUtil.success(msg='删除成功')
        else:
            return ResponseUtil.error(msg='删除失败，文件不存在')
    except Exception as e:
        logger.error(f'删除文件失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'删除失败: {str(e)}')


# ==================== 知识库查询（RAG） ====================


@knowledge_controller.post(
    '/project/{project_id}/query',
    summary='项目知识库查询（RAG）',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:query')],
)
@Log(title='知识库管理', business_type=BusinessType.OTHER, log_type='operate')
async def query_knowledge_by_project(
    request: Request,
    project_id: Annotated[int, Path(description='项目ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    query_request: KnowledgeQueryRequestModel,
) -> Response:
    """
    通过项目ID查询知识库（RAG问答）
    
    项目与知识库一对一，直接使用项目ID查询，自动使用对应的 workspace 进行数据隔离。
    确保查询结果只来自指定项目的文档。
    
    数据隔离机制：
    1. 通过项目的 workspace（project_{project_id}）进行查询
    2. workspace 格式：project_{project_id}
    3. anything-chat-rag 通过 LIGHTRAG-WORKSPACE header 实现数据隔离
    """
    try:
        # 使用 service 层的查询方法，确保数据隔离
        result = await KnowledgeService.query_knowledge_by_project(
            db=db,
            project_id=project_id,
            query=query_request.query,
            mode=query_request.mode,
            top_k=query_request.top_k
        )
        
        return ResponseUtil.success(data=result)
    except ValueError as e:
        return ResponseUtil.error(msg=str(e))
    except Exception as e:
        logger.error(f'项目知识库查询失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.post(
    '/{knowledge_id}/query',
    summary='知识库查询（RAG）',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:query')],
)
@Log(title='知识库管理', business_type=BusinessType.OTHER, log_type='operate')
async def query_knowledge(
    request: Request,
    knowledge_id: Annotated[int, Path(description='知识库ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    query_request: KnowledgeQueryRequestModel,
) -> Response:
    """
    知识库查询（RAG问答）
    
    通过知识库ID查询，自动使用对应的 workspace 进行数据隔离。
    确保查询结果只来自指定知识库的文档。
    
    数据隔离机制：
    1. 通过知识库的 collection_name（workspace）进行查询
    2. workspace 格式：project_{project_id}
    3. 如果提供了 project_id，会验证知识库是否属于指定项目
    4. anything-chat-rag 通过 LIGHTRAG-WORKSPACE header 实现数据隔离
    """
    try:
        # 使用 service 层的查询方法，确保数据隔离
        result = await KnowledgeService.query_knowledge(
            db=db,
            knowledge_id=knowledge_id,
            query=query_request.query,
            mode=query_request.mode,
            top_k=query_request.top_k,
            project_id=query_request.project_id  # 传递 project_id 进行隔离验证
        )
        
        return ResponseUtil.success(data=result)
    except ValueError as e:
        return ResponseUtil.error(msg=str(e))
    except Exception as e:
        logger.error(f'知识库查询失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


