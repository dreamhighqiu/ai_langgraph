"""
Agent控制器
提供AI Agent相关的API接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.response_util import ResponseUtil
from utils.log_util import logger

from module_testing.agents.agent_manager import get_agent_manager, reset_agent_manager

router = APIRouter(prefix='/testing/agent', tags=['AI Agent管理'])


# ============== Agent 信息接口 ==============

@router.get('/list', summary='获取可用Agent列表')
@CheckUserInterfaceAuth('testing:agent:list')
async def get_agent_list(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
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


@router.get('/info/{agent_type}', summary='获取Agent详情')
@CheckUserInterfaceAuth('testing:agent:query')
async def get_agent_info(
    agent_type: str,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
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


@router.get('/status', summary='获取Agent服务状态')
@CheckUserInterfaceAuth('testing:agent:query')
async def get_service_status(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """获取Agent服务状态（模式、连接状态等）"""
    try:
        agent_manager = get_agent_manager()
        status = await agent_manager.get_service_status()
        
        return ResponseUtil.success(dict_content=status)
    except Exception as e:
        logger.error(f'获取服务状态失败: {e}')
        return ResponseUtil.failure(msg=f'获取服务状态失败: {str(e)}')


@router.post('/reconnect', summary='重新连接Agent服务')
@CheckUserInterfaceAuth('testing:agent:edit')
@Log(title='重连Agent服务', business_type=2)
async def reconnect_service(
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
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

@router.post('/chat', summary='与Agent对话')
@CheckUserInterfaceAuth('testing:agent:chat')
@Log(title='Agent对话', business_type=1)
async def chat_with_agent(
    request: dict,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
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
        agent_type = request.get('agent_type')
        message = request.get('message')
        thread_id = request.get('thread_id')
        
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

@router.post('/generate', summary='AI生成测试脚本')
@CheckUserInterfaceAuth('testing:agent:generate')
@Log(title='AI生成脚本', business_type=1)
async def generate_script(
    request: dict,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
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
        agent_type = request.get('agent_type')
        prompt = request.get('prompt')
        config = request.get('config', {})
        
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

@router.post('/execute', summary='执行测试脚本')
@CheckUserInterfaceAuth('testing:agent:execute')
@Log(title='执行测试脚本', business_type=1)
async def execute_script(
    request: dict,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
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
        agent_type = request.get('agent_type')
        script_content = request.get('script_content')
        config = request.get('config', {})
        
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

@router.post('/rag/import', summary='导入数据到RAG知识库')
@CheckUserInterfaceAuth('testing:agent:import')
@Log(title='导入RAG数据', business_type=1)
async def import_to_rag(
    request: dict,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    导入数据到RAG知识库
    
    请求体：
    {
        "url": "https://api.example.com/swagger.json",
        "data_type": "api_doc"  // 数据类型: api_doc, web_page
    }
    """
    try:
        url = request.get('url')
        data_type = request.get('data_type', 'api_doc')
        
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


@router.post('/rag/query', summary='查询RAG知识库')
@CheckUserInterfaceAuth('testing:agent:query')
async def query_rag(
    request: dict,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    """
    查询RAG知识库
    
    请求体：
    {
        "question": "登录接口的请求参数有哪些？"
    }
    """
    try:
        question = request.get('question')
        
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

