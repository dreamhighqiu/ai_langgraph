"""
知识库管理控制器
"""
import asyncio
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
from sqlalchemy import and_
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
    '/{knowledge_ids}',
    summary='删除知识库（支持批量删除）',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:remove')],
)
@Log(title='知识库管理', business_type=BusinessType.DELETE, log_type='operate')
async def delete_knowledge(
    request: Request,
    knowledge_ids: Annotated[str, Path(description='知识库ID列表，逗号分隔，如：1,2,3')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """删除知识库（支持单个或批量删除）"""
    try:
        # 解析ID列表（支持单个ID或逗号分隔的多个ID）
        id_list = [int(id_str.strip()) for id_str in knowledge_ids.split(',') if id_str.strip()]
        
        if not id_list:
            return ResponseUtil.error(msg='知识库ID不能为空')
        
        # 批量删除
        success_count = await KnowledgeService.delete_knowledges(
            db=db,
            knowledge_ids=id_list,
            delete_by=current_user.user.user_name
        )
        
        if success_count > 0:
            if len(id_list) == 1:
                return ResponseUtil.success(msg='删除成功')
            else:
                return ResponseUtil.success(msg=f'删除成功，共删除 {success_count}/{len(id_list)} 个知识库')
        else:
            return ResponseUtil.error(msg='删除失败，知识库不存在')
    except ValueError as e:
        return ResponseUtil.error(msg=f'知识库ID格式错误: {str(e)}')
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
        # 获取base_url用于生成文件URL
        base_url = str(request.base_url).rstrip('/')
        # 移除API前缀（如果有）
        if '/dev-api' in base_url or '/prod-api' in base_url:
            base_url = base_url.rsplit('/', 1)[0]
        
        result = await KnowledgeService.upload_knowledge_file_by_project(
            db=db,
            project_id=project_id,
            file=file,
            create_by=current_user.user.user_name,
            remark=remark,
            base_url=base_url  # 传递base_url
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
    '/files/all',
    summary='查询所有项目的文件列表',
    response_model=PageResponseModel[KnowledgeFileModel],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def get_all_files(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_id: Optional[int] = Query(None, description='项目ID（可选，用于过滤）'),
    file_name: Optional[str] = Query(None, description='文件名称'),
    process_status: Optional[str] = Query(None, description='处理状态'),
) -> Response:
    """
    查询所有项目的文件列表（不按项目过滤，或按项目ID过滤）
    
    如果提供了project_id，则只查询该项目的文件；否则查询所有项目的文件
    """
    try:
        query = KnowledgeFileQueryModel(
            page_num=page_num,
            page_size=page_size,
            knowledge_id=None,  # 不按knowledge_id过滤，查询所有
            file_name=file_name,
            process_status=process_status
        )
        
        # 如果提供了project_id，需要先获取该项目的知识库ID
        if project_id:
            from module_testing.dao.knowledge_dao import KnowledgeDao
            knowledge = await KnowledgeDao.select_knowledge_by_project_id(db, project_id)
            if knowledge:
                query.knowledge_id = knowledge.knowledge_id
            else:
                # 项目没有知识库，返回空列表
                return ResponseUtil.success(data={'rows': [], 'total': 0}, msg='项目暂无知识库')
        
        # 获取base_url用于生成文件URL
        base_url = str(request.base_url).rstrip('/')
        # 移除API前缀（如果有）
        if '/dev-api' in base_url or '/prod-api' in base_url:
            base_url = base_url.rsplit('/', 1)[0]
        
        file_list, total = await KnowledgeService.get_file_list(db, query, base_url=base_url)
        
        # 为每个文件添加项目信息
        from module_testing.dao.knowledge_dao import KnowledgeDao
        from module_testing.dao.project_dao import ProjectDAO
        result_rows = []
        for f in file_list:
            file_dict = f.model_dump()
            # 获取文件所属的知识库和项目信息
            knowledge = await KnowledgeDao.select_knowledge_by_id(db, f.knowledge_id)
            if knowledge:
                file_dict['project_id'] = knowledge.project_id
                # 查询项目名称
                project = await ProjectDAO.get_by_id(db, knowledge.project_id)
                file_dict['project_name'] = project.project_name if project else None
                file_dict['knowledge_name'] = knowledge.knowledge_name
            result_rows.append(file_dict)
        
        return ResponseUtil.success(
            data={'rows': result_rows, 'total': total}
        )
    except Exception as e:
        logger.error(f'查询所有文件列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


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
        
        # 获取base_url用于生成文件URL
        base_url = str(request.base_url).rstrip('/')
        # 移除API前缀（如果有）
        if '/dev-api' in base_url or '/prod-api' in base_url:
            base_url = base_url.rsplit('/', 1)[0]
        
        file_list, total = await KnowledgeService.get_file_list(db, query, base_url=base_url)
        
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
        
        # 获取base_url用于生成文件URL
        base_url = str(request.base_url).rstrip('/')
        # 移除API前缀（如果有）
        if '/dev-api' in base_url or '/prod-api' in base_url:
            base_url = base_url.rsplit('/', 1)[0]
        
        file_list, total = await KnowledgeService.get_file_list(db, query, base_url=base_url)
        
        return ResponseUtil.success(
            data={'rows': [f.model_dump() for f in file_list], 'total': total}
        )
    except Exception as e:
        logger.error(f'查询文件列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.get(
    '/files/{file_id}/download',
    summary='下载/预览文件（支持MinIO预签名URL和本地文件直接下载）',
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def download_file(
    request: Request,
    file_id: Annotated[int, Path(description='文件ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    preview: bool = Query(False, description='是否预览（true=预览，false=下载）'),
):
    """
    下载或预览文件
    
    如果是MinIO存储：
      - 生成预签名URL并重定向（支持预览和下载）
    如果是本地存储：
      - 直接返回文件内容（根据preview参数设置Content-Disposition）
    """
    try:
        from module_testing.storage.minio_client import MinioClientManager
        from fastapi.responses import StreamingResponse, RedirectResponse
        import io
        import mimetypes
        
        # 获取文件信息
        from module_testing.dao.knowledge_dao import KnowledgeFileDao
        file_record = await KnowledgeFileDao.select_file_by_id(db, file_id)
        if not file_record:
            return ResponseUtil.error(msg='文件不存在')
        
        minio_client = MinioClientManager.get_client()
        
        # 统一使用直接下载文件内容的方式，避免预签名URL的签名问题
        # 这样可以更好地控制MIME类型和响应头
        success, file_content = minio_client.download_file(file_record.file_path)
        if not success or file_content is None:
            return ResponseUtil.error(msg='文件不存在或无法读取')
        
        # 检测MIME类型
        mime_type, _ = mimetypes.guess_type(file_record.file_name)
        if not mime_type:
            # 根据文件扩展名设置默认MIME类型
            file_ext = file_record.file_name.lower().split('.')[-1] if '.' in file_record.file_name else ''
            mime_map = {
                'pdf': 'application/pdf',
                'txt': 'text/plain',
                'md': 'text/markdown',
                'html': 'text/html',
                'htm': 'text/html',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xls': 'application/vnd.ms-excel',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'ppt': 'application/vnd.ms-powerpoint',
                'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'json': 'application/json',
                'xml': 'application/xml',
            }
            mime_type = mime_map.get(file_ext, 'application/octet-stream')
        
        # 设置响应头
        # 处理文件名编码，支持中文文件名（RFC 5987）
        from urllib.parse import quote
        
        # 对文件名进行URL编码，用于RFC 5987格式
        filename_encoded = quote(file_record.file_name, safe='')
        
        # 检查文件名是否包含非ASCII字符
        try:
            # 尝试编码为ASCII，如果失败则说明包含非ASCII字符
            file_record.file_name.encode('ascii')
            # 如果成功，文件名是ASCII安全的，可以直接使用
            ascii_safe = True
        except UnicodeEncodeError:
            # 包含非ASCII字符，需要使用RFC 5987格式
            ascii_safe = False
        
        headers = {
            'Content-Type': mime_type,
            'Cache-Control': 'no-cache',
        }
        
        # 构建Content-Disposition头
        if ascii_safe:
            # ASCII文件名，使用简单格式
        if preview:
                content_disposition = f'inline; filename="{file_record.file_name}"'
        else:
                content_disposition = f'attachment; filename="{file_record.file_name}"'
        else:
            # 非ASCII文件名，使用RFC 5987格式
            if preview:
                content_disposition = f'inline; filename*=UTF-8\'\'{filename_encoded}'
            else:
                content_disposition = f'attachment; filename*=UTF-8\'\'{filename_encoded}'
        
        # 将Content-Disposition编码为latin-1（HTTP头要求）
        # 但RFC 5987格式已经是ASCII安全的，所以可以直接使用
        headers['Content-Disposition'] = content_disposition
        
        # 返回文件内容
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=mime_type,
            headers=headers
        )
    except Exception as e:
        logger.error(f'下载文件失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'下载失败: {str(e)}')


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


@knowledge_controller.get(
    '/project/{project_id}/rag-documents',
    summary='获取项目RAG处理后的文档列表',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:files')],
)
async def get_project_rag_documents(
    request: Request,
    project_id: Annotated[int, Path(description='项目ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    status_filter: Optional[str] = Query(None, description='状态过滤：PENDING/PROCESSING/PREPROCESSED/PROCESSED/FAILED'),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(50, ge=10, le=200, description='每页数量'),
    sort_field: str = Query('updated_at', description='排序字段'),
    sort_direction: str = Query('desc', description='排序方向'),
) -> Response:
    """获取项目RAG处理后的文档列表"""
    try:
        from module_testing.dao.knowledge_dao import KnowledgeDao
        # 获取项目对应的知识库
        knowledge = await KnowledgeDao.select_knowledge_by_project_id(db, project_id)
        if not knowledge:
            return ResponseUtil.error(msg=f'项目 {project_id} 尚未创建知识库')
        
        # 获取RAG处理后的文档列表
        lightrag_manager = get_lightrag_manager()
        result = await lightrag_manager.get_documents_paginated(
            collection_name=knowledge.collection_name,
            status_filter=status_filter,
            page=page,
            page_size=page_size,
            sort_field=sort_field,
            sort_direction=sort_direction
        )
        
        return ResponseUtil.success(data=result)
    except Exception as e:
        logger.error(f'获取RAG文档列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.get(
    '/rag-documents/all',
    summary='获取所有项目的RAG处理后的文档列表',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:files')],
)
async def get_all_rag_documents(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    project_id: Optional[int] = Query(None, description='项目ID（可选，用于过滤）'),
    status_filter: Optional[str] = Query(None, description='状态过滤：PENDING/PROCESSING/PREPROCESSED/PROCESSED/FAILED'),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(50, ge=10, le=200, description='每页数量'),
    sort_field: str = Query('updated_at', description='排序字段'),
    sort_direction: str = Query('desc', description='排序方向'),
) -> Response:
    """
    获取所有项目的RAG处理后的文档列表
    
    如果提供了project_id，则只查询该项目的文档；否则查询所有项目的文档
    注意：由于LightRAG按workspace隔离，需要遍历所有知识库的workspace
    """
    try:
        from module_testing.dao.knowledge_dao import KnowledgeDao
        from module_testing.entity.vo.knowledge_vo import KnowledgeQueryModel
        
        # 获取所有知识库（或指定项目的知识库）
        if project_id:
            knowledge_list = [await KnowledgeDao.select_knowledge_by_project_id(db, project_id)]
            knowledge_list = [k for k in knowledge_list if k]  # 过滤None
        else:
            # 获取所有知识库，使用分批查询（page_size最大为100）
            knowledge_list = []
            page_num = 1
            page_size = 100
            while True:
                query = KnowledgeQueryModel(page_num=page_num, page_size=page_size)
                batch_list, total = await KnowledgeDao.select_knowledge_list(db, query)
                knowledge_list.extend(batch_list)
                if len(batch_list) < page_size or len(knowledge_list) >= total:
                    break
                page_num += 1
        
        if not knowledge_list:
            return ResponseUtil.success(data={
                'documents': [],
                'total': 0,
                'pagination': {'page': page, 'page_size': page_size, 'total_count': 0}
            })
        
        # 获取所有workspace的文档
        lightrag_manager = get_lightrag_manager()
        all_documents = []
        total_count = 0
        
        for knowledge in knowledge_list:
            try:
                # 分批获取每个知识库的所有文档（page_size最大为200）
                knowledge_docs = []
                rag_page = 1
                rag_page_size = 200  # LightRAG API限制：10-200
                
                while True:
                    try:
                        result = await lightrag_manager.get_documents_paginated(
                            collection_name=knowledge.collection_name,
                            status_filter=status_filter,
                            page=rag_page,
                            page_size=rag_page_size,
                            sort_field=sort_field,
                            sort_direction=sort_direction
                        )
                    except Exception as rag_error:
                        # 如果是502或其他服务错误，记录警告但继续处理其他知识库
                        error_msg = str(rag_error)
                        if '502' in error_msg or 'Bad Gateway' in error_msg or 'Connection' in error_msg:
                            logger.warning(f'LightRAG服务不可用，跳过知识库 {knowledge.knowledge_id} ({knowledge.knowledge_name}): {error_msg}')
                        else:
                            logger.warning(f'获取知识库 {knowledge.knowledge_id} 的RAG文档失败: {error_msg}')
                        break  # 跳出当前知识库的循环，继续处理下一个
                    
                    batch_docs = result.get('documents', [])
                    if not batch_docs:
                        break
                    
                    # 为每个文档添加项目信息和文件预览URL
                    for doc in batch_docs:
                        # doc可能是[doc_id, DocProcessingStatus]元组或对象
                        if isinstance(doc, (list, tuple)) and len(doc) == 2:
                            doc_id, doc_status = doc
                            if hasattr(doc_status, 'model_dump'):
                                doc_dict = {'id': doc_id, **doc_status.model_dump()}
                            elif isinstance(doc_status, dict):
                                doc_dict = {'id': doc_id, **doc_status}
                            else:
                                doc_dict = {'id': doc_id, 'status': str(doc_status)}
                        elif isinstance(doc, dict):
                            doc_dict = doc.copy()
                        else:
                            doc_dict = {'id': getattr(doc, 'id', None) if hasattr(doc, 'id') else None}
                        
                        doc_dict['project_id'] = knowledge.project_id
                        doc_dict['knowledge_id'] = knowledge.knowledge_id
                        doc_dict['knowledge_name'] = knowledge.knowledge_name
                        
                        # 尝试通过doc_id查找原始文件，添加预览URL
                        doc_id = doc_dict.get('id')
                        file_path = doc_dict.get('file_path')
                        knowledge_id = doc_dict.get('knowledge_id')
                        
                        file_record = None
                        if doc_id:
                            try:
                                from sqlalchemy import select
                                from module_testing.entity.do.knowledge_do import TestKnowledgeFile
                                # 方法1：通过doc_id查找
                                file_result = await db.execute(
                                    select(TestKnowledgeFile).where(TestKnowledgeFile.doc_id == doc_id)
                                )
                                file_record = file_result.scalar_one_or_none()
                                
                                # 方法2：如果通过doc_id找不到，尝试通过file_path和knowledge_id查找
                                if not file_record and file_path and knowledge_id:
                                    from sqlalchemy import and_
                                    file_result = await db.execute(
                                        select(TestKnowledgeFile).where(
                                            and_(
                                                TestKnowledgeFile.file_name == file_path,
                                                TestKnowledgeFile.knowledge_id == knowledge_id
                                            )
                                        )
                                    )
                                    file_record = file_result.scalar_one_or_none()
                                
                                if file_record:
                                    base_url = str(request.base_url).rstrip('/')
                                    if '/dev-api' in base_url or '/prod-api' in base_url:
                                        base_url = base_url.rsplit('/', 1)[0]
                                    doc_dict['file_id'] = file_record.file_id
                                    doc_dict['file_name'] = file_record.file_name
                                    doc_dict['file_url'] = f"{base_url}/testing/knowledge/files/{file_record.file_id}/download?preview=true"
                                    # 从文件名提取文件类型（TestKnowledgeFile模型没有file_type字段）
                                    doc_dict['file_type'] = KnowledgeService._get_file_type(file_record.file_name)
                                    logger.debug(f'成功为doc_id {doc_id} 找到文件记录: file_id={file_record.file_id}, file_name={file_record.file_name}')
                                else:
                                    logger.debug(f'未找到doc_id {doc_id} 的文件记录 (file_path={file_path}, knowledge_id={knowledge_id})')
                            except Exception as e:
                                logger.warning(f'查找doc_id {doc_id} 的文件记录时出错: {e}')
                        
                        knowledge_docs.append(doc_dict)
                    
                    # 检查是否还有更多数据
                    pagination = result.get('pagination', {})
                    total_docs = pagination.get('total_count', result.get('total', 0))
                    if len(knowledge_docs) >= total_docs or len(batch_docs) < rag_page_size:
                        break
                    rag_page += 1
                
                all_documents.extend(knowledge_docs)
                total_count += len(knowledge_docs)
            except Exception as e:
                logger.warning(f'获取知识库 {knowledge.knowledge_id} 的RAG文档失败: {e}')
                continue
        
        # 按更新时间排序
        if sort_field == 'updated_at':
            all_documents.sort(
                key=lambda x: x.get('updated_at', ''),
                reverse=(sort_direction == 'desc')
            )
        
        # 分页处理
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_documents = all_documents[start_idx:end_idx]
        
        return ResponseUtil.success(data={
            'documents': paginated_documents,
            'total': total_count,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })
    except Exception as e:
        logger.error(f'获取所有RAG文档列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.get(
    '/rag-documents/{doc_id}/file',
    summary='根据RAG文档ID获取原始文件信息并支持预览',
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def get_rag_document_file(
    request: Request,
    doc_id: Annotated[str, Path(description='RAG文档ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    preview: bool = Query(False, description='是否预览（true=预览，false=下载）'),
) -> Response:
    """
    根据RAG文档ID获取原始文件信息并支持预览
    
    通过doc_id在数据库中查找对应的文件记录，然后返回文件下载/预览URL
    """
    try:
        from module_testing.dao.knowledge_dao import KnowledgeFileDao
        from module_testing.storage.minio_client import MinioClientManager
        from fastapi.responses import RedirectResponse
        
        # 通过doc_id查找文件记录
        # 注意：doc_id可能存储在不同的字段中，需要查询数据库
        from sqlalchemy import select
        from module_testing.entity.do.knowledge_do import TestKnowledgeFile
        
        result = await db.execute(
            select(TestKnowledgeFile).where(TestKnowledgeFile.doc_id == doc_id)
        )
        file_record = result.scalar_one_or_none()
        
        if not file_record:
            return ResponseUtil.error(msg=f'未找到doc_id为 {doc_id} 的文件记录')
        
        # 生成文件下载/预览URL
        base_url = str(request.base_url).rstrip('/')
        if '/dev-api' in base_url or '/prod-api' in base_url:
            base_url = base_url.rsplit('/', 1)[0]
        
        file_url = f"{base_url}/testing/knowledge/files/{file_record.file_id}/download"
        if preview:
            file_url += "?preview=true"
        
        return ResponseUtil.success(data={
            'file_id': file_record.file_id,
            'file_name': file_record.file_name,
            'file_url': file_url,
            'file_type': KnowledgeService._get_file_type(file_record.file_name),  # 从文件名提取文件类型
            'file_size': file_record.file_size,
            'process_status': file_record.process_status,
            'doc_id': file_record.doc_id
        })
    except Exception as e:
        logger.error(f'获取RAG文档文件信息失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.get(
    '/processor/status',
    summary='获取知识库文件处理器状态',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def get_processor_status(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取知识库文件处理器状态和待处理文件统计"""
    try:
        from module_testing.service.knowledge_processor import get_processor
        from sqlalchemy import select, func
        from module_testing.entity.do.knowledge_do import TestKnowledgeFile
        
        processor = get_processor()
        processor_running = processor is not None and processor.running if processor else False
        
        # 统计待处理文件数量
        async with db.begin():
            pending_count_result = await db.execute(
                select(func.count(TestKnowledgeFile.file_id)).where(
                    TestKnowledgeFile.process_status == 'pending'
                )
            )
            pending_count = pending_count_result.scalar() or 0
            
            processing_count_result = await db.execute(
                select(func.count(TestKnowledgeFile.file_id)).where(
                    TestKnowledgeFile.process_status == 'processing'
                )
            )
            processing_count = processing_count_result.scalar() or 0
            
            failed_count_result = await db.execute(
                select(func.count(TestKnowledgeFile.file_id)).where(
                    TestKnowledgeFile.process_status == 'failed'
                )
            )
            failed_count = failed_count_result.scalar() or 0
        
        return ResponseUtil.success(data={
            'processor_running': processor_running,
            'processor_exists': processor is not None,
            'pending_files_count': pending_count,
            'processing_files_count': processing_count,
            'failed_files_count': failed_count,
            'message': '处理器运行中' if processor_running else '处理器未运行或已停止'
        })
    except Exception as e:
        logger.error(f'获取处理器状态失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


@knowledge_controller.post(
    '/processor/restart',
    summary='重启知识库文件处理器',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:list')],
)
async def restart_processor(
    request: Request,
) -> Response:
    """重启知识库文件处理器"""
    try:
        from module_testing.service.knowledge_processor import stop_processor, start_processor
        
        # 停止现有处理器
        await stop_processor()
        await asyncio.sleep(1)  # 等待1秒确保完全停止
        
        # 启动新处理器
        await start_processor(check_interval=10)
        
        return ResponseUtil.success(data={'message': '处理器重启成功'})
    except Exception as e:
        logger.error(f'重启处理器失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'重启失败: {str(e)}')


@knowledge_controller.get(
    '/{knowledge_id}/rag-documents',
    summary='获取知识库RAG处理后的文档列表',
    response_model=DataResponseModel[dict],
    dependencies=[UserInterfaceAuthDependency('testing:knowledge:files')],
)
async def get_knowledge_rag_documents(
    request: Request,
    knowledge_id: Annotated[int, Path(description='知识库ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    status_filter: Optional[str] = Query(None, description='状态过滤：PENDING/PROCESSING/PREPROCESSED/PROCESSED/FAILED'),
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(50, ge=10, le=200, description='每页数量'),
    sort_field: str = Query('updated_at', description='排序字段'),
    sort_direction: str = Query('desc', description='排序方向'),
) -> Response:
    """获取知识库RAG处理后的文档列表"""
    try:
        from module_testing.dao.knowledge_dao import KnowledgeDao
        # 获取知识库信息
        knowledge = await KnowledgeDao.select_knowledge_by_id(db, knowledge_id)
        if not knowledge:
            return ResponseUtil.error(msg='知识库不存在')
        
        # 获取RAG处理后的文档列表
        lightrag_manager = get_lightrag_manager()
        result = await lightrag_manager.get_documents_paginated(
            collection_name=knowledge.collection_name,
            status_filter=status_filter,
            page=page,
            page_size=page_size,
            sort_field=sort_field,
            sort_direction=sort_direction
        )
        
        return ResponseUtil.success(data=result)
    except Exception as e:
        logger.error(f'获取RAG文档列表失败: {e}', exc_info=True)
        return ResponseUtil.error(msg=f'查询失败: {str(e)}')


