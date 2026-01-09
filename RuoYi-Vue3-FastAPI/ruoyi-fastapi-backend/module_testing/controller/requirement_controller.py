"""
测试需求控制器(Controller)
"""
from typing import Annotated

from fastapi import Body, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.router import APIRouterPro
from common.aspect.pre_auth import PreAuthDependency, CurrentUserDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.db_seesion import DBSessionDependency
from common.annotation.log_annotation import Log
from common.enums import BusinessType
from common.vo import PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.response_util import ResponseUtil
from utils.log_util import logger

from module_testing.entity.vo.requirement_vo import (
    RequirementModel,
    RequirementPageQueryModel,
    RequirementAddModel,
    RequirementUpdateModel,
    GenerateScriptFromRequirementModel,
    AnalyzeRequirementModel
)
from module_testing.service.requirement_service import RequirementService


requirement_controller = APIRouterPro(
    prefix='/api/testing/requirement',
    order_num=25,
    tags=['测试管理-需求管理'],
    dependencies=[PreAuthDependency()],
    auto_register=True,
)


@requirement_controller.get(
    '/list',
    summary='获取需求分页列表',
    response_model=PageResponseModel[RequirementModel],
    dependencies=[UserInterfaceAuthDependency('testing:requirement:list')]
)
@Log(title='查询需求列表', business_type=BusinessType.QUERY)
async def get_requirement_list(
    request: Request,
    query: Annotated[RequirementPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取需求分页列表"""
    try:
        query_dict = query.model_dump()
        result = await RequirementService.get_requirement_list(db, query_dict, is_page=True)
        logger.info(f'获取需求列表成功，共 {result["total"]} 条')
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        logger.error(f'获取需求列表失败: {e}')
        return ResponseUtil.failure(msg=f'获取需求列表失败: {str(e)}')


@requirement_controller.get(
    '/{requirement_id}',
    summary='获取需求详情',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:requirement:query')]
)
@Log(title='查询需求详情', business_type=BusinessType.QUERY)
async def get_requirement_detail(
    request: Request,
    requirement_id: int,
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取需求详情"""
    try:
        requirement = await RequirementService.get_requirement_by_id(db, requirement_id)
        if not requirement:
            return ResponseUtil.failure(msg=f'需求不存在: {requirement_id}')
        
        # 转换为字典
        requirement_dict = {
            'requirement_id': requirement.requirement_id,
            'project_id': requirement.project_id,
            'requirement_name': requirement.requirement_name,
            'requirement_type': requirement.requirement_type,
            'description': requirement.description,
            'acceptance_criteria': requirement.acceptance_criteria,
            'priority': requirement.priority,
            'status': requirement.status,
            'tags': requirement.tags,
            'attachments': requirement.attachments,
            'create_by': requirement.create_by,
            'create_time': requirement.create_time,
            'update_by': requirement.update_by,
            'update_time': requirement.update_time,
            'remark': requirement.remark
        }
        
        return ResponseUtil.success(dict_content=requirement_dict)
    except Exception as e:
        logger.error(f'获取需求详情失败: {e}')
        return ResponseUtil.failure(msg=f'获取需求详情失败: {str(e)}')


@requirement_controller.post(
    '',
    summary='新增需求',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:requirement:add')]
)
@Log(title='新增需求', business_type=BusinessType.INSERT)
async def create_requirement(
    request: Request,
    body: Annotated[RequirementAddModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """新增需求"""
    try:
        requirement_data = body.model_dump()
        requirement = await RequirementService.create_requirement(
            db=db,
            requirement_data=requirement_data,
            current_user=current_user.user.user_name if current_user and current_user.user else None
        )
        
        return ResponseUtil.success(msg='创建需求成功', dict_content={
            'requirement_id': requirement.requirement_id,
            'requirement_name': requirement.requirement_name
        })
    except Exception as e:
        logger.error(f'创建需求失败: {e}')
        return ResponseUtil.failure(msg=f'创建需求失败: {str(e)}')


@requirement_controller.put(
    '',
    summary='修改需求',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:requirement:edit')]
)
@Log(title='修改需求', business_type=BusinessType.UPDATE)
async def update_requirement(
    request: Request,
    body: Annotated[RequirementUpdateModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """修改需求"""
    try:
        requirement_data = body.model_dump(exclude_none=True)
        requirement_id = requirement_data.pop('requirement_id')
        
        requirement = await RequirementService.update_requirement(
            db=db,
            requirement_id=requirement_id,
            requirement_data=requirement_data,
            current_user=current_user.user.user_name if current_user and current_user.user else None
        )
        
        return ResponseUtil.success(msg='更新需求成功', dict_content={
            'requirement_id': requirement.requirement_id
        })
    except Exception as e:
        logger.error(f'更新需求失败: {e}')
        return ResponseUtil.failure(msg=f'更新需求失败: {str(e)}')


@requirement_controller.delete(
    '/{requirement_ids}',
    summary='删除需求',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:requirement:remove')]
)
@Log(title='删除需求', business_type=BusinessType.DELETE)
async def delete_requirements(
    request: Request,
    requirement_ids: str,
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除需求"""
    try:
        ids = [int(id_str) for id_str in requirement_ids.split(',')]
        count = await RequirementService.delete_requirements(db, ids)
        
        return ResponseUtil.success(msg=f'删除需求成功，共 {count} 条')
    except Exception as e:
        logger.error(f'删除需求失败: {e}')
        return ResponseUtil.failure(msg=f'删除需求失败: {str(e)}')


@requirement_controller.post(
    '/generate/{requirement_id}',
    summary='从需求生成脚本（AI功能）',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:requirement:generate')]
)
@Log(title='AI生成脚本', business_type=BusinessType.INSERT)
async def generate_script_from_requirement(
    request: Request,
    requirement_id: int,
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    body: Annotated[dict, Body()] = {},
) -> Response:
    """
    从需求生成脚本（核心AI功能）
    
    请求体：
    {
        "config": {  // 可选配置
            "vus": 10,
            "duration": "30s",
            ...
        },
        "use_rag": true  // 是否使用RAG增强
    }
    """
    try:
        config = body.get('config', {})
        use_rag = body.get('use_rag', True)
        
        result = await RequirementService.generate_script_from_requirement(
            db=db,
            requirement_id=requirement_id,
            config=config,
            use_rag=use_rag,
            current_user=current_user.user_name
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                msg='生成脚本成功',
                dict_content={
                    'script_id': result['script_id'],
                    'script_name': result['script_name'],
                    'script_path': result['script_path'],
                    'agent_id': result['agent_id'],
                    'mode': result['mode']
                }
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '生成失败'))
    
    except Exception as e:
        logger.error(f'从需求生成脚本失败: {e}')
        return ResponseUtil.failure(msg=f'生成失败: {str(e)}')


@requirement_controller.post(
    '/analyze/{requirement_id}',
    summary='AI分析需求',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:requirement:analyze')]
)
@Log(title='AI分析需求', business_type=BusinessType.OTHER)
async def analyze_requirement(
    request: Request,
    requirement_id: int,
    db: Annotated[AsyncSession, DBSessionDependency()],
    body: Annotated[dict, Body()] = {},
) -> Response:
    """
    AI分析需求
    
    请求体：
    {
        "analyze_type": "feasibility"  // 分析类型：feasibility/complexity/risk
    }
    """
    try:
        analyze_type = body.get('analyze_type', 'feasibility')
        
        result = await RequirementService.analyze_requirement(
            db=db,
            requirement_id=requirement_id,
            analyze_type=analyze_type
        )
        
        if result.get('success'):
            return ResponseUtil.success(
                msg='分析完成',
                dict_content={
                    'analyze_type': result['analyze_type'],
                    'analysis': result['analysis'],
                    'agent_id': result['agent_id']
                }
            )
        else:
            return ResponseUtil.failure(msg=result.get('error', '分析失败'))
    
    except Exception as e:
        logger.error(f'AI分析需求失败: {e}')
        return ResponseUtil.failure(msg=f'分析失败: {str(e)}')


@requirement_controller.get(
    '/statistics',
    summary='获取需求统计信息',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:requirement:list')]
)
@Log(title='查询需求统计', business_type=BusinessType.QUERY)
async def get_requirement_statistics(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    project_id: int = Query(None, description='项目ID'),
) -> Response:
    """获取需求统计信息"""
    try:
        stats = await RequirementService.get_requirement_statistics(db, project_id)
        return ResponseUtil.success(dict_content=stats)
    except Exception as e:
        logger.error(f'获取需求统计失败: {e}')
        return ResponseUtil.failure(msg=f'获取统计信息失败: {str(e)}')

