"""
Agent控制器
提供AI Agent相关的API接口
"""
from typing import Annotated

from fastapi import Body, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.router import APIRouterPro
from common.aspect.pre_auth import PreAuthDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency
from common.annotation.log_annotation import Log
from common.enums import BusinessType
from common.vo import ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.response_util import ResponseUtil
from utils.log_util import logger

from module_testing.agents.agent_manager import get_agent_manager, reset_agent_manager

agent_controller = APIRouterPro(
    prefix='/testing/agent',
    order_num=40,
    tags=['测试管理-AI Agent管理'],
    dependencies=[PreAuthDependency()],
    auto_register=True
)


# ============== Agent 信息接口 ==============

@agent_controller.get(
    '/list',
    summary='获取可用Agent列表',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:list')]
)
async def get_agent_list(
    request: Request,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取所有可用的AI Agent列表"""
    try:
        agent_manager = get_agent_manager()
        agents = await agent_manager.list_available_agents()
        
        return ResponseUtil.success(dict_content={
            'agents': agents,
            'total': len(agents)
        })
    except Exception as e:
        logger.error(f'获取Agent列表失败: {e}')
        return ResponseUtil.failure(msg=f'获取Agent列表失败: {str(e)}')


@agent_controller.get(
    '/info/{agent_type}',
    summary='获取Agent详情',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:query')]
)
async def get_agent_info(
    request: Request,
    agent_type: str,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取指定Agent的详细信息"""
    try:
        agent_manager = get_agent_manager()
        info = await agent_manager.get_agent_info(agent_type)
        
        if info:
            return ResponseUtil.success(dict_content=info)
        else:
            return ResponseUtil.failure(msg=f'Agent不存在: {agent_type}')
    except Exception as e:
        logger.error(f'获取Agent信息失败: {e}')
        return ResponseUtil.failure(msg=f'获取Agent信息失败: {str(e)}')


@agent_controller.get(
    '/status',
    summary='获取Agent服务状态',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:query')]
)
async def get_service_status(
    request: Request,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """获取Agent服务状态（模式、连接状态等）"""
    try:
        agent_manager = get_agent_manager()
        status = await agent_manager.get_service_status()
        
        return ResponseUtil.success(dict_content=status)
    except Exception as e:
        logger.error(f'获取服务状态失败: {e}')
        return ResponseUtil.failure(msg=f'获取服务状态失败: {str(e)}')


@agent_controller.post(
    '/reconnect',
    summary='重新连接Agent服务',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:edit')]
)
@Log(title='重连Agent服务', business_type=BusinessType.UPDATE)
async def reconnect_service(
    request: Request,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """重新初始化Agent连接"""
    try:
        agent_manager = await reset_agent_manager()
        status = await agent_manager.get_service_status()
        
        return ResponseUtil.success(
            msg='重连成功',
            dict_content=status
        )
    except Exception as e:
        logger.error(f'重连服务失败: {e}')
        return ResponseUtil.failure(msg=f'重连服务失败: {str(e)}')


# ============== Agent 对话接口 ==============

@agent_controller.post(
    '/chat',
    summary='与Agent对话',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:chat')]
)
@Log(title='Agent对话', business_type=BusinessType.OTHER)
async def chat_with_agent(
    request: Request,
    body: Annotated[dict, Body()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    与指定Agent进行对话
    
    请求体：
    {
        "agent_type": "k6_agent",  // Agent类型
        "message": "请帮我生成一个登录接口的性能测试脚本",  // 用户消息
        "thread_id": null  // 可选，会话ID用于多轮对话
    }
    """
    try:
        agent_type = body.get('agent_type')
        message = body.get('message')
        thread_id = body.get('thread_id')
        
        if not agent_type or not message:
            return ResponseUtil.failure(msg='agent_type和message不能为空')
        
        agent_manager = get_agent_manager()
        result = await agent_manager.chat(agent_type, message, thread_id)
        
        if result.get('success'):
            return ResponseUtil.success(dict_content=result)
        else:
            return ResponseUtil.failure(msg=result.get('error', '对话失败'))
    
    except Exception as e:
        logger.error(f'Agent对话失败: {e}')
        return ResponseUtil.failure(msg=f'对话失败: {str(e)}')


# ============== 脚本生成接口 ==============

@agent_controller.post(
    '/generate',
    summary='AI生成测试脚本',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:generate')]
)
@Log(title='AI生成脚本', business_type=BusinessType.INSERT)
async def generate_script(
    request: Request,
    body: Annotated[dict, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    使用AI Agent生成测试脚本
    
    请求体：
    {
        "agent_type": "k6_agent",  // Agent类型: k6_agent, playwright, api_agent
        "prompt": "生成一个针对登录接口的性能测试，并发10用户，持续30秒",
        "config": {  // 可选配置
            "vus": 10,
            "duration": "30s",
            "target_url": "https://api.example.com/login"
        }
    }
    """
    try:
        agent_type = body.get('agent_type')
        prompt = body.get('prompt')
        config = body.get('config', {})
        
        if not agent_type or not prompt:
            return ResponseUtil.failure(msg='agent_type和prompt不能为空')
        
        agent_manager = get_agent_manager()
        result = await agent_manager.generate_script(agent_type, prompt, config)
        
        if result.get('success'):
            return ResponseUtil.success(dict_content={
                'script_content': result.get('script_content'),
                'agent_id': result.get('agent_id'),
                'mode': result.get('mode')
            })
        else:
            return ResponseUtil.failure(msg=result.get('error', '生成失败'))
    
    except Exception as e:
        logger.error(f'AI生成脚本失败: {e}')
        return ResponseUtil.failure(msg=f'生成失败: {str(e)}')


# ============== 脚本执行接口 ==============

@agent_controller.post(
    '/execute',
    summary='执行测试脚本',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:execute')]
)
@Log(title='执行测试脚本', business_type=BusinessType.OTHER)
async def execute_script(
    request: Request,
    body: Annotated[dict, Body()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    使用AI Agent执行测试脚本
    
    请求体：
    {
        "agent_type": "k6_agent",
        "script_content": "import http from 'k6/http'; ...",
        "config": {  // 可选执行配置
            "vus": 10,
            "duration": "30s"
        }
    }
    """
    try:
        agent_type = body.get('agent_type')
        script_content = body.get('script_content')
        config = body.get('config', {})
        
        if not agent_type or not script_content:
            return ResponseUtil.failure(msg='agent_type和script_content不能为空')
        
        agent_manager = get_agent_manager()
        result = await agent_manager.execute_script(agent_type, script_content, config)
        
        if result.get('success'):
            return ResponseUtil.success(dict_content={
                'result': result.get('result'),
                'agent_id': result.get('agent_id'),
                'mode': result.get('mode')
            })
        else:
            return ResponseUtil.failure(msg=result.get('error', '执行失败'))
    
    except Exception as e:
        logger.error(f'执行脚本失败: {e}')
        return ResponseUtil.failure(msg=f'执行失败: {str(e)}')


# ============== 知识库接口 ==============

@agent_controller.post(
    '/rag/import',
    summary='导入数据到RAG知识库',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:import')]
)
@Log(title='导入RAG数据', business_type=BusinessType.INSERT)
async def import_to_rag(
    request: Request,
    body: Annotated[dict, Body()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    导入数据到RAG知识库
    
    请求体：
    {
        "url": "https://api.example.com/swagger.json",
        "data_type": "api_doc"  // 数据类型: api_doc, web_page
    }
    """
    try:
        url = body.get('url')
        data_type = body.get('data_type', 'api_doc')
        
        if not url:
            return ResponseUtil.failure(msg='url不能为空')
        
        agent_manager = get_agent_manager()
        result = await agent_manager.import_data(url, data_type)
        
        if result.get('success'):
            return ResponseUtil.success(dict_content=result)
        else:
            return ResponseUtil.failure(msg=result.get('error', '导入失败'))
    
    except Exception as e:
        logger.error(f'导入RAG数据失败: {e}')
        return ResponseUtil.failure(msg=f'导入失败: {str(e)}')


@agent_controller.post(
    '/rag/query',
    summary='查询RAG知识库',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:agent:query')]
)
@Log(title='查询RAG知识库', business_type=BusinessType.OTHER)
async def query_rag(
    request: Request,
    body: Annotated[dict, Body()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    查询RAG知识库
    
    请求体：
    {
        "question": "登录接口的请求参数有哪些？"
    }
    """
    try:
        question = body.get('question')
        
        if not question:
            return ResponseUtil.failure(msg='question不能为空')
        
        agent_manager = get_agent_manager()
        result = await agent_manager.query_knowledge(question)
        
        if result.get('success'):
            return ResponseUtil.success(dict_content=result)
        else:
            return ResponseUtil.failure(msg=result.get('error', '查询失败'))
    
    except Exception as e:
        logger.error(f'查询RAG失败: {e}')
        return ResponseUtil.failure(msg=f'查询失败: {str(e)}')

