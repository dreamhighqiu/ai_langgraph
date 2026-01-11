"""
AI 聊天控制器 - 提供与 LangGraph Agent 交互的统一接口
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from typing import Any as AnyType
from uuid import UUID
import json
import uuid as uuid_module
from datetime import datetime

from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_testing.agents.langgraph_client import get_langgraph_client
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/ai-chat", tags=["AI 聊天"])


class CreateThreadRequest(BaseModel):
    """创建对话线程请求"""
    assistant_id: str
    metadata: Optional[Dict[str, Any]] = None


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    assistant_id: str
    message: str
    thread_id: Optional[str] = None
    project_id: Optional[int] = None
    folder_id: Optional[int] = None
    use_rag: bool = False
    knowledge_base_id: Optional[int] = Field(None, description="知识库ID（用于RAG检索）")
    config: Optional[Dict[str, Any]] = None
    stream: bool = True


class StreamMessageRequest(BaseModel):
    """流式发送消息请求"""
    assistant_id: str
    message: str
    thread_id: Optional[str] = None
    project_id: Optional[int] = Field(None, description="项目ID")
    folder_id: Optional[int] = Field(None, description="文件夹ID")
    use_rag: bool = Field(False, description="是否使用RAG增强")
    knowledge_base_id: Optional[int] = Field(None, description="知识库ID（用于RAG检索）")
    stream: bool = Field(True, description="是否流式响应")


class UpdateThreadRequest(BaseModel):
    """更新线程请求"""
    metadata: Optional[Dict[str, Any]] = None
    values: Optional[Dict[str, Any]] = None


@router.get("/health")
async def check_health():
    """检查 LangGraph 服务健康状态"""
    try:
        client = get_langgraph_client()
        is_healthy = await client.check_health()
        
        if is_healthy:
            return ResponseUtil.success(msg="LangGraph 服务正常")
        else:
            return ResponseUtil.failure(msg="LangGraph 服务不可用")
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return ResponseUtil.failure(msg=f"健康检查失败: {str(e)}")


@router.get("/assistants")
async def list_assistants():
    """获取所有可用的 Assistant 列表"""
    try:
        client = get_langgraph_client()
        assistants = await client.list_assistants()
        return ResponseUtil.success(data=assistants)
    except Exception as e:
        logger.error(f"获取 Assistant 列表失败: {e}")
        return ResponseUtil.failure(msg=f"获取失败: {str(e)}")


@router.get("/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    """获取指定 Assistant 的详细信息"""
    try:
        client = get_langgraph_client()
        assistant = await client.get_assistant(assistant_id)
        
        if assistant:
            return ResponseUtil.success(data=assistant)
        else:
            return ResponseUtil.failure(msg="Assistant 不存在")
    except Exception as e:
        logger.error(f"获取 Assistant 详情失败: {e}")
        return ResponseUtil.failure(msg=f"获取失败: {str(e)}")


@router.post("/threads")
async def create_thread(request: CreateThreadRequest):
    """创建新的对话线程"""
    try:
        client = get_langgraph_client()
        thread_id = await client.create_thread()
        
        if thread_id:
            return ResponseUtil.success(data={"thread_id": thread_id})
        else:
            return ResponseUtil.failure(msg="创建线程失败")
    except Exception as e:
        logger.error(f"创建线程失败: {e}")
        return ResponseUtil.failure(msg=f"创建失败: {str(e)}")


@router.get("/threads")
async def list_threads():
    """获取线程列表"""
    try:
        # TODO: 实现线程列表查询
        # 目前 LangGraph Client 没有 list_threads 方法
        # 可以返回空列表或从数据库查询
        return ResponseUtil.success(data=[])
    except Exception as e:
        logger.error(f"获取线程列表失败: {e}")
        return ResponseUtil.failure(msg=f"获取失败: {str(e)}")


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """删除线程"""
    try:
        # TODO: 实现线程删除
        # LangGraph Client 可能没有 delete_thread 方法
        # 可以标记为已删除或从数据库删除
        return ResponseUtil.success(msg="线程已删除")
    except Exception as e:
        logger.error(f"删除线程失败: {e}")
        return ResponseUtil.failure(msg=f"删除失败: {str(e)}")


class ResumeInterruptRequest(BaseModel):
    """恢复中断请求"""
    thread_id: str
    assistant_id: str
    resume_value: AnyType


@router.post("/resume")
async def resume_interrupt(request: ResumeInterruptRequest):
    """恢复中断的执行"""
    try:
        client = get_langgraph_client()
        # TODO: 实现中断恢复
        # LangGraph Client 需要支持 resume 功能
        return ResponseUtil.success(msg="中断已恢复")
    except Exception as e:
        logger.error(f"恢复中断失败: {e}")
        return ResponseUtil.failure(msg=f"恢复失败: {str(e)}")


@router.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """获取线程状态"""
    try:
        client = get_langgraph_client()
        state = await client.get_thread_state(thread_id)
        
        if state:
            return ResponseUtil.success(data=state)
        else:
            return ResponseUtil.failure(msg="获取线程状态失败")
    except Exception as e:
        logger.error(f"获取线程状态失败: {e}")
        return ResponseUtil.failure(msg=f"获取失败: {str(e)}")


@router.get("/threads/{thread_id}/history")
async def get_thread_history(thread_id: str):
    """获取线程的对话历史"""
    try:
        client = get_langgraph_client()
        history = await client.get_thread_history(thread_id)
        return ResponseUtil.success(data=history)
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        return ResponseUtil.failure(msg=f"获取失败: {str(e)}")


@router.post("/chat")
async def send_message(request: SendMessageRequest):
    """
    发送消息给 Agent
    支持流式和非流式两种模式
    """
    try:
        client = get_langgraph_client()
        
        # 构建配置
        config = request.config or {}
        if request.project_id:
            config['project_id'] = request.project_id
        if request.folder_id:
            config['folder_id'] = request.folder_id
        if request.use_rag:
            config['use_rag'] = True
        if request.knowledge_base_id:
            config['knowledge_base_id'] = request.knowledge_base_id
        
        if request.stream:
            # 流式响应
            async def stream_generator():
                try:
                    async for chunk in client.stream_agent(
                        assistant_id=request.assistant_id,
                        message=request.message,
                        thread_id=request.thread_id,
                        config=config
                    ):
                        # 转换为 SSE 格式
                        yield f"data: {json.dumps(chunk)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"流式响应错误: {e}")
                    error_chunk = {"error": str(e)}
                    yield f"data: {json.dumps(error_chunk)}\n\n"
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # 非流式响应
            result = await client.invoke_agent(
                assistant_id=request.assistant_id,
                message=request.message,
                thread_id=request.thread_id,
                config=config
            )
            
            if result.get('success'):
                return ResponseUtil.success(data=result)
            else:
                return ResponseUtil.failure(msg=result.get('error', '调用失败'))
                
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return ResponseUtil.failure(msg=f"发送失败: {str(e)}")


@router.post("/stream")
async def stream_message(request: StreamMessageRequest):
    """
    流式发送消息给 Agent（SSE）
    用于前端实时展示 AI 响应
    
    支持的事件类型：
    - thread_id: 线程ID
    - content: 文本内容
    - tool_call: 工具调用开始
    - tool_result: 工具调用结果
    - todos: 任务列表更新
    - files: 文件列表更新
    - interrupt: 中断请求
    - error: 错误信息
    """
    try:
        client = get_langgraph_client()
        thread_id = request.thread_id
        
        # 如果没有 thread_id，创建一个新的
        if not thread_id:
            thread_id = await client.create_thread()
            if not thread_id:
                thread_id = f"thread_{uuid_module.uuid4().hex[:12]}"
        
        # 构建配置
        config = {}
        if request.project_id:
            config['project_id'] = request.project_id
        if request.folder_id:
            config['folder_id'] = request.folder_id
        if request.use_rag:
            config['use_rag'] = True
        if request.knowledge_base_id:
            config['knowledge_base_id'] = request.knowledge_base_id
        
        async def event_generator():
            """SSE 事件生成器"""
            try:
                # 发送 thread_id
                yield f"data: {json.dumps({'type': 'thread_id', 'thread_id': thread_id})}\n\n"
                
                accumulated_content = ""
                
                # 调用 Agent
                async for chunk in client.stream_agent(
                    assistant_id=request.assistant_id,
                    message=request.message,
                    thread_id=thread_id,
                    config=config
                ):
                    # 处理错误
                    if 'error' in chunk:
                        yield f"data: {json.dumps({'type': 'error', 'error': chunk['error']})}\n\n"
                        continue
                    
                    # 处理消息内容
                    if 'messages' in chunk and isinstance(chunk['messages'], list):
                        for msg in chunk['messages']:
                            if msg.get('type') == 'ai' or msg.get('role') == 'assistant':
                                content = msg.get('content', '')
                                # 处理复杂的 content 格式
                                if isinstance(content, list):
                                    for item in content:
                                        if isinstance(item, dict):
                                            if item.get('type') == 'text':
                                                text = item.get('text', '')
                                                if text and text != accumulated_content:
                                                    new_content = text[len(accumulated_content):] if text.startswith(accumulated_content) else text
                                                    if new_content:
                                                        yield f"data: {json.dumps({'type': 'content', 'content': new_content})}\n\n"
                                                        accumulated_content = text
                                            elif item.get('type') == 'tool_use':
                                                yield f"data: {json.dumps({'type': 'tool_call', 'id': item.get('id', ''), 'name': item.get('name', ''), 'args': item.get('input', {})})}\n\n"
                                elif isinstance(content, str) and content:
                                    if content != accumulated_content:
                                        new_content = content[len(accumulated_content):] if content.startswith(accumulated_content) else content
                                        if new_content:
                                            yield f"data: {json.dumps({'type': 'content', 'content': new_content})}\n\n"
                                            accumulated_content = content
                                
                                # 处理工具调用
                                tool_calls = msg.get('tool_calls', [])
                                for tc in tool_calls:
                                    yield f"data: {json.dumps({'type': 'tool_call', 'id': tc.get('id', ''), 'name': tc.get('name', ''), 'args': tc.get('args', {})})}\n\n"
                            
                            elif msg.get('type') == 'tool' or msg.get('role') == 'tool':
                                yield f"data: {json.dumps({'type': 'tool_result', 'id': msg.get('tool_call_id', ''), 'name': msg.get('name', ''), 'result': msg.get('content', '')})}\n\n"
                    
                    # 处理直接的 content
                    elif 'content' in chunk:
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk['content']})}\n\n"
                    
                    # 处理工具调用
                    elif 'tool_call' in chunk or chunk.get('type') == 'tool_call':
                        yield f"data: {json.dumps({'type': 'tool_call', 'id': chunk.get('id', ''), 'name': chunk.get('name', ''), 'args': chunk.get('args', {})})}\n\n"
                    
                    # 处理工具结果
                    elif 'tool_result' in chunk or chunk.get('type') == 'tool_result':
                        yield f"data: {json.dumps({'type': 'tool_result', 'name': chunk.get('name', ''), 'result': chunk.get('result', '')})}\n\n"
                    
                    # 处理 todos
                    elif 'todos' in chunk:
                        yield f"data: {json.dumps({'type': 'todos', 'todos': chunk['todos']})}\n\n"
                    
                    # 处理 files
                    elif 'files' in chunk:
                        yield f"data: {json.dumps({'type': 'files', 'files': chunk['files']})}\n\n"
                    
                    # 处理中断
                    elif 'interrupt' in chunk:
                        yield f"data: {json.dumps({'type': 'interrupt', 'value': chunk['interrupt']})}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"流式响应错误: {e}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except Exception as e:
        logger.error(f"流式消息失败: {e}")
        return ResponseUtil.failure(msg=f"发送失败: {str(e)}")


@router.post("/send")
async def send_non_stream_message(request: StreamMessageRequest):
    """
    非流式发送消息给 Agent
    用于兼容不支持 SSE 的客户端
    """
    try:
        client = get_langgraph_client()
        thread_id = request.thread_id
        
        # 如果没有 thread_id，创建一个新的
        if not thread_id:
            thread_id = await client.create_thread()
            if not thread_id:
                thread_id = f"thread_{uuid_module.uuid4().hex[:12]}"
        
        # 构建配置
        config = {}
        if request.project_id:
            config['project_id'] = request.project_id
        if request.folder_id:
            config['folder_id'] = request.folder_id
        if request.use_rag:
            config['use_rag'] = True
        if request.knowledge_base_id:
            config['knowledge_base_id'] = request.knowledge_base_id
        
        # 调用 Agent
        result = await client.invoke_agent(
            assistant_id=request.assistant_id,
            message=request.message,
            thread_id=thread_id,
            config=config
        )
        
        if result.get('success'):
            return ResponseUtil.success(data={
                'content': result.get('content', ''),
                'thread_id': thread_id,
                'messages': result.get('messages', [])
            })
        else:
            return ResponseUtil.failure(msg=result.get('error', '调用失败'))
            
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return ResponseUtil.failure(msg=f"发送失败: {str(e)}")

